use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::sync::{RwLock, OnceLock};

use crate::theme::Palette;

const VERSION: u32 = 1;

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct Settings {
    pub version: u32,
    pub theme: String,
    pub language: String,
    pub ui_scale: f32,
    pub rpi_host: String,
    pub rpi_username: String,
    pub rpi_password: String,
    pub custom_theme: Option<Palette>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            version: VERSION,
            theme: "dark".to_string(),
            language: "en".to_string(),
            ui_scale: 1.0,
            rpi_host: String::new(),
            rpi_username: String::new(),
            rpi_password: String::new(),
            custom_theme: None,
        }
    }
}

fn config_path() -> Option<PathBuf> {
    let disr = directories::ProjectDirs::from("com", "OmniBoardStudio", "OmniBoardStudio")?;
    Some(disr.config_dir().join("settings.toml"))
}

//MARK: - Settings Implementation
impl Settings {
    pub fn load() -> Self {
        let Some(path) = config_path() else { return Self::default(); };

        match fs::read_to_string(&path) {
            Ok(text) => toml::from_str(&text).unwrap_or_else(|e| {
                eprintln!("Error parsing settings: {}", e);
                Self::default()
            }),
            Err(_) => {
                Self::default()
            }
        }
    }

    pub fn save(&self) {
        let Some(path) = config_path() else { return };

        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }

        let toml = match toml::to_string_pretty(self) {
            Ok(s) => s,
            Err(e) => {
                eprintln!("Error serializing settings: {}", e);
                return;
            }
        };

        let tmp = path.with_extension("toml.tmp");
        if fs::write(&tmp,toml).is_ok() {
            let _ = fs::rename(&tmp, &path);
        }
    }
}

static SETTINGS: OnceLock<RwLock<Settings>> = OnceLock::new();

pub fn init() {
    let _ = SETTINGS.set(RwLock::new(Settings::load()));
}

pub fn with<R> (f: impl FnOnce(&Settings) -> R) ->R {
    f(&SETTINGS.get().expect("Settings not initialized").read().unwrap())
}

pub fn update(f: impl FnOnce(&mut Settings)){
    let mut guard = SETTINGS.get().expect("Settings not initialized").write().unwrap();
    f(&mut guard);
    guard.save();
}