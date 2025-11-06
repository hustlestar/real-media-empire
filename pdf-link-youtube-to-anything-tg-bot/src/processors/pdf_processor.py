"""PDF processing module for extracting text content."""

import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import aiofiles
import pypdf
import requests
from telegram import File

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction from files and URLs."""

    @staticmethod
    async def extract_text_from_file(file: File) -> Optional[str]:
        """Extract text from a Telegram file object."""
        try:
            # Download file to temporary location
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                await file.download_to_drive(tmp_file.name)
                tmp_path = Path(tmp_file.name)

            text = await PDFProcessor._extract_text_from_path(tmp_path)
            
            # Clean up temporary file
            tmp_path.unlink()
            
            return text

        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            return None

    @staticmethod
    async def extract_text_from_url(url: str) -> Optional[str]:
        """Extract text from a PDF URL."""
        try:
            # Download PDF from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = Path(tmp_file.name)

            text = await PDFProcessor._extract_text_from_path(tmp_path)
            
            # Clean up temporary file
            tmp_path.unlink()
            
            return text

        except Exception as e:
            logger.error(f"Error extracting text from URL {url}: {e}")
            return None

    @staticmethod
    async def _extract_text_from_path(pdf_path: Path) -> Optional[str]:
        """Extract text from a PDF file path."""
        try:
            text_content = []

            async with aiofiles.open(pdf_path, 'rb') as file:
                pdf_content = await file.read()

            # Use pypdf to extract text - wrap bytes in BytesIO
            reader = pypdf.PdfReader(BytesIO(pdf_content))
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue

            if not text_content:
                logger.warning("No text content extracted from PDF")
                return None

            return "\n\n".join(text_content)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    @staticmethod
    async def extract_text_from_bytes(file_obj) -> Optional[str]:
        """Extract text from PDF bytes object.

        Args:
            file_obj: BytesIO or file-like object containing PDF data

        Returns:
            Extracted text or None
        """
        try:
            # Read content
            content = file_obj.read()

            # Use pypdf to extract text - wrap bytes in BytesIO if needed
            reader = pypdf.PdfReader(BytesIO(content) if isinstance(content, bytes) else content)
            text_content = []

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue

            if not text_content:
                logger.warning("No text content extracted from PDF")
                return None

            return "\n\n".join(text_content)

        except Exception as e:
            logger.error(f"Error extracting text from PDF bytes: {e}")
            return None

    @staticmethod
    def is_pdf_url(text: str) -> bool:
        """Check if the text is a PDF URL."""
        text = text.strip().lower()
        return (
            text.startswith(('http://', 'https://')) and
            (text.endswith('.pdf') or 'pdf' in text)
        )