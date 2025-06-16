# File: backend/config.py
# PixelPeak Configuration - All API Keys Hardcoded

import os
from typing import Dict, Any

class Config:
    """Application configuration with hardcoded API keys"""
    
    # =============================================================================
    # API KEYS (HARDCODED)
    # =============================================================================
    
    # Groq API Configuration
    GROQ_API_KEY = "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"
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Fastest model
    GROQ_MAX_TOKENS = 500
    GROQ_TEMPERATURE = 0.7
    
    # Pinecone Configuration  
    PINECONE_API_KEY = "pcsk_4gtsnm_3XzJTin9pujJRUfnyRPbHtgJ9QHzNsS2fJD6qkdA3AeedFEYtRgYkERuSeNkUp6"
    PINECONE_ENVIRONMENT = "gcp-starter"  # Free tier
    PINECONE_INDEX_NAME = "pixelpeak-eeg-patterns"
    PINECONE_DIMENSION = 384  # Sentence transformer dimension
    PINECONE_METRIC = "cosine"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = "sk_1d01aed3b1057694cb52588c284a7a6916a7e2ab708ecec1"
    ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
    ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - natural voice
    ELEVENLABS_MODEL_ID = "eleven_monolingual_v1"
    ELEVENLABS_VOICE_SETTINGS = {
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    }
    
    # Ready Player Me Configuration
    READY_PLAYER_ME_API_KEY = "sk_live_ktd-hz_DbbOoC5NOVJBeYtktt82coZtsUKLi"
    READY_PLAYER_ME_BASE_URL = "https://api.readyplayer.me/v1"
    READY_PLAYER_ME_SUBDOMAIN = "demo"  # Your subdomain
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    RELOAD = True
    
    # Database Settings
    REDIS_URL = "redis://localhost:6379"
    REDIS_DB = 0
    REDIS_TTL = 3600  # 1 hour
    
    # File Storage
    AUDIO_STORAGE_PATH = "backend/data/audio"
    SCENARIO_STORAGE_PATH = "backend/data/scenarios"
    EEG_PATTERNS_PATH = "backend/data/eeg_patterns"
    AVATAR_STORAGE_PATH = "backend/data/avatars"
    
    # Audio Settings
    AUDIO_FORMAT = "mp3"
    AUDIO_QUALITY = "high"
    MAX_AUDIO_DURATION = 30  # seconds
    AUDIO_SAMPLE_RATE = 22050
    
    # EEG Simulation Settings
    EEG_CHANNELS = 64
    EEG_SAMPLING_RATE = 256  # Hz
    EEG_WINDOW_SIZE = 1.0  # seconds
    
    # Scenario Generation
    MAX_SCENARIOS_PER_SESSION = 50
    SCENARIO_CACHE_TTL = 1800  # 30 minutes
    
    # =============================================================================
    # LLM PROMPTS
    # =============================================================================
    
    # Groq Prompts for Different Tasks
    GROQ_PROMPTS = {
        "generate_scenarios": """
You are an AI assistant helping create realistic EEG scenarios for a BCI system that helps stroke patients communicate through VR avatars.

Generate a realistic EEG scenario with the following format:

{
  "emotion": "calm|excited|sad|anxious|neutral",
  "direction": "forward|backward|left|right|stop|up|down",
  "emotion_confidence": 0.XX,
  "direction_confidence": 0.XX,
  "context": "Brief description of patient's mental state",
  "speech": "What the patient wants to communicate (under 20 words)",
  "medical_notes": "Relevant medical context for therapists"
}

Make the scenario realistic for a stroke patient in VR therapy. Focus on:
- Genuine emotional states during recovery
- Practical movement intentions
- Encouraging but honest communication
- Appropriate confidence levels (0.6-0.95)

Generate only the JSON, no additional text.
""",

        "emotion_to_speech": """
You are helping a stroke patient communicate through brain-computer interface.

Current brain signal analysis:
- Emotion: {emotion} (confidence: {emotion_confidence})
- Movement intention: {direction} (confidence: {direction_confidence})
- Context: {context}

Generate a natural, encouraging sentence (under 20 words) that reflects:
1. The patient's emotional state
2. Their movement intention
3. Appropriate tone for medical VR therapy

Examples:
- calm + forward: "I feel peaceful and ready to move ahead"
- excited + left: "I'm energized! Let's explore to the left"
- sad + stop: "I'm feeling down right now, I need a moment to pause"

Generate only the sentence, no additional text.
""",

        "context_analysis": """
Analyze the following EEG pattern data and provide context for a stroke patient's mental state:

EEG Features: {eeg_features}
Previous context: {previous_context}

Provide a brief medical context (under 30 words) that would help therapists understand the patient's current state.

Focus on:
- Emotional patterns
- Cognitive load
- Recovery indicators
- Therapy recommendations

Generate only the context text, no additional formatting.
"""
    }
    
    # =============================================================================
    # AVATAR CONFIGURATIONS
    # =============================================================================
    
    AVATAR_CONFIGS = {
        "default_male": {
            "gender": "male",
            "style": "realistic",
            "outfit": "casual",
            "expression": "calm"
        },
        "default_female": {
            "gender": "female", 
            "style": "realistic",
            "outfit": "medical",
            "expression": "encouraging"
        },
        "therapy_assistant": {
            "gender": "female",
            "style": "professional",
            "outfit": "therapist",
            "expression": "supportive"
        }
    }
    
    # =============================================================================
    # VOICE MAPPINGS
    # =============================================================================
    
    VOICE_EMOTION_MAPPING = {
        "calm": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "settings": {"stability": 0.85, "similarity_boost": 0.70}
        },
        "excited": {
            "voice_id": "29vD33N1CtxCmqQRPOHJ",  # Drew  
            "settings": {"stability": 0.60, "similarity_boost": 0.85}
        },
        "sad": {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah
            "settings": {"stability": 0.90, "similarity_boost": 0.75}
        },
        "anxious": {
            "voice_id": "oWAxZDx7w5VEj9dCyTzz",  # Grace
            "settings": {"stability": 0.70, "similarity_boost": 0.80}
        },
        "neutral": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "settings": {"stability": 0.75, "similarity_boost": 0.75}
        }
    }
    
    # =============================================================================
    # CORS AND SECURITY
    # =============================================================================
    
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # Allow all for development
    ]
    
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["*"]
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "backend/logs/pixelpeak.log",
                "mode": "a",
            },
        },
        "loggers": {
            "pixelpeak": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that all API keys are present"""
        return {
            "groq": bool(cls.GROQ_API_KEY and cls.GROQ_API_KEY.startswith("gsk_")),
            "pinecone": bool(cls.PINECONE_API_KEY and cls.PINECONE_API_KEY.startswith("pcsk_")),
            "elevenlabs": bool(cls.ELEVENLABS_API_KEY and cls.ELEVENLABS_API_KEY.startswith("sk_")),
            "ready_player_me": bool(cls.READY_PLAYER_ME_API_KEY and cls.READY_PLAYER_ME_API_KEY.startswith("sk_"))
        }
    
    @classmethod
    def get_voice_config(cls, emotion: str) -> Dict[str, Any]:
        """Get voice configuration for specific emotion"""
        return cls.VOICE_EMOTION_MAPPING.get(emotion, cls.VOICE_EMOTION_MAPPING["neutral"])
    
    @classmethod
    def get_avatar_config(cls, avatar_type: str = "default_female") -> Dict[str, Any]:
        """Get avatar configuration"""
        return cls.AVATAR_CONFIGS.get(avatar_type, cls.AVATAR_CONFIGS["default_female"])

# Create global config instance
config = Config()

# Validate API keys on import
api_key_status = config.validate_api_keys()
print("🔑 API Key Validation:")
for service, status in api_key_status.items():
    print(f"  {service}: {'✅' if status else '❌'}")

if not all(api_key_status.values()):
    print("⚠️  Some API keys are missing or invalid!")
else:
    print("✅ All API keys validated successfully!")