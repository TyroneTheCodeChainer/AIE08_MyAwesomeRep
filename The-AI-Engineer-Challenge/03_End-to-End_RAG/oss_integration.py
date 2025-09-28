"""
Session 03: Open Source LLM Integration
======================================

This module provides integration with open-source LLMs via Ollama,
aligning with the AI MakerSpace curriculum requirement for OSS model support.

INDUSTRY ALIGNMENT:
- Supports the "Advanced Build" requirement for OSS LLMs
- Enables local model deployment for cost efficiency
- Provides fallback options when cloud APIs are unavailable
- Demonstrates multi-model architecture patterns

SUPPORTED MODELS:
- Llama 3.1 (8B, 70B)
- Mistral 7B
- CodeLlama
- Gemma 2B, 7B
- Custom fine-tuned models
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import requests
import openai
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: str  # "openai", "ollama", "together"
    model_id: str
    max_tokens: int
    temperature: float
    context_length: int
    cost_per_1k_tokens: float = 0.0

class OSSModelManager:
    """
    Manages integration with open-source LLMs via Ollama and other providers.
    
    This class provides a unified interface for working with both cloud-based
    and local open-source models, enabling cost-effective AI applications.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 ollama_base_url: str = "http://localhost:11434",
                 together_api_key: str = None):
        """Initialize the OSS Model Manager."""
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.ollama_base_url = ollama_base_url
        self.together_api_key = together_api_key
        
        # Available models configuration
        self.models = {
            # OpenAI Models
            "gpt-4o-mini": ModelConfig(
                name="GPT-4o Mini",
                provider="openai",
                model_id="gpt-4o-mini",
                max_tokens=16384,
                temperature=0.7,
                context_length=128000,
                cost_per_1k_tokens=0.15
            ),
            "gpt-4o": ModelConfig(
                name="GPT-4o",
                provider="openai",
                model_id="gpt-4o",
                max_tokens=4096,
                temperature=0.7,
                context_length=128000,
                cost_per_1k_tokens=5.0
            ),
            
            # Ollama Models (Local)
            "llama3.1:8b": ModelConfig(
                name="Llama 3.1 8B",
                provider="ollama",
                model_id="llama3.1:8b",
                max_tokens=4096,
                temperature=0.7,
                context_length=8192,
                cost_per_1k_tokens=0.0
            ),
            "llama3.1:70b": ModelConfig(
                name="Llama 3.1 70B",
                provider="ollama",
                model_id="llama3.1:70b",
                max_tokens=4096,
                temperature=0.7,
                context_length=8192,
                cost_per_1k_tokens=0.0
            ),
            "mistral:7b": ModelConfig(
                name="Mistral 7B",
                provider="ollama",
                model_id="mistral:7b",
                max_tokens=4096,
                temperature=0.7,
                context_length=32768,
                cost_per_1k_tokens=0.0
            ),
            "codellama:7b": ModelConfig(
                name="CodeLlama 7B",
                provider="ollama",
                model_id="codellama:7b",
                max_tokens=4096,
                temperature=0.7,
                context_length=16384,
                cost_per_1k_tokens=0.0
            ),
            "gemma2:2b": ModelConfig(
                name="Gemma 2 2B",
                provider="ollama",
                model_id="gemma2:2b",
                max_tokens=4096,
                temperature=0.7,
                context_length=8192,
                cost_per_1k_tokens=0.0
            ),
            "gemma2:9b": ModelConfig(
                name="Gemma 2 9B",
                provider="ollama",
                model_id="gemma2:9b",
                max_tokens=4096,
                temperature=0.7,
                context_length=8192,
                cost_per_1k_tokens=0.0
            )
        }
        
        # Default model selection strategy
        self.default_strategy = "cost_effective"  # "cost_effective", "performance", "balanced"
        
    async def generate_response(self, 
                              prompt: str, 
                              model_id: str = None,
                              system_message: str = None,
                              max_tokens: int = None,
                              temperature: float = None) -> Dict[str, Any]:
        """
        Generate a response using the specified model.
        
        Args:
            prompt: The user prompt
            model_id: Specific model to use (if None, uses default strategy)
            system_message: System message for the conversation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary containing the response and metadata
        """
        if model_id is None:
            model_id = self._select_model_by_strategy()
        
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found. Available models: {list(self.models.keys())}")
        
        model_config = self.models[model_id]
        
        # Override config with provided parameters
        if max_tokens is None:
            max_tokens = model_config.max_tokens
        if temperature is None:
            temperature = model_config.temperature
        
        try:
            if model_config.provider == "openai":
                return await self._generate_openai_response(
                    prompt, system_message, model_config.model_id, max_tokens, temperature
                )
            elif model_config.provider == "ollama":
                return await self._generate_ollama_response(
                    prompt, system_message, model_config.model_id, max_tokens, temperature
                )
            elif model_config.provider == "together":
                return await self._generate_together_response(
                    prompt, system_message, model_config.model_id, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {model_config.provider}")
                
        except Exception as e:
            logger.error(f"Error generating response with {model_id}: {str(e)}")
            # Fallback to a different model
            return await self._fallback_generation(prompt, system_message, model_id)
    
    async def _generate_openai_response(self, 
                                      prompt: str, 
                                      system_message: str,
                                      model_id: str,
                                      max_tokens: int,
                                      temperature: float) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": model_id,
            "provider": "openai",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _generate_ollama_response(self, 
                                      prompt: str, 
                                      system_message: str,
                                      model_id: str,
                                      max_tokens: int,
                                      temperature: float) -> Dict[str, Any]:
        """Generate response using Ollama API."""
        # Check if model is available
        if not await self._is_ollama_model_available(model_id):
            raise ValueError(f"Model {model_id} not available in Ollama. Please pull it first.")
        
        # Prepare the request
        request_data = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        if system_message:
            request_data["system"] = system_message
        
        # Make the request
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json=request_data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        return {
            "content": result["response"],
            "model": model_id,
            "provider": "ollama",
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
            },
            "finish_reason": "stop"
        }
    
    async def _generate_together_response(self, 
                                        prompt: str, 
                                        system_message: str,
                                        model_id: str,
                                        max_tokens: int,
                                        temperature: float) -> Dict[str, Any]:
        """Generate response using Together AI API."""
        if not self.together_api_key:
            raise ValueError("Together AI API key not provided")
        
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        request_data = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=request_data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Together AI API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": model_id,
            "provider": "together",
            "usage": result["usage"],
            "finish_reason": result["choices"][0]["finish_reason"]
        }
    
    async def _is_ollama_model_available(self, model_id: str) -> bool:
        """Check if a model is available in Ollama."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"] == model_id for model in models)
            return False
        except:
            return False
    
    async def _fallback_generation(self, 
                                 prompt: str, 
                                 system_message: str,
                                 failed_model: str) -> Dict[str, Any]:
        """Fallback to a different model if the primary one fails."""
        logger.warning(f"Falling back from {failed_model}")
        
        # Try OpenAI GPT-4o-mini as fallback
        try:
            return await self._generate_openai_response(
                prompt, system_message, "gpt-4o-mini", 4096, 0.7
            )
        except Exception as e:
            logger.error(f"Fallback also failed: {str(e)}")
            return {
                "content": "I apologize, but I'm unable to generate a response at the moment. Please try again later.",
                "model": "fallback",
                "provider": "error",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "finish_reason": "error",
                "error": str(e)
            }
    
    def _select_model_by_strategy(self) -> str:
        """Select model based on the configured strategy."""
        if self.default_strategy == "cost_effective":
            # Prefer free Ollama models
            ollama_models = [k for k, v in self.models.items() if v.provider == "ollama"]
            if ollama_models:
                return ollama_models[0]  # Return first available Ollama model
            return "gpt-4o-mini"  # Fallback to cheapest OpenAI model
        
        elif self.default_strategy == "performance":
            # Prefer most capable models
            return "gpt-4o"
        
        elif self.default_strategy == "balanced":
            # Balance between cost and performance
            return "gpt-4o-mini"
        
        else:
            return "gpt-4o-mini"
    
    async def pull_ollama_model(self, model_id: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/pull",
                json={"name": model_id},
                timeout=300  # 5 minutes timeout for model pulling
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model {model_id}: {str(e)}")
            return False
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models with their configurations."""
        return [
            {
                "model_id": model_id,
                "name": config.name,
                "provider": config.provider,
                "max_tokens": config.max_tokens,
                "context_length": config.context_length,
                "cost_per_1k_tokens": config.cost_per_1k_tokens
            }
            for model_id, config in self.models.items()
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all model providers."""
        health_status = {
            "openai": False,
            "ollama": False,
            "together": False
        }
        
        # Check OpenAI
        try:
            await self.openai_client.models.list()
            health_status["openai"] = True
        except:
            pass
        
        # Check Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            health_status["ollama"] = response.status_code == 200
        except:
            pass
        
        # Check Together AI
        if self.together_api_key:
            try:
                headers = {"Authorization": f"Bearer {self.together_api_key}"}
                response = requests.get(
                    "https://api.together.xyz/v1/models",
                    headers=headers,
                    timeout=5
                )
                health_status["together"] = response.status_code == 200
            except:
                pass
        
        return health_status

# Example usage and testing
async def main():
    """Example usage of the OSS Model Manager."""
    # Initialize the manager
    model_manager = OSSModelManager(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        ollama_base_url="http://localhost:11434",
        together_api_key=os.getenv("TOGETHER_API_KEY")
    )
    
    # Check health
    health = await model_manager.health_check()
    print(f"Health status: {health}")
    
    # Generate response with default model
    response = await model_manager.generate_response(
        "Explain the benefits of using open-source LLMs in production applications."
    )
    
    print(f"Response: {response['content']}")
    print(f"Model used: {response['model']} ({response['provider']})")

if __name__ == "__main__":
    asyncio.run(main())

