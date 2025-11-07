"""URL detection and classification utilities."""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse

from processors.pdf_processor import PDFProcessor
from processors.youtube_processor import YouTubeProcessor
from processors.web_scraper import WebScraperProcessor

class URLDetector:
    """Detects and classifies URLs for appropriate processing."""

    @staticmethod
    def classify_url(text: str) -> Tuple[Optional[str], str]:
        """Classify a URL to determine the appropriate processor.
        
        Args:
            text: The text that might contain a URL
            
        Returns:
            Tuple of (url_type, cleaned_url) where url_type is one of:
            - 'youtube': YouTube video URL
            - 'pdf': PDF document URL
            - 'web': General web page URL
            - None: Not a valid URL
        """
        text = text.strip()
        
        # Must be a URL
        if not text.startswith(('http://', 'https://')):
            return None, text
            
        try:
            parsed = urlparse(text)
            if not parsed.netloc:
                return None, text
        except Exception:
            return None, text
        
        # Clean URL (remove fragments and some query params that don't affect content)
        cleaned_url = URLDetector._clean_url(text)
        
        if YouTubeProcessor.is_youtube_url(cleaned_url):
            return 'youtube', cleaned_url
            
        if PDFProcessor.is_pdf_url(cleaned_url):
            return 'pdf', cleaned_url
            
        if WebScraperProcessor.is_web_url(cleaned_url):
            return 'web', cleaned_url
            
        return None, text

    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean URL by removing unnecessary parameters and fragments."""
        try:
            parsed = urlparse(url)
            
            # For YouTube, preserve important query parameters
            if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
                return url  # Let YouTube processor handle its own cleaning
                
            # For other URLs, clean up common tracking parameters
            query_parts = []
            if parsed.query:
                params = parsed.query.split('&')
                for param in params:
                    param_name = param.split('=')[0].lower()
                    # Keep important parameters, remove tracking ones
                    if param_name not in [
                        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                        'fbclid', 'gclid', 'ref', 'source', 'campaign',
                        '_ga', '_gl', 'mc_cid', 'mc_eid'
                    ]:
                        query_parts.append(param)
            
            # Reconstruct URL without fragment and with cleaned query
            cleaned_query = '&'.join(query_parts) if query_parts else ''
            
            result = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if cleaned_query:
                result += f"?{cleaned_query}"
                
            return result
            
        except Exception:
            return url

    @staticmethod
    def extract_urls_from_text(text: str) -> list:
        """Extract all URLs from text.
        
        Args:
            text: Text that may contain URLs
            
        Returns:
            List of URLs found in the text
        """
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return urls

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if a string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def get_domain_info(url: str) -> dict:
        """Get domain information from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return {
                'domain': domain,
                'subdomain': parsed.netloc,
                'path': parsed.path,
                'scheme': parsed.scheme,
                'full_domain': parsed.netloc
            }
        except Exception:
            return {
                'domain': 'unknown',
                'subdomain': 'unknown',
                'path': '',
                'scheme': 'unknown',
                'full_domain': 'unknown'
            }

    @staticmethod
    def is_media_url(url: str) -> bool:
        """Check if URL points to media content (images, videos, audio)."""
        media_extensions = [
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
            # Videos
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
            # Audio
            '.mp3', '.wav', '.ogg', '.m4a', '.flac'
        ]
        
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in media_extensions)

    @staticmethod
    def suggest_processor(url: str) -> str:
        """Suggest the best processor for a given URL.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Suggested processor name or 'unknown'
        """
        url_type, _ = URLDetector.classify_url(url)
        
        if url_type:
            return url_type
        
        # Additional heuristics for edge cases
        domain_info = URLDetector.get_domain_info(url)
        domain = domain_info['domain']
        
        # Common article/blog platforms
        article_domains = [
            'medium.com', 'substack.com', 'wordpress.com', 'blogger.com',
            'linkedin.com', 'dev.to', 'hashnode.com', 'notion.so',
            'github.io', 'readthedocs.io'
        ]
        
        if any(article_domain in domain for article_domain in article_domains):
            return 'web'
        
        # News websites
        news_domains = [
            'bbc.com', 'cnn.com', 'reuters.com', 'ap.org', 'npr.org',
            'theguardian.com', 'nytimes.com', 'wsj.com', 'bloomberg.com'
        ]
        
        if any(news_domain in domain for news_domain in news_domains):
            return 'web'
        
        # Technical documentation
        tech_domains = [
            'docs.python.org', 'developer.mozilla.org', 'stackoverflow.com',
            'github.com', 'gitlab.com', 'bitbucket.org'
        ]
        
        if any(tech_domain in domain for tech_domain in tech_domains):
            return 'web'
        
        return 'unknown'