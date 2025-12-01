from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid

class ModelProvider(str, Enum):
    OPENROUTER = "openrouter"
    LITELLM = "litellm"
    LOCAL = "local"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None
    
class ModelInfo(BaseModel):
    id: str
    name: str
    provider: ModelProvider
    description: str
    context_window: int
    max_tokens: int
    pricing: Dict[str, float]  # input, output per 1M tokens
    capabilities: List[str] = []
    is_available: bool = True
    is_local: bool = False
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str
    max_tokens: Optional[int] = 1000
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None
    
class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
class ChatResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Usage
    
class StreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    
class FileAnalysisRequest(BaseModel):
    file_path: str
    file_type: str
    query: Optional[str] = "Analyze this file"
    model: str = "gpt-4-vision-preview"
    
class FileAnalysisResponse(BaseModel):
    summary: str
    insights: List[str]
    metadata: Dict[str, Any]
    
class VoiceRequest(BaseModel):
    text: str
    voice: str = "alloy"
    speed: float = Field(1.0, ge=0.25, le=4.0)
    
class VoiceResponse(BaseModel):
    audio_url: str
    duration: float
    
class HealthStatus(BaseModel):
    status: str
    available_models: int
    total_requests: int
    avg_response_time: float
    errors: List[str] = []
