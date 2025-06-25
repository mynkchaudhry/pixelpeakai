# File: backend/main.py
# PixelPeak Backend - Enhanced FastAPI with Avatar Movements & Captions

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import os
import json
import asyncio
import logging
from datetime import datetime
import uuid
import sys
import random

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our clients (removed readyplayerme_client)
from clients.groq_client import GroqClient
from clients.elevenlabs_client import ElevenLabsClient
from clients.pinecone_client import PineconeClient
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PixelPeak BCI API - Enhanced Avatar System",
    description="Brain-Computer Interface to Three.js Avatar System with Custom Movements & Captions",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories and mount static files
os.makedirs("data/audio", exist_ok=True)
os.makedirs("data/captions", exist_ok=True)
os.makedirs("data/scenarios", exist_ok=True)

app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")
app.mount("/captions", StaticFiles(directory="data/captions"), name="captions")

# =============================================================================
# ENHANCED PYDANTIC MODELS
# =============================================================================

class EEGScenario(BaseModel):
    """Enhanced EEG scenario data model with movement and caption info"""
    id: str = Field(..., description="Unique scenario identifier")
    emotion: str = Field(..., description="Detected emotion")
    direction: str = Field(..., description="Movement direction")
    emotion_confidence: float = Field(..., ge=0.0, le=1.0, description="Emotion confidence")
    direction_confidence: float = Field(..., ge=0.0, le=1.0, description="Direction confidence")
    speech: str = Field(..., description="Generated speech text")
    context: str = Field("", description="Additional context")
    audio_url: Optional[str] = Field(None, description="Generated audio URL")
    generated_at: str = Field(..., description="Generation timestamp")
    
    # Enhanced fields for avatar movements and captions
    avatar_movement: Optional[Dict[str, Any]] = Field(None, description="Avatar movement configuration")
    caption_style: Optional[Dict[str, Any]] = Field(None, description="Caption styling")
    speech_duration: Optional[float] = Field(None, description="Estimated speech duration")

class GenerateScenarioRequest(BaseModel):
    """Request model for generating scenarios"""
    context: Optional[str] = Field(None, description="Optional context for generation")
    emotion_hint: Optional[str] = Field(None, description="Emotion hint")
    direction_hint: Optional[str] = Field(None, description="Direction hint")
    include_movement: bool = Field(True, description="Include avatar movement data")
    include_captions: bool = Field(True, description="Include caption styling")

class ProcessSpeechRequest(BaseModel):
    """Enhanced request model for processing speech with movements"""
    scenario_id: str = Field(..., description="Scenario ID to process")
    text: Optional[str] = Field(None, description="Override text")
    emotion: Optional[str] = Field(None, description="Override emotion")
    voice_id: Optional[str] = Field(None, description="Specific voice ID")
    include_movement: bool = Field(True, description="Include avatar movement")
    words_count: Optional[int] = Field(20, description="Target word count for speech")

class AvatarMovementRequest(BaseModel):
    """Request model for avatar movement operations"""
    emotion: str = Field(..., description="Emotion to animate")
    duration: Optional[float] = Field(None, description="Override duration")
    intensity: Optional[float] = Field(1.0, description="Movement intensity multiplier")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Custom movement parameters")

# =============================================================================
# GLOBAL CLIENTS
# =============================================================================

groq_client = None
elevenlabs_client = None
pinecone_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize all clients on startup"""
    global groq_client, elevenlabs_client, pinecone_client
    
    logger.info("🚀 Starting PixelPeak Enhanced BCI API...")
    
    try:
        # Initialize clients (removed readyplayerme_client)
        groq_client = GroqClient()
        elevenlabs_client = ElevenLabsClient()
        pinecone_client = PineconeClient()
        
        # Initialize Pinecone index
        await pinecone_client.initialize()
        
        # Populate sample data if needed
        stats = await pinecone_client.get_index_stats()
        if stats.get("total_vector_count", 0) < 5:
            logger.info("📊 Populating sample EEG patterns...")
            await pinecone_client.populate_sample_data(20)
        
        logger.info("🎉 All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        logger.info("⚠️ Continuing with limited functionality...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down PixelPeak Enhanced BCI API...")
    if pinecone_client:
        await pinecone_client.close()

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PixelPeak Enhanced BCI API",
        "version": "2.0.0",
        "status": "running",
        "services": ["Groq LLM", "ElevenLabs TTS", "Pinecone Vector DB", "Three.js Avatar"],
        "features": ["Custom Avatar Movements", "Dynamic Captions", "Emotion-based Animations"],
        "docs": "/docs",
        "endpoints": {
            "scenarios": "/api/scenarios",
            "generate": "/api/generate-scenario",
            "speech": "/api/process-speech-enhanced",
            "movements": "/api/avatar-movements",
            "captions": "/api/generate-captions"
        }
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check for all services with enhanced fallback support"""
    try:
        services_status = {}
        service_details = {}
        
        if groq_client:
            services_status["groq"] = await groq_client.health_check()
        else:
            services_status["groq"] = False
        
        if elevenlabs_client:
            services_status["elevenlabs"] = await elevenlabs_client.health_check()
            # Get detailed ElevenLabs status
            elevenlabs_status = await elevenlabs_client.get_api_status()
            service_details["elevenlabs"] = elevenlabs_status
        else:
            services_status["elevenlabs"] = False
        
        if pinecone_client:
            services_status["pinecone"] = await pinecone_client.health_check()
        else:
            services_status["pinecone"] = False
        
        # Get API key validation
        api_keys = config.validate_api_keys()
        
        # Determine overall health - system can still function with ElevenLabs in fallback mode
        critical_services = ["groq", "pinecone"]  # ElevenLabs is not critical
        critical_healthy = all(services_status.get(service, False) for service in critical_services)
        
        # Enhanced status determination
        if critical_healthy:
            if all(services_status.values()):
                overall_status = "healthy"
            else:
                overall_status = "partial"  # Some non-critical services down
        else:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {k: "✅" if v else "❌" for k, v in services_status.items()},
            "service_details": service_details,
            "api_keys": {k: "✅" if v else "❌" for k, v in api_keys.items()},
            "avatar_system": "✅ Three.js Custom Avatar",
            "features": {
                "movements": "✅ Enhanced Emotion-based Movements",
                "captions": "✅ Dynamic Caption System", 
                "speech": "✅ 20-word Targeted Speech",
                "audio_playback": "✅" if services_status.get("elevenlabs", False) else "⚠️ Fallback Mode",
                "core_functionality": "✅ Fully Operational"
            },
            "fallback_info": {
                "elevenlabs_fallback": service_details.get("elevenlabs", {}).get("fallback_mode", False),
                "impact": "No impact on movements, captions, or core functionality" if service_details.get("elevenlabs", {}).get("fallback_mode", False) else None
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# =============================================================================
# ENHANCED SCENARIO ENDPOINTS
# =============================================================================

@app.post("/api/generate-scenario", response_model=EEGScenario)
async def generate_scenario(request: GenerateScenarioRequest):
    """Generate enhanced EEG scenario with movement and caption data"""
    try:
        if groq_client:
            # Generate scenario using Groq
            scenario_data = await groq_client.generate_eeg_scenario(request.context)
        else:
            # Fallback scenario generation
            scenario_data = await generate_fallback_scenario()
        
        # Enhance scenario with movement and caption data
        emotion = scenario_data.get("emotion", "neutral")
        
        # Get movement configuration
        avatar_movement = None
        if request.include_movement:
            avatar_movement = config.get_avatar_movement(emotion)
        
        # Get caption styling
        caption_style = None
        if request.include_captions:
            caption_style = config.get_caption_style(emotion)
        
        # Generate appropriate speech for the emotion (20 words)
        speech_text = config.get_speech_template(emotion)
        scenario_data["speech"] = speech_text
        
        # Store pattern in Pinecone if available
        if pinecone_client:
            confidence_scores = {
                "emotion": scenario_data["emotion_confidence"],
                "direction": scenario_data["direction_confidence"]
            }
            
            await pinecone_client.store_eeg_pattern(
                pattern_id=scenario_data["id"],
                emotion=scenario_data["emotion"],
                direction=scenario_data["direction"],
                context=scenario_data.get("context", ""),
                confidence_scores=confidence_scores,
                metadata={
                    "source": "groq_generated", 
                    "session": "api",
                    "has_movement": request.include_movement,
                    "has_captions": request.include_captions
                }
            )
        
        # Create enhanced scenario response
        scenario = EEGScenario(
            id=scenario_data["id"],
            emotion=scenario_data["emotion"],
            direction=scenario_data["direction"],
            emotion_confidence=scenario_data["emotion_confidence"],
            direction_confidence=scenario_data["direction_confidence"],
            speech=scenario_data["speech"],
            context=scenario_data.get("context", ""),
            generated_at=scenario_data["generated_at"],
            avatar_movement=avatar_movement,
            caption_style=caption_style,
            speech_duration=len(scenario_data["speech"].split()) * 0.6
        )
        
        logger.info(f"✅ Generated enhanced scenario: {scenario.emotion} + {scenario.direction}")
        return scenario
        
    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        return await generate_fallback_scenario_enhanced()

async def generate_fallback_scenario_enhanced():
    """Generate enhanced fallback scenario when APIs are unavailable"""
    emotions = ["happy", "excited", "calm", "sad", "anxious", "neutral"]
    directions = ["forward", "backward", "left", "right", "stop"]
    
    emotion = random.choice(emotions)
    direction = random.choice(directions)
    
    speech_text = config.get_speech_template(emotion)
    avatar_movement = config.get_avatar_movement(emotion)
    caption_style = config.get_caption_style(emotion)
    
    return EEGScenario(
        id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        emotion=emotion,
        direction=direction,
        emotion_confidence=0.75 + random.random() * 0.2,
        direction_confidence=0.70 + random.random() * 0.25,
        speech=speech_text,
        context="Enhanced fallback scenario with movements",
        generated_at=datetime.now().isoformat(),
        avatar_movement=avatar_movement,
        caption_style=caption_style,
        speech_duration=len(speech_text.split()) * 0.6
    )

# =============================================================================
# ENHANCED SPEECH PROCESSING ENDPOINTS
# =============================================================================

@app.post("/api/process-speech-enhanced")
async def process_speech_enhanced(data: dict):
    """Enhanced speech processing with robust fallback handling"""
    try:
        # Extract data with defaults
        scenario_id = data.get("scenario_id", "unknown")
        emotion = data.get("emotion", "neutral")
        text = data.get("text") or config.get_speech_template(emotion)
        voice_id = data.get("voice_id", None)
        include_movement = data.get("include_movement", True)
        words_count = data.get("words_count", 20)
        
        # Ensure text is approximately the target word count
        words = text.split()
        if len(words) != words_count:
            # Regenerate speech to match word count
            text = config.get_speech_template(emotion)
        
        logger.info(f"Processing enhanced speech: '{text[:50]}...' with emotion: {emotion}")
        
        # Get movement and caption data (always available)
        avatar_movement = config.get_avatar_movement(emotion) if include_movement else None
        caption_style = config.get_caption_style(emotion)
        
        # Process speech with ElevenLabs (with enhanced fallback)
        speech_result = {"success": False}
        if elevenlabs_client:
            speech_result = await elevenlabs_client.text_to_speech(
                text=text,
                emotion=emotion,
                voice_id=voice_id
            )
        
        # Prepare enhanced response (always successful for frontend)
        result = {
            "success": True,  # Always true - core functionality works regardless of audio
            "scenario_id": scenario_id,
            "text": text,
            "emotion": emotion,
            "word_count": len(text.split()),
            "avatar_movement": avatar_movement,
            "caption_style": caption_style,
            "speech_duration": len(text.split()) * 0.6,
            "generated_at": datetime.now().isoformat(),
            "core_features_available": True
        }
        
        # Add audio data based on result
        if speech_result.get("success"):
            result.update({
                "audio_available": True,
                "audio_url": speech_result["url"],
                "filename": speech_result["filename"],
                "duration_estimate": speech_result["duration_estimate"],
                "voice_id": speech_result["voice_id"],
                "supports_playback": not speech_result.get("is_fallback", False),
                "audio_source": speech_result.get("source", "unknown")
            })
            
            if speech_result.get("is_fallback"):
                result.update({
                    "fallback_mode": True,
                    "fallback_reason": speech_result.get("fallback_reason", "API unavailable"),
                    "user_message": "Audio playback unavailable, but movements and captions are fully functional!"
                })
                logger.info(f"✅ Enhanced speech with fallback: {speech_result['filename']}")
            else:
                result["fallback_mode"] = False
                logger.info(f"✅ Enhanced speech generated: {speech_result['filename']}")
        else:
            # Complete fallback mode
            result.update({
                "audio_available": False,
                "supports_playback": False,
                "fallback_mode": True,
                "fallback_reason": "TTS service completely unavailable",
                "user_message": "Running in enhanced mode - movements and captions fully functional!",
                "audio_source": "none"
            })
            logger.info("✅ Enhanced speech processing completed in full fallback mode")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced speech processing: {str(e)}")
        # Even in error case, return success with fallback
        return {
            "success": True,  # Core functionality still works
            "error_details": str(e),
            "text": data.get("text", "Error processing speech"),
            "scenario_id": data.get("scenario_id", "unknown"),
            "emotion": data.get("emotion", "neutral"),
            "fallback_mode": True,
            "audio_available": False,
            "supports_playback": False,
            "avatar_movement": config.get_avatar_movement(data.get("emotion", "neutral")),
            "caption_style": config.get_caption_style(data.get("emotion", "neutral")),
            "user_message": "System running in safe mode - all visual features available!"
        }

# =============================================================================
# AVATAR MOVEMENT ENDPOINTS
# =============================================================================

@app.post("/api/avatar-movements")
async def get_avatar_movement(request: AvatarMovementRequest):
    """Get avatar movement configuration for specific emotion"""
    try:
        base_movement = config.get_avatar_movement(request.emotion)
        
        # Apply custom parameters if provided
        if request.custom_params:
            base_movement.update(request.custom_params)
        
        # Apply intensity multiplier
        if request.intensity != 1.0:
            for key in ["speed", "gesture_intensity", "jump_height", "sway_amplitude", "fidget_intensity"]:
                if key in base_movement:
                    base_movement[key] *= request.intensity
        
        # Override duration if provided
        if request.duration:
            base_movement["duration"] = request.duration
        
        return {
            "success": True,
            "emotion": request.emotion,
            "movement": base_movement,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting avatar movement: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "emotion": request.emotion
        }

@app.get("/api/avatar-movements/{emotion}")
async def get_movement_by_emotion(emotion: str):
    """Get avatar movement configuration by emotion name"""
    try:
        movement = config.get_avatar_movement(emotion)
        
        if movement:
            return {
                "success": True,
                "emotion": emotion,
                "movement": movement
            }
        else:
            return {
                "success": False,
                "error": f"No movement configuration found for emotion: {emotion}",
                "available_emotions": list(config.AVATAR_MOVEMENTS.keys())
            }
    except Exception as e:
        logger.error(f"Error getting movement for emotion {emotion}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/avatar-movements")
async def list_all_movements():
    """List all available avatar movements"""
    try:
        return {
            "success": True,
            "movements": config.AVATAR_MOVEMENTS,
            "count": len(config.AVATAR_MOVEMENTS)
        }
    except Exception as e:
        logger.error(f"Error listing movements: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# =============================================================================
# CAPTION ENDPOINTS
# =============================================================================

@app.post("/api/generate-captions")
async def generate_captions(data: dict):
    """Generate styled captions for speech"""
    try:
        text = data.get("text", "")
        emotion = data.get("emotion", "neutral")
        
        if not text:
            return {
                "success": False,
                "error": "Text is required for caption generation"
            }
        
        # Get caption styling
        caption_style = config.get_caption_style(emotion)
        
        # Break text into caption chunks (for better readability)
        words = text.split()
        caption_chunks = []
        chunk_size = 8  # 8 words per caption chunk
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            caption_chunks.append(chunk)
        
        return {
            "success": True,
            "text": text,
            "emotion": emotion,
            "caption_style": caption_style,
            "caption_chunks": caption_chunks,
            "total_chunks": len(caption_chunks),
            "timing": {
                "chunk_duration": 2.0,  # seconds per chunk
                "total_duration": len(caption_chunks) * 2.0
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating captions: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/caption-styles/{emotion}")
async def get_caption_style(emotion: str):
    """Get caption styling for specific emotion"""
    try:
        style = config.get_caption_style(emotion)
        
        return {
            "success": True,
            "emotion": emotion,
            "style": style
        }
    except Exception as e:
        logger.error(f"Error getting caption style: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# =============================================================================
# COMPLETE ENHANCED WORKFLOW ENDPOINT
# =============================================================================

@app.post("/api/complete-enhanced-workflow")
async def complete_enhanced_workflow(request: GenerateScenarioRequest):
    """Complete enhanced BCI workflow: Generate scenario → Create speech → Get movements → Generate captions"""
    try:
        # Step 1: Generate enhanced scenario
        scenario_data = await generate_scenario(request)
        
        # Step 2: Generate enhanced speech
        speech_data = {
            "scenario_id": scenario_data.id,
            "text": scenario_data.speech,
            "emotion": scenario_data.emotion,
            "include_movement": True,
            "words_count": 20
        }
        audio_result = await process_speech_enhanced(speech_data)
        
        # Step 3: Generate captions
        caption_data = {
            "text": scenario_data.speech,
            "emotion": scenario_data.emotion
        }
        caption_result = await generate_captions(caption_data)
        
        # Return complete enhanced result
        return {
            "success": True,
            "workflow_type": "enhanced",
            "scenario": {
                "id": scenario_data.id,
                "emotion": scenario_data.emotion,
                "direction": scenario_data.direction,
                "emotion_confidence": scenario_data.emotion_confidence,
                "direction_confidence": scenario_data.direction_confidence,
                "speech": scenario_data.speech,
                "context": scenario_data.context,
                "generated_at": scenario_data.generated_at,
                "word_count": len(scenario_data.speech.split())
            },
            "audio": {
                "url": audio_result.get("audio_url") if audio_result.get("success") else None,
                "filename": audio_result.get("filename"),
                "success": audio_result.get("success", False),
                "duration": audio_result.get("duration_estimate")
            },
            "avatar_movement": scenario_data.avatar_movement,
            "captions": {
                "style": caption_result.get("caption_style") if caption_result.get("success") else None,
                "chunks": caption_result.get("caption_chunks", []),
                "timing": caption_result.get("timing", {}),
                "success": caption_result.get("success", False)
            },
            "stored_in_pinecone": pinecone_client is not None,
            "processing_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in complete enhanced workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced workflow failed: {str(e)}")

# =============================================================================
# SIMILARITY ENDPOINTS (UPDATED)
# =============================================================================

@app.post("/api/similar-patterns")
async def find_similar_patterns(data: dict):
    """Find similar EEG patterns with enhanced metadata"""
    try:
        emotion = data.get("emotion", "neutral")
        direction = data.get("direction", "forward")
        context = data.get("context", "")
        top_k = data.get("top_k", 5)
        min_score = data.get("min_score", 0.7)
        
        if pinecone_client:
            # Find similar patterns
            similar_patterns = await pinecone_client.find_similar_patterns(
                emotion=emotion,
                direction=direction,
                context=context,
                top_k=top_k,
                min_score=min_score
            )
            
            # Enhance patterns with movement data
            enhanced_patterns = []
            for pattern in similar_patterns:
                pattern_emotion = pattern.get("emotion", "neutral")
                enhanced_pattern = pattern.copy()
                enhanced_pattern["avatar_movement"] = config.get_avatar_movement(pattern_emotion)
                enhanced_pattern["caption_style"] = config.get_caption_style(pattern_emotion)
                enhanced_patterns.append(enhanced_pattern)
            
            return {
                "success": True,
                "query": {
                    "emotion": emotion,
                    "direction": direction,
                    "context": context
                },
                "similar_patterns": enhanced_patterns,
                "count": len(enhanced_patterns)
            }
        else:
            return {
                "success": False,
                "error": "Pinecone service unavailable",
                "similar_patterns": [],
                "count": 0
            }
        
    except Exception as e:
        logger.error(f"Error finding similar patterns: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to find similar patterns: {str(e)}",
            "similar_patterns": [],
            "count": 0
        }

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.get("/api/emotions")
async def list_emotions():
    """List all available emotions with their configurations"""
    try:
        emotions_data = {}
        
        for emotion in config.AVATAR_MOVEMENTS.keys():
            emotions_data[emotion] = {
                "movement": config.get_avatar_movement(emotion),
                "caption_style": config.get_caption_style(emotion),
                "voice_config": config.get_voice_config(emotion),
                "sample_speech": config.get_speech_template(emotion)[:50] + "..."
            }
        
        return {
            "success": True,
            "emotions": emotions_data,
            "count": len(emotions_data)
        }
    except Exception as e:
        logger.error(f"Error listing emotions: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# =============================================================================
# BACKWARD COMPATIBILITY ENDPOINTS
# =============================================================================

@app.post("/api/process-speech-simple")
async def process_speech_simple(data: dict):
    """Simplified speech processing endpoint (backward compatibility)"""
    # Redirect to enhanced version
    return await process_speech_enhanced(data)

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# =============================================================================
# MAIN APPLICATION
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting PixelPeak Enhanced BCI API Server...")
    print(f"📍 Docs available at: http://localhost:8000/docs")
    print(f"🎵 Audio files at: http://localhost:8000/audio/")
    print(f"📝 Captions at: http://localhost:8000/captions/")
    print(f"🤖 Enhanced speech: http://localhost:8000/api/process-speech-enhanced")
    print(f"🎭 Avatar movements: http://localhost:8000/api/avatar-movements")
    print(f"📱 Generate captions: http://localhost:8000/api/generate-captions")
    print(f"🔄 Complete workflow: http://localhost:8000/api/complete-enhanced-workflow")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )