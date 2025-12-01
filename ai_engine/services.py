import asyncio
import time
from typing import List, AsyncGenerator, Dict, Any
import json
import logging
from datetime import datetime

from .models import (
    ChatRequest, ChatResponse, ChatChoice, Usage, 
    ModelInfo, StreamChunk, HealthStatus, ModelProvider
)
from .providers import OpenRouterProvider, LiteLLMProvider

logger = logging.getLogger(__name__)

class AIModelService:
    """Main AI Model Service - handles model routing and management"""
    
    def __init__(self):
        self.openrouter = OpenRouterProvider()
        self.litellm = LiteLLMProvider()
        self.models_cache: Dict[str, ModelInfo] = {}
        self.request_count = 0
        self.response_times = []
        
    async def initialize(self):
        """Initialize all model providers"""
        try:
            await self.openrouter.initialize()
            await self.litellm.initialize()
            await self._refresh_models_cache()
            logger.info("AI Model Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Model Service: {e}")
            raise
    
    async def _refresh_models_cache(self):
        """Refresh the models cache"""
        try:
            # Get models from all providers
            openrouter_models = await self.openrouter.get_available_models()
            litellm_models = await self.litellm.get_available_models()
            
            # Combine models
            all_models = openrouter_models + litellm_models
            
            # Update cache
            for model in all_models:
                self.models_cache[model.id] = model
                
            logger.info(f"Refreshed models cache: {len(all_models)} models available")
            
        except Exception as e:
            logger.error(f"Failed to refresh models cache: {e}")
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of all available models"""
        return list(self.models_cache.values())
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Get model info
            model_info = self.models_cache.get(request.model)
            if not model_info:
                raise ValueError(f"Model {request.model} not found")
            
            # Route to appropriate provider
            if model_info.provider == ModelProvider.OPENROUTER:
                response = await self.openrouter.chat_completion(request)
            elif model_info.provider == ModelProvider.LITELLM:
                response = await self.litellm.chat_completion(request)
            else:
                raise ValueError(f"Unsupported provider: {model_info.provider}")
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream chat completion"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Get model info
            model_info = self.models_cache.get(request.model)
            if not model_info:
                raise ValueError(f"Model {request.model} not found")
            
            # Route to appropriate provider
            if model_info.provider == ModelProvider.OPENROUTER:
                async for chunk in self.openrouter.stream_chat(request):
                    yield chunk
            elif model_info.provider == ModelProvider.LITELLM:
                async for chunk in self.litellm.stream_chat(request):
                    yield chunk
            else:
                raise ValueError(f"Unsupported provider: {model_info.provider}")
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            raise
    
    async def health_check(self) -> HealthStatus:
        """Check health of all providers"""
        try:
            available_models = len(self.models_cache)
            avg_response_time = sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0
            
            return HealthStatus(
                status="healthy",
                available_models=available_models,
                total_requests=self.request_count,
                avg_response_time=avg_response_time
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthStatus(
                status="unhealthy",
                available_models=0,
                total_requests=self.request_count,
                avg_response_time=0,
                errors=[str(e)]
            )

class StreamingService:
    """Service for handling streaming responses"""
    
    @staticmethod
    async def create_streaming_response(ai_service: AIModelService, request: ChatRequest):
        """Create streaming response for FastAPI"""
        from fastapi.responses import StreamingResponse
        
        async def generate():
            async for chunk in ai_service.stream_chat(request):
                yield f"data: {json.dumps(chunk.dict())}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")

class SmartRouter:
    """Smart routing for model selection based on cost, performance, and availability"""
    
    def __init__(self, ai_service: AIModelService):
        self.ai_service = ai_service
        
    async def select_best_model(self, request: ChatRequest) -> str:
        """Select the best model for the given request"""
        models = await self.ai_service.get_available_models()
        
        # Filter available models
        available_models = [m for m in models if m.is_available]
        
        if not available_models:
            raise ValueError("No models available")
        
        # Smart selection logic
        # For now, return the first available model
        # TODO: Implement cost/performance-based selection
        return available_models[0].id
    
    async def get_fallback_model(self, preferred_model: str) -> str:
        """Get fallback model if preferred model is not available"""
        models = await self.ai_service.get_available_models()
        
        # Find available models excluding the preferred one
        fallback_models = [m for m in models if m.is_available and m.id != preferred_model]
        
        if not fallback_models:
            raise ValueError("No fallback models available")
        
        # Prefer local models for privacy
        local_models = [m for m in fallback_models if m.is_local]
        if local_models:
            return local_models[0].id
        
        # Otherwise return first available
        return fallback_models[0].id
