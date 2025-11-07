"""AI providers for the Telegram bot template."""

import logging
from typing import Optional, Dict, Any
import aiohttp
import asyncio
import json

from core.ai_interface import AIProviderInterface

logger = logging.getLogger(__name__)

class OpenRouterProvider(AIProviderInterface):
    """OpenRouter AI provider for chat completions."""

    def __init__(self, api_key: str, model: str = "deepseek/deepseek-chat-v3-0324"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/content-processor-bot",
            "X-Title": "Content Processor Bot",
        }

        logger.info(f"OpenRouter provider initialized with model: {model}")

    async def get_response(self, message: str, user_id: int, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
        """Get AI response for a user message.

        Args:
            message: User's message
            user_id: Optional user ID for tracking
            system_prompt: Optional system prompt to customize behavior

        Returns:
            AI response string
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant. Respond in a friendly and informative way."})

            messages.append({"role": "user", "content": message})
            
            logger.info(f"=== SENDING TO LLM (user_id: {user_id}) ===")
            logger.info(f"Model: {self.model}")
            logger.info(f"System Prompt: {messages[0]['content']}")
            logger.info(f"User Prompt: {messages[1]['content']}")
            logger.info("=" * 50)

            max_tokens = kwargs.get('max_tokens', 4000)
            temperature = kwargs.get('temperature', 0.7)
            top_p = kwargs.get('top_p', 0.9)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", headers=self.headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)  # Increased timeout for long content
                ) as response:

                    if response.status == 200:
                        data = await response.json()

                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0]["message"]["content"]

                            if "usage" in data:
                                usage = data["usage"]
                                logger.debug(
                                    f"OpenRouter usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                                    f"Completion: {usage.get('completion_tokens', 0)}, "
                                    f"Total: {usage.get('total_tokens', 0)}"
                                )

                            return content.strip()
                        else:
                            logger.error("No choices in OpenRouter response")
                            return "I'm sorry, I couldn't generate a response."

                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")

                        if response.status == 401:
                            return "AI service authentication failed. Please check the API key."
                        elif response.status == 429:
                            return "AI service is currently busy. Please try again in a moment."
                        elif response.status >= 500:
                            return "AI service is temporarily unavailable. Please try again later."
                        else:
                            return "I'm having trouble processing your request right now."

        except asyncio.TimeoutError:
            logger.error("OpenRouter request timeout")
            return "The AI service is taking too long to respond. Please try again."

        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return "I encountered an error while processing your message. Please try again."

    async def get_streaming_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None):
        """Get streaming AI response (generator).

        Args:
            message: User's message
            user_id: Optional user ID for tracking
            system_prompt: Optional system prompt to customize behavior

        Yields:
            Chunks of AI response
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant. Respond in a friendly and informative way."})

            messages.append({"role": "user", "content": message})

            payload = {"model": self.model, "messages": messages, "max_tokens": 1000, "temperature": 0.7, "stream": True}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", headers=self.headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode("utf-8").strip()

                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove 'data: ' prefix

                                if data_str == "[DONE]":
                                    break

                                try:
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        if "content" in delta:
                                            yield delta["content"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter streaming error {response.status}: {error_text}")
                        yield "Error: Unable to get streaming response."

        except Exception as e:
            logger.error(f"OpenRouter streaming error: {e}")
            yield "Error: Streaming response failed."

    async def get_models(self) -> Dict[str, Any]:
        """Get available models from OpenRouter.

        Returns:
            Dictionary with model information
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models", headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to get models: {response.status}")
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return {"error": str(e)}

    def is_available(self) -> bool:
        """Check if the AI provider is properly configured."""
        return bool(self.api_key and self.model)

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information."""
        return {
            "provider": "OpenRouter",
            "model": self.model,
            "base_url": self.base_url,
            "max_tokens": 4000,
            "supports_streaming": True
        }

    def get_provider_name(self) -> str:
        """Get the name of the AI provider."""
        return "OpenRouter"

    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration (excluding sensitive data)."""
        return {
            "provider": "OpenRouter",
            "model": self.model,
            "base_url": self.base_url,
            "default_max_tokens": 4000,
            "default_temperature": 0.7,
            "supports_streaming": True,
            "supports_system_prompts": True
        }

    async def test_connection(self) -> bool:
        """Test the connection to OpenRouter API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_message = "Hello"
            response = await self.get_response(test_message, user_id=0)
            return response is not None and not str(response).startswith("Error:") and not str(response).startswith("AI service")

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class MockAIProvider(AIProviderInterface):
    """Mock AI provider for testing without API calls."""

    def __init__(self):
        self.model = "mock-model"
        logger.info("Mock AI provider initialized")

    async def get_response(self, message: str, user_id: int, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
        """Return a mock response."""
        return f"Mock response to: {message[:50]}{'...' if len(message) > 50 else ''}"

    async def get_streaming_response(self, message: str, user_id: Optional[int] = None, system_prompt: Optional[str] = None):
        """Return a mock streaming response."""
        mock_response = f"Mock streaming response to: {message}"
        for word in mock_response.split():
            yield word + " "

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {
            "provider": "Mock",
            "model": self.model,
            "base_url": "mock://localhost",
            "max_tokens": 1000,
            "supports_streaming": True
        }

    def get_provider_name(self) -> str:
        """Get the name of the AI provider."""
        return "Mock"

    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration (excluding sensitive data)."""
        return {
            "provider": "Mock",
            "model": self.model,
            "base_url": "mock://localhost",
            "default_max_tokens": 1000,
            "default_temperature": 0.7,
            "supports_streaming": True,
            "supports_system_prompts": True
        }

    async def test_connection(self) -> bool:
        """Mock connection test always succeeds."""
        return True
