#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod translation_manager;
mod theme;
mod widgets;

use eframe::egui;
use std::fs;
use std::path::{PathBuf, Path};
use std::sync::mpsc::{Receiver, channel};
use notify::{RecommendedWatcher, RecursiveMode, Watcher, Event};

use crate::translation_manager::tr;
use crate::widgets::{file_button_simple};


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
        println!("Content of {}:\n{}", path.display(), content);
    } else {
        eprintln!("Failed to read file: {}", path.display());
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
            eprintln!("Failed to create Projects directory: {e}");
        }
    }
}

fn main() -> eframe::Result<()> {
    create_projects_directory();
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1000.0, 700.0])
            .with_title("OmniBoard Studio"),
        renderer: eframe::Renderer::Glow,
        ..Default::default()
    };
    translation_manager::init("en");
    eframe::run_native(
        "OmniBoard Studio",
        options,
        Box::new(|cc| {
            cc.egui_ctx.set_style(theme::style());
            if let Some(gl) = &cc.gl {
                use eframe::glow::HasContext as _;
                let renderer = unsafe { gl.get_parameter_string(eframe::glow::RENDERER) };
                eprintln!("Renderer: {renderer}");
            }
            Box::new(OmniBoardStudio::new(&cc.egui_ctx))
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
    _watcher: RecommendedWatcher,
}

impl OmniBoardStudio {
    fn new(ctx: &egui::Context) -> Self {
        let (tx, rx) = channel();

        let ctx = ctx.clone();
        let mut watcher = notify::recommended_watcher(move |res| {
            let _ = tx.send(res);
            ctx.request_repaint();
        }).expect("Failed to create file watcher");

        watcher
            .watch(Path::new("./Projects"), RecursiveMode::Recursive)
            .expect("Failed to watch Projects directory");
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
}

impl eframe::App for OmniBoardStudio {

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {

        let mut changed = false;
        while let Ok(_event) = self.fs_rx.try_recv() {
            changed = true;
        }
        if changed {
            self.refresh_files();
        }

        let _window_width = ctx.screen_rect().width();
        let _window_height = ctx.screen_rect().height();

        egui::TopBottomPanel::top("Menu bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                ui.menu_button(tr("main_GUI.menu.file"), |ui| {
                    if ui.button(tr("main_GUI.menu.new")).clicked() {
                        println!("New file");
                    }
                    if ui.button(tr("main_GUI.menu.open")).clicked() {
                        println!("Open file");
                    }
                });
            })
        });

        egui::SidePanel::left("File Sidebar")
            .resizable(true)
            .default_width(300.0)
            .width_range(150.0..=(_window_width*0.5).max(150.0))
            .show(ctx, |ui| {
                egui::ScrollArea::horizontal()
                    .auto_shrink(false)
                    .show(ui, |ui| {
                        ui.style_mut().wrap = Some(false);
                        ui.heading(tr("main_GUI.hub.file_sidebar_title"));
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
                    ui.style_mut().wrap = Some(false);
                    ui.label("Main Hub")
                });
        });
    }
}