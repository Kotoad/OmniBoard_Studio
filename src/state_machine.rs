use crate::graph::BlockType;

use std::collections::HashSet;

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum AppState {
    MainWindow,
    SettingsWindow,
    BlocksWindow,
    #[allow(dead_code)]
    Compiling,
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum CanvasState {
    Idle,
    #[allow(dead_code)]
    AddingBlock,
    #[allow(dead_code)]
    AddingPath,
    #[allow(dead_code)]
    MovingItem,
    #[allow(dead_code)]
    DeletingItem,
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum AppTab {
    Hub,
    VisualEditor,
    CodeEditor,
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum SettingsTab {
    General,
    Themes,
    Rpi,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum BlocksLibraryTab {
    Basic,
    Logic,
    IO,
    Math,
    Functions,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Theme {
    Dark,
    Light,
    SolarizedLight,
    SolarizedDark,
    Monokai,
    Dracula,
    Catppuccin,
    OneDark,
    Gruvbox,
    Nord,
    Custom,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Language {
    English,
    Czech,
}
pub struct AppStateMachine {
    state: AppState,
    canvas: CanvasState,
    open_windows: HashSet<String>,
    app_tab: AppTab,
    settings_tab: SettingsTab,
    blocks_library_tab: BlocksLibraryTab,
    block: BlockType,
    basic_block: BlockType,
    logic_block: BlockType,
    math_block: BlockType,
    io_block: BlockType,
}

pub fn theme_from_str(theme_str: &str) -> Theme {
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
        _ => Theme::Custom,
    }
}

pub fn str_from_theme(theme: Theme) -> &'static str {
    match theme {
        Theme::Dark => "Dark",
        Theme::Light => "Light",
        Theme::SolarizedLight => "SolarizedLight",
        Theme::SolarizedDark => "SolarizedDark",
        Theme::Monokai => "Monokai",
        Theme::Dracula => "Dracula",
        Theme::Catppuccin => "Catppuccin",
        Theme::OneDark => "OneDark",
        Theme::Gruvbox => "Gruvbox",
        Theme::Nord => "Nord",
        Theme::Custom => "Custom",
    }
}

pub fn language_from_str(language_str: &str) -> Language {
    match language_str {
        "en" => Language::English,
        "cs" => Language::Czech,
        _ => Language::English,
    }
}

pub fn str_from_language(language: Language) -> &'static str {
    match language {
        Language::English => "en",
        Language::Czech => "cs",
    }
}

//MARK: - AppStateMachine Implementation
impl AppStateMachine {
    pub fn new() -> Self {
        Self {
            state: AppState::MainWindow,
            canvas: CanvasState::Idle,
            open_windows: HashSet::new(),
            app_tab: AppTab::Hub,
            settings_tab: SettingsTab::General,
            blocks_library_tab: BlocksLibraryTab::Basic,
            block: BlockType::Start,
            basic_block: BlockType::Start,
            logic_block: BlockType::If,
            math_block: BlockType::Add,
            io_block: BlockType::Button,
        }
    }

    pub fn can_open_window(&self) -> bool {
        self.canvas == CanvasState::Idle
    }

    pub fn on_open_settings_window(&mut self) -> bool {
        if self.can_open_window() {
            self.state = AppState::SettingsWindow;
            self.open_windows.insert("settings".to_string());
            true
        } else {
            false
        }
    }

    pub fn on_close_settings_window(&mut self) {
        self.state = AppState::MainWindow;
        self.open_windows.remove("settings");
    }

    pub fn on_open_blocks_library_window(&mut self) -> bool {
        if self.can_open_window() && self.app_tab == AppTab::VisualEditor {
            self.state = AppState::BlocksWindow;
            self.open_windows.insert("blocks_library".to_string());
            true
        } else {
            false
        }
    }

    pub fn on_close_blocks_library_window(&mut self) {
        self.state = AppState::MainWindow;
        self.open_windows.remove("blocks_library");
    }

    pub fn is_open(&self, window: &str) -> bool {
        self.open_windows.contains(window)
    }

    pub fn set_app_tab(&mut self, tab: AppTab) {
        self.app_tab = tab;
    }

    pub fn get_app_tab(&self) -> AppTab {
        self.app_tab
    }

    pub fn set_settings_tab(&mut self, tab: SettingsTab) {
        self.settings_tab = tab;
    }

    pub fn get_settings_tab(&self) -> SettingsTab {
        self.settings_tab
    }

    pub fn get_blocks_library_tab(&self) -> BlocksLibraryTab {
        self.blocks_library_tab
    }

    pub fn set_blocks_library_tab(&mut self, tab: BlocksLibraryTab) {
        self.blocks_library_tab = tab;
    }

    pub fn get_current_block(&self) -> BlockType {
        self.block
    }

    pub fn get_current_basic_block(&self) -> BlockType {
        self.basic_block
    }

    pub fn get_current_logic_block(&self) -> BlockType {
        self.logic_block
    }

    pub fn get_current_math_block(&self) -> BlockType {
        self.math_block
    }

    pub fn get_current_io_block(&self) -> BlockType {
        self.io_block
    }

    pub fn set_current_block(&mut self, block: BlockType) {
        self.block = block;
        match self.get_blocks_library_tab() {
            BlocksLibraryTab::Basic => self.basic_block = block,
            BlocksLibraryTab::Logic => self.logic_block = block,
            BlocksLibraryTab::Math => self.math_block = block,
            BlocksLibraryTab::IO => self.io_block = block,
            _ => {}
        }
    }
}
