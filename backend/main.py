# File: backend/main.py
# PixelPeak Backend - Complete Fixed FastAPI Application

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
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

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our clients with fixed paths
from clients.groq_client import GroqClient
from clients.elevenlabs_client import ElevenLabsClient
from clients.pinecone_client import PineconeClient
from clients.readyplayerme_client import ReadyPlayerMeClient
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PixelPeak BCI API",
    description="Brain-Computer Interface to VR Avatar System with Groq, ElevenLabs, Pinecone & Ready Player Me",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories and mount static files
os.makedirs("data/audio", exist_ok=True)
os.makedirs("data/avatars", exist_ok=True)
os.makedirs("data/scenarios", exist_ok=True)

app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")
app.mount("/avatars", StaticFiles(directory="data/avatars"), name="avatars")

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class EEGScenario(BaseModel):
    """EEG scenario data model"""
    id: str = Field(..., description="Unique scenario identifier")
    emotion: str = Field(..., description="Detected emotion")
    direction: str = Field(..., description="Movement direction")
    emotion_confidence: float = Field(..., ge=0.0, le=1.0, description="Emotion confidence")
    direction_confidence: float = Field(..., ge=0.0, le=1.0, description="Direction confidence")
    speech: str = Field(..., description="Generated speech text")
    context: str = Field("", description="Additional context")
    audio_url: Optional[str] = Field(None, description="Generated audio URL")
    generated_at: str = Field(..., description="Generation timestamp")

class GenerateScenarioRequest(BaseModel):
    """Request model for generating scenarios"""
    context: Optional[str] = Field(None, description="Optional context for generation")
    emotion_hint: Optional[str] = Field(None, description="Emotion hint")
    direction_hint: Optional[str] = Field(None, description="Direction hint")

class ProcessSpeechRequest(BaseModel):
    """Request model for processing speech"""
    scenario_id: str = Field(..., description="Scenario ID to process")
    text: Optional[str] = Field(None, description="Override text")
    emotion: Optional[str] = Field(None, description="Override emotion")
    voice_id: Optional[str] = Field(None, description="Specific voice ID")

class AvatarRequest(BaseModel):
    """Request model for avatar operations"""
    avatar_type: str = Field("therapy_assistant", description="Avatar preset type")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Avatar customizations")

class SimilarPatternsRequest(BaseModel):
    """Request model for finding similar EEG patterns"""
    emotion: str = Field(..., description="Current emotion")
    direction: str = Field(..., description="Current direction")
    context: str = Field("", description="Current context")
    top_k: int = Field(5, ge=1, le=20, description="Number of results")
    min_score: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")

# =============================================================================
# GLOBAL CLIENTS
# =============================================================================

groq_client = None
elevenlabs_client = None
pinecone_client = None
readyplayerme_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize all clients on startup"""
    global groq_client, elevenlabs_client, pinecone_client, readyplayerme_client
    
    logger.info("🚀 Starting PixelPeak BCI API...")
    
    try:
        # Initialize all clients
        groq_client = GroqClient()
        elevenlabs_client = ElevenLabsClient()
        pinecone_client = PineconeClient()
        readyplayerme_client = ReadyPlayerMeClient()
        
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
        # Continue anyway for demo purposes
        logger.info("⚠️ Continuing with limited functionality...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down PixelPeak BCI API...")
    if pinecone_client:
        await pinecone_client.close()

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PixelPeak BCI API",
        "version": "1.0.0",
        "status": "running",
        "services": ["Groq LLM", "ElevenLabs TTS", "Pinecone Vector DB", "Ready Player Me"],
        "docs": "/docs",
        "endpoints": {
            "scenarios": "/api/scenarios",
            "generate": "/api/generate-scenario",
            "speech": "/api/process-speech",
            "speech_simple": "/api/process-speech-simple",
            "avatars": "/api/avatars",
            "similar": "/api/similar-patterns"
        }
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check for all services"""
    try:
        # Test all services
        services_status = {}
        
        if groq_client:
            services_status["groq"] = await groq_client.health_check()
        else:
            services_status["groq"] = False
        
        if elevenlabs_client:
            services_status["elevenlabs"] = await elevenlabs_client.health_check()
        else:
            services_status["elevenlabs"] = False
        
        if pinecone_client:
            services_status["pinecone"] = await pinecone_client.health_check()
        else:
            services_status["pinecone"] = False
        
        if readyplayerme_client:
            services_status["ready_player_me"] = await readyplayerme_client.health_check()
        else:
            services_status["ready_player_me"] = False
        
        # Get API key validation
        api_keys = config.validate_api_keys()
        
        all_healthy = all(services_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": {k: "✅" if v else "❌" for k, v in services_status.items()},
            "api_keys": {k: "✅" if v else "❌" for k, v in api_keys.items()},
            "uptime": "operational"
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
# SCENARIO ENDPOINTS
# =============================================================================

@app.get("/api/scenarios", response_model=List[EEGScenario])
async def get_scenarios():
    """Get list of recent EEG scenarios"""
    try:
        # Return mock scenarios for demo
        mock_scenarios = [
            EEGScenario(
                id="demo_1",
                emotion="calm",
                direction="forward",
                emotion_confidence=0.87,
                direction_confidence=0.92,
                speech="I feel peaceful and ready to move forward",
                context="Patient in relaxed state",
                generated_at=datetime.now().isoformat()
            ),
            EEGScenario(
                id="demo_2", 
                emotion="excited",
                direction="left",
                emotion_confidence=0.94,
                direction_confidence=0.78,
                speech="I'm energized! Let's turn left and explore",
                context="High energy state",
                generated_at=datetime.now().isoformat()
            ),
            EEGScenario(
                id="demo_3",
                emotion="sad",
                direction="stop",
                emotion_confidence=0.76,
                direction_confidence=0.85,
                speech="I'm feeling down right now, I need to pause",
                context="Low mood, needs support",
                generated_at=datetime.now().isoformat()
            )
        ]
        
        return mock_scenarios
        
    except Exception as e:
        logger.error(f"Error getting scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-scenario", response_model=EEGScenario)
async def generate_scenario(request: GenerateScenarioRequest):
    """Generate new EEG scenario using Groq LLM"""
    try:
        if groq_client:
            # Generate scenario using Groq
            scenario_data = await groq_client.generate_eeg_scenario(request.context)
            
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
                    metadata={"source": "groq_generated", "session": "api"}
                )
            
            # Convert to response model
            scenario = EEGScenario(
                id=scenario_data["id"],
                emotion=scenario_data["emotion"],
                direction=scenario_data["direction"],
                emotion_confidence=scenario_data["emotion_confidence"],
                direction_confidence=scenario_data["direction_confidence"],
                speech=scenario_data["speech"],
                context=scenario_data.get("context", ""),
                generated_at=scenario_data["generated_at"]
            )
            
            logger.info(f"✅ Generated scenario: {scenario.emotion} + {scenario.direction}")
            return scenario
        else:
            # Fallback if Groq not available
            return await generate_fallback_scenario()
        
    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        return await generate_fallback_scenario()

async def generate_fallback_scenario():
    """Generate fallback scenario when APIs are unavailable"""
    import random
    
    emotions = ["calm", "excited", "sad", "anxious", "neutral"]
    directions = ["forward", "backward", "left", "right", "stop"]
    
    emotion = random.choice(emotions)
    direction = random.choice(directions)
    
    fallback_speeches = {
        ("calm", "forward"): "I feel peaceful and ready to move forward",
        ("excited", "left"): "I'm energized! Let's turn left and explore",
        ("sad", "stop"): "I'm feeling down right now, I need to pause",
        ("calm", "right"): "Let me calmly turn to the right",
        ("anxious", "backward"): "I'm feeling nervous, can we go back?"
    }
    
    speech = fallback_speeches.get(
        (emotion, direction), 
        f"I feel {emotion} and want to go {direction}"
    )
    
    return EEGScenario(
        id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        emotion=emotion,
        direction=direction,
        emotion_confidence=0.75 + random.random() * 0.2,
        direction_confidence=0.70 + random.random() * 0.25,
        speech=speech,
        context="Fallback scenario - API unavailable",
        generated_at=datetime.now().isoformat()
    )

# =============================================================================
# SPEECH PROCESSING ENDPOINTS (FIXED)
# =============================================================================

@app.post("/api/process-speech")
async def process_speech(request: ProcessSpeechRequest):
    """Convert scenario text to speech using ElevenLabs (Strict validation)"""
    try:
        text = request.text or "I want to communicate through my thoughts"
        emotion = request.emotion or "calm"
        
        logger.info(f"Processing speech (strict): '{text}' with emotion: {emotion}")
        
        if elevenlabs_client:
            # Generate speech using ElevenLabs
            speech_result = await elevenlabs_client.text_to_speech(
                text=text,
                emotion=emotion,
                voice_id=request.voice_id
            )
            
            if speech_result["success"]:
                return {
                    "success": True,
                    "scenario_id": request.scenario_id,
                    "text": text,
                    "emotion": emotion,
                    "audio_url": speech_result["url"],
                    "filename": speech_result["filename"],
                    "duration_estimate": speech_result["duration_estimate"],
                    "voice_id": speech_result["voice_id"],
                    "generated_at": speech_result["generated_at"]
                }
            else:
                return {
                    "success": False,
                    "error": speech_result.get("error", "TTS generation failed"),
                    "fallback_url": speech_result.get("url"),
                    "text": text,
                    "emotion": emotion,
                    "scenario_id": request.scenario_id
                }
        else:
            # Fallback response
            return {
                "success": False,
                "error": "TTS service unavailable",
                "text": text,
                "emotion": emotion,
                "scenario_id": request.scenario_id
            }
        
    except Exception as e:
        logger.error(f"Error processing speech: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to process speech: {str(e)}",
            "text": request.text if hasattr(request, 'text') else "Unknown",
            "scenario_id": request.scenario_id if hasattr(request, 'scenario_id') else "unknown"
        }

@app.post("/api/process-speech-simple")
async def process_speech_simple(data: dict):
    """Simplified speech processing endpoint that accepts any JSON (For frontend compatibility)"""
    try:
        # Extract data with defaults
        scenario_id = data.get("scenario_id", "unknown")
        text = data.get("text", "I want to communicate through my thoughts")
        emotion = data.get("emotion", "calm")
        voice_id = data.get("voice_id", None)
        
        logger.info(f"Processing speech (simple): '{text}' with emotion: {emotion}")
        
        if elevenlabs_client:
            # Generate speech using ElevenLabs
            speech_result = await elevenlabs_client.text_to_speech(
                text=text,
                emotion=emotion,
                voice_id=voice_id
            )
            
            if speech_result["success"]:
                result = {
                    "success": True,
                    "scenario_id": scenario_id,
                    "text": text,
                    "emotion": emotion,
                    "audio_url": speech_result["url"],
                    "filename": speech_result["filename"],
                    "duration_estimate": speech_result["duration_estimate"],
                    "voice_id": speech_result["voice_id"],
                    "generated_at": speech_result["generated_at"]
                }
                logger.info(f"✅ Speech generated successfully: {speech_result['filename']}")
                return result
            else:
                logger.warning(f"TTS generation failed: {speech_result.get('error')}")
                return {
                    "success": False,
                    "error": speech_result.get("error", "TTS generation failed"),
                    "text": text,
                    "emotion": emotion,
                    "scenario_id": scenario_id
                }
        else:
            # Mock response when ElevenLabs is not available
            logger.info("ElevenLabs not available, returning mock response")
            return {
                "success": False,
                "error": "TTS service unavailable - using mock mode",
                "text": text,
                "emotion": emotion,
                "scenario_id": scenario_id,
                "mock_audio_url": f"/audio/mock_{emotion}_{scenario_id}.mp3",
                "duration_estimate": len(text.split()) * 0.6
            }
        
    except Exception as e:
        logger.error(f"Error in simplified speech processing: {str(e)}")
        return {
            "success": False,
            "error": f"Speech processing failed: {str(e)}",
            "text": data.get("text", "unknown"),
            "scenario_id": data.get("scenario_id", "unknown")
        }

# =============================================================================
# PINECONE SIMILARITY ENDPOINTS
# =============================================================================

@app.post("/api/similar-patterns")
async def find_similar_patterns(request: SimilarPatternsRequest):
    """Find similar EEG patterns using Pinecone vector search"""
    try:
        if pinecone_client:
            # Find similar patterns
            similar_patterns = await pinecone_client.find_similar_patterns(
                emotion=request.emotion,
                direction=request.direction,
                context=request.context,
                top_k=request.top_k,
                min_score=request.min_score
            )
            
            return {
                "success": True,
                "query": {
                    "emotion": request.emotion,
                    "direction": request.direction,
                    "context": request.context
                },
                "similar_patterns": similar_patterns,
                "count": len(similar_patterns)
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

@app.get("/api/patterns/stats")
async def get_pattern_stats():
    """Get Pinecone index statistics"""
    try:
        if pinecone_client:
            stats = await pinecone_client.get_index_stats()
            return {
                "success": True,
                "stats": stats
            }
        else:
            return {
                "success": False,
                "error": "Pinecone service unavailable"
            }
    except Exception as e:
        logger.error(f"Error getting pattern stats: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# =============================================================================
# AVATAR ENDPOINTS (Ready Player Me)
# =============================================================================

@app.post("/api/avatars/create-preset")
async def create_preset_avatar(request: AvatarRequest):
    """Create avatar from preset using Ready Player Me"""
    try:
        if readyplayerme_client:
            avatar_result = await readyplayerme_client.create_preset_avatar(
                preset_type=request.avatar_type,
                customizations=request.customizations
            )
            return avatar_result
        else:
            return {
                "success": False,
                "error": "Ready Player Me service unavailable"
            }
        
    except Exception as e:
        logger.error(f"Error creating avatar: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create avatar: {str(e)}"
        }

@app.get("/api/avatars")
async def list_avatars():
    """List all user avatars"""
    try:
        if readyplayerme_client:
            avatars = await readyplayerme_client.list_user_avatars()
            return {
                "success": True,
                "avatars": avatars,
                "count": len(avatars)
            }
        else:
            return {
                "success": False,
                "error": "Ready Player Me service unavailable"
            }
    except Exception as e:
        logger.error(f"Error listing avatars: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# =============================================================================
# AUDIO FILE SERVING
# =============================================================================

@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    """Serve audio files"""
    try:
        file_path = os.path.join("data/audio", filename)
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"inline; filename={filename}"}
            )
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        logger.error(f"Error serving audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# COMPLETE WORKFLOW ENDPOINT
# =============================================================================

@app.post("/api/complete-workflow")
async def complete_workflow(request: GenerateScenarioRequest):
    """Complete BCI workflow: Generate scenario → Create speech → Store pattern"""
    try:
        # Step 1: Generate scenario
        scenario_data = await generate_scenario(request)
        
        # Step 2: Generate speech if ElevenLabs is available
        audio_result = {"success": False}
        if elevenlabs_client:
            try:
                speech_data = {
                    "scenario_id": scenario_data.id,
                    "text": scenario_data.speech,
                    "emotion": scenario_data.emotion
                }
                audio_result = await process_speech_simple(speech_data)
            except Exception as e:
                logger.error(f"Speech generation failed in workflow: {str(e)}")
        
        # Return complete result
        return {
            "success": True,
            "scenario": {
                "id": scenario_data.id,
                "emotion": scenario_data.emotion,
                "direction": scenario_data.direction,
                "emotion_confidence": scenario_data.emotion_confidence,
                "direction_confidence": scenario_data.direction_confidence,
                "speech": scenario_data.speech,
                "context": scenario_data.context,
                "generated_at": scenario_data.generated_at
            },
            "audio": {
                "url": audio_result.get("audio_url") if audio_result.get("success") else None,
                "filename": audio_result.get("filename"),
                "success": audio_result.get("success", False)
            },
            "stored_in_pinecone": pinecone_client is not None
        }
        
    except Exception as e:
        logger.error(f"Error in complete workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

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
    
    print("🚀 Starting PixelPeak BCI API Server...")
    print(f"📍 Docs available at: http://localhost:8000/docs")
    print(f"🎵 Audio files at: http://localhost:8000/audio/")
    print(f"👤 Avatar files at: http://localhost:8000/avatars/")
    print(f"🔧 Speech endpoint: http://localhost:8000/api/process-speech-simple")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )