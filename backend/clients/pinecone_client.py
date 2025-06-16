# File: backend/clients/pinecone_client.py
# Pinecone Vector Database Client with FIXED imports

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json
import uuid
import sys
import os

# Add parent directory to path to import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import config from parent directory with fallback
try:
    from config import config
except ImportError:
    # Fallback config if import fails
    class FallbackConfig:
        PINECONE_API_KEY = "pcsk_4gtsnm_3XzJTin9pujJRUfnyRPbHtgJ9QHzNsS2fJD6qkdA3AeedFEYtRgYkERuSeNkUp6"
        PINECONE_INDEX_NAME = "pixelpeak-eeg-patterns"
        PINECONE_DIMENSION = 384
        PINECONE_METRIC = "cosine"
        PINECONE_CLOUD = "gcp"
        PINECONE_REGION = "us-central1"
    config = FallbackConfig()

logger = logging.getLogger(__name__)

class PineconeClient:
    """Pinecone vector database client for EEG pattern storage and retrieval"""
    
    def __init__(self):
        """Initialize Pinecone client with hardcoded API key"""
        self.api_key = config.PINECONE_API_KEY
        self.index_name = config.PINECONE_INDEX_NAME
        self.dimension = config.PINECONE_DIMENSION
        self.metric = config.PINECONE_METRIC
        
        # Try to import Pinecone and SentenceTransformer
        try:
            from pinecone import Pinecone, ServerlessSpec
            from sentence_transformers import SentenceTransformer
            
            self.pc = Pinecone(api_key=self.api_key)
            self.index = None
            
            # Initialize sentence transformer for embeddings
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
            self.available = True
            
            logger.info(f"🗄️ Pinecone client initialized for index: {self.index_name}")
            
        except ImportError as e:
            logger.warning(f"🗄️ Pinecone or SentenceTransformers not installed: {str(e)}")
            logger.info("🗄️ Running in mock mode - install with: pip install pinecone-client sentence-transformers")
            self.pc = None
            self.index = None
            self.embedder = None
            self.available = False
    
    async def initialize(self):
        """Initialize or create the Pinecone index"""
        if not self.available:
            logger.info("✅ Pinecone initialized (mock mode)")
            return True
            
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                try:
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric=self.metric,
                        spec={
                            "serverless": {
                                "cloud": config.PINECONE_CLOUD if hasattr(config, 'PINECONE_CLOUD') else "gcp",
                                "region": config.PINECONE_REGION if hasattr(config, 'PINECONE_REGION') else "us-central1"
                            }
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not create index: {str(e)}")
                    logger.info("Using mock mode instead")
                    self.available = False
                    return True
                
                # Wait for index to be ready
                logger.info("Waiting for index to be ready...")
                await asyncio.sleep(10)
            
            # Connect to index
            try:
                self.index = self.pc.Index(self.index_name)
                
                # Get index stats
                stats = self.index.describe_index_stats()
                logger.info(f"✅ Connected to index. Total vectors: {stats.total_vector_count}")
            except Exception as e:
                logger.warning(f"Could not connect to index: {str(e)}")
                self.available = False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            logger.info("Falling back to mock mode")
            self.available = False
            return True
    
    async def health_check(self) -> bool:
        """Check if Pinecone is accessible"""
        if not self.available:
            return False
        try:
            if self.index:
                stats = self.index.describe_index_stats()
                return True
            return False
        except Exception as e:
            logger.error(f"Pinecone health check failed: {str(e)}")
            return False
    
    def create_eeg_embedding(
        self, 
        emotion: str, 
        direction: str, 
        context: str = "", 
        confidence_scores: Optional[Dict[str, float]] = None
    ) -> np.ndarray:
        """Create embedding for EEG pattern data"""
        try:
            if not self.available or not self.embedder:
                # Return random embedding as fallback
                return np.random.random(self.dimension)
            
            # Create text representation of EEG pattern
            confidence_text = ""
            if confidence_scores:
                emotion_conf = confidence_scores.get('emotion', 0.0)
                direction_conf = confidence_scores.get('direction', 0.0)
                confidence_text = f" with emotion confidence {emotion_conf:.2f} and direction confidence {direction_conf:.2f}"
            
            eeg_text = f"Patient emotion is {emotion}, movement intention is {direction}{confidence_text}. {context}".strip()
            
            # Generate embedding using sentence transformer
            embedding = self.embedder.encode([eeg_text])[0]
            
            logger.debug(f"Created embedding for: {emotion} + {direction}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating EEG embedding: {str(e)}")
            # Return random embedding as fallback
            return np.random.random(self.dimension)
    
    async def store_eeg_pattern(
        self,
        pattern_id: str,
        emotion: str,
        direction: str,
        context: str = "",
        confidence_scores: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store EEG pattern in Pinecone"""
        try:
            if not self.available or not self.index:
                logger.info(f"✅ Stored EEG pattern (mock): {pattern_id} ({emotion}, {direction})")
                return True
            
            # Create embedding
            embedding = self.create_eeg_embedding(emotion, direction, context, confidence_scores)
            
            # Prepare metadata
            vector_metadata = {
                "emotion": emotion,
                "direction": direction,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "emotion_confidence": confidence_scores.get('emotion', 0.0) if confidence_scores else 0.0,
                "direction_confidence": confidence_scores.get('direction', 0.0) if confidence_scores else 0.0,
            }
            
            # Add custom metadata
            if metadata:
                vector_metadata.update(metadata)
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": pattern_id,
                    "values": embedding.tolist(),
                    "metadata": vector_metadata
                }]
            )
            
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
        """Find similar EEG patterns in the database"""
        try:
            if not self.available or not self.index:
                # Return mock similar patterns
                import random
                
                similar_patterns = []
                for i in range(min(top_k, 3)):
                    similar_patterns.append({
                        "id": f"pattern_{i+1}",
                        "similarity_score": round(0.75 + random.random() * 0.2, 3),
                        "emotion": emotion,
                        "direction": direction,
                        "context": f"Similar {emotion} patient wanting to {direction}",
                        "emotion_confidence": round(0.7 + random.random() * 0.25, 2),
                        "direction_confidence": round(0.7 + random.random() * 0.25, 2),
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {"source": "mock_similarity"}
                    })
                
                logger.info(f"✅ Found {len(similar_patterns)} similar patterns (mock) for {emotion}+{direction}")
                return similar_patterns
            
            # Create query embedding
            query_embedding = self.create_eeg_embedding(emotion, direction, context, confidence_scores)
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )
            
            # Filter and format results
            similar_patterns = []
            for match in search_results.matches:
                if match.score >= min_score:
                    pattern_data = {
                        "id": match.id,
                        "similarity_score": float(match.score),
                        "emotion": match.metadata.get("emotion"),
                        "direction": match.metadata.get("direction"),
                        "context": match.metadata.get("context"),
                        "emotion_confidence": match.metadata.get("emotion_confidence"),
                        "direction_confidence": match.metadata.get("direction_confidence"),
                        "timestamp": match.metadata.get("timestamp"),
                        "metadata": match.metadata
                    }
                    similar_patterns.append(pattern_data)
            
            logger.info(f"✅ Found {len(similar_patterns)} similar patterns for {emotion}+{direction}")
            return similar_patterns
            
        except Exception as e:
            logger.error(f"Error finding similar patterns: {str(e)}")
            # Return mock data as fallback
            return [
                {
                    "id": "fallback_pattern",
                    "similarity_score": 0.8,
                    "emotion": emotion,
                    "direction": direction,
                    "context": f"Fallback pattern for {emotion} + {direction}",
                    "emotion_confidence": 0.75,
                    "direction_confidence": 0.8,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"source": "fallback"}
                }
            ]
    
    async def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific pattern by ID"""
        try:
            if not self.available or not self.index:
                return {
                    "id": pattern_id,
                    "metadata": {"source": "mock"},
                    "values": []
                }
            
            fetch_result = self.index.fetch(ids=[pattern_id])
            
            if pattern_id in fetch_result.vectors:
                vector_data = fetch_result.vectors[pattern_id]
                return {
                    "id": pattern_id,
                    "values": vector_data.values,
                    "metadata": vector_data.metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching pattern {pattern_id}: {str(e)}")
            return None
    
    async def delete_pattern(self, pattern_id: str) -> bool:
        """Delete pattern from database"""
        try:
            if not self.available or not self.index:
                logger.info(f"✅ Deleted pattern (mock): {pattern_id}")
                return True
                
            self.index.delete(ids=[pattern_id])
            logger.info(f"✅ Deleted pattern: {pattern_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern_id}: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            if not self.available or not self.index:
                return {
                    "total_vector_count": 25,
                    "dimension": self.dimension,
                    "index_fullness": 0.1,
                    "namespaces": {}
                }
            
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {
                "total_vector_count": 0,
                "dimension": self.dimension,
                "index_fullness": 0.0,
                "namespaces": {}
            }
    
    async def populate_sample_data(self, count: int = 20) -> bool:
        """Populate index with sample EEG patterns for testing"""
        try:
            if not self.available:
                logger.info(f"✅ Populated {count} sample patterns (mock)")
                return True
            
            sample_patterns = [
                {"emotion": "calm", "direction": "forward", "context": "Patient feeling peaceful, ready to progress"},
                {"emotion": "excited", "direction": "left", "context": "High energy, wants to explore left side"},
                {"emotion": "sad", "direction": "stop", "context": "Feeling down, needs emotional support"},
                {"emotion": "calm", "direction": "right", "context": "Thoughtful state, deliberate right turn"},
                {"emotion": "excited", "direction": "forward", "context": "Enthusiastic about moving ahead"},
                {"emotion": "anxious", "direction": "backward", "context": "Feeling nervous, wants to retreat"},
                {"emotion": "neutral", "direction": "stop", "context": "Resting state, no specific intention"},
                {"emotion": "calm", "direction": "up", "context": "Looking up with peaceful mindset"},
                {"emotion": "excited", "direction": "down", "context": "Energetic downward focus"},
                {"emotion": "sad", "direction": "left", "context": "Melancholy, turning away"},
            ]
            
            # Extend patterns to requested count
            extended_patterns = (sample_patterns * ((count // len(sample_patterns)) + 1))[:count]
            
            success_count = 0
            for i, pattern in enumerate(extended_patterns):
                pattern_id = f"sample_{i+1:03d}_{uuid.uuid4().hex[:8]}"
                
                confidence_scores = {
                    "emotion": np.random.uniform(0.7, 0.95),
                    "direction": np.random.uniform(0.6, 0.9)
                }
                
                metadata = {
                    "source": "sample_data",
                    "session_id": f"session_{(i % 5) + 1}",
                    "patient_id": f"patient_{(i % 3) + 1}"
                }
                
                success = await self.store_eeg_pattern(
                    pattern_id=pattern_id,
                    emotion=pattern["emotion"],
                    direction=pattern["direction"],
                    context=pattern["context"],
                    confidence_scores=confidence_scores,
                    metadata=metadata
                )
                
                if success:
                    success_count += 1
            
            logger.info(f"✅ Populated {success_count}/{count} sample patterns")
            return success_count == count
            
        except Exception as e:
            logger.error(f"Error populating sample data: {str(e)}")
            return False
    
    async def search_by_emotion(self, emotion: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search patterns by emotion"""
        try:
            if not self.available or not self.index:
                # Return mock patterns
                return [
                    {
                        "id": f"emotion_pattern_{i}",
                        "metadata": {
                            "emotion": emotion,
                            "direction": ["forward", "left", "right"][i % 3],
                            "context": f"Mock {emotion} pattern {i+1}",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    for i in range(min(limit, 3))
                ]
            
            # Use filter to search by emotion
            query_results = self.index.query(
                vector=[0.0] * self.dimension,  # Dummy vector
                filter={"emotion": {"$eq": emotion}},
                top_k=limit,
                include_metadata=True
            )
            
            patterns = []
            for match in query_results.matches:
                patterns.append({
                    "id": match.id,
                    "metadata": match.metadata
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error searching by emotion: {str(e)}")
            return []
    
    async def close(self):
        """Cleanup connections"""
        # Pinecone client doesn't require explicit closing
        logger.info("🛑 Pinecone client closed")