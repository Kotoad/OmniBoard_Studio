use std::collections::HashSet;
use std::sync::{RwLock, OnceLock};

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

pub struct AppStateMachine {
    state: AppState,
    canvas: CanvasState,
    open_windows: HashSet<String>,
    settings_tab: SettingsTab,
    current_theme: Theme,
}

//MARK: - AppStateMachine Implementation
impl AppStateMachine {
     pub fn new() -> Self {
        Self {
            state: AppState::MainWindow,
            canvas: CanvasState::Idle,
            open_windows: HashSet::new(),
            settings_tab: SettingsTab::General,
            current_theme: Theme::Dark,
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

    pub fn set_settings_tab(&mut self, tab: SettingsTab) {
        self.settings_tab = tab;
    }

    pub fn get_settings_tab(&self) -> SettingsTab {
        self.settings_tab
    }
}