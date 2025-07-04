import json
import os

class Localization:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Localization, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.current_language = "en"
        self.translations = {}
        self.available_languages = {
            "en": "English",
            "ru": "Русский",
            "uk": "Українська",
            "kk": "Қазақша",
            "fr": "Français",
            "es": "Español",
            "pl": "Polski",
            "de": "Deutsch"
        }
        self.load_translations()

    def load_translations(self):
        localization_dir = os.path.dirname(__file__)
        for lang_code in self.available_languages.keys():
            try:
                with open(os.path.join(localization_dir, f"{lang_code}.json"), "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)
            except FileNotFoundError:
                print(f"Translation file for {lang_code} not found")

    def set_language(self, language_code):
        if language_code in self.available_languages:
            self.current_language = language_code

    def get(self, key_path, default=""):
        keys = key_path.split(".")
        current = self.translations.get(self.current_language, {})
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current if isinstance(current, str) else default

    def get_available_languages(self):
        return self.available_languages
