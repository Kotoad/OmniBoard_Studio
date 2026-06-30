use eframe::egui::{self, Color32, Ui};
use i18n_embed_fl::fl;
use log::debug;

use crate::{OmniBoardStudio, settings, state_machine, theme};
use crate::translation_manager::LOADER;

//MARK: - Color ruw
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

        let label = match color_category {
            "main_darker" => fl!(LOADER, "settings-window-theme-tab-main-darker"),
            "main" => fl!(LOADER, "settings-window-theme-tab-main"),
            "main_lighter" => fl!(LOADER, "settings-window-theme-tab-main-lighter"),
            "text" => fl!(LOADER, "settings-window-theme-tab-text"),
            "highlight" => fl!(LOADER, "settings-window-theme-tab-highlight"),
            "highlight_text" => fl!(LOADER, "settings-window-theme-tab-highlight-text"),
            "warning" => fl!(LOADER, "settings-window-theme-tab-warning"),
            "dark" => fl!(LOADER, "settings-window-theme-tab-dark"),
            "shadow" => fl!(LOADER, "settings-window-theme-tab-shadow"),
            _ => String::new(),
        };
        ui.label(label);

        let mut rgb = {
            let lin = egui::Rgba::from(c);          // Color32 (sRGB) -> linear
            [lin.r(), lin.g(), lin.b()]
        };

        let picker = ui.color_edit_button_rgb(&mut rgb);

        let id = ui.id().with(("hex", color_category));
        let live_hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());


        let mut hex = if ui.memory(|m| m.has_focus(id)) {
            ui.data_mut(|d| d.get_temp::<String>(id)).unwrap_or_else(|| live_hex.clone())
        } else {
            live_hex.clone()
        };

        if picker.changed() {
            hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());
            c = egui::Color32::from(egui::Rgba::from_rgb(rgb[0], rgb[1], rgb[2]));
        }

        let hex_edit = ui.add(egui::TextEdit::singleline(&mut hex).id(id).desired_width(70.0).char_limit(7));
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

//MARK: - OmniBoardStudio Implementation
impl OmniBoardStudio {
    //MARK: - General Tab UI
    fn general_tab_ui(&mut self, ui: &mut Ui) {

        let mut current_language = state_machine::with(|sm| sm.get_current_language());

        ui.heading(fl!(LOADER, "settings-window-general-tab-heading"));

        ui.label(fl!(LOADER, "settings-window-general-tab-language"));

        egui::ComboBox::from_label(fl!(LOADER, "settings-window-general-tab-language-combo"))
            .selected_text(match current_language {
                state_machine::Language::English => fl!(LOADER, "settings-window-general-tab-language-english"),
                state_machine::Language::Czech => fl!(LOADER, "settings-window-general-tab-language-czech"),
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(&mut current_language, state_machine::Language::English, fl!(LOADER, "settings-window-general-tab-language-english"));
                ui.selectable_value(&mut current_language, state_machine::Language::Czech, fl!(LOADER, "settings-window-general-tab-language-czech"));
            });
        
        if state_machine::with(|sm| sm.language_changed(current_language)) {
            state_machine::with_mut(|sm| sm.set_current_language(current_language));
            match current_language {
                state_machine::Language::English => {
                    crate::translation_manager::switch_language("en");
                }
                state_machine::Language::Czech => {
                    crate::translation_manager::switch_language("cs");
                }
            }
            settings::update(|s| s.language = match current_language {
                state_machine::Language::English => "en".to_string(),
                state_machine::Language::Czech => "cs".to_string(),
            });
        }

        ui.separator();

        let mut current_ui_scale = state_machine::with(|sm| sm.get_ui_scale());

        ui.label(fl!(LOADER, "settings-window-general-tab-ui-scale"));

        ui.horizontal(|ui| {
            let scale_slider = ui.add(
            egui::Slider::new(&mut current_ui_scale, 0.8..=1.3)
                .text(fl!(LOADER, "settings-window-general-tab-ui-scale-slider"))
                .show_value(true)
                .step_by(0.1)
            );

            if ui.button(fl!(LOADER, "settings-window-general-tab-ui-scale-reset")).clicked() {
                current_ui_scale = 1.0;
                state_machine::with_mut(|sm| sm.set_ui_scale(current_ui_scale));
                settings::update(|s| s.ui_scale = current_ui_scale);
                ui.ctx().set_pixels_per_point(current_ui_scale);
            }

            if scale_slider.changed() {
            state_machine::with_mut(|sm| sm.set_ui_scale(current_ui_scale));
            }
            
            if scale_slider.drag_stopped() || (scale_slider.changed() && !scale_slider.dragged()) {
                settings::update(|s| s.ui_scale = current_ui_scale);
                ui.ctx().set_pixels_per_point(current_ui_scale);
            }
        });
    }

    //MARK: - Theme Tab UI
    fn theme_tab_ui(&mut self, ui: &mut Ui) {

        let mut changed: bool = false;
        let mut current_theme = state_machine::with(|sm| sm.get_current_theme());
        let current_theme_str;

        ui.heading(fl!(LOADER, "settings-window-theme-tab-heading"));
        egui::ComboBox::from_label(fl!(LOADER, "settings-window-theme-tab-combo"))
            .selected_text(match current_theme {
                state_machine::Theme::Light => fl!(LOADER, "settings-window-theme-tab-light-theme"),
                state_machine::Theme::Dark => fl!(LOADER, "settings-window-theme-tab-dark-theme"),
                state_machine::Theme::Nord => fl!(LOADER, "settings-window-theme-tab-nord-theme"),
                state_machine::Theme::Dracula => fl!(LOADER, "settings-window-theme-tab-dracula-theme"),
                state_machine::Theme::Gruvbox => fl!(LOADER, "settings-window-theme-tab-gruvbox-theme"),
                state_machine::Theme::SolarizedDark => fl!(LOADER, "settings-window-theme-tab-solarized-dark-theme"),
                state_machine::Theme::SolarizedLight => fl!(LOADER, "settings-window-theme-tab-solarized-light-theme"),
                state_machine::Theme::Monokai => fl!(LOADER, "settings-window-theme-tab-monokai-theme"),
                state_machine::Theme::OneDark => fl!(LOADER, "settings-window-theme-tab-one-dark-theme"),
                state_machine::Theme::Catppuccin => fl!(LOADER, "settings-window-theme-tab-catppuccin-theme"),
                state_machine::Theme::Custom => fl!(LOADER, "settings-window-theme-tab-custom-theme"),
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(&mut current_theme, state_machine::Theme::Light, fl!(LOADER, "settings-window-theme-tab-light-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Dark, fl!(LOADER, "settings-window-theme-tab-dark-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Nord, fl!(LOADER, "settings-window-theme-tab-nord-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Dracula, fl!(LOADER, "settings-window-theme-tab-dracula-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Gruvbox, fl!(LOADER, "settings-window-theme-tab-gruvbox-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::SolarizedDark, fl!(LOADER, "settings-window-theme-tab-solarized-dark-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::SolarizedLight, fl!(LOADER, "settings-window-theme-tab-solarized-light-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Monokai, fl!(LOADER, "settings-window-theme-tab-monokai-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::OneDark, fl!(LOADER, "settings-window-theme-tab-one-dark-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Catppuccin, fl!(LOADER, "settings-window-theme-tab-catppuccin-theme"));
                ui.selectable_value(&mut current_theme, state_machine::Theme::Custom, fl!(LOADER, "settings-window-theme-tab-custom-theme"));
            });

        if state_machine::with(|sm| sm.theme_changed(current_theme)) {
            state_machine::with_mut(|sm| sm.set_current_theme(current_theme.clone()));
            current_theme_str = state_machine::with(|sm| sm.get_theme_str());
            theme::install_theme_from_str(ui.ctx(), &current_theme_str);
            settings::update(|s| s.theme = current_theme_str.clone());
        }
        
        egui::ScrollArea::vertical()
            .auto_shrink(false)
            .show(ui, |ui| {
                ui.heading(fl!(LOADER, "settings-window-theme-tab-heading"));
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
            
        if changed {
            state_machine::with_mut(|sm| sm.set_current_theme(state_machine::Theme::Custom));
            settings::update(|s| s.theme = "Custom".to_string());
        }
    }
    //MARK: - Settings Window
    pub(crate) fn settings_window(&mut self, ctx: &egui::Context) {
        if !state_machine::with(|sm| sm.is_open("settings")) {
            return;
        }

        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("settings_window"),
            egui::ViewportBuilder::default()
                .with_title(fl!(LOADER, "settings-window-title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {

                    let mut settings_tab = state_machine::with(|sm| sm.get_settings_tab());

                    ui.horizontal(|ui| {
                        ui.selectable_value(&mut settings_tab, state_machine::SettingsTab::General, fl!(LOADER, "settings-window-general-tab"));
                        ui.selectable_value(&mut settings_tab, state_machine::SettingsTab::Themes, fl!(LOADER, "settings-window-theme-tab"));
                        ui.selectable_value(&mut settings_tab, state_machine::SettingsTab::Rpi, fl!(LOADER, "settings-window-rpi-tab"));
                    });
                    state_machine::with_mut(|sm| sm.set_settings_tab(settings_tab));

                    ui.separator();

                    match settings_tab {
                        state_machine::SettingsTab::General => {
                            self.general_tab_ui(ui)
                        }
                        state_machine::SettingsTab::Themes => {
                            self.theme_tab_ui(ui);
                        }
                        state_machine::SettingsTab::Rpi => {
                            // Show Rpi settings
                        }
                    }

                    
                });
                if ctx.input(|i| i.viewport().close_requested()) {
                    debug!("Settings window closed");
                    state_machine::with_mut(|sm| sm.on_close_settings_window());
                }
            }
            
        );        
    }
}