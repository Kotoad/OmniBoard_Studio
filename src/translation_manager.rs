use std::collections::HashMap;
use std::fs;
use std::path::{PathBuf, Path};
use serde_json::Value;
use std::sync::{OnceLock, RwLock, Mutex};

const TRANSLATIONS_DIR: &str = "./resources/Translations";
const DEFAULT_LANGUAGE: &str = "en";

static TRANSLATION_MANAGER: OnceLock<RwLock<TranslationManager>> = OnceLock::new();

pub struct TranslationManager {
    translation_dir: PathBuf,

    current_language: String,

    translations: HashMap<String, Value>,

    available_languages: HashMap<String, String>,

    cache: Mutex<HashMap<String, String>>,
}

impl TranslationManager {
    pub fn new(start_language: &str) -> Self {
        let mut manager = Self {
            translation_dir: PathBuf::from(TRANSLATIONS_DIR),
            current_language: DEFAULT_LANGUAGE.to_string(),
            translations: HashMap::new(),
            available_languages: HashMap::new(),
            cache: Mutex::new(HashMap::new()),
        };
        manager.load_available_languages();

        manager.load_language(DEFAULT_LANGUAGE);

        if manager.available_languages.contains_key(start_language) {
            manager.load_language(start_language);
        } else {
            eprintln!("Language '{}' not found, defaulting to '{}'", start_language, DEFAULT_LANGUAGE);
        }
        manager
    }

    fn load_available_languages(&mut self) {
        if !self.translation_dir.exists() {
            eprintln!("Translations directory '{}' does not exist. Falling back to default language.", self.translation_dir.display());
            self.available_languages.insert(DEFAULT_LANGUAGE.into(), "English".into());
            return;
        }

        let entries = match fs::read_dir(&self.translation_dir) {
            Ok(entries) => entries,
            Err(e) => {
                eprintln!("Failed to read translations directory: {e}");
                return;
            }
        };

        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();

            if path.extension().and_then(|ext| ext.to_str()) != Some("json") {
                continue;
            }
            
            let Some(lang_code) = path.file_stem().and_then(|stem| stem.to_str()) else {
                continue;
            };

            match Self::read_json(&path) {
                Some(tree) => {
                    if let Some(lang_name) = nested_get(&tree, "main_GUI._metadata.language_name").and_then(|v| v.as_str()) {
                        self.available_languages.insert(lang_code.to_string(), lang_name.to_string());
                        self.translations.insert(lang_code.to_string(), tree);
                    } else {
                        eprintln!("Language file '{}' is missing 'main_GUI._metadata.language_name'. Skipping.", path.display());
                    }
                }
                None => eprintln!("Failed to read language file '{}'. Skipping.", path.display()),
            }
        }
    }

    fn load_language(&mut self, lang_code: &str) -> bool {
        if self.translations.contains_key(lang_code) {
            self.current_language = lang_code.to_string();
            return true;
        }
        else {
            eprintln!("Language '{}' is not available.", lang_code);
            false
        }
    }

    pub fn switch_language(&mut self, lang_code: &str) -> bool {
        if !self.available_languages.contains_key(lang_code) {
            eprintln!("Language '{}' is not available.", lang_code);
            return false;
        }
        let success = self.load_language(lang_code);
        if success {
            self.cache.lock().unwrap().clear();
        }
        success
    }

    pub fn tr(&self, key: &str) -> String {
        if let Some(cached) = self.cache.lock().unwrap().get(key) {
            return cached.clone();
        }
        let translation = self.tr_args(key, &[]);
        self.cache.lock().unwrap().insert(key.to_string(), translation.clone());
        translation
    }

    pub fn tr_args(&self, key: &str, args: &[(&str, &str)]) -> String {
        
        let raw = self
            .lookup(&self.current_language, key)
            .or_else(|| self.lookup(DEFAULT_LANGUAGE, key));

        let mut text = match raw {
            Some(s) => s.to_string(),
            None => {
                eprintln!("Translation key '{}' not found in language '{}'", key, self.current_language);
                return key.to_string();
            }
        };

        for (name, value) in args {
            text = text.replace(&format!("{{{}}}", name), value);
        }
        text
    }

    fn lookup(&self, lang_code: &str, key: &str) -> Option<&str> {
        self.translations.get(lang_code).and_then(|tree| nested_get(tree, key)).and_then(Value::as_str)
    }

    pub fn current_language(&self) -> &str {
        &self.current_language
    }

    pub fn available_languages(&self) -> &HashMap<String, String> {
        &self.available_languages
    }

    fn read_json(path: &Path) -> Option<Value> {
        let text = fs::read_to_string(path).ok()?;
        serde_json::from_str(&text).ok()
    }
}

pub fn init(start_language: &str) {
    let _ = TRANSLATION_MANAGER.set(RwLock::new(TranslationManager::new(start_language)));
}

pub fn tr(key: &str) -> String {
    TRANSLATION_MANAGER
        .get()
        .expect("TranslationManager not initialized")
        .read()
        .expect("Failed to acquire read lock on TranslationManager")
        .tr(key)
}

pub fn switch_language(lang_code: &str) -> bool {
    TRANSLATION_MANAGER
        .get()
        .expect("TranslationManager not initialized")
        .write()
        .expect("Failed to acquire write lock on TranslationManager")
        .switch_language(lang_code)
}

fn nested_get<'a>(data: &'a Value, dotted_key: &str) -> Option<&'a Value> {
    let mut current = data;
    for part in dotted_key.split('.') {
        current = current.get(part)?;
    }
    Some(current)
}