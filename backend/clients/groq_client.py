# File: backend/clients/groq_client.py
# Groq LLM Client with FIXED imports

import json
import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os
import sys

# Add parent directory to path to import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import Groq client
try:
    from groq import Groq
except ImportError:
    print("⚠️ Groq not installed. Install with: pip install groq")
    Groq = None

# Import config from parent directory
try:
    from config import config
except ImportError:
    # Fallback config if import fails
    class FallbackConfig:
        GROQ_API_KEY = "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"
        GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
        GROQ_MAX_TOKENS = 500
        GROQ_TEMPERATURE = 0.7
        GROQ_PROMPTS = {
            "generate_scenarios": """Generate a realistic EEG scenario JSON with emotion, direction, confidence scores, context, speech, and medical_notes."""
        }
    config = FallbackConfig()

logger = logging.getLogger(__name__)

class GroqClient:
    """Groq LLM client for generating EEG scenarios and processing thoughts"""
    
    def __init__(self):
        """Initialize Groq client with hardcoded API key"""
        self.api_key = config.GROQ_API_KEY
        self.model = config.GROQ_MODEL
        self.max_tokens = config.GROQ_MAX_TOKENS
        self.temperature = config.GROQ_TEMPERATURE
        
        # Initialize Groq client
        try:
            if Groq:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"🤖 Groq client initialized with model: {self.model}")
            else:
                self.client = None
                logger.warning("🤖 Groq client not available")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None
    
    async def health_check(self) -> bool:
        """Check if Groq API is accessible"""
        if not self.client:
            return False
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model,
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Groq health check failed: {str(e)}")
            return False
    
    async def generate_eeg_scenario(self, custom_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a realistic EEG scenario using Groq LLM"""
        if not self.client:
            return self._get_fallback_scenario()
            
        try:
            prompt = """Generate a realistic EEG scenario for a BCI system helping stroke patients communicate through VR avatars.

Return ONLY a JSON object with this exact format:
{
  "emotion": "calm",
  "direction": "forward",
  "emotion_confidence": 0.87,
  "direction_confidence": 0.92,
  "context": "Brief description of patient's mental state",
  "speech": "What the patient wants to communicate (under 20 words)",
  "medical_notes": "Relevant medical context for therapists"
}

Emotions: calm, excited, sad, anxious, neutral
Directions: forward, backward, left, right, stop, up, down
"""
            
            if custom_context:
                prompt += f"\n\nAdditional context: {custom_context}"
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in BCI systems and stroke patient therapy. Generate realistic, medically-appropriate EEG scenarios. Return only valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            scenario_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                start = scenario_text.find('{')
                end = scenario_text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_text = scenario_text[start:end]
                    scenario_data = json.loads(json_text)
                else:
                    scenario_data = json.loads(scenario_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {scenario_text}")
                return self._get_fallback_scenario()
            
            # Add metadata
            scenario_data.update({
                "id": f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            })
            
            logger.info(f"✅ Generated scenario: {scenario_data.get('emotion', 'unknown')} + {scenario_data.get('direction', 'unknown')}")
            return scenario_data
            
        except Exception as e:
            logger.error(f"Error generating scenario: {str(e)}")
            return self._get_fallback_scenario()
    
    def _get_fallback_scenario(self) -> Dict[str, Any]:
        """Return a fallback scenario if Groq API fails"""
        import random
        
        emotions = ["calm", "excited", "sad", "neutral", "anxious"]
        directions = ["forward", "left", "right", "stop", "backward"]
        
        emotion = random.choice(emotions)
        direction = random.choice(directions)
        
        fallback_speeches = {
            ("calm", "forward"): "I feel peaceful and ready to move forward",
            ("excited", "left"): "I'm energized! Let's turn left and explore",
            ("sad", "stop"): "I'm feeling down and need to pause here",
            ("calm", "right"): "Let me calmly turn to the right",
            ("anxious", "backward"): "I'm feeling nervous, can we go back?",
            ("neutral", "forward"): "I want to continue moving ahead",
            ("excited", "forward"): "I'm excited to keep going forward!"
        }
        
        speech = fallback_speeches.get(
            (emotion, direction), 
            f"I feel {emotion} and want to go {direction}"
        )
        
        return {
            "id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "emotion": emotion,
            "direction": direction,
            "emotion_confidence": round(0.7 + random.random() * 0.25, 2),
            "direction_confidence": round(0.65 + random.random() * 0.3, 2),
            "speech": speech,
            "context": f"Fallback scenario - {emotion} patient wanting to {direction}",
            "medical_notes": "Generated locally due to API connectivity issues",
            "generated_at": datetime.now().isoformat(),
            "model_used": "fallback",
            "tokens_used": 0
        }

    async def emotion_to_speech(
        self, 
        emotion: str, 
        direction: str, 
        emotion_confidence: float,
        direction_confidence: float,
        context: Optional[str] = None
    ) -> str:
        """Convert emotion and direction to natural speech using Groq"""
        if not self.client:
            return self._get_fallback_speech(emotion, direction)
            
        try:
            prompt = f"""You are helping a stroke patient communicate through brain-computer interface.

Current brain signal analysis:
- Emotion: {emotion} (confidence: {emotion_confidence:.2f})
- Movement intention: {direction} (confidence: {direction_confidence:.2f})
- Context: {context or 'VR therapy session'}

Generate ONE natural, encouraging sentence (under 20 words) that reflects the patient's emotional state and movement intention.

Examples:
- calm + forward: "I feel peaceful and ready to move ahead"
- excited + left: "I'm energized! Let's explore to the left"
- sad + stop: "I'm feeling down right now, I need a moment to pause"

Generate only the sentence, no additional text."""
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate AI helping stroke patients communicate. Generate encouraging, natural speech that reflects their mental state."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=100,
                temperature=0.7
            )
            
            speech_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            speech_text = speech_text.replace('"', '').replace("'", "").strip()
            
            logger.info(f"✅ Generated speech: '{speech_text}'")
            return speech_text
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return self._get_fallback_speech(emotion, direction)
    
    def _get_fallback_speech(self, emotion: str, direction: str) -> str:
        """Return fallback speech if API fails"""
        fallback_templates = {
            "calm": "I feel calm and want to {direction}",
            "excited": "I'm excited! Let's {direction}",
            "sad": "I'm feeling sad but I'll {direction}",
            "anxious": "I'm anxious but trying to {direction}",
            "neutral": "I want to {direction}"
        }
        
        template = fallback_templates.get(emotion, "I want to {direction}")
        
        direction_mapping = {
            "forward": "move forward",
            "backward": "go back", 
            "left": "turn left",
            "right": "turn right",
            "stop": "stop here",
            "up": "look up",
            "down": "look down"
        }
        
        direction_text = direction_mapping.get(direction, direction)
        return template.format(direction=direction_text)