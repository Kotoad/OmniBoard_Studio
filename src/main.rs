#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod translation_manager;
mod theme;
mod widgets;
mod settings_window;
mod state_machine;
mod settings;
mod visual_editor;
mod blocks_library;
mod blocks_data;

use eframe::egui;
use std::fs;
use std::path::{PathBuf, Path};
use std::sync::mpsc::{Receiver, channel};
use notify::{RecommendedWatcher, RecursiveMode, Watcher, Event};
use i18n_embed_fl::fl;
use log::{debug, info, warn, error};
use std::io::Write;

use crate::translation_manager::LOADER;
use crate::widgets::{file_button_simple};


macro_rules! tool_img {
    ($file:literal) => {
        egui::ImageSource::Bytes {
            uri: std::borrow::Cow::Borrowed(concat!("../resources/images/tool_bar/", $file)),
            bytes: egui::load::Bytes::Static(include_bytes!(concat!("../resources/images/tool_bar/", $file)))
        }
    };
}

//MARK: - Helpers
fn read_omni_files() -> Vec<std::path::PathBuf> {
    match fs::read_dir("./Projects") {
        Ok(entries) => entries
            .filter_map(Result::ok)
            .filter(|entry| entry.file_type().map(|ft| ft.is_file()).unwrap_or(false))
            .filter(|entry| {
                let binding = entry.path();
                let ext = binding.extension().and_then(|ext| ext.to_str());
                ext == Some("omni") || (cfg!(debug_assertions) && ext == Some("json"))
            })
            .map(|entry| entry.path())
            .collect(),
        Err(_) => Vec::new(),
    }
}

fn format_time(t: std::time::SystemTime) -> String {
    let datetime: chrono::DateTime<chrono::Local> = t.into();
    datetime.format("%Y-%m-%d %H:%M").to_string()
}

fn create_projects_directory() {
    let path = "./Projects";
    if !std::path::Path::new(path).exists() {
        if let Err(e) = std::fs::create_dir(path) {
            error!("Failed to create Projects directory: {e}");
        }
    }
}

//MARK: - Main
fn main() -> eframe::Result<()> {
    
    env_logger::Builder::new()
        .filter_level(log::LevelFilter::Warn)
        .filter_module("Omniboard_Studio", log::LevelFilter::Debug)
        .format(|buf, record| {
            let level = record.level();
            let style = buf.default_level_style(level);
            writeln!(
                buf,
                "[{style}{level}{style:#}] {}:{}\n    {}",
                record.target(),
                record.line().unwrap_or(0),
                record.args()
            )
        })
        .init();
    
    create_projects_directory();

    settings::init();
    let lang = settings::with(|s| s.language.clone());
    let theme = settings::with(|s| s.theme.clone()).to_string();
    let scale = settings::with(|s| s.ui_scale);

    translation_manager::init();
    state_machine::init();

    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1000.0, 700.0])
            .with_title("OmniBoard Studio"),
        renderer: eframe::Renderer::Glow,
        ..Default::default()
    };
    
    eframe::run_native(
        "OmniBoard Studio",
        options,
        Box::new(move |cc| {
            theme::install_theme_from_str(&cc.egui_ctx, &theme);
            let theme = state_machine::with_mut(|sm| sm.get_theme_from_str(&theme));
            state_machine::with_mut(|sm| sm.set_current_theme(theme));
            translation_manager::switch_language(&lang);
            cc.egui_ctx.set_pixels_per_point(scale);
            egui_extras::install_image_loaders(&cc.egui_ctx);
            if let Some(gl) = &cc.gl {
                use eframe::glow::HasContext as _;
                let renderer = unsafe { gl.get_parameter_string(eframe::glow::RENDERER) };
                info!("Renderer: {renderer}");
            }
            Ok(Box::new(OmniBoardStudio::new(&cc.egui_ctx)))
        }),
    )
}

struct ProjectFile {
    path: PathBuf,
    name: String,
    created: String,
    last_modified: String,
}

struct OmniBoardStudio {
    files: Vec<ProjectFile>,
    fs_rx: Receiver<notify::Result<Event>>,
    _watcher: Option<RecommendedWatcher>,
    visual_editor: visual_editor::VisualEditor,
    current_file: Option<PathBuf>,
}

//MARK: - OmniBoardStudio Implementation
impl OmniBoardStudio {
    fn new(ctx: &egui::Context) -> Self {
        let (tx, rx) = channel();

        let ctx = ctx.clone();
        let watcher = notify::recommended_watcher(move |res| {
            let _ = tx.send(res);
            ctx.request_repaint();
        }).and_then(|mut w| {
            w.watch(Path::new("./Projects"), RecursiveMode::Recursive)?;
            Ok(w)
        })
            .map_err(|e| warn!("File watching disabled: {e}"))
            .ok();

        let mut app = Self { 
            files: Vec::new(),
            fs_rx: rx,
            _watcher: watcher,
            visual_editor: visual_editor::VisualEditor::new(),
            current_file: None,
            };
        app.refresh_files();
        app
    }

    //MARK: - File Management

    fn new_file(&mut self) {
        self.visual_editor = visual_editor::VisualEditor::new();
        self.current_file = None;
    }

    fn open_via_file_dialog(&mut self) {
        let mut dialog = rfd::FileDialog::new()
            .set_title(fl!(LOADER, "main-gui-dialogs-file-dialogs-open-title"))
            .add_filter("OmniBoard project", &["omni"]);
        if cfg!(debug_assertions) {
            dialog = dialog.add_filter("Debug JSON", &["json"])
        }

        if let Some(path) = dialog.pick_file() {
            self.visual_editor.load(&path);
            if path.extension().and_then(|e| e.to_str()) == Some("json") {
                self.current_file = Some(path.with_extension(""))
            } else {
                self.current_file = Some(path)
            }
            state_machine::with_mut(|sm| sm.set_app_tab(state_machine::AppTab::VisualEditor));
        }
    }

    fn save(&mut self) {
        match &self.current_file {
            Some(path) => self.visual_editor.save(path),
            None => self.save_as(),
        }
    }

    fn save_as(&mut self) {
        if let Some(mut path) = rfd::FileDialog::new()
            .set_title(fl!(LOADER, "main-gui-dialogs-file-dialogs-save-title"))
            .add_filter("OmniBoard project", &["omni"])
            .set_file_name("untitled.omni")
            .save_file()
        {
            if path.extension().is_none() {
                path.set_extension("omni");
            }
            self.visual_editor.save(&path);
            if path.extension().and_then(|e| e.to_str()) == Some("json") {
                self.current_file = Some(path.with_extension(""))
            } else {
                self.current_file = Some(path)
            }
        }
    }

    fn refresh_files(&mut self) {
        self.files = read_omni_files()
            .into_iter()
            .map(|path| {
                let name = path
                    .file_stem()
                    .map(|s| s.to_string_lossy().into_owned())
                    .unwrap_or_default();
                let meta = path.metadata().ok();                 // ONE stat call
                let created = meta.as_ref().and_then(|m| m.created().ok())
                    .map(format_time).unwrap_or_else(|| "Unknown".into());
                let last_modified = meta.as_ref().and_then(|m| m.modified().ok())
                    .map(format_time).unwrap_or_else(|| "Unknown".into());
                ProjectFile { path, name, created, last_modified }
            })
            .collect();
    }

    fn check_open_windows(&mut self, ctx: &egui::Context) {
        let mut open_windows = Vec::new();
        state_machine::with(|sm| {
            if sm.is_open("settings") {
                open_windows.push("settings");
            }
            if sm.is_open("blocks_library") {
                open_windows.push("blocks_library");
            }
        });
        for window in open_windows {
            match window {
                "settings" => self.open_settings_window(ctx),
                "blocks_library" => self.visual_editor.blocks_library(ctx),
                _ => {},
            }
        }
    }


    fn open_settings_window(&mut self, ctx: &egui::Context) {
        self.settings_window(ctx);
    }

    //MARK: - GUI
    fn hub_tab_ui(&mut self, ctx: &egui::Context) {

        let _window_width: f32 = ctx.screen_rect().width();

        egui::SidePanel::left("File Sidebar")
            .resizable(true)
            .default_width(300.0)
            .width_range(150.0..=(_window_width*0.5).max(150.0))
            .show(ctx, |ui| {
                egui::ScrollArea::horizontal()
                    .auto_shrink(false)
                    .show(ui, |ui| {
                        ui.style_mut().wrap_mode = Some(egui::TextWrapMode::Extend);
                        ui.heading(fl!(LOADER, "hub-file-sidebar-title"));
                        ui.separator();

                        for file in &self.files {
                            if file_button_simple(ui, &file.name, &file.created, &file.last_modified).clicked() {
                                self.visual_editor.load(&file.path);
                                if file.path.extension().and_then(|e| e.to_str()) == Some("json") {
                                    self.current_file = Some(file.path.with_extension(""))
                                } else {
                                    self.current_file = Some(file.path.clone())
                                }
                                state_machine::with_mut(|sm| sm.set_app_tab(state_machine::AppTab::VisualEditor));
                            }
                        }
                    });
            });

        egui::CentralPanel::default().show(ctx, |ui| {
            egui::ScrollArea::both()
                .auto_shrink(false)
                .show(ui, |ui| {
                    ui.style_mut().wrap_mode = Some(egui::TextWrapMode::Extend);
                    ui.label("Main Hub")
                });
        });
    }
}

//MARK: - eframe::App Implementation
impl eframe::App for OmniBoardStudio {

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {

        let mut changed = false;
        while self.fs_rx.try_recv().is_ok() { changed = true; }
        if changed { self.refresh_files(); }


        let current_tab = state_machine::with(|sm| sm.get_app_tab());

        let pal = crate::theme::palette(ctx);
        egui::TopBottomPanel::top("Menu bar")
            .frame(egui::Frame::none().fill(pal.base).inner_margin(egui::Margin::symmetric(8.0, 4.0)))
            .show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                    let v = ui.visuals_mut();
  
                    v.widgets.noninteractive.bg_stroke.color = pal.window; 

                ui.menu_button(fl!(LOADER, "main-gui-menu-file"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-new")).clicked() {
                        self.new_file();
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-open")).clicked() {
                        self.open_via_file_dialog();
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-save")).clicked() {
                        self.save();
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-save-as")).clicked() {
                        self.save_as();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button(fl!(LOADER, "main-gui-menu-exit")).clicked() {
                        ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                    }
                });
                ui.menu_button(fl!(LOADER, "main-gui-menu-blocks"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-block-library")).clicked() {
                        state_machine::with_mut(|sm| sm.on_open_blocks_library_window());
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-gui-menu-view"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-hub")).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::Hub); });
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-visual-editor")).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::VisualEditor); });
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-code-editor")).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::CodeEditor); });
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-gui-menu-compile"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-compile-code")).clicked() {
                        debug!("Compile code");
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-gui-menu-settings"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-settings")).clicked() {
                        state_machine::with_mut(|sm| { sm.on_open_settings_window(); });
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-gui-menu-help"), |ui| {
                    if ui.button(fl!(LOADER, "main-gui-menu-get-started")).clicked() {
                        debug!("Get Started");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-tutorials")).clicked() {
                        debug!("View Tutorials");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-gui-menu-faq")).clicked() {
                        debug!("View FAQ");
                        ui.close_menu();
                    }
                });
            });
            ui.visuals_mut().widgets.noninteractive.bg_stroke = egui::Stroke::new(1.0, pal.window);
            ui.separator();
        });
        egui::TopBottomPanel::top("Toolbar")
            .frame(egui::Frame::none().fill(pal.base).inner_margin(egui::Margin::symmetric(8.0, 4.0)))
            .show(ctx, |ui| {
                ui.spacing_mut().button_padding = egui::vec2(2.0, 2.0);

                ui.horizontal(|ui| {

                    ui.spacing_mut().item_spacing.x = 8.0;

                    let v = ui.visuals_mut();

                    v.widgets.noninteractive.bg_stroke.color = pal.window; 

                    let h = 16.0;
                    let new_file = egui::Image::new(tool_img!("New_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(new_file)).clicked() {
                        self.new_file();
                    }

                    let open_file = egui::Image::new(tool_img!("Open_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(open_file)).clicked() {
                        self.open_via_file_dialog();
                    }

                    let save_file = egui::Image::new(tool_img!("Save_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(save_file)).clicked() {
                        self.save();
                    }
                    
                    ui.add(egui::Separator::default().spacing(0.0));

                    let block_library = egui::Image::new(tool_img!("Block_library.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(block_library)).clicked() {
                        state_machine::with_mut(|sm| sm.on_open_blocks_library_window());
                    }

                    ui.add(egui::Separator::default().spacing(0.0));

                    let view_hub = egui::Image::new(tool_img!("View_hub.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(view_hub)).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::Hub); });
                    }

                    let view_visual_editor = egui::Image::new(tool_img!("View_visual_editor.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(view_visual_editor)).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::VisualEditor); });
                    }

                    let view_code_editor = egui::Image::new(tool_img!("View_code_editor.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(view_code_editor)).clicked() {
                        state_machine::with_mut(|sm| { sm.set_app_tab(state_machine::AppTab::CodeEditor); });
                    }

                    ui.add(egui::Separator::default().spacing(0.0));

                    let compile_code = egui::Image::new(tool_img!("Run_and_compile.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(compile_code)).clicked() {
                        debug!("Compile code");
                    }

                    ui.add(egui::Separator::default().spacing(0.0));

                    let settings = egui::Image::new(tool_img!("Settings.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(settings)).clicked() {
                        state_machine::with_mut(|sm| { sm.on_open_settings_window(); });
                    }
                });
            });

        match current_tab {
            state_machine::AppTab::Hub => self.hub_tab_ui(ctx),
            state_machine::AppTab::VisualEditor => {
                self.visual_editor.show_visual_editor(ctx);
            },
            state_machine::AppTab::CodeEditor => {
                egui::CentralPanel::default().show(ctx, |ui| {
                    ui.label("Code Editor");
                });
            },
        }

        self.check_open_windows(ctx);
    }
}