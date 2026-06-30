use std::collections::HashSet;
use std::sync::{RwLock, OnceLock};

use crate::settings;



static STATE_MACHINE: OnceLock<RwLock<AppStateMachine>> = OnceLock::new();

pub fn init() {
    let _ = STATE_MACHINE.set(RwLock::new(AppStateMachine::new()));
}

// read access
pub fn with<R>(f: impl FnOnce(&AppStateMachine) -> R) -> R {
    f(&STATE_MACHINE.get().expect("state machine not initialized").read().unwrap())
}

// write access (transitions)
pub fn with_mut<R>(f: impl FnOnce(&mut AppStateMachine) -> R) -> R {
    f(&mut STATE_MACHINE.get().expect("state machine not initialized").write().unwrap())
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum AppState { MainWindow, SettingsWindow, BlocksWindow, Compiling }

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum CanvasState { Idle, AddingBlock, AddingPath, MovingItem, DeletingItem }

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum SettingsTab { General, Themes, Rpi }

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Theme { Dark, Light, SolarizedLight, SolarizedDark, Monokai, Dracula, Catppuccin, OneDark, Gruvbox, Nord, Custom }

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Language { English, Czech }

pub struct AppStateMachine {
    scale: f32,
    state: AppState,
    canvas: CanvasState,
    open_windows: HashSet<String>,
    settings_tab: SettingsTab,
    current_theme: Theme,
    current_language: Language,
}

//MARK: - AppStateMachine Implementation
impl AppStateMachine {
     pub fn new() -> Self {
        let current_theme_str = settings::with(|s| s.theme.clone());
        let current_language_str = settings::with(|s| s.language.clone());

        let current_theme = match current_theme_str.as_str() {
            "Light" => Theme::Light,
            "Dark" => Theme::Dark,
            "SolarizedLight" => Theme::SolarizedLight,
            "SolarizedDark" => Theme::SolarizedDark,
            "Monokai" => Theme::Monokai,
            "Dracula" => Theme::Dracula,
            "Catppuccin" => Theme::Catppuccin,
            "OneDark" => Theme::OneDark,
            "Gruvbox" => Theme::Gruvbox,
            "Nord" => Theme::Nord,
            _ => Theme::Custom
        };

        let current_language = match current_language_str.as_str() {
            "en" => Language::English,
            "cs" => Language::Czech,
            _ => Language::English,
        };

        Self {
            scale: settings::with(|s| s.ui_scale),
            state: AppState::MainWindow,
            canvas: CanvasState::Idle,
            open_windows: HashSet::new(),
            settings_tab: SettingsTab::General,
            current_theme: current_theme,
            current_language: current_language,
        }
    }

    pub fn can_open_window(&self) -> bool { self.canvas == CanvasState::Idle }

    pub fn on_open_settings_window(&mut self) -> bool {
        if self.can_open_window() {
            self.state = AppState::SettingsWindow;
            self.open_windows.insert("settings".to_string());
            true
        }
        else { false }
    }

    pub fn on_close_settings_window(&mut self) {
        self.state = AppState::MainWindow;
        self.open_windows.remove("settings");
    }

    pub fn is_open(&self, window: &str) -> bool { self.open_windows.contains(window) }

    pub fn set_current_theme(&mut self, theme: Theme) {
        self.current_theme = theme;
    }

    pub fn get_current_theme(&self) -> Theme {
        self.current_theme
    }

    pub fn theme_changed(&self, wanted_theme: Theme) -> bool {
        if self.current_theme != wanted_theme {
            true
        } else {
            false
        }
    }

    pub fn get_theme_str(&self) -> String {
        match self.current_theme {
            Theme::Light => "Light".to_string(),
            Theme::Dark => "Dark".to_string(),
            Theme::SolarizedLight => "SolarizedLight".to_string(),
            Theme::SolarizedDark => "SolarizedDark".to_string(),
            Theme::Monokai => "Monokai".to_string(),
            Theme::Dracula => "Dracula".to_string(),
            Theme::Catppuccin => "Catppuccin".to_string(),
            Theme::OneDark => "OneDark".to_string(),
            Theme::Gruvbox => "Gruvbox".to_string(),
            Theme::Nord => "Nord".to_string(),
            Theme::Custom => "Custom".to_string(),
        }
    }

    pub fn get_theme_from_str(&self, theme_str: &str) -> Theme {
        match theme_str {
            "Light" => Theme::Light,
            "Dark" => Theme::Dark,
            "SolarizedLight" => Theme::SolarizedLight,
            "SolarizedDark" => Theme::SolarizedDark,
            "Monokai" => Theme::Monokai,
            "Dracula" => Theme::Dracula,
            "Catppuccin" => Theme::Catppuccin,
            "OneDark" => Theme::OneDark,
            "Gruvbox" => Theme::Gruvbox,
            "Nord" => Theme::Nord,
            _ => Theme::Custom
        }
    }

    pub fn set_current_language(&mut self, language: Language) {
        self.current_language = language;
    }

    pub fn get_current_language(&self) -> Language {
        self.current_language
    }

    pub fn language_changed(&self, wanted_language: Language) -> bool {
        if self.current_language != wanted_language {
            true
        } else {
            false
        }
    }

    pub fn set_ui_scale(&mut self, scale: f32) {
        self.scale = scale;
    }

    pub fn get_ui_scale(&self) -> f32 {
        self.scale
    }

    pub fn set_settings_tab(&mut self, tab: SettingsTab) {
        self.settings_tab = tab;
    }

    pub fn get_settings_tab(&self) -> SettingsTab {
        self.settings_tab
    }
}