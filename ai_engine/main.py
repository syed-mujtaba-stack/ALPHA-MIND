from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from contextlib import asynccontextmanager

from .models import ChatRequest, ChatResponse, ModelInfo
from .services import AIModelService, StreamingService
from .utils import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("AI Engine starting up...")
    ai_service = AIModelService()
    await ai_service.initialize()
    app.state.ai_service = ai_service
    yield
    # Shutdown
    logger.info("AI Engine shutting down...")

app = FastAPI(
    title="ALPHA MIND AI Engine",
    description="Hybrid AI Model Gateway for ALPHA MIND Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/")
async def root():
    return {"message": "ALPHA MIND AI Engine", "status": "running"}

@app.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """Get list of available AI models"""
    try:
        ai_service = app.state.ai_service
        return await ai_service.get_available_models()
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Generate chat completion"""
    try:
        ai_service = app.state.ai_service
        return await ai_service.chat_completion(request)
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat completion"""
    try:
        ai_service = app.state.ai_service
        return StreamingService.create_streaming_response(ai_service, request)
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: int):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process chat message
            ai_service = app.state.ai_service
            request = ChatRequest(**message_data)
            
            # Stream response back to client
            async for chunk in ai_service.stream_chat(request):
                await manager.send_personal_message(
                    json.dumps(chunk.dict()), websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        ai_service = app.state.ai_service
        status = await ai_service.health_check()
        return {
            "status": "healthy",
            "models": status["available_models"],
            "engine": "ALPHA MIND AI Engine v1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000, reload=True)
