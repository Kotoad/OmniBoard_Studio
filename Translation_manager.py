from Imports import json, os, Path, get_Utils

Utils = get_Utils()

class TranslationManager:
    _instance = None
    _isinitialized = False
    _current_language = Utils.app_settings.language
    _translations = {}
    available_translations = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._isinitialized = False
        return cls._instance

    def __init__(self):
        if self._isinitialized:
            return

        self._isinitialized = True
        base_path = Utils.get_base_path()
        self.translation_dir = base_path / 'resources' / 'Translations'
        self._load_available_translations()
        if Utils.app_settings.language in self.available_translations:
            print("Loading user preferred language:", Utils.app_settings.language)
            self._load_translation(Utils.app_settings.language) 

    def _load_available_translations(self):

        if not self.translation_dir.exists():
            print(f"Translation directory {self.translation_dir} does not exist.\nDefaulting to English only.")
            self.available_translations = {'en': 'English'}
            return

        for json_file in self.translation_dir.glob('*.json'):
            lang_code = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang_name = self._get_nested_value(data, 'main_GUI._metadata.language_name')
                    if lang_code and lang_name:
                        self.available_translations[lang_code] = lang_name  
                    else:
                        print(f"Warning: Missing 'main_GUI._metadata.language_name' in {json_file}. Skipping.")
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse {json_file}. Skipping.")
            except Exception as e:
                print(f"Warning: An error occurred while loading {json_file}: {e}. Skipping.")
        
    def _load_translation(self, lang_code):
        if lang_code in self._translations:
            self._current_language = lang_code
            return True

        translation_file = self.translation_dir / f"{lang_code}.json"

        if not translation_file.exists():
            print(f"Translation file for '{lang_code}' does not exist. Defaulting to English.")
            return False
        
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                self._translations[lang_code] = json.load(f)
            self._current_language = lang_code
            print(f"Loaded translation for '{lang_code}'.")
            return True
        except json.JSONDecodeError:
            print(f"Error: Failed to parse translation file for '{lang_code}'. Defaulting to English.")
            return False
        except Exception as e:
            print(f"Error: An error occurred while loading translation for '{lang_code}': {e}. Defaulting to English.")
            return False
        
    def set_language(self, lang_code):
        if lang_code not in self.available_translations:
            print(f"Language '{lang_code}' is not available. Available languages: {list(self.available_translations.keys())}")
            return False

        if self._load_translation(lang_code):
            print(f"Language set to '{lang_code}'.")
            self._current_language = lang_code
            return True

        return False

    def translate(self, key, default=None, **kwargs):
        text = self._get_nested_value(self._translations.get(self._current_language, {}), key)

        if text is None and self._current_language != 'en':
            text = self._get_nested_value(self._translations.get('en', {}), key)

        if text is None:
            text = default or key
            print(f"Warning: Missing translation for key '{key}' in language '{self._current_language}'.")

        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Missing placeholder {e} in translation for key '{key}'.")
            
        return text

    def _get_nested_value(self, data_dict, nested_key):
        keys = nested_key.split('.')
        current_value = data_dict

        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return None
        return current_value
    
    def get_current_language(self):
        return self._current_language

    def get_available_languages(self):
        return self.available_translations.copy()