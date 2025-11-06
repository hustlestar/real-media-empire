"""Temporary content storage for processing."""

import logging
import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ContentStorage:
    """Simple in-memory storage for extracted content awaiting processing."""

    def __init__(self, ttl_hours: int = 24):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._user_collections: Dict[int, List[str]] = {}  # Maps user_id to list of content_ids
        self._retry_storage: Dict[str, Dict[str, Any]] = {}  # Stores retry context for failed operations
        self._ttl_hours = ttl_hours

    def store_content(self, content: str, source_type: str, source_info: Optional[Dict] = None, user_id: Optional[int] = None) -> str:
        """Store content and return a unique ID."""
        content_id = str(uuid.uuid4())[:8]  # Short ID for callbacks
        
        self._storage[content_id] = {
            'content': content,
            'source_type': source_type,
            'source_info': source_info or {},
            'created_at': datetime.now(),
            'processing_state': 'ready',  # ready, awaiting_prompt, processing, completed
            'processing_type': None,
            'user_prompt': None,
            'user_id': user_id
        }
        
        # Add to user's collection if user_id provided
        if user_id:
            if user_id not in self._user_collections:
                self._user_collections[user_id] = []
            self._user_collections[user_id].append(content_id)
        
        # Clean up old entries
        self._cleanup_expired()
        
        logger.info(f"Stored content with ID: {content_id} for user: {user_id}")
        return content_id

    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content by ID."""
        self._cleanup_expired()
        return self._storage.get(content_id)

    def remove_content(self, content_id: str) -> bool:
        """Remove content by ID."""
        if content_id in self._storage:
            del self._storage[content_id]
            logger.info(f"Removed content with ID: {content_id}")
            return True
        return False

    def _cleanup_expired(self) -> None:
        """Remove expired content."""
        now = datetime.now()
        expired_ids = []
        
        for content_id, data in self._storage.items():
            if now - data['created_at'] > timedelta(hours=self._ttl_hours):
                expired_ids.append(content_id)
        
        for expired_id in expired_ids:
            # Remove from user collections
            user_id = self._storage[expired_id].get('user_id')
            if user_id and user_id in self._user_collections:
                if expired_id in self._user_collections[user_id]:
                    self._user_collections[user_id].remove(expired_id)
                if not self._user_collections[user_id]:
                    del self._user_collections[user_id]
            
            del self._storage[expired_id]
            logger.debug(f"Removed expired content: {expired_id}")

    def update_content_state(self, content_id: str, processing_type: str = None, user_prompt: str = None,
                            processing_state: str = None, user_id: int = None, output_language: str = None) -> bool:
        """Update content processing state and metadata."""
        if content_id not in self._storage:
            logger.error(f"Cannot update - content {content_id} not found in storage")
            return False
            
        content_data = self._storage[content_id]
        
        updates = []
        if processing_type is not None:
            content_data['processing_type'] = processing_type
            updates.append(f"type={processing_type}")
        if user_prompt is not None:
            content_data['user_prompt'] = user_prompt
            updates.append(f"prompt={user_prompt}")  # Full prompt, no truncation
        if processing_state is not None:
            content_data['processing_state'] = processing_state
            updates.append(f"state={processing_state}")
        if user_id is not None:
            content_data['user_id'] = user_id
            updates.append(f"user={user_id}")
        if output_language is not None:
            content_data['output_language'] = output_language
            updates.append(f"language={output_language}")

        logger.info(f"Updated content {content_id}: {', '.join(updates)}")
        return True

    def get_user_content(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all content items for a specific user."""
        self._cleanup_expired()
        
        if user_id not in self._user_collections:
            return []
        
        content_items = []
        for content_id in self._user_collections[user_id]:
            if content_id in self._storage:
                content_items.append({
                    'id': content_id,
                    **self._storage[content_id]
                })
        
        return content_items
    
    def clear_user_content(self, user_id: int) -> int:
        """Clear all content for a specific user. Returns number of items cleared."""
        if user_id not in self._user_collections:
            return 0
        
        cleared_count = 0
        content_ids = self._user_collections[user_id].copy()
        
        for content_id in content_ids:
            if content_id in self._storage:
                del self._storage[content_id]
                cleared_count += 1
        
        del self._user_collections[user_id]
        logger.info(f"Cleared {cleared_count} content items for user {user_id}")
        return cleared_count
    
    def get_combined_content(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get all user's content combined into a single structure."""
        content_items = self.get_user_content(user_id)
        
        if not content_items:
            return None
        
        combined = {
            'total_sources': len(content_items),
            'sources': [],
            'combined_text': ""
        }
        
        for idx, item in enumerate(content_items, 1):
            source_info = item.get('source_info', {})
            source_desc = f"Source {idx} ({item['source_type']})"
            
            if 'title' in source_info:
                source_desc += f": {source_info['title']}"
            elif 'url' in source_info:
                source_desc += f": {source_info['url']}"
            elif 'filename' in source_info:
                source_desc += f": {source_info['filename']}"
            
            combined['sources'].append({
                'description': source_desc,
                'type': item['source_type'],
                'info': source_info
            })
            
            combined['combined_text'] += f"\n\n{'='*50}\n{source_desc}\n{'='*50}\n\n{item['content']}"
        
        return combined

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        self._cleanup_expired()
        states = {}
        for data in self._storage.values():
            state = data.get('processing_state', 'unknown')
            states[state] = states.get(state, 0) + 1

        return {
            'total_items': len(self._storage),
            'total_users': len(self._user_collections),
            'ttl_hours': self._ttl_hours,
            'states': states,
            'users_with_content': {user_id: len(content_ids)
                                  for user_id, content_ids in self._user_collections.items()}
        }

    def store_retry_context(self, operation_type: str, user_id: int, user_language: str, **kwargs) -> str:
        """Store retry context for failed operations.

        Args:
            operation_type: Type of operation ('pdf_document', 'pdf_url', 'youtube_url', 'web_url', 'ai_message', 'content_processing')
            user_id: User ID
            user_language: User's language
            **kwargs: Additional operation-specific parameters

        Returns:
            Retry context ID
        """
        retry_id = str(uuid.uuid4())[:8]

        self._retry_storage[retry_id] = {
            'operation_type': operation_type,
            'user_id': user_id,
            'user_language': user_language,
            'created_at': datetime.now(),
            'params': kwargs
        }

        logger.info(f"Stored retry context {retry_id} for operation {operation_type}, user {user_id}")
        return retry_id

    def get_retry_context(self, retry_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve retry context by ID."""
        self._cleanup_expired_retry()
        return self._retry_storage.get(retry_id)

    def remove_retry_context(self, retry_id: str) -> bool:
        """Remove retry context by ID."""
        if retry_id in self._retry_storage:
            del self._retry_storage[retry_id]
            logger.info(f"Removed retry context {retry_id}")
            return True
        return False

    def _cleanup_expired_retry(self) -> None:
        """Remove expired retry contexts."""
        now = datetime.now()
        expired_ids = []

        for retry_id, data in self._retry_storage.items():
            if now - data['created_at'] > timedelta(hours=self._ttl_hours):
                expired_ids.append(retry_id)

        for expired_id in expired_ids:
            del self._retry_storage[expired_id]
            logger.debug(f"Removed expired retry context: {expired_id}")