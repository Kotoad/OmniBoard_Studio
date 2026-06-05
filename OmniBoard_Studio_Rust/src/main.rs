#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use eframe::egui;

fn main() -> eframe::Result<()> {
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
        Box::new(|cc| {
            if let Some(gl) = &cc.gl {
                use eframe::glow::HasContext as _;
                let renderer = unsafe { gl.get_parameter_string(eframe::glow::RENDERER) };
                eprintln!("Renderer: {renderer}");
            }
            Box::new(OmniBoardStudio::new())
        }),
    )
}

struct OmniBoardStudio {
}

impl OmniBoardStudio {
    fn new() -> Self {
        Self {}
    }
}

impl eframe::App for OmniBoardStudio {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::SidePanel::left("Project Explorer")
            .resizable(true)
            .default_width(180.0)
            .width_range(120.0..=400.0)
            .show(ctx, |ui| {
                egui::ScrollArea::horizontal()
                    .auto_shrink(false)
                    .show(ui, |ui| {
                        ui.style_mut().wrap = Some(false);
                        ui.heading("Project Explorer");
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