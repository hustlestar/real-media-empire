"""Basic command handlers for the Telegram bot template."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.database import DatabaseManager
from core.keyboard_manager import KeyboardManager
from core.locale_manager import LocaleManager
from processors.ai_processor import AIProcessor
from utils.content_storage import ContentStorage

logger = logging.getLogger(__name__)

class BasicHandlers:
    """Handles basic bot commands like /start, /help, /about."""

    def __init__(self, locale_manager: LocaleManager, keyboard_manager: KeyboardManager, database: DatabaseManager, config, ai_processor=None, content_storage=None, message_handler=None):
        self.locale_manager = locale_manager
        self.keyboard_manager = keyboard_manager
        self.database = database
        self.config = config
        self.ai_processor = ai_processor
        self.content_storage = content_storage
        self.message_handler = message_handler

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        chat = update.effective_chat

        if not user:
            return

        try:
            # Ensure user exists in database
            user_data = await self.database.ensure_user(user_id=user.id, username=user.username, language=self.config.default_language)

            user_language = user_data.get("language", self.config.default_language)

            welcome_text = self.locale_manager.format(
                "welcome_message",
                language=user_language,
                bot_name=self.config.bot_name,
                description=self.config.bot_description,
                version=self.config.bot_version,
            )

            keyboard = self.keyboard_manager.get_main_menu_keyboard(user_language)

            await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

            logger.info(f"User {user.id} (@{user.username}) started the bot")

        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        user = update.effective_user

        if not user:
            return

        try:
            user_language = await self.database.get_user_language(user.id)

            # Available commands
            commands = ["/start - Start the bot", "/help - Show this help message", "/about - About this bot"]

            help_text = self.locale_manager.format("help_message", language=user_language, available_commands="\n".join(commands))

            keyboard = self.keyboard_manager.get_back_keyboard(user_language)

            await update.message.reply_text(help_text, reply_markup=keyboard, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /about command."""
        user = update.effective_user

        if not user:
            return

        try:
            user_language = await self.database.get_user_language(user.id)

            about_text = self.locale_manager.format(
                "about_message",
                language=user_language,
                bot_name=self.config.bot_name,
                description=self.config.bot_description,
                version=self.config.bot_version,
            )

            keyboard = self.keyboard_manager.get_back_keyboard(user_language)

            await update.message.reply_text(about_text, reply_markup=keyboard, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error in about command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")

    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        user = query.from_user

        if not user:
            return

        await query.answer()
        
        logger.info(f"CALLBACK: user={user.id} (@{user.username}), data={query.data}")

        try:
            user_language = await self.database.get_user_language(user.id)

            if query.data == "help":
                await self._show_help(query, user_language)

            elif query.data == "about":
                await self._show_about(query, user_language)

            elif query.data == "settings":
                await self._show_settings(query, user_language)

            elif query.data == "change_language":
                await self._show_language_selection(query, user_language)

            elif query.data.startswith("set_language_"):
                new_language = query.data.split("_")[-1]
                await self._set_language(query, user.id, new_language)

            elif query.data == "back_to_menu":
                await self._show_main_menu(query, user_language)

            elif query.data.startswith("select_"):
                await self._handle_processing_selection(query, user.id, user_language)

            elif query.data.startswith("lang_"):
                await self._handle_language_selection(query, user.id, user_language)

            elif query.data.startswith("prompt_"):
                await self._handle_prompt_request(query, user.id, user_language)

            elif query.data.startswith("process_"):
                await self._handle_content_processing(query, user.id, user_language)
            
            elif query.data.startswith("add_more_"):
                await self._handle_add_more_sources(query, user.id, user_language)
            
            elif query.data.startswith("process_all_"):
                await self._handle_process_all_sources(query, user.id, user_language)
            
            elif query.data.startswith("clear_all_"):
                await self._handle_clear_all_sources(query, user.id, user_language)
            
            elif query.data.startswith("combined_"):
                await self._handle_combined_processing(query, user.id, user_language)

            elif query.data.startswith("retry_"):
                await self._handle_retry(query, user.id, user_language)

            elif query.data.startswith("cancel_retry_"):
                retry_id = query.data.replace("cancel_retry_", "")
                self.content_storage.remove_retry_context(retry_id)
                await query.edit_message_text("✅ Retry cancelled.")

            else:
                logger.warning(f"Unknown callback data: {query.data}")
                await query.edit_message_text(self.locale_manager.get("unknown_command", user_language))

        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
            await query.edit_message_text("Sorry, something went wrong. Please try again.")

    async def _show_help(self, query, language: str) -> None:
        """Show help message."""
        commands = ["/start - Start the bot", "/help - Show help message", "/about - About this bot"]

        help_text = self.locale_manager.format("help_message", language=language, available_commands="\n".join(commands))

        keyboard = self.keyboard_manager.get_back_keyboard(language)

        await query.edit_message_text(help_text, reply_markup=keyboard, parse_mode="Markdown")

    async def _show_about(self, query, language: str) -> None:
        """Show about message."""
        about_text = self.locale_manager.format(
            "about_message",
            language=language,
            bot_name=self.config.bot_name,
            description=self.config.bot_description,
            version=self.config.bot_version,
        )

        keyboard = self.keyboard_manager.get_back_keyboard(language)

        await query.edit_message_text(about_text, reply_markup=keyboard, parse_mode="Markdown")

    async def _show_settings(self, query, language: str) -> None:
        """Show settings menu."""
        settings_text = "⚙️ Settings"
        keyboard = self.keyboard_manager.get_settings_keyboard(language)

        await query.edit_message_text(settings_text, reply_markup=keyboard)

    async def _show_language_selection(self, query, current_language: str) -> None:
        """Show language selection menu."""
        text = self.locale_manager.get("language_selection", current_language)
        keyboard = self.keyboard_manager.get_language_selection_keyboard(current_language)

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _set_language(self, query, user_id: int, new_language: str) -> None:
        """Set user's language preference."""
        try:
            success = await self.database.update_user_language(user_id, new_language)

            if success:
                # Show confirmation
                confirmation_text = self.locale_manager.get("language_changed", new_language)
                keyboard = self.keyboard_manager.get_main_menu_keyboard(new_language)

                await query.edit_message_text(confirmation_text, reply_markup=keyboard)

                logger.info(f"User {user_id} changed language to {new_language}")
            else:
                await query.edit_message_text("Failed to update language preference.")

        except Exception as e:
            logger.error(f"Error setting language: {e}")
            await query.edit_message_text("Sorry, something went wrong while changing the language.")

    async def _show_main_menu(self, query, language: str) -> None:
        """Show main menu."""
        welcome_text = self.locale_manager.format(
            "welcome_message",
            language=language,
            bot_name=self.config.bot_name,
            description=self.config.bot_description,
            version=self.config.bot_version,
        )

        keyboard = self.keyboard_manager.get_main_menu_keyboard(language)

        await query.edit_message_text(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

    async def _handle_content_processing(self, query, user_id: int, user_language: str) -> None:
        """Handle content processing callbacks."""
        if not self.ai_processor or not self.content_storage:
            await query.edit_message_text("❌ AI processing is not available.")
            return

        try:
            if query.data.startswith("process_summary_"):
                processing_type = "summary"
                content_id = query.data.replace("process_summary_", "")
            elif query.data.startswith("process_mvp_plan_"):
                processing_type = "mvp_plan"
                content_id = query.data.replace("process_mvp_plan_", "")
            elif query.data.startswith("process_content_ideas_"):
                processing_type = "content_ideas"
                content_id = query.data.replace("process_content_ideas_", "")
            else:
                await query.edit_message_text("❌ Invalid processing request.")
                return

            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                await query.edit_message_text("❌ Content not found or expired. Please try again.")
                return

            content = content_data['content']
            source_type = content_data['source_type']
            output_language = content_data.get('output_language', 'en')  # Default to English

            # Show processing message
            processing_messages = {
                "summary": "📄 Generating summary...",
                "mvp_plan": "🚀 Creating MVP plan...",
                "content_ideas": "💡 Generating content ideas..."
            }

            processing_msg = processing_messages.get(processing_type, "⏳ Processing...")
            await query.edit_message_text(processing_msg)

            result = await self.ai_processor.process_content(
                content=content,
                processing_type=processing_type,
                source_type=source_type,
                user_id=user_id,
                language=output_language
            )

            if result:
                # Split long messages if needed
                if len(result) > 4000:
                    await query.edit_message_text(result[:4000] + "...")
                    
                    remaining = result[4000:]
                    while remaining:
                        chunk = remaining[:4000]
                        remaining = remaining[4000:]
                        
                        if remaining:
                            chunk += "..."
                        
                        await query.message.reply_text(chunk, parse_mode="Markdown")
                else:
                    await query.edit_message_text(result, parse_mode="Markdown")
                
                # Clean up stored content after processing
                self.content_storage.remove_content(content_id)
                
            else:
                await query.edit_message_text("❌ Failed to process content. Please try again.")

        except Exception as e:
            logger.error(f"Error in content processing: {e}")
            await query.edit_message_text("❌ Error processing content. Please try again.")

    async def _handle_processing_selection(self, query, user_id: int, user_language: str) -> None:
        """Handle processing type selection (summary, mvp, content_ideas)."""
        if not self.content_storage:
            await query.edit_message_text("❌ Content storage is not available.")
            return

        try:
            if query.data.startswith("select_summary_"):
                processing_type = "summary"
                content_id = query.data.replace("select_summary_", "")
            elif query.data.startswith("select_mvp_plan_"):
                processing_type = "mvp_plan"
                content_id = query.data.replace("select_mvp_plan_", "")
            elif query.data.startswith("select_content_ideas_"):
                processing_type = "content_ideas"
                content_id = query.data.replace("select_content_ideas_", "")
            else:
                await query.edit_message_text("❌ Invalid selection.")
                return

            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                logger.error(f"Content {content_id} not found for user {user_id}")
                await query.edit_message_text("❌ Content not found or expired. Please try again.")
                return

            logger.info(f"Processing selection: type={processing_type}, content_id={content_id}, user={user_id}")
            logger.info(f"Content exists: {len(content_data.get('content', ''))} chars")
            
            self.content_storage.update_content_state(
                content_id=content_id,
                processing_type=processing_type,
                processing_state="awaiting_prompt",
                user_id=user_id
            )
            
            logger.info(f"Updated content state to 'awaiting_prompt' for content {content_id}")

            # Show language selection options
            keyboard = self.keyboard_manager.get_language_processing_keyboard(content_id, processing_type, user_language)

            processing_names = {
                "summary": "📄 Summary",
                "mvp_plan": "🚀 MVP Plan",
                "content_ideas": "💡 Content Ideas"
            }

            selected_name = processing_names.get(processing_type, processing_type.replace("_", " ").title())

            await query.edit_message_text(
                f"You selected: **{selected_name}**\n\n"
                f"Choose the output language:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in processing selection: {e}")
            await query.edit_message_text("❌ Error processing selection. Please try again.")

    async def _handle_language_selection(self, query, user_id: int, user_language: str) -> None:
        """Handle language selection for processing."""
        if not self.content_storage:
            await query.edit_message_text("❌ Content storage is not available.")
            return

        try:
            # Parse callback data: lang_{language}_{processing_type}_{content_id}
            parts = query.data.split("_")
            if len(parts) < 4:
                await query.edit_message_text("❌ Invalid language selection.")
                return

            output_language = parts[1]  # en, ru, es
            processing_type = parts[2]  # summary, mvp_plan, content_ideas
            content_id = "_".join(parts[3:])  # in case content_id contains underscores

            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                await query.edit_message_text("❌ Content not found or expired. Please try again.")
                return

            # Store the selected language in content data
            self.content_storage.update_content_state(
                content_id=content_id,
                processing_type=processing_type,
                output_language=output_language,
                processing_state="awaiting_prompt"
            )

            # Show prompt options with language selected
            keyboard = self.keyboard_manager.get_prompt_options_keyboard(content_id, processing_type, user_language)

            language_names = {"en": "English", "ru": "Russian", "es": "Spanish"}
            lang_name = language_names.get(output_language, output_language)

            processing_names = {
                "summary": "📄 Summary",
                "mvp_plan": "🚀 MVP Plan",
                "content_ideas": "💡 Content Ideas"
            }

            selected_name = processing_names.get(processing_type, processing_type.replace("_", " ").title())

            await query.edit_message_text(
                f"✅ **{selected_name}** in **{lang_name}**\n\n"
                f"Would you like to add custom instructions for the AI, or process with default settings?",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in language selection: {e}")
            await query.edit_message_text("❌ Error processing language selection. Please try again.")

    async def _handle_prompt_request(self, query, user_id: int, user_language: str) -> None:
        """Handle request for custom user prompt."""
        if not self.content_storage:
            await query.edit_message_text("❌ Content storage is not available.")
            return

        try:
            logger.info(f"Handle prompt request: {query.data}")
            
            if query.data.startswith("prompt_summary_"):
                processing_type = "summary"
                content_id = query.data.replace("prompt_summary_", "")
            elif query.data.startswith("prompt_mvp_plan_"):
                processing_type = "mvp_plan"
                content_id = query.data.replace("prompt_mvp_plan_", "")
            elif query.data.startswith("prompt_content_ideas_"):
                processing_type = "content_ideas"
                content_id = query.data.replace("prompt_content_ideas_", "")
            else:
                await query.edit_message_text("❌ Invalid prompt request.")
                return

            logger.info(f"Parsed: type={processing_type}, content_id={content_id}")

            content_data = self.content_storage.get_content(content_id)
            if not content_data:
                logger.error(f"Content {content_id} not found")
                await query.edit_message_text("❌ Content not found or expired. Please try again.")
                return

            self.content_storage.update_content_state(
                content_id=content_id,
                processing_state="awaiting_user_prompt"  # Must match what message.py checks for
            )
            
            logger.info(f"Updated content {content_id} state to 'awaiting_user_prompt' for user {user_id}")

            await query.edit_message_text(
                f"✏️ **Custom Instructions**\n\n"
                f"Please send your custom instructions for the AI processing.\n\n"
                f"For example:\n"
                f"• Focus on technical aspects\n"
                f"• Make it beginner-friendly\n" 
                f"• Emphasize practical applications\n"
                f"• Include specific examples\n\n"
                f"Send your message now, or type 'skip' to use default settings.",
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in prompt request: {e}")
            await query.edit_message_text("❌ Error processing prompt request. Please try again.")
    
    async def _handle_add_more_sources(self, query, user_id: int, user_language: str) -> None:
        """Handle adding more sources to collection."""
        try:
            content_id = query.data.replace("add_more_", "")
            
            collecting_mode_text = self.locale_manager.get("collecting_mode", user_language)
            
            await query.edit_message_text(
                f"{collecting_mode_text}\n\n"
                f"Send me another:\n"
                f"• PDF file or URL\n"
                f"• YouTube video link\n"
                f"• Web page URL",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in add more sources: {e}")
            await query.edit_message_text("❌ Error. Please try again.")
    
    async def _handle_process_all_sources(self, query, user_id: int, user_language: str) -> None:
        """Handle processing all collected sources together."""
        if not self.ai_processor or not self.content_storage:
            await query.edit_message_text("❌ Processing is not available.")
            return
        
        try:
            content_id = query.data.replace("process_all_", "")
            
            # Get all user's content
            combined_data = self.content_storage.get_combined_content(user_id)
            
            if not combined_data:
                no_sources_text = self.locale_manager.get("no_sources_to_process", user_language)
                await query.edit_message_text(no_sources_text)
                return
            
            # Show processing options for combined content
            keyboard = [
                [{"text": "📄 Summary", "callback_data": f"combined_summary_{user_id}"}],
                [{"text": "🚀 MVP Plan", "callback_data": f"combined_mvp_{user_id}"}],
                [{"text": "💡 Content Ideas", "callback_data": f"combined_ideas_{user_id}"}],
            ]
            
            kb = self.keyboard_manager.create_inline_keyboard([keyboard], user_language)
            
            processing_text = self.locale_manager.get("processing_multiple_sources", user_language).format(
                count=combined_data['total_sources']
            )
            
            await query.edit_message_text(
                f"{processing_text}\n\n"
                f"Choose what you'd like me to do with all {combined_data['total_sources']} sources:",
                reply_markup=kb,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in process all sources: {e}")
            await query.edit_message_text("❌ Error processing sources. Please try again.")
    
    async def _handle_clear_all_sources(self, query, user_id: int, user_language: str) -> None:
        """Handle clearing all collected sources."""
        if not self.content_storage:
            await query.edit_message_text("❌ Content storage is not available.")
            return
        
        try:
            # Clear all user's content
            cleared_count = self.content_storage.clear_user_content(user_id)
            
            cleared_text = self.locale_manager.get("all_sources_cleared", user_language)
            
            await query.edit_message_text(
                f"{cleared_text}\n\n"
                f"Removed {cleared_count} source(s).\n\n"
                f"Send me new content to process.",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in clear all sources: {e}")
            await query.edit_message_text("❌ Error clearing sources. Please try again.")
    
    async def _handle_retry(self, query, user_id: int, user_language: str) -> None:
        """Handle retry of failed operations."""
        if not self.content_storage or not self.message_handler:
            await query.edit_message_text("❌ Retry is not available.")
            return

        try:
            # Parse retry_id from callback data
            retry_id = query.data.replace("retry_", "")

            # Get retry context
            retry_context = self.content_storage.get_retry_context(retry_id)
            if not retry_context:
                await query.edit_message_text("❌ Retry context expired. Please try the operation again.")
                return

            operation_type = retry_context['operation_type']
            params = retry_context['params']

            # Show processing message
            await query.edit_message_text("🔄 Retrying operation...")

            # Re-execute the failed operation based on type
            if operation_type == 'pdf_document':
                document = params.get('document')
                await self.message_handler._handle_pdf_document(query, document, user_language, user_id)

            elif operation_type == 'pdf_url':
                url = params.get('url')
                await self.message_handler._handle_pdf_url(query, url, user_language, user_id)

            elif operation_type == 'youtube_url':
                url = params.get('url')
                await self.message_handler._handle_youtube_url(query, url, user_language, user_id)

            elif operation_type == 'web_url':
                url = params.get('url')
                await self.message_handler._handle_web_url(query, url, user_language, user_id)

            elif operation_type == 'ai_message':
                user_message = params.get('user_message')
                await self.message_handler._handle_ai_message(query, user_message, user_language, user_id)

            elif operation_type == 'content_processing':
                content_id = params.get('content_id')
                processing_type = params.get('processing_type')
                # Get content data and process
                content_data = self.content_storage.get_content(content_id)
                if content_data:
                    await self.message_handler._process_content_with_prompt(content_id, processing_type, user_id, user_language, query.message)
                else:
                    await query.edit_message_text("❌ Content not found or expired.")

            # Remove retry context after successful retry attempt
            self.content_storage.remove_retry_context(retry_id)

        except Exception as e:
            logger.error(f"Error in retry handler: {e}")
            await query.edit_message_text("❌ Error retrying operation. Please try again.")

    async def _handle_combined_processing(self, query, user_id: int, user_language: str) -> None:
        """Handle processing of combined sources."""
        if not self.ai_processor or not self.content_storage:
            await query.edit_message_text("❌ Processing is not available.")
            return

        try:
            # Parse processing type
            if query.data.startswith("combined_summary_"):
                processing_type = "summary"
            elif query.data.startswith("combined_mvp_"):
                processing_type = "mvp_plan"
            elif query.data.startswith("combined_ideas_"):
                processing_type = "content_ideas"
            else:
                await query.edit_message_text("❌ Invalid processing type.")
                return
            
            # Get combined content
            combined_data = self.content_storage.get_combined_content(user_id)
            
            if not combined_data:
                no_sources_text = self.locale_manager.get("no_sources_to_process", user_language)
                await query.edit_message_text(no_sources_text)
                return
            
            # Show processing message
            processing_text = self.locale_manager.get("processing_multiple_sources", user_language).format(
                count=combined_data['total_sources']
            )
            await query.edit_message_text(processing_text)
            
            # Process combined content (use user's preferred language for combined processing)
            result = await self.ai_processor.process_combined_content(
                combined_data=combined_data,
                processing_type=processing_type,
                user_id=user_id,
                language=user_language
            )
            
            if result:
                # Split long messages if needed
                if len(result) > 4000:
                    await query.edit_message_text(result[:4000] + "...", parse_mode="Markdown")
                    
                    remaining = result[4000:]
                    while remaining:
                        chunk = remaining[:4000]
                        remaining = remaining[4000:]
                        
                        if remaining:
                            chunk += "..."
                        
                        await query.message.reply_text(chunk, parse_mode="Markdown")
                else:
                    await query.edit_message_text(result, parse_mode="Markdown")
                
                # Clear processed content
                self.content_storage.clear_user_content(user_id)
                
            else:
                await query.edit_message_text("❌ Failed to process combined content. Please try again.")
            
        except Exception as e:
            logger.error(f"Error in combined processing: {e}")
            await query.edit_message_text("❌ Error processing combined content. Please try again.")
