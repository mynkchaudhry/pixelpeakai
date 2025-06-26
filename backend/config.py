# File: backend/config.py
# PixelPeak Configuration - Enhanced with Three.js Avatar Movements and Captions

import os
from typing import Dict, Any

class Config:
    """Application configuration with enhanced Three.js avatar settings"""
    
    # =============================================================================
    # API KEYS (HARDCODED)
    # =============================================================================
    
    # Groq API Configuration
    GROQ_API_KEY = "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"
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_MAX_TOKENS = 500
    GROQ_TEMPERATURE = 0.7
    
    # Pinecone Configuration  
    PINECONE_API_KEY = "pcsk_4gtsnm_3XzJTin9pujJRUfnyRPbHtgJ9QHzNsS2fJD6qkdA3AeedFEYtRgYkERuSeNkUp6"
    PINECONE_ENVIRONMENT = "gcp-starter"
    PINECONE_INDEX_NAME = "pixelpeak-eeg-patterns"
    PINECONE_DIMENSION = 384
    PINECONE_METRIC = "cosine"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"
    
    # ElevenLabs Configuration
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
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    RELOAD = True
    
    # File Storage
    AUDIO_STORAGE_PATH = "backend/data/audio"
    SCENARIO_STORAGE_PATH = "backend/data/scenarios"
    EEG_PATTERNS_PATH = "backend/data/eeg_patterns"
    CAPTIONS_STORAGE_PATH = "backend/data/captions"
    
    # Audio Settings
    AUDIO_FORMAT = "mp3"
    AUDIO_QUALITY = "high"
    MAX_AUDIO_DURATION = 30
    AUDIO_SAMPLE_RATE = 22050
    
    # =============================================================================
    # ENHANCED THREE.JS AVATAR MOVEMENT CONFIGURATIONS
    # =============================================================================
    
    AVATAR_MOVEMENTS = {
        "happy": {
            "action": "walk_and_jump",
            "duration": 5.0,
            "steps": 8,
            "jump_height": 0.3,
            "speed": 1.2,
            "walk_distance": 2.0,
            "description": "Avatar walks forward with joyful bouncing steps",
            "facial_expression": "big_smile",
            "arm_movement": "swing_energetic",
            "body_posture": "upright_confident",
            "head_movement": "slight_nod",
            "speech_words": 20
        },
        "excited": {
            "action": "energetic_gestures",
            "duration": 4.0,
            "gesture_intensity": 1.5,
            "speed": 1.8,
            "description": "Avatar makes energetic hand gestures and body movements",
            "facial_expression": "wide_smile",
            "arm_movement": "wave_enthusiastic",
            "body_posture": "dynamic_bouncing",
            "head_movement": "excited_turn",
            "speech_words": 20
        },
        "calm": {
            "action": "gentle_sway",
            "duration": 6.0,
            "sway_amplitude": 0.1,
            "speed": 0.5,
            "description": "Avatar gently sways with peaceful movements",
            "facial_expression": "serene_smile",
            "arm_movement": "gentle_flow",
            "body_posture": "relaxed_centered",
            "head_movement": "slow_breathing",
            "speech_words": 20
        },
        "sad": {
            "action": "sit_and_slump",
            "duration": 7.0,
            "sit_height": 0.5,
            "slump_angle": 0.3,
            "speed": 0.3,
            "description": "Avatar slowly sits down and slumps forward showing sadness",
            "facial_expression": "downturned_mouth",
            "arm_movement": "hanging_loose",
            "body_posture": "slumped_forward",
            "head_movement": "look_down",
            "speech_words": 20
        },
        "anxious": {
            "action": "nervous_fidget",
            "duration": 5.0,
            "fidget_intensity": 1.2,
            "speed": 2.0,
            "description": "Avatar shows nervous fidgeting and restless movements",
            "facial_expression": "worried_frown",
            "arm_movement": "nervous_touch",
            "body_posture": "tense_shoulders",
            "head_movement": "look_around",
            "speech_words": 20
        },
        "neutral": {
            "action": "idle_breathing",
            "duration": 3.0,
            "breathing_depth": 0.05,
            "speed": 1.0,
            "description": "Avatar stands calmly with natural breathing",
            "facial_expression": "neutral",
            "arm_movement": "natural_rest",
            "body_posture": "balanced_stance",
            "head_movement": "subtle_look",
            "speech_words": 20
        }
    }
    
    # =============================================================================
    # SPEECH AND CAPTION CONFIGURATIONS
    # =============================================================================
    
    SPEECH_TEMPLATES = {
        "happy": [
            "I feel so joyful and energetic today! Life is beautiful and I'm grateful for this moment of happiness and peace.",
            "What a wonderful feeling of pure joy! I'm excited about all the possibilities ahead and feeling incredibly positive right now.",
            "This happiness fills my heart completely! I want to share this amazing energy with everyone around me today."
        ],
        "excited": [
            "I'm absolutely thrilled and can barely contain this energy! Everything seems possible and I'm ready for any adventure that comes.",
            "This excitement is incredible! I feel like I could accomplish anything and I'm buzzing with positive energy and enthusiasm right now.",
            "I'm so energized and excited! This feeling of anticipation and joy is making everything seem brighter and more amazing."
        ],
        "calm": [
            "I feel so peaceful and centered right now. This tranquility brings clarity to my thoughts and serenity to my soul.",
            "What a beautiful sense of calm washes over me. I'm grateful for this moment of stillness and inner peace today.",
            "This calmness feels like a warm embrace. I'm breathing deeply and feeling completely at peace with myself and the world."
        ],
        "sad": [
            "I'm feeling quite heavy and melancholy today. Sometimes we need these quiet moments to process our deeper emotions and feelings.",
            "This sadness feels overwhelming right now. I need some time to sit with these feelings and find comfort in solitude.",
            "I'm going through a difficult emotional time. It's okay to feel sad sometimes and I'm allowing myself this space to heal."
        ],
        "anxious": [
            "I'm feeling quite nervous and restless right now. My mind is racing with worried thoughts and I need to find some calm.",
            "This anxiety is making me feel unsettled. I'm trying to breathe through these uncomfortable feelings and find my center again.",
            "I feel tense and worried about many things. It's challenging but I'm working on managing these anxious thoughts and emotions."
        ],
        "neutral": [
            "I'm feeling steady and balanced today. Not particularly high or low, just existing peacefully in this moment of equilibrium.",
            "This neutral state feels comfortable right now. I'm neither excited nor sad, just present and aware of my surroundings.",
            "I'm in a calm, neutral space today. It's nice to feel balanced and centered without strong emotions pulling me either way."
        ]
    }
    
    # =============================================================================
    # CAPTION STYLING CONFIGURATIONS
    # =============================================================================
    
    CAPTION_STYLES = {
        "happy": {
            "color": "#FFD700",
            "background": "rgba(255, 215, 0, 0.1)",
            "border_color": "#FFD700",
            "font_weight": "bold",
            "animation": "bounce",
            "emoji": "😊"
        },
        "excited": {
            "color": "#FF6B35",
            "background": "rgba(255, 107, 53, 0.1)",
            "border_color": "#FF6B35",
            "font_weight": "bold",
            "animation": "pulse",
            "emoji": "🤩"
        },
        "calm": {
            "color": "#81C784",
            "background": "rgba(129, 199, 132, 0.1)",
            "border_color": "#81C784",
            "font_weight": "normal",
            "animation": "fade",
            "emoji": "😌"
        },
        "sad": {
            "color": "#9E9E9E",
            "background": "rgba(158, 158, 158, 0.1)",
            "border_color": "#9E9E9E",
            "font_weight": "normal",
            "animation": "slow_fade",
            "emoji": "😢"
        },
        "anxious": {
            "color": "#FF8C94",
            "background": "rgba(255, 140, 148, 0.1)",
            "border_color": "#FF8C94",
            "font_weight": "normal",
            "animation": "shake",
            "emoji": "😰"
        },
        "neutral": {
            "color": "#90A4AE",
            "background": "rgba(144, 164, 174, 0.1)",
            "border_color": "#90A4AE",
            "font_weight": "normal",
            "animation": "none",
            "emoji": "😐"
        }
    }
    
    # =============================================================================
    # VOICE MAPPINGS (UPDATED)
    # =============================================================================
    
    VOICE_EMOTION_MAPPING = {
        "happy": {
            "voice_id": "29vD33N1CtxCmqQRPOHJ",  # Drew - energetic
            "settings": {"stability": 0.60, "similarity_boost": 0.85, "style": 0.2}
        },
        "excited": {
            "voice_id": "29vD33N1CtxCmqQRPOHJ",  # Drew
            "settings": {"stability": 0.50, "similarity_boost": 0.90, "style": 0.3}
        },
        "calm": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "settings": {"stability": 0.85, "similarity_boost": 0.70, "style": 0.0}
        },
        "sad": {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah
            "settings": {"stability": 0.90, "similarity_boost": 0.75, "style": 0.1}
        },
        "anxious": {
            "voice_id": "oWAxZDx7w5VEj9dCyTzz",  # Grace
            "settings": {"stability": 0.70, "similarity_boost": 0.80, "style": 0.2}
        },
        "neutral": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "settings": {"stability": 0.75, "similarity_boost": 0.75, "style": 0.0}
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
    # UTILITY METHODS
    # =============================================================================
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that all API keys are present"""
        return {
            "groq": bool(cls.GROQ_API_KEY and cls.GROQ_API_KEY.startswith("gsk_")),
            "pinecone": bool(cls.PINECONE_API_KEY and cls.PINECONE_API_KEY.startswith("pcsk_")),
            "elevenlabs": bool(cls.ELEVENLABS_API_KEY and cls.ELEVENLABS_API_KEY.startswith("sk_"))
        }
    
    @classmethod
    def get_voice_config(cls, emotion: str) -> Dict[str, Any]:
        """Get voice configuration for specific emotion"""
        return cls.VOICE_EMOTION_MAPPING.get(emotion, cls.VOICE_EMOTION_MAPPING["neutral"])
    
    @classmethod
    def get_avatar_movement(cls, emotion: str) -> Dict[str, Any]:
        """Get avatar movement configuration for emotion"""
        return cls.AVATAR_MOVEMENTS.get(emotion, cls.AVATAR_MOVEMENTS["neutral"])
    
    @classmethod
    def get_speech_template(cls, emotion: str) -> str:
        """Get random speech template for emotion"""
        import random
        templates = cls.SPEECH_TEMPLATES.get(emotion, cls.SPEECH_TEMPLATES["neutral"])
        return random.choice(templates)
    
    @classmethod
    def get_caption_style(cls, emotion: str) -> Dict[str, Any]:
        """Get caption styling for emotion"""
        return cls.CAPTION_STYLES.get(emotion, cls.CAPTION_STYLES["neutral"])

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