use eframe::egui::{self, Color32, Ui};
use crate::{OmniBoardStudio, state_machine, theme};
use crate::translation_manager::tr;

fn color_row(ui: &mut Ui, color_category: &str) {
    ui.horizontal(|ui|{
        let mut pal = theme::palette(ui.ctx());

        let mut c = match color_category {
            "main_darker" => pal.window,
            "main" => pal.base,
            "main_lighter" => pal.alternate_base,
            "text" => pal.text,
            "highlight" => pal.highlight,
            "highlight_text" => pal.highlighted_text,
            "warning" => pal.bright_text,
            "dark" => pal.dark,
            "shadow" => pal.shadow,
            _ => Color32::from_rgb(0, 0, 0),
        };

        ui.label(tr(&format!("settings_window.theme.{}", color_category)));

        let picker = ui.color_edit_button_srgba(&mut c);

        let id = ui.id().with(("hex", color_category));
        let mut hex = ui
            .data_mut(|d| d.get_temp(id))
            .unwrap_or_else(|| format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b()));

        if picker.changed() {
            hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());
        }

        let hex_edit = ui.add(egui::TextEdit::singleline(&mut hex).desired_width(70.0).char_limit(7));
        if hex_edit.changed() {
            println!("Hex changed to: {}\n", hex);
            let digits: String = hex.chars().filter(|ch| ch.is_ascii_hexdigit()).map(|ch| ch.to_ascii_uppercase()).take(6).collect();
            hex = format!("#{}", digits);
            let s = hex.trim_start_matches('#');
            if s.len() == 6 {
                if let Ok(rgb) = u32::from_str_radix(s, 16) {
                    c = Color32::from_rgb(
                        ((rgb >> 16) & 0xFF) as u8,
                        ((rgb >> 8) & 0xFF) as u8,
                        (rgb & 0xFF) as u8,
                    );
                }
            }
        }

        ui.data_mut(|d| d.insert_temp(id, hex));

        let changed = picker.changed() || hex_edit.changed();

        if changed {
            let mut to_change = Vec::new();

            if color_category == "main_darker" {
                to_change.push(&mut pal.window);
                to_change.push(&mut pal.tooltip_base);
            }
            else if color_category == "main" {
                to_change.push(&mut pal.base);
                to_change.push(&mut pal.button);
                to_change.push(&mut pal.midlight);
                to_change.push(&mut pal.mid);
            }
            else if color_category == "main_lighter" {
                to_change.push(&mut pal.alternate_base);
                to_change.push(&mut pal.light);
            }
            else if color_category == "text" {
                to_change.push(&mut pal.text);
                to_change.push(&mut pal.window_text);
                to_change.push(&mut pal.placeholder_text);
                to_change.push(&mut pal.tooltip_text);
                to_change.push(&mut pal.button_text);
            }
            else if color_category == "highlight" {
                to_change.push(&mut pal.highlight);
                to_change.push(&mut pal.link);
            }
            else if color_category == "highlight_text" {
                to_change.push(&mut pal.highlighted_text);
                to_change.push(&mut pal.link_visited);
                
            }
            else if color_category == "warning" {
                to_change.push(&mut pal.bright_text);
            }
            
            else if color_category == "dark" {
                to_change.push(&mut pal.dark);
            }
            else if color_category == "shadow" {
                to_change.push(&mut pal.shadow);
            }

            for color in to_change {
                println!("Changing color {:#?} from category {}\n", c, color_category);
                *color = c;
            }

            theme::install(ui.ctx(), pal);
        }
    });
}

impl OmniBoardStudio {
    pub(crate) fn settings_window(&mut self, ctx: &egui::Context) {
        if !state_machine::with(|sm| sm.is_open("settings")) {
            return;
        }

        let mut current_theme_str = state_machine::with(|sm| sm.get_current_theme());

        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("settings_window"),
            egui::ViewportBuilder::default()
                .with_title(tr("setting_window.title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    ui.label(tr("settings_window.theme.theme_combo"));
                    egui::ComboBox::from_label(tr("settings_window.theme.theme_combo"))
                        .selected_text(match current_theme_str.as_str() {
                            "light" => tr("settings_window.theme.light"),
                            "dark" => tr("settings_window.theme.dark"),
                            _ => tr("settings_window.theme.dark"),
                        })
                        .show_ui(ui, |ui| {
                            ui.selectable_value(&mut current_theme_str, "light".to_string(), tr("settings_window.theme.light"));
                            ui.selectable_value(&mut current_theme_str, "dark".to_string(), tr("settings_window.theme.dark"));
                        });

                    if state_machine::with_mut(|sm| sm.theme_changed(current_theme_str.clone())) {
                        state_machine::with_mut(|sm| sm.set_current_theme(current_theme_str.clone()));
                        theme::get_palette_str(ctx, &current_theme_str);
                    }

                    egui::ScrollArea::vertical()
                        .auto_shrink(false)
                        .show(ui, |ui| {
                            ui.heading(tr("settings_window.theme"));
                            color_row(ui, "main_darker");
                            color_row(ui, "main");
                            color_row(ui, "main_lighter");
                            color_row(ui, "text");
                            color_row(ui, "highlight");
                            color_row(ui, "highlight_text");
                            color_row(ui, "warning");
                            color_row(ui, "dark");
                            color_row(ui, "shadow");
                        });
                });
                if ctx.input(|i| i.viewport().close_requested()) {
                    print!("Settings window closed");
                    state_machine::with_mut(|sm| sm.on_close_settings_window());
                }
            }
            
        );        
    }

    
    
}