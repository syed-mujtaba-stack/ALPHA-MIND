import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with default value"""
    return os.getenv(key, default)

def validate_api_key(api_key: str, provider: str) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    
    # Basic validation for different providers
    if provider == "openrouter":
        return len(api_key) > 20 and api_key.startswith("sk-or-v1-")
    elif provider == "openai":
        return len(api_key) > 20 and api_key.startswith("sk-")
    
    return len(api_key) > 10

def calculate_cost(tokens: int, pricing: Dict[str, float]) -> float:
    """Calculate cost based on token count and pricing"""
    input_cost = (tokens * pricing.get('input', 0)) / 1_000_000
    output_cost = (tokens * pricing.get('output', 0)) / 1_000_000
    return input_cost + output_cost

def format_model_name(model_id: str) -> str:
    """Format model ID for display"""
    parts = model_id.split('/')
    if len(parts) > 1:
        return f"{parts[0].title()} {parts[1].replace('-', ' ').title()}"
    return model_id.replace('-', ' ').title()

def sanitize_message(content: str) -> str:
    """Sanitize message content for logging"""
    if len(content) > 100:
        return content[:100] + "..."
    return content

class Timer:
    """Simple timer context manager"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

import time
