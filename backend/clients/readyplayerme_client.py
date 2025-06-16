# File: backend/clients/pinecone_client.py
# Minimal Pinecone Client with FIXED imports

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class PineconeClient:
    """Minimal Pinecone client for EEG pattern storage and retrieval"""
    
    def __init__(self):
        """Initialize Pinecone client"""
        try:
            from config import config
            self.api_key = config.PINECONE_API_KEY
            self.index_name = config.PINECONE_INDEX_NAME
            self.dimension = config.PINECONE_DIMENSION
        except ImportError:
            self.api_key = "pcsk_4gtsnm_3XzJTin9pujJRUfnyRPbHtgJ9QHzNsS2fJD6qkdA3AeedFEYtRgYkERuSeNkUp6"
            self.index_name = "pixelpeak-eeg-patterns"
            self.dimension = 384
        
        # Try to import Pinecone
        try:
            from pinecone import Pinecone, ServerlessSpec
            from sentence_transformers import SentenceTransformer
            
            self.pc = Pinecone(api_key=self.api_key)
            self.index = None
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.available = True
            logger.info(f"🗄️ Pinecone client initialized for index: {self.index_name}")
        except ImportError:
            logger.warning("🗄️ Pinecone or SentenceTransformers not installed - using mock mode")
            self.pc = None
            self.index = None
            self.embedder = None
            self.available = False
    
    async def initialize(self):
        """Initialize or create the Pinecone index"""
        if not self.available:
            return False
        
        try:
            # For demo purposes, just return True
            # In production, you would create/connect to the index here
            logger.info("✅ Pinecone index initialized (mock mode)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Pinecone is accessible"""
        return self.available
    
    async def store_eeg_pattern(
        self,
        pattern_id: str,
        emotion: str,
        direction: str,
        context: str = "",
        confidence_scores: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store EEG pattern (mock implementation)"""
        try:
            if not self.available:
                logger.info(f"✅ Stored EEG pattern (mock): {pattern_id} ({emotion}, {direction})")
                return True
            
            # Real implementation would store in Pinecone
            logger.info(f"✅ Stored EEG pattern: {pattern_id} ({emotion}, {direction})")
            return True
            
        except Exception as e:
            logger.error(f"Error storing EEG pattern: {str(e)}")
            return False
    
    async def find_similar_patterns(
        self,
        emotion: str,
        direction: str,
        context: str = "",
        confidence_scores: Optional[Dict[str, float]] = None,
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar EEG patterns (mock implementation)"""
        try:
            if not self.available:
                # Return mock similar patterns
                import random
                
                similar_patterns = []
                for i in range(min(top_k, 3)):
                    similar_patterns.append({
                        "id": f"pattern_{i+1}",
                        "similarity_score": 0.8 + random.random() * 0.15,
                        "emotion": emotion,
                        "direction": direction,
                        "context": f"Similar pattern with {emotion} emotion and {direction} direction",
                        "emotion_confidence": 0.7 + random.random() * 0.25,
                        "direction_confidence": 0.7 + random.random() * 0.25,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {"source": "mock"}
                    })
                
                logger.info(f"✅ Found {len(similar_patterns)} similar patterns (mock) for {emotion}+{direction}")
                return similar_patterns
            
            # Real implementation would search Pinecone
            return []
            
        except Exception as e:
            logger.error(f"Error finding similar patterns: {str(e)}")
            return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics (mock implementation)"""
        try:
            return {
                "total_vector_count": 25,
                "dimension": self.dimension,
                "index_fullness": 0.1,
                "namespaces": {}
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}
    
    async def populate_sample_data(self, count: int = 20) -> bool:
        """Populate index with sample data (mock implementation)"""
        try:
            logger.info(f"✅ Populated {count} sample patterns (mock)")
            return True
        except Exception as e:
            logger.error(f"Error populating sample data: {str(e)}")
            return False
    
    async def close(self):
        """Cleanup connections"""
        logger.info("🛑 Pinecone client closed")


# =============================================================================
# File: backend/clients/readyplayerme_client.py
# Minimal Ready Player Me Client with FIXED imports
# =============================================================================

import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import uuid
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class ReadyPlayerMeClient:
    """Minimal Ready Player Me client for avatar generation"""
    
    def __init__(self):
        """Initialize Ready Player Me client"""
        try:
            from config import config
            self.api_key = config.READY_PLAYER_ME_API_KEY
            self.base_url = config.READY_PLAYER_ME_BASE_URL
            self.subdomain = config.READY_PLAYER_ME_SUBDOMAIN
        except ImportError:
            self.api_key = "sk_live_ktd-hz_DbbOoC5NOVJBeYtktt82coZtsUKLi"
            self.base_url = "https://api.readyplayer.me/v1"
            self.subdomain = "demo"
        
        # Avatar storage directory
        os.makedirs("data/avatars", exist_ok=True)
        
        logger.info(f"👤 Ready Player Me client initialized with subdomain: {self.subdomain}")
    
    async def health_check(self) -> bool:
        """Check if Ready Player Me API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.get(f"{self.base_url}/applications", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Ready Player Me health check failed: {str(e)}")
            return False
    
    async def create_preset_avatar(
        self, 
        preset_type: str = "therapy_assistant",
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create avatar from preset (mock implementation)"""
        try:
            # Mock avatar creation
            avatar_id = f"avatar_{uuid.uuid4().hex[:8]}"
            
            avatar_data = {
                "success": True,
                "avatar_id": avatar_id,
                "avatar_url": f"https://models.readyplayer.me/{avatar_id}.glb",
                "local_path": f"data/avatars/{avatar_id}.glb",
                "preset_type": preset_type,
                "config": customizations or {},
                "created_at": datetime.now().isoformat(),
                "model_format": "glb",
                "animations_included": True,
                "ready_for_vr": True
            }
            
            logger.info(f"✅ Created preset avatar (mock): {avatar_id} ({preset_type})")
            return avatar_data
            
        except Exception as e:
            logger.error(f"Error creating preset avatar: {str(e)}")
            return self._get_fallback_avatar()
    
    async def create_avatar_from_photo(
        self, 
        photo_data: bytes, 
        gender: str = "female",
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """Create avatar from photo (mock implementation)"""
        try:
            avatar_id = f"photo_avatar_{uuid.uuid4().hex[:8]}"
            
            avatar_data = {
                "success": True,
                "avatar_id": avatar_id,
                "avatar_url": f"https://models.readyplayer.me/{avatar_id}.glb",
                "local_path": f"data/avatars/{avatar_id}.glb",
                "gender": gender,
                "style": style,
                "created_at": datetime.now().isoformat(),
                "model_format": "glb",
                "ready_for_vr": True
            }
            
            logger.info(f"✅ Created avatar from photo (mock): {avatar_id}")
            return avatar_data
            
        except Exception as e:
            logger.error(f"Error creating avatar from photo: {str(e)}")
            return self._get_fallback_avatar(gender, style)
    
    async def get_avatar_animations(self, avatar_id: str) -> List[Dict[str, Any]]:
        """Get available animations for avatar (mock implementation)"""
        try:
            animations = self._get_default_animations()
            logger.info(f"✅ Retrieved {len(animations)} animations (mock) for {avatar_id}")
            return animations
        except Exception as e:
            logger.error(f"Error getting avatar animations: {str(e)}")
            return self._get_default_animations()
    
    async def list_user_avatars(self) -> List[Dict[str, Any]]:
        """List all avatars for the user (mock implementation)"""
        try:
            avatars = [
                {
                    "avatar_id": "demo_avatar_1",
                    "name": "Therapy Assistant",
                    "created_at": datetime.now().isoformat(),
                    "status": "ready"
                },
                {
                    "avatar_id": "demo_avatar_2", 
                    "name": "Patient Avatar",
                    "created_at": datetime.now().isoformat(),
                    "status": "ready"
                }
            ]
            
            logger.info(f"✅ Retrieved {len(avatars)} user avatars (mock)")
            return avatars
        except Exception as e:
            logger.error(f"Error listing avatars: {str(e)}")
            return []
    
    async def get_avatar_info(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """Get avatar information by ID (mock implementation)"""
        try:
            return {
                "avatar_id": avatar_id,
                "name": "Mock Avatar",
                "status": "ready",
                "created_at": datetime.now().isoformat(),
                "model_url": f"https://models.readyplayer.me/{avatar_id}.glb"
            }
        except Exception as e:
            logger.error(f"Error getting avatar info: {str(e)}")
            return None
    
    async def delete_avatar(self, avatar_id: str) -> bool:
        """Delete avatar (mock implementation)"""
        try:
            logger.info(f"✅ Deleted avatar (mock): {avatar_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting avatar: {str(e)}")
            return False
    
    def _get_fallback_avatar(self, gender: str = "female", style: str = "realistic") -> Dict[str, Any]:
        """Return fallback avatar data if API fails"""
        fallback_id = f"fallback_{gender}_{style}_{uuid.uuid4().hex[:8]}"
        
        return {
            "success": False,
            "avatar_id": fallback_id,
            "avatar_url": "https://models.readyplayer.me/fallback.glb",
            "local_path": "",
            "gender": gender,
            "style": style,
            "created_at": datetime.now().isoformat(),
            "model_format": "glb",
            "ready_for_vr": True,
            "is_fallback": True,
            "error": "API unavailable, using fallback avatar"
        }
    
    def _get_default_animations(self) -> List[Dict[str, Any]]:
        """Return default animation list"""
        return [
            {
                "id": "idle",
                "name": "Idle",
                "type": "loop",
                "duration": 5.0,
                "description": "Default idle animation",
                "suitable_for_speech": True,
                "emotion_tag": "neutral"
            },
            {
                "id": "talking",
                "name": "Talking",
                "type": "loop", 
                "duration": 3.0,
                "description": "Speaking animation with lip sync",
                "suitable_for_speech": True,
                "emotion_tag": "neutral"
            },
            {
                "id": "happy",
                "name": "Happy",
                "type": "oneshot",
                "duration": 2.0,
                "description": "Happy expression animation",
                "suitable_for_speech": False,
                "emotion_tag": "excited"
            },
            {
                "id": "sad",
                "name": "Sad",
                "type": "oneshot",
                "duration": 2.5,
                "description": "Sad expression animation", 
                "suitable_for_speech": False,
                "emotion_tag": "sad"
            },
            {
                "id": "calm",
                "name": "Calm",
                "type": "loop",
                "duration": 4.0,
                "description": "Peaceful, meditative animation",
                "suitable_for_speech": True,
                "emotion_tag": "calm"
            }
        ]