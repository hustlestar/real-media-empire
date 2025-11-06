"""Utility for saving LLM outputs as markdown files."""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)

class MarkdownSaver:
    """Saves LLM outputs as markdown files."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the markdown saver.
        
        Args:
            output_dir: Directory to save markdown files. Defaults to 'outputs' in project root.
        """
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / "outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Markdown saver initialized with output directory: {self.output_dir}")
    
    def save_output(
        self, 
        content: str, 
        processing_type: str, 
        source_type: str,
        user_id: int,
        title: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> Tuple[Path, str]:
        """Save LLM output as a markdown file.
        
        Args:
            content: The LLM output content
            processing_type: Type of processing (summary, mvp_plan, content_ideas)
            source_type: Type of source (PDF, YouTube, Web article)
            user_id: Telegram user ID
            title: Optional title for the document
            user_prompt: Optional user's custom instructions
            
        Returns:
            Tuple of (file_path, filename)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        type_map = {
            "summary": "summary",
            "mvp_plan": "mvp",
            "content_ideas": "ideas"
        }
        
        file_prefix = type_map.get(processing_type, processing_type)
        filename = f"{file_prefix}_{user_id}_{timestamp}.md"
        file_path = self.output_dir / filename
        
        # Prepare the full markdown content
        full_content = self._prepare_markdown(
            content=content,
            processing_type=processing_type,
            source_type=source_type,
            title=title,
            user_prompt=user_prompt,
            timestamp=datetime.now()
        )
        
        # Save the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Saved markdown output to: {file_path}")
            return file_path, filename
            
        except Exception as e:
            logger.error(f"Error saving markdown file: {e}")
            raise
    
    def _prepare_markdown(
        self,
        content: str,
        processing_type: str,
        source_type: str,
        title: Optional[str],
        user_prompt: Optional[str],
        timestamp: datetime
    ) -> str:
        """Prepare the full markdown document with metadata.
        
        Args:
            content: The main content
            processing_type: Type of processing
            source_type: Type of source
            title: Optional title
            user_prompt: Optional user instructions
            timestamp: Generation timestamp
            
        Returns:
            Complete markdown document
        """
        # Extract title from content if not provided
        if not title:
            # Try to extract first heading from content
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            else:
                type_titles = {
                    "summary": "Content Summary",
                    "mvp_plan": "MVP Development Plan",
                    "content_ideas": "Content Ideas & Strategy"
                }
                title = type_titles.get(processing_type, "AI Generated Content")
        
        # Build the document
        doc_parts = []
        
        # Add metadata header
        doc_parts.append("---")
        doc_parts.append(f"title: {title}")
        doc_parts.append(f"type: {processing_type}")
        doc_parts.append(f"source: {source_type}")
        doc_parts.append(f"generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if user_prompt:
            doc_parts.append(f"custom_instructions: {user_prompt}")
        doc_parts.append("---")
        doc_parts.append("")
        
        # Add the main content
        doc_parts.append(content)
        
        # Add footer
        doc_parts.append("")
        doc_parts.append("---")
        doc_parts.append("")
        doc_parts.append(f"*Generated on {timestamp.strftime('%B %d, %Y at %H:%M')}*")
        doc_parts.append("")
        doc_parts.append("*Powered by AI Content Processor Bot*")
        
        return "\n".join(doc_parts)
    
    def get_recent_files(self, limit: int = 10) -> list:
        """Get list of recently saved markdown files.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file paths sorted by modification time
        """
        try:
            files = sorted(
                self.output_dir.glob("*.md"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return files[:limit]
        except Exception as e:
            logger.error(f"Error getting recent files: {e}")
            return []