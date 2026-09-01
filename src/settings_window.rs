use eframe::egui::{self, Color32, Ui};
use i18n_embed_fl::fl;
use log::debug;

use crate::translation_manager::LOADER;
use crate::{settings, state_machine, theme, OmniBoardStudio};

//MARK: - Color row
fn color_row(ui: &mut Ui, color_category: &str, settings: &mut settings::Settings) -> bool {
    ui.horizontal(|ui| {
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
            let lin = egui::Rgba::from(c); // Color32 (sRGB) -> linear
            [lin.r(), lin.g(), lin.b()]
        };

        let picker = ui.color_edit_button_rgb(&mut rgb);

        let id = ui.id().with(("hex", color_category));
        let live_hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());

        let mut hex = if ui.memory(|m| m.has_focus(id)) {
            ui.data_mut(|d| d.get_temp::<String>(id))
                .unwrap_or_else(|| live_hex.clone())
        } else {
            live_hex.clone()
        };

        if picker.changed() {
            hex = format!("#{:02X}{:02X}{:02X}", c.r(), c.g(), c.b());
            c = egui::Color32::from(egui::Rgba::from_rgb(rgb[0], rgb[1], rgb[2]));
        }

        let hex_edit = ui.add(
            egui::TextEdit::singleline(&mut hex)
                .id(id)
                .desired_width(70.0)
                .char_limit(7),
        );
        if hex_edit.changed() {
            let digits: String = hex
                .chars()
                .filter(|ch| ch.is_ascii_hexdigit())
                .map(|ch| ch.to_ascii_uppercase())
                .take(6)
                .collect();
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
            } else if color_category == "main" {
                to_change.push(&mut pal.base);
                to_change.push(&mut pal.button);
                to_change.push(&mut pal.midlight);
                to_change.push(&mut pal.mid);
            } else if color_category == "main_lighter" {
                to_change.push(&mut pal.alternate_base);
                to_change.push(&mut pal.light);
            } else if color_category == "text" {
                to_change.push(&mut pal.text);
                to_change.push(&mut pal.window_text);
                to_change.push(&mut pal.placeholder_text);
                to_change.push(&mut pal.tooltip_text);
                to_change.push(&mut pal.button_text);
            } else if color_category == "highlight" {
                to_change.push(&mut pal.highlight);
                to_change.push(&mut pal.link);
            } else if color_category == "highlight_text" {
                to_change.push(&mut pal.highlighted_text);
                to_change.push(&mut pal.link_visited);
            } else if color_category == "warning" {
                to_change.push(&mut pal.bright_text);
            } else if color_category == "dark" {
                to_change.push(&mut pal.dark);
            } else if color_category == "shadow" {
                to_change.push(&mut pal.shadow);
            }

            for color in to_change {
                *color = c;
            }

            theme::install(ui, pal);
            settings.custom_theme = Some(pal);
        }
        changed
    })
    .inner
}

//MARK: - OmniBoardStudio Implementation
impl OmniBoardStudio {
    //MARK: - General Tab UI
    fn general_tab_ui(&mut self, ui: &mut Ui) {
        let mut current_language = state_machine::language_from_str(&self.settings.language);

        ui.heading(fl!(LOADER, "settings-window-general-tab-heading"));

        ui.label(fl!(LOADER, "settings-window-general-tab-language"));

        egui::ComboBox::from_label(fl!(LOADER, "settings-window-general-tab-language-combo"))
            .selected_text(match current_language {
                state_machine::Language::English => {
                    fl!(LOADER, "settings-window-general-tab-language-english")
                }
                state_machine::Language::Czech => {
                    fl!(LOADER, "settings-window-general-tab-language-czech")
                }
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(
                    &mut current_language,
                    state_machine::Language::English,
                    fl!(LOADER, "settings-window-general-tab-language-english"),
                );
                ui.selectable_value(
                    &mut current_language,
                    state_machine::Language::Czech,
                    fl!(LOADER, "settings-window-general-tab-language-czech"),
                );
            });

        if current_language != state_machine::language_from_str(&self.settings.language) {
            match current_language {
                state_machine::Language::English => {
                    crate::translation_manager::switch_language("en");
                }
                state_machine::Language::Czech => {
                    crate::translation_manager::switch_language("cs");
                }
            }
            self.settings.language = state_machine::str_from_language(current_language).to_string();
            self.settings.save();
        }

        ui.separator();

        let mut current_ui_scale = self.settings.ui_scale;

        ui.label(fl!(LOADER, "settings-window-general-tab-ui-scale"));

        ui.horizontal(|ui| {
            let scale_slider = ui.add(
                egui::Slider::new(&mut current_ui_scale, 0.8..=1.3)
                    .text(fl!(LOADER, "settings-window-general-tab-ui-scale-slider"))
                    .show_value(true)
                    .step_by(0.1),
            );

            if ui
                .button(fl!(LOADER, "settings-window-general-tab-ui-scale-reset"))
                .clicked()
            {
                current_ui_scale = 1.0;
                self.settings.ui_scale = current_ui_scale;
                self.settings.save();
                ui.ctx().set_pixels_per_point(current_ui_scale);
            }

            if scale_slider.changed() {
                self.settings.ui_scale = current_ui_scale;
                ui.ctx().set_pixels_per_point(current_ui_scale);
            }

            if scale_slider.drag_stopped() || (scale_slider.changed() && !scale_slider.dragged()) {
                self.settings.save();
            }
        });
    }

    //MARK: - Theme Tab UI
    fn theme_tab_ui(&mut self, ui: &mut Ui) {
        let mut changed: bool = false;
        let mut current_theme = state_machine::theme_from_str(&self.settings.theme);

        ui.heading(fl!(LOADER, "settings-window-theme-tab-heading"));
        egui::ComboBox::from_label(fl!(LOADER, "settings-window-theme-tab-combo"))
            .selected_text(match current_theme {
                state_machine::Theme::Light => fl!(LOADER, "settings-window-theme-tab-light-theme"),
                state_machine::Theme::Dark => fl!(LOADER, "settings-window-theme-tab-dark-theme"),
                state_machine::Theme::Nord => fl!(LOADER, "settings-window-theme-tab-nord-theme"),
                state_machine::Theme::Dracula => {
                    fl!(LOADER, "settings-window-theme-tab-dracula-theme")
                }
                state_machine::Theme::Gruvbox => {
                    fl!(LOADER, "settings-window-theme-tab-gruvbox-theme")
                }
                state_machine::Theme::SolarizedDark => {
                    fl!(LOADER, "settings-window-theme-tab-solarized-dark-theme")
                }
                state_machine::Theme::SolarizedLight => {
                    fl!(LOADER, "settings-window-theme-tab-solarized-light-theme")
                }
                state_machine::Theme::Monokai => {
                    fl!(LOADER, "settings-window-theme-tab-monokai-theme")
                }
                state_machine::Theme::OneDark => {
                    fl!(LOADER, "settings-window-theme-tab-one-dark-theme")
                }
                state_machine::Theme::Catppuccin => {
                    fl!(LOADER, "settings-window-theme-tab-catppuccin-theme")
                }
                state_machine::Theme::Custom => {
                    fl!(LOADER, "settings-window-theme-tab-custom-theme")
                }
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Light,
                    fl!(LOADER, "settings-window-theme-tab-light-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Dark,
                    fl!(LOADER, "settings-window-theme-tab-dark-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Nord,
                    fl!(LOADER, "settings-window-theme-tab-nord-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Dracula,
                    fl!(LOADER, "settings-window-theme-tab-dracula-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Gruvbox,
                    fl!(LOADER, "settings-window-theme-tab-gruvbox-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::SolarizedDark,
                    fl!(LOADER, "settings-window-theme-tab-solarized-dark-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::SolarizedLight,
                    fl!(LOADER, "settings-window-theme-tab-solarized-light-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Monokai,
                    fl!(LOADER, "settings-window-theme-tab-monokai-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::OneDark,
                    fl!(LOADER, "settings-window-theme-tab-one-dark-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Catppuccin,
                    fl!(LOADER, "settings-window-theme-tab-catppuccin-theme"),
                );
                ui.selectable_value(
                    &mut current_theme,
                    state_machine::Theme::Custom,
                    fl!(LOADER, "settings-window-theme-tab-custom-theme"),
                );
            });

        if current_theme != state_machine::theme_from_str(&self.settings.theme) {
            let current_theme_str = state_machine::str_from_theme(current_theme);
            theme::install_theme_from_str(ui.ctx(), current_theme_str, &self.settings);
            self.settings.theme = current_theme_str.to_string();
            self.settings.save();
        }

        egui::ScrollArea::vertical()
            .auto_shrink(false)
            .show(ui, |ui| {
                ui.heading(fl!(LOADER, "settings-window-theme-tab-heading"));
                changed |= color_row(ui, "main_darker", &mut self.settings);
                changed |= color_row(ui, "main", &mut self.settings);
                changed |= color_row(ui, "main_lighter", &mut self.settings);
                changed |= color_row(ui, "text", &mut self.settings);
                changed |= color_row(ui, "highlight", &mut self.settings);
                changed |= color_row(ui, "highlight_text", &mut self.settings);
                changed |= color_row(ui, "warning", &mut self.settings);
                changed |= color_row(ui, "dark", &mut self.settings);
                changed |= color_row(ui, "shadow", &mut self.settings);
            });

        if changed && self.settings.theme != "Custom" {
            self.settings.theme = "Custom".to_string();
            self.settings.save();
        }
    }
    //MARK: - Settings Window
    pub(crate) fn settings_window(&mut self, ctx: &egui::Context) {
        if !self.state_machine.is_open("settings") {
            return;
        }

        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("settings_window"),
            egui::ViewportBuilder::default()
                .with_title(fl!(LOADER, "settings-window-title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    let mut settings_tab = self.state_machine.get_settings_tab();

                    ui.horizontal(|ui| {
                        ui.selectable_value(
                            &mut settings_tab,
                            state_machine::SettingsTab::General,
                            fl!(LOADER, "settings-window-general-tab"),
                        );
                        ui.selectable_value(
                            &mut settings_tab,
                            state_machine::SettingsTab::Themes,
                            fl!(LOADER, "settings-window-theme-tab"),
                        );
                        ui.selectable_value(
                            &mut settings_tab,
                            state_machine::SettingsTab::Rpi,
                            fl!(LOADER, "settings-window-rpi-tab"),
                        );
                    });
                    self.state_machine.set_settings_tab(settings_tab);

                    ui.separator();

                    match settings_tab {
                        state_machine::SettingsTab::General => self.general_tab_ui(ui),
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
                    self.settings.save();
                    self.state_machine.on_close_settings_window();
                }
            },
        );
    }
}
