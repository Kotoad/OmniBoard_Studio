use eframe::egui::{self, Color32, Ui};
use crate::{OmniBoardStudio, settings, state_machine, theme};
use crate::translation_manager::tr;

fn color_row(ui: &mut Ui, color_category: &str) -> bool {
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

        ui.label(tr(&format!("settings_window.theme_tab.{}", color_category)));

        let mut rgb = {
            let lin = egui::Rgba::from(c);          // Color32 (sRGB) -> linear
            [lin.r(), lin.g(), lin.b()]
        };

        let picker = ui.color_edit_button_rgb(&mut rgb);

        let id = ui.id().with(("hex", color_category));
        let mut hex = ui
            .data_mut(|d| d.get_temp(id))
            .unwrap_or_else(|| format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b()));

        if picker.changed() {
            hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());
            c = egui::Color32::from(egui::Rgba::from_rgb(rgb[0], rgb[1], rgb[2]));
        }

        let hex_edit = ui.add(egui::TextEdit::singleline(&mut hex).desired_width(70.0).char_limit(7));
        if hex_edit.changed() {
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
                *color = c;
            }

            theme::install(ui.ctx(), pal);

            settings::update(|s| s.custom_theme = Some(pal));
        }
        changed
    }).inner
}

impl OmniBoardStudio {
    pub(crate) fn settings_window(&mut self, ctx: &egui::Context) {
        if !state_machine::with(|sm| sm.is_open("settings")) {
            return;
        }

        let mut changed = false;
        let mut current_theme_str = state_machine::with(|sm| sm.get_current_theme());

        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("settings_window"),
            egui::ViewportBuilder::default()
                .with_title(tr("settings_window.title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    ui.label(tr("settings_window.theme_tab.theme_heading"));
                    egui::ComboBox::from_label(tr("settings_window.theme_tab.theme_combo"))
                        .selected_text(match current_theme_str.as_str() {
                            "light" => tr("settings_window.theme_tab.light_theme"),
                            "dark" => tr("settings_window.theme_tab.dark_theme"),
                            "nord" => tr("settings_window.theme_tab.nord_theme"),
                            "dracula" => tr("settings_window.theme_tab.dracula_theme"),
                            "gruvbox" => tr("settings_window.theme_tab.gruvbox_theme"),
                            "solarized_dark" => tr("settings_window.theme_tab.solarized_dark_theme"),
                            "solarized_light" => tr("settings_window.theme_tab.solarized_light_theme"),
                            "monokai" => tr("settings_window.theme_tab.monokai_theme"),
                            "one_dark" => tr("settings_window.theme_tab.one_dark_theme"),
                            "catppuccin" => tr("settings_window.theme_tab.catppuccin_theme"),
                            "custom" => tr("settings_window.theme_tab.custom_theme"),
                            _ => tr("settings_window.theme_tab.dark_theme"),
                        })
                        .show_ui(ui, |ui| {
                            ui.selectable_value(&mut current_theme_str, "light".to_string(), tr("settings_window.theme_tab.light_theme"));
                            ui.selectable_value(&mut current_theme_str, "dark".to_string(), tr("settings_window.theme_tab.dark_theme"));
                            ui.selectable_value(&mut current_theme_str, "nord".to_string(), tr("settings_window.theme_tab.nord_theme"));
                            ui.selectable_value(&mut current_theme_str, "dracula".to_string(), tr("settings_window.theme_tab.dracula_theme"));
                            ui.selectable_value(&mut current_theme_str, "gruvbox".to_string(), tr("settings_window.theme_tab.gruvbox_theme"));
                            ui.selectable_value(&mut current_theme_str, "solarized_dark".to_string(), tr("settings_window.theme_tab.solarized_dark_theme"));
                            ui.selectable_value(&mut current_theme_str, "solarized_light".to_string(), tr("settings_window.theme_tab.solarized_light_theme"));
                            ui.selectable_value(&mut current_theme_str, "monokai".to_string(), tr("settings_window.theme_tab.monokai_theme"));
                            ui.selectable_value(&mut current_theme_str, "one_dark".to_string(), tr("settings_window.theme_tab.one_dark_theme"));
                            ui.selectable_value(&mut current_theme_str, "catppuccin".to_string(), tr("settings_window.theme_tab.catppuccin_theme"));
                            ui.selectable_value(&mut current_theme_str, "custom".to_string(), tr("settings_window.theme_tab.custom_theme"));
                        });

                    if state_machine::with(|sm| sm.theme_changed(&current_theme_str)) {
                        state_machine::with_mut(|sm| sm.set_current_theme(current_theme_str.clone()));
                        theme::get_palette_str(ctx, &current_theme_str);
                        settings::update(|s| s.theme = current_theme_str.clone());
                    }
                    
                    egui::ScrollArea::vertical()
                        .auto_shrink(false)
                        .show(ui, |ui| {
                            ui.heading(tr("settings_window.theme_tab.theme_heading"));
                            
                            changed |= color_row(ui, "main_darker");
                            changed |= color_row(ui, "main");
                            changed |= color_row(ui, "main_lighter");
                            changed |= color_row(ui, "text");
                            changed |= color_row(ui, "highlight");
                            changed |= color_row(ui, "highlight_text");
                            changed |= color_row(ui, "warning");
                            changed |= color_row(ui, "dark");
                            changed |= color_row(ui, "shadow");
                        });
                });
                if changed {
                    state_machine::with_mut(|sm| sm.set_current_theme("custom".to_string()));
                    settings::update(|s| s.theme = "custom".to_string());
                }
                if ctx.input(|i| i.viewport().close_requested()) {
                    print!("Settings window closed");
                    state_machine::with_mut(|sm| sm.on_close_settings_window());
                }
            }
            
        );        
    }

    
    
}