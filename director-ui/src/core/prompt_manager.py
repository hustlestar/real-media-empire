"""Prompt management for AI processing."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages AI prompts from YAML configuration."""

    def __init__(self, prompts_file: str = None):
        """Initialize the prompt manager.
        
        Args:
            prompts_file: Path to the prompts YAML file. If None, uses default location.
        """
        if prompts_file is None:
            # Default location relative to the project root
            project_root = Path(__file__).parent.parent.parent
            prompts_file = project_root / "config" / "prompts.yaml"
        
        self.prompts_file = Path(prompts_file)
        self._prompts: Dict[str, Any] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompts from YAML file."""
        try:
            if not self.prompts_file.exists():
                logger.error(f"Prompts file not found: {self.prompts_file}")
                return

            with open(self.prompts_file, 'r', encoding='utf-8') as file:
                self._prompts = yaml.safe_load(file) or {}
            
            logger.info(f"Loaded prompts from {self.prompts_file}")
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML prompts file: {e}")
        except Exception as e:
            logger.error(f"Error loading prompts file: {e}")

    def reload_prompts(self) -> None:
        """Reload prompts from file."""
        logger.info("Reloading prompts from file")
        self._load_prompts()

    def get_system_prompt(self, processing_type: str, source_type: str) -> Optional[str]:
        """Get system prompt for a processing type.
        
        Args:
            processing_type: Type of processing (summary, mvp_plan, content_ideas)
            source_type: Type of source content (PDF document, YouTube video, etc.)
            
        Returns:
            System prompt string with source_type formatted, or None if not found
        """
        try:
            prompt_template = self._prompts.get(processing_type, {}).get('system_prompt')
            if prompt_template:
                formatted_prompt = prompt_template.format(source_type=source_type)
                logger.debug(f"Retrieved system prompt for {processing_type}: {formatted_prompt}")  # Full prompt
                return formatted_prompt
            else:
                logger.warning(f"System prompt not found for processing type: {processing_type}")
                logger.debug(f"Available processing types: {list(self._prompts.keys())}")
                return None
        except KeyError as e:
            logger.error(f"Error getting system prompt for {processing_type}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting system prompt: {e}")
            return None

    def get_user_prompt(self, processing_type: str, source_type: str, content: str) -> Optional[str]:
        """Get user prompt for a processing type.
        
        Args:
            processing_type: Type of processing (summary, mvp_plan, content_ideas)
            source_type: Type of source content (PDF document, YouTube video, etc.)
            content: The actual content to be processed
            
        Returns:
            User prompt string with variables formatted, or None if not found
        """
        try:
            max_length = self.get_config('content_limits', 'max_content_length', 8000)
            truncation_indicator = self.get_config('content_limits', 'append_truncation_indicator', '...')
            
            # Truncate content if necessary
            if len(content) > max_length:
                content = content[:max_length] + truncation_indicator

            prompt_template = self._prompts.get('user_prompts', {}).get(processing_type)
            if prompt_template:
                return prompt_template.format(source_type=source_type, content=content)
            else:
                logger.warning(f"User prompt not found for processing type: {processing_type}")
                return None
        except KeyError as e:
            logger.error(f"Error getting user prompt for {processing_type}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user prompt: {e}")
            return None

    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value from prompts file.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        try:
            return self._prompts.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Error getting config {section}.{key}: {e}")
            return default

    def get_all_processing_types(self) -> list:
        """Get list of all available processing types."""
        processing_types = []
        for key in self._prompts.keys():
            if key not in ['user_prompts', 'content_limits', 'processing']:
                if isinstance(self._prompts[key], dict) and 'system_prompt' in self._prompts[key]:
                    processing_types.append(key)
        return processing_types

    def validate_prompts(self) -> Dict[str, list]:
        """Validate that all required prompts are present.
        
        Returns:
            Dictionary with 'missing' and 'invalid' lists
        """
        required_types = ['summary', 'mvp_plan', 'content_ideas']
        missing = []
        invalid = []
        
        for ptype in required_types:
            if ptype not in self._prompts:
                missing.append(f"{ptype} (entire section)")
            elif 'system_prompt' not in self._prompts[ptype]:
                missing.append(f"{ptype}.system_prompt")
            
            if 'user_prompts' not in self._prompts:
                missing.append("user_prompts (entire section)")
            elif ptype not in self._prompts.get('user_prompts', {}):
                missing.append(f"user_prompts.{ptype}")
        
        return {
            'missing': missing,
            'invalid': invalid
        }

    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return self._prompts.get('processing', {
            'retry_attempts': 3,
            'timeout_seconds': 60,
            'cache_results': True,
            'cache_ttl_hours': 24
        })

    def is_loaded(self) -> bool:
        """Check if prompts are loaded successfully."""
        return bool(self._prompts)

    def get_prompts_info(self) -> Dict[str, Any]:
        """Get information about loaded prompts."""
        validation = self.validate_prompts()
        return {
            'file_path': str(self.prompts_file),
            'file_exists': self.prompts_file.exists(),
            'is_loaded': self.is_loaded(),
            'available_types': self.get_all_processing_types(),
            'validation': validation,
            'config': self.get_processing_config()
        }