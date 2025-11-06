"""Message handler for the Telegram bot template."""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from core.ai_interface import AIProviderInterface
from core.database import DatabaseManager
from core.keyboard_manager import KeyboardManager
from core.locale_manager import LocaleManager
from processors.pdf_processor import PDFProcessor
from processors.youtube_processor import YouTubeProcessor
from processors.web_scraper import WebScraperProcessor
from processors.ai_processor import AIProcessor
from utils.content_storage import ContentStorage
from utils.url_detector import URLDetector
from utils.markdown_saver import MarkdownSaver

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handles text messages from users."""

    def __init__(
        self,
        locale_manager: LocaleManager,
        keyboard_manager: KeyboardManager,
        database: DatabaseManager,
        ai_provider: Optional[AIProviderInterface],
        config,
        content_service,
    ):
        self.locale_manager = locale_manager
        self.keyboard_manager = keyboard_manager
        self.database = database
        self.ai_provider = ai_provider
        self.config = config
        self.content_service = content_service  # Shared service with API
        self.content_storage = ContentStorage()  # Only for temporary UI workflow state
        self.ai_processor = AIProcessor(ai_provider) if ai_provider else None
        self.markdown_saver = MarkdownSaver()

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages."""
        user = update.effective_user
        message = update.message

        if not user or not message or not message.text:
            return

        try:
            # Ensure user exists in database
            user_data = await self.database.ensure_user(user_id=user.id, username=user.username, language=self.config.default_language)

            user_language = user_data.get("language", self.config.default_language)
            user_message = message.text.strip()

            logger.info(f"User {user.id} (@{user.username}) sent: {user_message[:100]}...")

            prompt_handled = await self._check_and_handle_user_prompt(update, user_message, user_language, user.id)
            
            if not prompt_handled:
                # Use URL detector to classify the URL
                url_type, cleaned_url = URLDetector.classify_url(user_message)
                
                if url_type == 'youtube':
                    await self._handle_youtube_url(update, cleaned_url, user_language, user.id)
                elif url_type == 'pdf':
                    await self._handle_pdf_url(update, cleaned_url, user_language, user.id)
                elif url_type == 'web':
                    await self._handle_web_url(update, cleaned_url, user_language, user.id)
                elif self.ai_provider and self.ai_provider.is_available():
                    await self._handle_ai_message(update, user_message, user_language, user.id)
                else:
                    await self._handle_simple_echo(update, user_message, user_language)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.reply_text(self.locale_manager.get("error_occurred", user_language))

    async def _handle_ai_message(self, update: Update, user_message: str, user_language: str, user_id: int) -> None:
        """Handle message with AI response."""
        message = update.message

        try:
            # Send "processing" message
            processing_msg = await message.reply_text(self.locale_manager.get("processing", user_language), do_quote=True)

            system_prompt = self._get_system_prompt(user_language)
            ai_response = await self.ai_provider.get_response(message=user_message, user_id=user_id, system_prompt=system_prompt)

            await processing_msg.delete()

            await message.reply_text(ai_response, do_quote=True, parse_mode="Markdown")

            logger.info(f"AI response sent to user {user_id}")

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")

            # Try to delete processing message
            try:
                await processing_msg.delete()
            except:
                pass

            retry_id = self.content_storage.store_retry_context(
                operation_type='ai_message',
                user_id=user_id,
                user_language=user_language,
                user_message=user_message
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text(self.locale_manager.get("ai_not_available", user_language), reply_markup=keyboard, do_quote=True)

    async def _handle_simple_echo(self, update: Update, user_message: str, user_language: str) -> None:
        """Handle message with simple echo response."""
        message = update.message

        try:
            # Simple echo response
            echo_response = f"You said: {user_message}"

            keyboard = self.keyboard_manager.get_main_menu_keyboard(user_language)

            await message.reply_text(echo_response, reply_markup=keyboard, do_quote=True)

        except Exception as e:
            logger.error(f"Error in echo response: {e}")
            await message.reply_text(self.locale_manager.get("error_occurred", user_language))

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on user language."""
        prompts = {
            "en": "You are a helpful assistant. Respond in a friendly and informative way in English.",
            "ru": "Ты полезный помощник. Отвечай дружелюбно и информативно на русском языке.",
            "es": "Eres un asistente útil. Responde de manera amigable e informativa en español.",
        }

        return prompts.get(language, prompts["en"])

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.database.get_user_language(user.id)

            # Simple response for photos
            await message.reply_text("📸 I received your photo! Unfortunately, I can't process images yet.", do_quote=True)

            logger.info(f"User {user.id} sent a photo")

        except Exception as e:
            logger.error(f"Error handling photo: {e}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document messages."""
        user = update.effective_user
        message = update.message

        if not user or not message or not message.document:
            return

        try:
            user_data = await self.database.ensure_user(user_id=user.id, username=user.username, language=self.config.default_language)
            user_language = user_data.get("language", self.config.default_language)

            document = message.document
            
            if document.mime_type == 'application/pdf' or document.file_name.lower().endswith('.pdf'):
                await self._handle_pdf_document(update, document, user_language, user.id)
            else:
                await message.reply_text("📄 I can only process PDF files. Please send a PDF document.", do_quote=True)

            logger.info(f"User {user.id} sent a document: {document.file_name}")

        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await message.reply_text("❌ Error processing document. Please try again.", do_quote=True)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.database.get_user_language(user.id)

            # Simple response for voice messages
            await message.reply_text("🎤 I received your voice message! Unfortunately, I can't process audio yet.", do_quote=True)

            logger.info(f"User {user.id} sent a voice message")

        except Exception as e:
            logger.error(f"Error handling voice: {e}")

    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle sticker messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.database.get_user_language(user.id)

            # Fun response for stickers
            sticker_responses = ["😄 Nice sticker!", "🎉 I love stickers!", "😊 That's a cool sticker!", "👍 Great choice!"]

            import random

            response = random.choice(sticker_responses)

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent a sticker")

        except Exception as e:
            logger.error(f"Error handling sticker: {e}")

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle location messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.database.get_user_language(user.id)
            location = message.location

            response = f"📍 Thanks for sharing your location!\n"
            response += f"Latitude: {location.latitude}\n"
            response += f"Longitude: {location.longitude}"

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent location: {location.latitude}, {location.longitude}")

        except Exception as e:
            logger.error(f"Error handling location: {e}")

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle contact messages."""
        user = update.effective_user
        message = update.message

        if not user or not message:
            return

        try:
            user_language = await self.database.get_user_language(user.id)
            contact = message.contact

            response = f"👤 Thanks for sharing the contact!\n"
            response += f"Name: {contact.first_name}"
            if contact.last_name:
                response += f" {contact.last_name}"
            if contact.phone_number:
                response += f"\nPhone: {contact.phone_number}"

            await message.reply_text(response, do_quote=True)

            logger.info(f"User {user.id} sent contact: {contact.first_name}")

        except Exception as e:
            logger.error(f"Error handling contact: {e}")

    async def _handle_pdf_document(self, update: Update, document, user_language: str, user_id: int) -> None:
        """Handle PDF document processing."""
        message = update.message
        
        try:
            processing_msg = await message.reply_text("📄 Processing PDF document...", do_quote=True)
            
            file = await document.get_file()
            text_content = await PDFProcessor.extract_text_from_file(file)
            
            await processing_msg.delete()
            
            if not text_content:
                await message.reply_text("❌ Could not extract text from PDF. Please ensure it's a text-based PDF.", do_quote=True)
                return
                
            # Store content and show processing options
            content_id = self.content_storage.store_content(
                content=text_content,
                source_type="PDF document",
                source_info={"filename": document.file_name, "size": document.file_size},
                user_id=user_id
            )
            
            # Check if user has other content stored
            user_content = self.content_storage.get_user_content(user_id)
            keyboard = self.keyboard_manager.get_multi_content_keyboard(content_id, user_language, len(user_content))
            
            sources_text = self.locale_manager.get("sources_added", user_language).format(
                current=len(user_content), total=len(user_content)
            )
            
            await message.reply_text(
                f"✅ PDF processed successfully!\n\n"
                f"📄 **{document.file_name}**\n"
                f"📊 Extracted {len(text_content)} characters\n\n"
                f"{sources_text}\n\n"
                f"Choose what you'd like to do:",
                reply_markup=keyboard,
                do_quote=True,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF document: {e}")
            retry_id = self.content_storage.store_retry_context(
                operation_type='pdf_document',
                user_id=user_id,
                user_language=user_language,
                document=document
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text("❌ Error processing PDF. Please try again.", reply_markup=keyboard, do_quote=True)

    async def _handle_pdf_url(self, update: Update, url: str, user_language: str, user_id: int) -> None:
        """Handle PDF URL processing."""
        message = update.message

        try:
            processing_msg = await message.reply_text("📄 Downloading and processing PDF from URL...", do_quote=True)

            # Save content to database using ContentService (shared with API)
            try:
                content, is_new = await self.content_service.get_or_create_from_url(
                    url=url,
                    source_type='pdf_url',
                    user_id=user_id,
                    force_reprocess=False
                )
                content_id = content['id']
                text_content = await self.content_service.get_content_text(content_id)
                logger.info(f"{'Created new' if is_new else 'Retrieved existing'} PDF content in database: {content_id}")
            except Exception as e:
                logger.error(f"Error saving PDF content to database: {e}")
                await processing_msg.delete()
                await message.reply_text("❌ Error processing PDF. Please try again.", do_quote=True)
                return

            await processing_msg.delete()

            if not text_content:
                await message.reply_text("❌ Could not extract text from PDF URL. Please check the link.", do_quote=True)
                return

            # Store workflow state in temporary storage (for UI interactions)
            temp_content_id = self.content_storage.store_content(
                content=text_content,
                source_type="PDF URL",
                source_info={"url": url, 'db_id': str(content_id)},
                user_id=user_id
            )

            # Check if user has other content stored
            user_content = self.content_storage.get_user_content(user_id)
            keyboard = self.keyboard_manager.get_multi_content_keyboard(temp_content_id, user_language, len(user_content))
            
            sources_text = self.locale_manager.get("sources_added", user_language).format(
                current=len(user_content), total=len(user_content)
            )
            
            await message.reply_text(
                f"✅ PDF processed successfully!\n\n"
                f"🔗 **Source:** {url[:50]}...\n"
                f"📊 Extracted {len(text_content)} characters\n\n"
                f"{sources_text}\n\n"
                f"Choose what you'd like to do:",
                reply_markup=keyboard,
                do_quote=True,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF URL: {e}")
            retry_id = self.content_storage.store_retry_context(
                operation_type='pdf_url',
                user_id=user_id,
                user_language=user_language,
                url=url
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text("❌ Error processing PDF URL. Please check the link and try again.", reply_markup=keyboard, do_quote=True)

    async def _handle_youtube_url(self, update: Update, url: str, user_language: str, user_id: int) -> None:
        """Handle YouTube URL processing."""
        message = update.message
        
        try:
            processing_msg = await message.reply_text("🎥 Processing YouTube video...", do_quote=True)

            youtube_processor = YouTubeProcessor()
            video_data = await youtube_processor.extract_content_from_url(url)
            
            await processing_msg.delete()
            
            if not video_data:
                await message.reply_text("❌ Could not process YouTube video. Please check the link.", do_quote=True)
                return

            # Check if transcript is available - reject videos without transcripts
            transcript = video_data.get('transcript')
            if not transcript or len(transcript.strip()) < 50:  # Require meaningful transcript content
                # Store retry context
                retry_id = self.content_storage.store_retry_context(
                    operation_type='youtube',
                    user_id=user_id,
                    user_language=user_language,
                    url=url
                )
                keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)

                await message.reply_text(
                    "❌ **No transcript available for this video**\n\n"
                    "I can only process YouTube videos that have:\n"
                    "• English subtitles/captions\n"
                    "• Auto-generated captions\n"
                    "• Manual transcripts\n\n"
                    "Please try a different video with available subtitles.",
                    do_quote=True,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                return

            # Save content to database using ContentService (shared with API)
            try:
                content, is_new = await self.content_service.get_or_create_from_url(
                    url=url,
                    source_type='youtube',
                    user_id=user_id,
                    force_reprocess=False
                )
                content_id = content['id']
                logger.info(f"{'Created new' if is_new else 'Retrieved existing'} content in database: {content_id}")
            except Exception as e:
                logger.error(f"Error saving content to database: {e}")
                await message.reply_text("❌ Error saving content. Please try again.", do_quote=True)
                return

            # Combine title and transcript for display
            content_parts = []
            if video_data.get('title'):
                content_parts.append(f"Title: {video_data['title']}")
            content_parts.append(f"Transcript: {transcript}")
            full_content = "\n\n".join(content_parts)

            # Store workflow state in temporary storage (for UI interactions)
            temp_content_id = self.content_storage.store_content(
                content=full_content,
                source_type="YouTube video",
                source_info={'db_id': str(content_id), **video_data},
                user_id=user_id
            )

            # Check if user has other content stored
            user_content = self.content_storage.get_user_content(user_id)
            keyboard = self.keyboard_manager.get_multi_content_keyboard(temp_content_id, user_language, len(user_content))
            
            duration_str = f"{video_data.get('duration', 0) // 60}:{video_data.get('duration', 0) % 60:02d}" if video_data.get('duration') else "Unknown"
            
            sources_text = self.locale_manager.get("sources_added", user_language).format(
                current=len(user_content), total=len(user_content)
            )
            
            await message.reply_text(
                f"✅ YouTube video processed successfully!\n\n"
                f"🎥 **{video_data.get('title', 'Unknown Title')}**\n"
                f"⏱️ Duration: {duration_str}\n"
                f"📊 Extracted {len(full_content)} characters\n\n"
                f"{sources_text}\n\n"
                f"Choose what you'd like to do:",
                reply_markup=keyboard,
                do_quote=True,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing YouTube URL: {e}")
            retry_id = self.content_storage.store_retry_context(
                operation_type='youtube_url',
                user_id=user_id,
                user_language=user_language,
                url=url
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text("❌ Error processing YouTube video. Please check the link and try again.", reply_markup=keyboard, do_quote=True)

    async def _handle_web_url(self, update: Update, url: str, user_language: str, user_id: int) -> None:
        """Handle web page URL scraping."""
        message = update.message

        try:
            processing_msg = await message.reply_text("🌐 Scraping web page content...", do_quote=True)

            # Save content to database using ContentService (shared with API)
            try:
                content, is_new = await self.content_service.get_or_create_from_url(
                    url=url,
                    source_type='web',
                    user_id=user_id,
                    force_reprocess=False
                )
                content_id = content['id']
                full_content = await self.content_service.get_content_text(content_id)
                logger.info(f"{'Created new' if is_new else 'Retrieved existing'} web content in database: {content_id}")
            except Exception as e:
                logger.error(f"Error saving web content to database: {e}")
                await processing_msg.delete()
                await message.reply_text("❌ Error processing web page. Please try again.", do_quote=True)
                return

            await processing_msg.delete()

            if not full_content or len(full_content.strip()) < 50:
                await message.reply_text("❌ No meaningful content found on the web page.", do_quote=True)
                return

            # Get metadata for display
            metadata = content.get('metadata', {})
            domain_info = URLDetector.get_domain_info(url)
            domain = domain_info['domain']

            # Store workflow state in temporary storage (for UI interactions)
            temp_content_id = self.content_storage.store_content(
                content=full_content,
                source_type="Web article",
                source_info={
                    "url": url,
                    "domain": domain,
                    "title": metadata.get('title', 'Unknown Title'),
                    "word_count": metadata.get('word_count', 0),
                    'db_id': str(content_id)
                },
                user_id=user_id
            )

            # Check if user has other content stored
            user_content = self.content_storage.get_user_content(user_id)
            keyboard = self.keyboard_manager.get_multi_content_keyboard(temp_content_id, user_language, len(user_content))

            word_count = metadata.get('word_count', 0)
            
            sources_text = self.locale_manager.get("sources_added", user_language).format(
                current=len(user_content), total=len(user_content)
            )
            
            await message.reply_text(
                f"✅ Web page scraped successfully!\n\n"
                f"🌐 **{metadata.get('title', 'Unknown Title')}**\n"
                f"🔗 Source: {domain}\n"
                f"📊 Extracted {word_count} words\n\n"
                f"{sources_text}\n\n"
                f"Choose what you'd like to do:",
                reply_markup=keyboard,
                do_quote=True,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing web URL: {e}")
            retry_id = self.content_storage.store_retry_context(
                operation_type='web_url',
                user_id=user_id,
                user_language=user_language,
                url=url
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text("❌ Error scraping web page. Please check the link and try again.", reply_markup=keyboard, do_quote=True)

    async def _check_and_handle_user_prompt(self, update: Update, user_message: str, user_language: str, user_id: int) -> bool:
        """Check if user is providing a custom prompt and handle it."""
        # Find any content awaiting user prompt for this user
        logger.debug(f"Checking for awaiting content for user {user_id}")
        for content_id, content_data in self.content_storage._storage.items():
            logger.debug(f"Content {content_id}: state={content_data.get('processing_state')}, user={content_data.get('user_id')}")
            if (content_data.get('processing_state') == 'awaiting_user_prompt' and 
                content_data.get('user_id') == user_id):
                
                logger.info(f"Found content {content_id} awaiting user prompt for user {user_id}")
                await self._handle_received_user_prompt(update, content_id, user_message, user_language, user_id)
                return True
        
        logger.debug(f"No content awaiting prompt for user {user_id}")
        return False

    async def _handle_received_user_prompt(self, update: Update, content_id: str, user_prompt: str, user_language: str, user_id: int) -> None:
        """Handle received user prompt for content processing."""
        message = update.message
        
        try:
            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                await message.reply_text("❌ Content not found or expired. Please try again.", do_quote=True)
                return

            processing_type = content_data.get('processing_type')
            if not processing_type:
                await message.reply_text("❌ Processing type not found. Please try again.", do_quote=True)
                return

            if user_prompt.lower().strip() in ['skip', '/skip', 'no', 'none']:
                user_prompt = None
                await message.reply_text("✅ Using default settings. Processing now...", do_quote=True)
            else:
                await message.reply_text("✅ Custom instructions received. Processing now...", do_quote=True)

            self.content_storage.update_content_state(
                content_id=content_id,
                user_prompt=user_prompt,
                processing_state="processing"
            )

            await self._process_content_with_prompt(content_id, processing_type, user_id, user_language, message)

        except Exception as e:
            logger.error(f"Error handling user prompt: {e}")
            await message.reply_text("❌ Error processing your instructions. Please try again.", do_quote=True)

    async def _process_content_with_prompt(self, content_id: str, processing_type: str, user_id: int, user_language: str, message) -> None:
        """Process content with optional user prompt."""
        if not self.ai_processor:
            await message.reply_text("❌ AI processing is not available.")
            return

        try:
            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                await message.reply_text("❌ Content not found or expired. Please try again.")
                return

            content = content_data['content']
            source_type = content_data['source_type']
            user_prompt = content_data.get('user_prompt')

            # Show processing message
            processing_messages = {
                "summary": "📄 Generating summary...",
                "mvp_plan": "🚀 Creating MVP plan...",
                "content_ideas": "💡 Generating content ideas..."
            }
            
            processing_msg = processing_messages.get(processing_type, "⏳ Processing...")
            status_message = await message.reply_text(processing_msg, do_quote=True)

            output_language = content_data.get('output_language', 'en')  # Default to English

            result = await self.ai_processor.process_content_with_user_prompt(
                content=content,
                processing_type=processing_type,
                source_type=source_type,
                user_id=user_id,
                user_prompt=user_prompt,
                language=output_language
            )

            await status_message.delete()

            if result:
                # Save as markdown file
                try:
                    source_info = content_data.get('source_info', {})
                    title = source_info.get('title')
                    
                    file_path, filename = self.markdown_saver.save_output(
                        content=result,
                        processing_type=processing_type,
                        source_type=source_type,
                        user_id=user_id,
                        title=title,
                        user_prompt=user_prompt
                    )
                    
                    # Send the markdown file
                    with open(file_path, 'rb') as doc:
                        await message.reply_document(
                            document=doc,
                            filename=filename,
                            caption=f"📄 Here's your {processing_type.replace('_', ' ').title()} as a markdown file.\n\nYou can open this in any text editor or markdown viewer.",
                            do_quote=True
                        )
                    
                    # Also send as message (split if needed)
                    if len(result) > 4000:
                        await message.reply_text(result[:4000] + "...", parse_mode="Markdown", do_quote=True)
                        
                        remaining = result[4000:]
                        while remaining:
                            chunk = remaining[:4000]
                            remaining = remaining[4000:]
                            
                            if remaining:
                                chunk += "..."
                            
                            await message.reply_text(chunk, parse_mode="Markdown")
                    else:
                        await message.reply_text(result, parse_mode="Markdown", do_quote=True)
                    
                except Exception as e:
                    logger.error(f"Error saving/sending markdown file: {e}")
                    # Still send the text even if file save fails
                    if len(result) > 4000:
                        await message.reply_text(result[:4000] + "...", parse_mode="Markdown", do_quote=True)
                        remaining = result[4000:]
                        while remaining:
                            chunk = remaining[:4000]
                            remaining = remaining[4000:]
                            if remaining:
                                chunk += "..."
                            await message.reply_text(chunk, parse_mode="Markdown")
                    else:
                        await message.reply_text(result, parse_mode="Markdown", do_quote=True)
                
                # Clean up stored content after processing
                self.content_storage.remove_content(content_id)
                
            else:
                await message.reply_text("❌ Failed to process content. Please try again.")

        except Exception as e:
            logger.error(f"Error in content processing with prompt: {e}")
            retry_id = self.content_storage.store_retry_context(
                operation_type='content_processing',
                user_id=user_id,
                user_language=user_language,
                content_id=content_id,
                processing_type=processing_type
            )
            keyboard = self.keyboard_manager.get_retry_keyboard(retry_id, user_language)
            await message.reply_text("❌ Error processing content. Please try again.", reply_markup=keyboard)
