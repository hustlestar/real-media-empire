"""Abstract interface for AI providers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AIProviderInterface(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def get_response(
        self, 
        message: str, 
        user_id: int, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """Get AI response for a message.
        
        Args:
            message: User message to process
            user_id: ID of the user making the request
            system_prompt: Optional system prompt to guide the AI
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AI response string or None if failed
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the AI provider.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available and properly configured.
        
        Returns:
            True if available, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model being used.
        
        Returns:
            Dictionary containing model information
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the AI provider.
        
        Returns:
            Provider name string
        """
        pass

    @abstractmethod
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration (excluding sensitive data like API keys).
        
        Returns:
            Dictionary containing provider configuration
        """
        pass