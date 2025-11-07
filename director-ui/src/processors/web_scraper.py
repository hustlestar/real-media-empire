"""Web scraping processor using Crawl4AI for article and webpage content extraction."""

import logging
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

logger = logging.getLogger(__name__)

class WebScraperProcessor:
    """Handles web page scraping and content extraction using Crawl4AI."""

    @staticmethod
    def is_web_url(text: str) -> bool:
        """Check if the text is a valid web URL (not PDF or YouTube)."""
        text = text.strip()
        
        # Must start with http/https
        if not text.startswith(('http://', 'https://')):
            return False
        
        try:
            parsed = urlparse(text)
            if not parsed.netloc:
                return False
        except Exception:
            return False
        
        # Exclude PDF URLs
        if text.lower().endswith('.pdf') or 'pdf' in text.lower():
            return False
            
        # Exclude YouTube URLs
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
            r'youtube\.com\/shorts\/',
            r'm\.youtube\.com\/watch\?v='
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in youtube_patterns):
            return False
            
        return True

    @staticmethod
    async def extract_content_from_url(url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a web URL using Crawl4AI.

        Args:
            url: The web URL to scrape

        Returns:
            Dictionary containing extracted content and metadata, or None if failed
        """
        try:
            async with AsyncWebCrawler(verbose=True, headless=True) as crawler:
                # First, try basic crawling to get main content
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    bypass_cache=True,
                    css_selector="article, main, .content, .post, .entry, [role='main']",
                    exclude_tags=['nav', 'footer', 'header', 'aside', 'script', 'style']
                )

                if not result.success:
                    logger.error(f"Failed to crawl URL {url}: {result.error_message}")
                    return None

                main_content = result.cleaned_html or result.markdown or ""

                if not main_content or len(main_content.strip()) < 50:
                    # Fallback: try without CSS selector
                    result = await crawler.arun(
                        url=url,
                        word_count_threshold=10,
                        bypass_cache=True
                    )

                    if not result.success:
                        return None

                    main_content = result.cleaned_html or result.markdown or ""
                
                if not main_content or len(main_content.strip()) < 50:
                    logger.warning(f"No meaningful content extracted from {url}")
                    return None
                
                title = result.metadata.get('title', 'Unknown Title') if result.metadata else 'Unknown Title'
                description = result.metadata.get('description', '') if result.metadata else ''
                
                # Try to get title from content if not available in metadata
                if title == 'Unknown Title' and result.cleaned_html:
                    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', result.cleaned_html, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        title = title_match.group(1).strip()
                
                return {
                    'title': title,
                    'content': main_content,
                    'description': description,
                    'url': url,
                    'word_count': len(main_content.split()),
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error extracting content from URL {url}: {e}")
            return None

    @staticmethod
    async def extract_with_ai_strategy(url: str, extraction_prompt: str = None) -> Optional[Dict[str, Any]]:
        """Extract content using AI-powered extraction strategy.
        
        Args:
            url: The web URL to scrape
            extraction_prompt: Custom prompt for AI extraction
            
        Returns:
            Dictionary containing AI-extracted content and metadata, or None if failed
        """
        try:
            # Default extraction prompt for articles/content
            if not extraction_prompt:
                extraction_prompt = """
                Extract the main article content from this webpage. Focus on:
                1. The main title/headline
                2. The full article text or main content
                3. Key points and important information
                4. Author information if available
                5. Publication date if available
                
                Ignore navigation, ads, sidebars, comments, and other non-essential elements.
                Return the content in a clean, readable format.
                """
            
            extraction_strategy = LLMExtractionStrategy(
                provider="openai/gpt-4o-mini",  # Using a smaller model for extraction
                api_token=None,  # Will use default from environment
                instruction=extraction_prompt
            )
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    remove_overlay_elements=True
                )
                
                if not result.success:
                    logger.error(f"AI extraction failed for {url}: {result.error_message}")
                    # Fallback to regular extraction
                    return await WebScraperProcessor.extract_content_from_url(url)
                
                extracted_content = result.extracted_content
                
                if not extracted_content or len(str(extracted_content).strip()) < 50:
                    logger.warning(f"AI extraction returned minimal content for {url}")
                    # Fallback to regular extraction
                    return await WebScraperProcessor.extract_content_from_url(url)
                
                return {
                    'title': result.metadata.get('title', 'Unknown Title') if result.metadata else 'Unknown Title',
                    'content': str(extracted_content),
                    'description': result.metadata.get('description', '') if result.metadata else '',
                    'url': url,
                    'word_count': len(str(extracted_content).split()),
                    'extraction_method': 'ai',
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error in AI extraction for URL {url}: {e}")
            # Fallback to regular extraction
            return await WebScraperProcessor.extract_content_from_url(url)

    @staticmethod
    async def extract_structured_data(url: str, schema_type: str = "article") -> Optional[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata) from webpage.
        
        Args:
            url: The web URL to scrape
            schema_type: Type of schema to look for (article, product, etc.)
            
        Returns:
            Dictionary containing structured data, or None if not found
        """
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    bypass_cache=True,
                    extract_structured_data=True
                )
                
                if not result.success or not result.structured_data:
                    return None
                
                # Look for relevant structured data
                structured_data = result.structured_data
                
                # Try to find article or relevant schema
                article_data = None
                if isinstance(structured_data, list):
                    for item in structured_data:
                        if isinstance(item, dict):
                            item_type = item.get('@type', '').lower()
                            if schema_type.lower() in item_type or 'article' in item_type:
                                article_data = item
                                break
                elif isinstance(structured_data, dict):
                    article_data = structured_data
                
                if article_data:
                    return {
                        'title': article_data.get('headline') or article_data.get('name', 'Unknown Title'),
                        'content': article_data.get('articleBody') or article_data.get('description', ''),
                        'author': article_data.get('author', {}).get('name') if isinstance(article_data.get('author'), dict) else article_data.get('author'),
                        'date_published': article_data.get('datePublished'),
                        'url': url,
                        'structured_data': article_data,
                        'success': True
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error extracting structured data from {url}: {e}")
            return None

    @staticmethod
    def clean_extracted_content(content: str) -> str:
        """Clean and format extracted content."""
        if not content:
            return ""
        
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up common artifacts
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', ' ')
        
        return content.strip()

    @staticmethod
    def get_domain_name(url: str) -> str:
        """Extract domain name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown"