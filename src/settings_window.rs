use eframe::egui::{self, Color32, Ui};
use crate::{OmniBoardStudio, state_machine, theme};
use crate::translation_manager::tr;

fn color_row(ui: &mut Ui, label: &str, c: &mut Color32) -> bool {
    let r = ui.color_edit_button_srgba(c);   // sRGBA picker -> matches Palette's Color32
    ui.label(label);
    r.changed()
}

impl OmniBoardStudio {
    pub(crate) fn settings_window(&mut self, ctx: &egui::Context) {
        if !state_machine::with(|sm| sm.is_open("settings")) {
            return;
        }

        let mut pal = theme::palette(ctx);
        let mut changed = false;

        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("settings_window"),
            egui::ViewportBuilder::default()
                .with_title(tr("setting_window.title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    egui::ScrollArea::vertical()
                        .auto_shrink(false)
                        .show(ui, |ui| {
                            changed |= color_row(ui, "Window", &mut pal.window);
                        });
                });
                if ctx.input(|i| i.viewport().close_requested()) {
                    print!("Settings window closed");
                    state_machine::with_mut(|sm| sm.on_close_settings_window());
                }
            }
            
        );

        if changed {
            theme::install(ctx, pal);
        }

        
    }

    
    
}