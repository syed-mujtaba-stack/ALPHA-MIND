import asyncio
import aiohttp
import json
import time
from typing import List, AsyncGenerator, Dict, Any
import logging
from datetime import datetime

from .models import (
    ChatRequest, ChatResponse, ChatChoice, Usage, 
    ModelInfo, StreamChunk, ModelProvider
)

logger = logging.getLogger(__name__)

class OpenRouterProvider:
    """OpenRouter API provider for cloud models"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        
    async def initialize(self):
        """Initialize the provider"""
        import os
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.warning("OpenRouter API key not found")
            return
        
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        logger.info("OpenRouter provider initialized")
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get available models from OpenRouter"""
        if not self.session:
            return []
        
        try:
            async with self.session.get(f"{self.base_url}/models") as response:
                data = await response.json()
                
                models = []
                for model_data in data.get('data', []):
                    # Only include popular models
                    if model_data.get('id') in [
                        'openai/gpt-4',
                        'openai/gpt-4-turbo',
                        'openai/gpt-3.5-turbo',
                        'anthropic/claude-3-opus',
                        'anthropic/claude-3-sonnet',
                        'anthropic/claude-3-haiku',
                        'google/gemini-pro',
                        'meta-llama/llama-3-70b-instruct',
                        'mistralai/mistral-large'
                    ]:
                        model = ModelInfo(
                            id=model_data['id'],
                            name=model_data['name'],
                            provider=ModelProvider.OPENROUTER,
                            description=model_data.get('description', ''),
                            context_window=model_data.get('context_length', 4096),
                            max_tokens=model_data.get('context_length', 4096),
                            pricing={
                                'input': model_data.get('pricing', {}).get('prompt', 0),
                                'output': model_data.get('pricing', {}).get('completion', 0)
                            },
                            capabilities=model_data.get('capabilities', []),
                            is_available=True,
                            is_local=False
                        )
                        models.append(model)
                
                return models
                
        except Exception as e:
            logger.error(f"Failed to get OpenRouter models: {e}")
            return []
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion"""
        if not self.session:
            raise ValueError("OpenRouter not initialized")
        
        try:
            payload = {
                "model": request.model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
            
            async with self.session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                data = await response.json()
                
                return ChatResponse(
                    id=data.get('id', ''),
                    created=data.get('created', int(time.time())),
                    model=data.get('model', request.model),
                    choices=[
                        ChatChoice(
                            index=choice.get('index', 0),
                            message=ChatMessage(
                                role=choice['message']['role'],
                                content=choice['message']['content']
                            ),
                            finish_reason=choice.get('finish_reason')
                        )
                        for choice in data.get('choices', [])
                    ],
                    usage=Usage(
                        prompt_tokens=data.get('usage', {}).get('prompt_tokens', 0),
                        completion_tokens=data.get('usage', {}).get('completion_tokens', 0),
                        total_tokens=data.get('usage', {}).get('total_tokens', 0)
                    )
                )
                
        except Exception as e:
            logger.error(f"OpenRouter chat completion failed: {e}")
            raise
    
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream chat completion"""
        if not self.session:
            raise ValueError("OpenRouter not initialized")
        
        try:
            payload = {
                "model": request.model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": True
            }
            
            async with self.session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            yield StreamChunk(
                                id=data.get('id', ''),
                                created=data.get('created', int(time.time())),
                                model=data.get('model', request.model),
                                choices=data.get('choices', [])
                            )
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"OpenRouter stream chat failed: {e}")
            raise

class LiteLLMProvider:
    """LiteLLM provider for local models"""
    
    def __init__(self):
        self.base_url = "http://localhost:4000"  # LiteLLM server
        self.session = None
        
    async def initialize(self):
        """Initialize the provider"""
        self.session = aiohttp.ClientSession()
        logger.info("LiteLLM provider initialized")
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get available local models"""
        models = []
        
        # Common local models that can be loaded
        local_models_config = [
            {
                'id': 'llama-3-8b-instruct',
                'name': 'Llama 3 8B Instruct',
                'description': 'Meta\'s Llama 3 8B parameter instruction-tuned model',
                'context_window': 8192,
                'pricing': {'input': 0, 'output': 0}
            },
            {
                'id': 'mistral-7b-instruct',
                'name': 'Mistral 7B Instruct',
                'description': 'Mistral AI\'s 7B parameter instruction-tuned model',
                'context_window': 4096,
                'pricing': {'input': 0, 'output': 0}
            },
            {
                'id': 'phi-3-mini',
                'name': 'Phi-3 Mini',
                'description': 'Microsoft\'s Phi-3 Mini 3.8B parameter model',
                'context_window': 4096,
                'pricing': {'input': 0, 'output': 0}
            }
        ]
        
        for model_config in local_models_config:
            model = ModelInfo(
                id=model_config['id'],
                name=model_config['name'],
                provider=ModelProvider.LITELLM,
                description=model_config['description'],
                context_window=model_config['context_window'],
                max_tokens=model_config['context_window'],
                pricing=model_config['pricing'],
                capabilities=['text-generation'],
                is_available=True,  # Assume available if LiteLLM is running
                is_local=True
            )
            models.append(model)
        
        return models
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion using local model"""
        if not self.session:
            raise ValueError("LiteLLM not initialized")
        
        try:
            payload = {
                "model": f"local/{request.model}",
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                data = await response.json()
                
                return ChatResponse(
                    id=data.get('id', ''),
                    created=data.get('created', int(time.time())),
                    model=data.get('model', request.model),
                    choices=[
                        ChatChoice(
                            index=choice.get('index', 0),
                            message=ChatMessage(
                                role=choice['message']['role'],
                                content=choice['message']['content']
                            ),
                            finish_reason=choice.get('finish_reason')
                        )
                        for choice in data.get('choices', [])
                    ],
                    usage=Usage(
                        prompt_tokens=data.get('usage', {}).get('prompt_tokens', 0),
                        completion_tokens=data.get('usage', {}).get('completion_tokens', 0),
                        total_tokens=data.get('usage', {}).get('total_tokens', 0)
                    )
                )
                
        except Exception as e:
            logger.error(f"LiteLLM chat completion failed: {e}")
            raise
    
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream chat completion using local model"""
        if not self.session:
            raise ValueError("LiteLLM not initialized")
        
        try:
            payload = {
                "model": f"local/{request.model}",
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": True
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            yield StreamChunk(
                                id=data.get('id', ''),
                                created=data.get('created', int(time.time())),
                                model=data.get('model', request.model),
                                choices=data.get('choices', [])
                            )
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"LiteLLM stream chat failed: {e}")
            raise
