# File: backend/clients/elevenlabs_client.py
# Enhanced ElevenLabs TTS Client with Robust Fallback System

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
import json

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
            "happy": {
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
            },
            "calm": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "settings": {"stability": 0.85, "similarity_boost": 0.70}
            }
        }
        
        @classmethod
        def get_voice_config(cls, emotion: str) -> Dict[str, Any]:
            return cls.VOICE_EMOTION_MAPPING.get(emotion, cls.VOICE_EMOTION_MAPPING["neutral"])
    
    config = FallbackConfig()

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    """Enhanced ElevenLabs TTS client with robust fallback system"""
    
    def __init__(self):
        """Initialize ElevenLabs client with enhanced fallback capabilities"""
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = config.ELEVENLABS_BASE_URL
        self.default_voice_id = config.ELEVENLABS_VOICE_ID
        self.model_id = config.ELEVENLABS_MODEL_ID
        self.voice_settings = config.ELEVENLABS_VOICE_SETTINGS
        
        # Track API status
        self.api_available = True
        self.last_error = None
        self.fallback_mode = False
        
        # Create audio storage directory
        os.makedirs("data/audio", exist_ok=True)
        
        logger.info(f"🎵 Enhanced ElevenLabs client initialized with robust fallback")
    
    async def health_check(self) -> bool:
        """Enhanced health check with better error handling"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"xi-api-key": self.api_key}
                async with session.get(
                    f"{self.base_url}/voices", 
                    headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.api_available = True
                        self.fallback_mode = False
                        return True
                    elif response.status == 401:
                        error_data = await response.json()
                        logger.warning(f"🔒 ElevenLabs API access restricted: {error_data}")
                        self.api_available = False
                        self.fallback_mode = True
                        self.last_error = "API access restricted - using fallback mode"
                        return False
                    else:
                        logger.warning(f"⚠️ ElevenLabs API returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {str(e)}")
            self.api_available = False
            self.fallback_mode = True
            self.last_error = str(e)
            return False
    
    async def text_to_speech(
        self,
        text: str,
        emotion: str = "neutral",
        voice_id: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhanced text to speech with smart fallback system"""
        
        # Always try fallback first if we know API is unavailable
        if self.fallback_mode or not self.api_available:
            logger.info(f"🔄 Using enhanced fallback mode for {emotion} emotion")
            return await self._create_enhanced_fallback_response(text, emotion)
        
        try:
            # Attempt ElevenLabs API call
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
                
                async with session.post(
                    url, 
                    json=payload, 
                    headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        # Success - save audio file
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
                            "duration_estimate": len(text.split()) * 0.6,
                            "source": "elevenlabs_api"
                        }
                        
                        logger.info(f"✅ Generated speech via ElevenLabs: {filename} ({len(text)} chars)")
                        self.api_available = True
                        self.fallback_mode = False
                        return result
                    
                    elif response.status == 401:
                        # API access restricted
                        error_data = await response.json()
                        logger.warning(f"🔒 ElevenLabs API access restricted: {error_data}")
                        self.api_available = False
                        self.fallback_mode = True
                        self.last_error = "API access restricted"
                        return await self._create_enhanced_fallback_response(text, emotion)
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error {response.status}: {error_text}")
                        return await self._create_enhanced_fallback_response(text, emotion)
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            self.api_available = False
            self.fallback_mode = True
            self.last_error = str(e)
            return await self._create_enhanced_fallback_response(text, emotion)
    
    async def _create_enhanced_fallback_response(self, text: str, emotion: str) -> Dict[str, Any]:
        """Create enhanced fallback response with mock audio data"""
        
        # Generate mock filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fallback_{emotion}_{timestamp}_{text_hash}.json"
        filepath = os.path.join("data/audio", filename)
        
        # Create mock audio metadata file
        mock_data = {
            "text": text,
            "emotion": emotion,
            "word_count": len(text.split()),
            "duration_estimate": len(text.split()) * 0.6,
            "generated_at": datetime.now().isoformat(),
            "voice_characteristics": self._get_voice_characteristics(emotion),
            "fallback_reason": self.last_error or "ElevenLabs API unavailable",
            "instructions": "This is a fallback response. The avatar will still perform movements and captions will be displayed."
        }
        
        # Save mock data
        try:
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(mock_data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save fallback data: {str(e)}")
        
        return {
            "success": True,  # Mark as success for frontend compatibility
            "filename": filename,
            "filepath": filepath,
            "url": f"/audio/{filename}",
            "text": text,
            "emotion": emotion,
            "voice_id": "fallback",
            "voice_settings": self._get_settings_for_emotion(emotion),
            "file_size": len(json.dumps(mock_data)),
            "generated_at": datetime.now().isoformat(),
            "duration_estimate": len(text.split()) * 0.6,
            "source": "enhanced_fallback",
            "is_fallback": True,
            "fallback_reason": self.last_error or "ElevenLabs API unavailable",
            "supports_playback": False,  # Frontend will know not to try audio playback
            "supports_movement": True,   # Movement and captions still work
            "supports_captions": True
        }
    
    def _get_voice_characteristics(self, emotion: str) -> Dict[str, str]:
        """Get voice characteristics for fallback mode"""
        characteristics = {
            "happy": {
                "tone": "Bright and cheerful",
                "pace": "Energetic and upbeat",
                "pitch": "Higher and more expressive"
            },
            "excited": {
                "tone": "Very enthusiastic and dynamic",
                "pace": "Fast and animated",
                "pitch": "High with lots of variation"
            },
            "calm": {
                "tone": "Peaceful and soothing",
                "pace": "Slow and measured",
                "pitch": "Lower and steady"
            },
            "sad": {
                "tone": "Gentle and melancholic",
                "pace": "Slow and deliberate",
                "pitch": "Lower with less variation"
            },
            "anxious": {
                "tone": "Tense and worried",
                "pace": "Variable, sometimes rushed",
                "pitch": "Higher with nervous inflection"
            },
            "neutral": {
                "tone": "Balanced and natural",
                "pace": "Normal conversational speed",
                "pitch": "Mid-range and consistent"
            }
        }
        return characteristics.get(emotion, characteristics["neutral"])
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get current API status and fallback information"""
        return {
            "api_available": self.api_available,
            "fallback_mode": self.fallback_mode,
            "last_error": self.last_error,
            "supports_audio": self.api_available,
            "supports_movement": True,
            "supports_captions": True,
            "recommendation": "Use enhanced fallback mode for full functionality without audio" if self.fallback_mode else "API fully operational"
        }
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices with fallback support"""
        if not self.api_available:
            return self._get_fallback_voices()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"xi-api-key": self.api_key}
                async with session.get(
                    f"{self.base_url}/voices", 
                    headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
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
                        return self._get_fallback_voices()
        
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return self._get_fallback_voices()
    
    def _get_voice_for_emotion(self, emotion: str) -> str:
        """Get appropriate voice ID for emotion"""
        voice_config = config.get_voice_config(emotion)
        return voice_config["voice_id"]
    
    def _get_settings_for_emotion(self, emotion: str) -> Dict[str, Any]:
        """Get voice settings for emotion"""
        voice_config = config.get_voice_config(emotion)
        return voice_config["settings"]
    
    def _get_fallback_voices(self) -> List[Dict[str, Any]]:
        """Return fallback voice list when API is unavailable"""
        return [
            {
                "voice_id": "fallback_calm",
                "name": "Calm Voice (Fallback)",
                "category": "fallback",
                "description": "Simulated calm, soothing voice for therapeutic sessions",
                "preview_url": None,
                "available_for_tiers": ["fallback"],
                "characteristics": self._get_voice_characteristics("calm")
            },
            {
                "voice_id": "fallback_happy",
                "name": "Happy Voice (Fallback)", 
                "category": "fallback",
                "description": "Simulated cheerful, upbeat voice for positive sessions",
                "preview_url": None,
                "available_for_tiers": ["fallback"],
                "characteristics": self._get_voice_characteristics("happy")
            },
            {
                "voice_id": "fallback_neutral",
                "name": "Neutral Voice (Fallback)",
                "category": "fallback",
                "description": "Simulated balanced, natural voice for general use",
                "preview_url": None,
                "available_for_tiers": ["fallback"],
                "characteristics": self._get_voice_characteristics("neutral")
            }
        ]