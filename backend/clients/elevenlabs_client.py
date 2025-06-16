# File: backend/clients/elevenlabs_client.py
# ElevenLabs TTS Client with FIXED imports

import os
import asyncio
import aiofiles
import aiohttp
from typing import Dict, Optional, Any
import logging
from datetime import datetime
import hashlib
import sys
from typing import List

# Add parent directory to path to import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import config from parent directory
try:
    from config import config
except ImportError:
    # Fallback config if import fails
    class FallbackConfig:
        ELEVENLABS_API_KEY = "sk_1d01aed3b1057694cb52588c284a7a6916a7e2ab708ecec1"
        ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
        ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
        ELEVENLABS_MODEL_ID = "eleven_monolingual_v1"
        ELEVENLABS_VOICE_SETTINGS = {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        VOICE_EMOTION_MAPPING = {
            "calm": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "settings": {"stability": 0.85, "similarity_boost": 0.70}
            },
            "excited": {
                "voice_id": "29vD33N1CtxCmqQRPOHJ",
                "settings": {"stability": 0.60, "similarity_boost": 0.85}
            },
            "sad": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "settings": {"stability": 0.90, "similarity_boost": 0.75}
            },
            "anxious": {
                "voice_id": "oWAxZDx7w5VEj9dCyTzz",
                "settings": {"stability": 0.70, "similarity_boost": 0.80}
            },
            "neutral": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "settings": {"stability": 0.75, "similarity_boost": 0.75}
            }
        }
        
        @classmethod
        def get_voice_config(cls, emotion: str) -> Dict[str, Any]:
            return cls.VOICE_EMOTION_MAPPING.get(emotion, cls.VOICE_EMOTION_MAPPING["neutral"])
    
    config = FallbackConfig()

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    """ElevenLabs TTS client for converting text to speech"""
    
    def __init__(self):
        """Initialize ElevenLabs client with hardcoded API key"""
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = config.ELEVENLABS_BASE_URL
        self.default_voice_id = config.ELEVENLABS_VOICE_ID
        self.model_id = config.ELEVENLABS_MODEL_ID
        self.voice_settings = config.ELEVENLABS_VOICE_SETTINGS
        
        # Create audio storage directory
        os.makedirs("data/audio", exist_ok=True)
        
        logger.info(f"🎵 ElevenLabs client initialized with voice: {self.default_voice_id}")
    
    async def health_check(self) -> bool:
        """Check if ElevenLabs API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"xi-api-key": self.api_key}
                async with session.get(f"{self.base_url}/voices", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {str(e)}")
            return False
    
    async def text_to_speech(
        self,
        text: str,
        emotion: str = "neutral",
        voice_id: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert text to speech using ElevenLabs API"""
        try:
            selected_voice_id = voice_id or self._get_voice_for_emotion(emotion)
            voice_settings = custom_settings or self._get_settings_for_emotion(emotion)
            
            # Generate unique filename
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{emotion}_{timestamp}_{text_hash}.mp3"
            filepath = os.path.join("data/audio", filename)
            
            payload = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": voice_settings
            }
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/text-to-speech/{selected_voice_id}"
                
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        result = {
                            "success": True,
                            "filename": filename,
                            "filepath": filepath,
                            "url": f"/audio/{filename}",
                            "text": text,
                            "emotion": emotion,
                            "voice_id": selected_voice_id,
                            "voice_settings": voice_settings,
                            "file_size": os.path.getsize(filepath),
                            "generated_at": datetime.now().isoformat(),
                            "duration_estimate": len(text.split()) * 0.6
                        }
                        
                        logger.info(f"✅ Generated speech: {filename} ({len(text)} chars)")
                        return result
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error {response.status}: {error_text}")
                        return self._get_fallback_audio_response(text, emotion)
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return self._get_fallback_audio_response(text, emotion)
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices from ElevenLabs"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"xi-api-key": self.api_key}
                async with session.get(f"{self.base_url}/voices", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        voices = data.get("voices", [])
                        
                        formatted_voices = []
                        for voice in voices:
                            formatted_voices.append({
                                "voice_id": voice.get("voice_id"),
                                "name": voice.get("name"),
                                "category": voice.get("category"),
                                "description": voice.get("description"),
                                "preview_url": voice.get("preview_url"),
                                "available_for_tiers": voice.get("available_for_tiers", [])
                            })
                        
                        logger.info(f"✅ Retrieved {len(formatted_voices)} voices")
                        return formatted_voices
                    
                    else:
                        logger.error(f"Failed to get voices: {response.status}")
                        return self._get_default_voices()
        
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return self._get_default_voices()
    
    def _get_voice_for_emotion(self, emotion: str) -> str:
        """Get appropriate voice ID for emotion"""
        voice_config = config.get_voice_config(emotion)
        return voice_config["voice_id"]
    
    def _get_settings_for_emotion(self, emotion: str) -> Dict[str, Any]:
        """Get voice settings for emotion"""
        voice_config = config.get_voice_config(emotion)
        return voice_config["settings"]
    
    def _get_default_voices(self) -> List[Dict[str, Any]]:
        """Return default voice list if API fails"""
        return [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "premade",
                "description": "Calm, soothing female voice",
                "preview_url": None,
                "available_for_tiers": ["free", "starter", "creator"]
            },
            {
                "voice_id": "29vD33N1CtxCmqQRPOHJ", 
                "name": "Drew",
                "category": "premade",
                "description": "Energetic male voice",
                "preview_url": None,
                "available_for_tiers": ["free", "starter", "creator"]
            },
            {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Sarah",
                "category": "premade", 
                "description": "Warm, caring female voice",
                "preview_url": None,
                "available_for_tiers": ["free", "starter", "creator"]
            }
        ]
    
    def _get_fallback_audio_response(self, text: str, emotion: str) -> Dict[str, Any]:
        """Return fallback response if TTS fails"""
        filename = f"fallback_{emotion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("data/audio", filename)
        
        # Create a text file as fallback
        try:
            with open(filepath, 'w') as f:
                f.write(f"Fallback TTS: {text}")
        except:
            pass
        
        return {
            "success": False,
            "error": "TTS API unavailable, using fallback",
            "filename": filename,
            "filepath": filepath,
            "url": f"/audio/{filename}",
            "text": text,
            "emotion": emotion,
            "voice_id": "fallback",
            "voice_settings": {},
            "file_size": len(text),
            "generated_at": datetime.now().isoformat(),
            "duration_estimate": len(text.split()) * 0.6,
            "is_fallback": True
        }