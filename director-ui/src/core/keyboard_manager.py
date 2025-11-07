"""Keyboard management for the Telegram bot template."""

import logging
from typing import List, Dict, Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.locale_manager import LocaleManager

logger = logging.getLogger(__name__)

class KeyboardManager:
    """Manages inline keyboards for the bot."""

    def __init__(self, locale_manager: LocaleManager):
        self.locale_manager = locale_manager
        self._keyboards_cache: Dict[str, InlineKeyboardMarkup] = {}

    def get_main_menu_keyboard(self, language: str = "en") -> InlineKeyboardMarkup:
        """Get the main menu keyboard."""
        cache_key = f"main_menu_{language}"

        if cache_key not in self._keyboards_cache:
            keyboard = [
                [InlineKeyboardButton(self.locale_manager.get("help", language), callback_data="help")],
                [InlineKeyboardButton(self.locale_manager.get("about", language), callback_data="about")],
                [InlineKeyboardButton(self.locale_manager.get("settings", language), callback_data="settings")],
            ]

            self._keyboards_cache[cache_key] = InlineKeyboardMarkup(keyboard)

        return self._keyboards_cache[cache_key]

    def get_settings_keyboard(self, language: str = "en") -> InlineKeyboardMarkup:
        """Get the settings keyboard."""
        cache_key = f"settings_{language}"

        if cache_key not in self._keyboards_cache:
            keyboard = [
                [InlineKeyboardButton(self.locale_manager.get("language", language), callback_data="change_language")],
                [InlineKeyboardButton(self.locale_manager.get("back_to_menu", language), callback_data="back_to_menu")],
            ]

            self._keyboards_cache[cache_key] = InlineKeyboardMarkup(keyboard)

        return self._keyboards_cache[cache_key]

    def get_language_selection_keyboard(self, current_language: str = "en") -> InlineKeyboardMarkup:
        """Get the language selection keyboard."""
        available_languages = self.locale_manager.get_available_languages()
        keyboard = []

        for lang in available_languages:
            flag = self.locale_manager.get_language_flag(lang)
            name = self.locale_manager.get_language_name(lang)

            text = f"{flag} {name}"
            if lang == current_language:
                text += " ✅"

            keyboard.append([InlineKeyboardButton(text, callback_data=f"set_language_{lang}")])

        keyboard.append([InlineKeyboardButton(self.locale_manager.get("back_to_menu", current_language), callback_data="settings")])

        return InlineKeyboardMarkup(keyboard)

    def get_back_keyboard(self, language: str = "en", callback_data: str = "back_to_menu") -> InlineKeyboardMarkup:
        """Get a simple back button keyboard."""
        cache_key = f"back_{callback_data}_{language}"

        if cache_key not in self._keyboards_cache:
            keyboard = [[InlineKeyboardButton(self.locale_manager.get("back_to_menu", language), callback_data=callback_data)]]

            self._keyboards_cache[cache_key] = InlineKeyboardMarkup(keyboard)

        return self._keyboards_cache[cache_key]

    def get_confirmation_keyboard(self, language: str = "en", action: str = "confirm") -> InlineKeyboardMarkup:
        """Get a confirmation keyboard with Yes/No buttons."""
        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data=f"{action}_yes"), InlineKeyboardButton("❌ No", callback_data=f"{action}_no")],
            [InlineKeyboardButton(self.locale_manager.get("back_to_menu", language), callback_data="back_to_menu")],
        ]

        return InlineKeyboardMarkup(keyboard)

    def create_custom_keyboard(self, buttons: List[Dict[str, Any]], language: str = "en") -> InlineKeyboardMarkup:
        """Create a custom keyboard from button configuration.

        Args:
            buttons: List of button configs with 'text' and 'callback_data' keys
            language: Language for localization

        Returns:
            InlineKeyboardMarkup: The created keyboard
        """
        keyboard = []

        for button_config in buttons:
            text = button_config.get("text", "Button")
            callback_data = button_config.get("callback_data", "unknown")

            if text.startswith("locale:"):
                key = text[7:]  # Remove "locale:" prefix
                text = self.locale_manager.get(key, language)

            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])

        return InlineKeyboardMarkup(keyboard)

    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]], language: str = "en") -> InlineKeyboardMarkup:
        """Create an inline keyboard from a 2D list of button configurations.

        Args:
            buttons: 2D list where each inner list represents a row of buttons
            language: Language for localization

        Returns:
            InlineKeyboardMarkup: The created keyboard
        """
        keyboard = []

        for row in buttons:
            keyboard_row = []
            for button_config in row:
                text = button_config.get("text", "Button")
                callback_data = button_config.get("callback_data", "unknown")
                url = button_config.get("url")

                if text.startswith("locale:"):
                    key = text[7:]  # Remove "locale:" prefix
                    text = self.locale_manager.get(key, language)

                if url:
                    keyboard_row.append(InlineKeyboardButton(text, url=url))
                else:
                    keyboard_row.append(InlineKeyboardButton(text, callback_data=callback_data))

            keyboard.append(keyboard_row)

        return InlineKeyboardMarkup(keyboard)

    def get_admin_keyboard(self, language: str = "en") -> InlineKeyboardMarkup:
        """Get admin-specific keyboard (for future admin features)."""
        keyboard = [
            [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton(self.locale_manager.get("back_to_menu", language), callback_data="back_to_menu")],
        ]

        return InlineKeyboardMarkup(keyboard)

    def clear_cache(self) -> None:
        """Clear the keyboard cache."""
        self._keyboards_cache.clear()
        logger.debug("Keyboard cache cleared")

    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the keyboard cache."""
        return {"cached_keyboards": len(self._keyboards_cache), "cache_keys": list(self._keyboards_cache.keys())}

    def create_url_keyboard(self, buttons: List[Dict[str, str]], language: str = "en") -> InlineKeyboardMarkup:
        """Create a keyboard with URL buttons.

        Args:
            buttons: List of button configs with 'text' and 'url' keys
            language: Language for localization

        Returns:
            InlineKeyboardMarkup: The created keyboard
        """
        keyboard = []

        for button_config in buttons:
            text = button_config.get("text", "Link")
            url = button_config.get("url", "https://example.com")

            if text.startswith("locale:"):
                key = text[7:]  # Remove "locale:" prefix
                text = self.locale_manager.get(key, language)

            keyboard.append([InlineKeyboardButton(text, url=url)])

        return InlineKeyboardMarkup(keyboard)

    def add_back_button(
        self, keyboard: InlineKeyboardMarkup, language: str = "en", callback_data: str = "back_to_menu"
    ) -> InlineKeyboardMarkup:
        """Add a back button to an existing keyboard."""
        buttons = keyboard.inline_keyboard.copy()
        buttons.append([InlineKeyboardButton(self.locale_manager.get("back_to_menu", language), callback_data=callback_data)])

        return InlineKeyboardMarkup(buttons)

    def get_content_processing_keyboard(self, content_id: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get the content processing options keyboard."""
        keyboard = [
            [InlineKeyboardButton("📄 Summary", callback_data=f"select_summary_{content_id}")],
            [InlineKeyboardButton("🚀 MVP Plan", callback_data=f"select_mvp_plan_{content_id}")],
            [InlineKeyboardButton("💡 Content Ideas", callback_data=f"select_content_ideas_{content_id}")],
        ]

        return InlineKeyboardMarkup(keyboard)

    def get_language_processing_keyboard(self, content_id: str, processing_type: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get language selection keyboard for processing."""
        keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data=f"lang_en_{processing_type}_{content_id}")],
            [InlineKeyboardButton("🇷🇺 Russian", callback_data=f"lang_ru_{processing_type}_{content_id}")],
            [InlineKeyboardButton("🇪🇸 Spanish", callback_data=f"lang_es_{processing_type}_{content_id}")],
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_prompt_options_keyboard(self, content_id: str, processing_type: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get keyboard for user prompt options."""
        keyboard = [
            [InlineKeyboardButton("✏️ Add Custom Instructions", callback_data=f"prompt_{processing_type}_{content_id}")],
            [InlineKeyboardButton("🚀 Process Now", callback_data=f"process_{processing_type}_{content_id}")],
        ]

        return InlineKeyboardMarkup(keyboard)
    
    def get_multi_content_keyboard(self, content_id: str, language: str = "en", total_sources: int = 1) -> InlineKeyboardMarkup:
        """Get keyboard for multi-source content collection."""
        keyboard = []

        # Add more sources button
        add_more_text = self.locale_manager.get("add_more_sources", language)
        keyboard.append([InlineKeyboardButton(add_more_text, callback_data=f"add_more_{content_id}")])

        # Process all sources button (if multiple sources)
        if total_sources > 1:
            process_all_text = self.locale_manager.get("process_all_sources", language).format(count=total_sources)
            keyboard.append([InlineKeyboardButton(process_all_text, callback_data=f"process_all_{content_id}")])

        # Processing options for single item
        keyboard.append([InlineKeyboardButton("📄 Summary", callback_data=f"select_summary_{content_id}")])
        keyboard.append([InlineKeyboardButton("🚀 MVP Plan", callback_data=f"select_mvp_plan_{content_id}")])
        keyboard.append([InlineKeyboardButton("💡 Content Ideas", callback_data=f"select_content_ideas_{content_id}")])

        # Clear all sources button (if multiple sources)
        if total_sources > 1:
            clear_text = self.locale_manager.get("clear_sources", language)
            keyboard.append([InlineKeyboardButton(clear_text, callback_data=f"clear_all_{content_id}")])

        return InlineKeyboardMarkup(keyboard)

    def get_retry_keyboard(self, retry_id: str, language: str = "en", include_cancel: bool = False) -> InlineKeyboardMarkup:
        """Get retry keyboard for error messages.

        Args:
            retry_id: Retry context ID
            language: User's language
            include_cancel: Whether to include cancel button

        Returns:
            InlineKeyboardMarkup with retry button
        """
        retry_text = self.locale_manager.get("retry_button", language)
        keyboard = [[InlineKeyboardButton(retry_text, callback_data=f"retry_{retry_id}")]]

        if include_cancel:
            cancel_text = self.locale_manager.get("cancel_button", language)
            keyboard.append([InlineKeyboardButton(cancel_text, callback_data=f"cancel_retry_{retry_id}")])

        return InlineKeyboardMarkup(keyboard)
