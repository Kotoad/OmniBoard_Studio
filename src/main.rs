#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod translation_manager;
mod theme;
mod widgets;
mod settings_window;
mod state_machine;
mod settings;

use eframe::egui;
use std::fs;
use std::path::{PathBuf, Path};
use std::sync::mpsc::{Receiver, channel};
use notify::{RecommendedWatcher, RecursiveMode, Watcher, Event};
use i18n_embed_fl::fl;
use log::{debug, info, warn, error};

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
                entry.path()
                    .extension()
                    .and_then(|ext| ext.to_str())
                    == Some("omni")
            })
            .map(|entry| entry.path())
            .collect(),
        Err(_) => Vec::new(),
    }
}

fn read_omni_file(path: &std::path::Path) {
    let content = fs::read_to_string(path).ok();
    if let Some(content) = content {
        debug!("Content of {}:\n{}", path.display(), content);
    } else {
        error!("Failed to read file: {}", path.display());
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
    env_logger::init();
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
            };
        app.refresh_files();
        app
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
        });
        for window in open_windows {
            match window {
                "settings" => self.open_settings_window(ctx),
                _ => {},
            }
        }
    }

    fn open_settings_window(&mut self, ctx: &egui::Context) {
        self.settings_window(ctx);
    }
}

//MARK: - eframe::App Implementation
impl eframe::App for OmniBoardStudio {

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {

        let mut changed = false;
        while self.fs_rx.try_recv().is_ok() { changed = true; }
        if changed { self.refresh_files(); }

        let _window_width = ctx.screen_rect().width();
        let _window_height = ctx.screen_rect().height();
        let pal = crate::theme::palette(ctx);
        egui::TopBottomPanel::top("Menu bar")
            .frame(egui::Frame::none().fill(pal.base).inner_margin(egui::Margin::symmetric(8.0, 4.0)))
            .show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                    let v = ui.visuals_mut();
  
                    v.widgets.noninteractive.bg_stroke.color = pal.window; 

                ui.menu_button(fl!(LOADER, "main-GUI-menu-new"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-new")).clicked() {
                        debug!("New file");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-open")).clicked() {
                        debug!("Open file");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-save")).clicked() {
                        debug!("Save file");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-save-as")).clicked() {
                        debug!("Save As");
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button(fl!(LOADER, "main-GUI-menu-exit")).clicked() {
                        ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                    }
                });
                ui.menu_button(fl!(LOADER, "main-GUI-menu-blocks"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-block-library")).clicked() {
                        debug!("View block library");
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-GUI-menu-view"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-hub")).clicked() {
                        debug!("View Hub");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-visual-editor")).clicked() {
                        debug!("View visual editor");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-code-editor")).clicked() {
                        debug!("View code editor");
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-GUI-menu-compile"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-compile-code")).clicked() {
                        debug!("Compile code");
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-GUI-menu-settings"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-settings")).clicked() {
                        state_machine::with_mut(|sm| { sm.on_open_settings_window(); });
                        ui.close_menu();
                    }
                });
                ui.menu_button(fl!(LOADER, "main-GUI-menu-help"), |ui| {
                    if ui.button(fl!(LOADER, "main-GUI-menu-get-started")).clicked() {
                        debug!("Get Started");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-tutorials")).clicked() {
                        debug!("View Tutorials");
                        ui.close_menu();
                    }
                    if ui.button(fl!(LOADER, "main-GUI-menu-faq")).clicked() {
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
                ui.spacing_mut().item_spacing.x = 8.0;

                ui.horizontal(|ui| {
                    let v = ui.visuals_mut();
  
                    v.widgets.noninteractive.bg_stroke.color = pal.window; 

                    let h = 16.0;
                    let new_file = egui::Image::new(tool_img!("New_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(new_file)).clicked() {
                        debug!("New file");
                    }

                    let open_file = egui::Image::new(tool_img!("Open_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(open_file)).clicked() {
                        debug!("Open file");
                    }

                    let save_file = egui::Image::new(tool_img!("Save_file.png"))
                        .fit_to_exact_size(egui::vec2(h, h))
                        .tint(ui.visuals().text_color());
                    if ui.add(egui::ImageButton::new(save_file)).clicked() {
                        debug!("Save file");
                    }

                    ui.separator();

                });
            });

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
                                read_omni_file(&file.path)
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
        self.check_open_windows(ctx);
    }
}