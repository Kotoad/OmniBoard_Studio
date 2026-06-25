// ============================================================================
//  THEME / STYLESHEET — ported from the PyQt app's QPalette
// ----------------------------------------------------------------------------
//  The Python app (Test_colors.py) defines its look as a Qt QPalette with two
//  themes: "Slate Dark" and "Warm Light". This file reproduces those EXACT
//  colours in egui, keeping the original QPalette role names so the two apps
//  stay in sync — change a colour in Python, change the same field here.
//
//  Qt has ~22 palette "roles" (Window, Base, Button, Highlight, ...). egui has
//  a different model (5 widget states), so below we (1) store the Qt roles
//  verbatim in `Palette`, then (2) map them onto egui's Visuals the same way
//  Qt's "Fusion" style does (Button at rest, lighter on hover, etc.).
//
//  WIRE UP (in main.rs run_native closure):
//      cc.egui_ctx.set_style(crate::theme::style());          // Slate Dark
//      // or: cc.egui_ctx.set_style(theme::style_from(Palette::light()));
// ============================================================================

use eframe::egui::{
    self, Color32, FontFamily, FontId, Rounding, Stroke, Style, TextStyle, Visuals,
};

use serde::{Deserialize, Serialize};

use crate::state_machine;
use crate::settings;

// Small helper so the colour table below reads like the Python QColor(r,g,b).
const fn rgb(r: u8, g: u8, b: u8) -> Color32 {
    Color32::from_rgb(r, g, b)
}

// ----------------------------------------------------------------------------
//  1) THE PALETTE  — one field per Qt QPalette.ColorRole used in Test_colors.py
// ----------------------------------------------------------------------------
#[derive(Clone, Copy, Deserialize, Serialize, Debug)] // needed so it can be stored in egui's context data
pub struct Palette {
    pub window: Color32,            // Window      — main background / panels
    pub window_text: Color32,       // WindowText  — text on panels
    pub base: Color32,              // Base        — input / list backgrounds
    pub alternate_base: Color32,    // AlternateBase — hover / striped rows
    pub text: Color32,              // Text
    pub placeholder_text: Color32,  // PlaceholderText — dim/secondary text
    pub tooltip_base: Color32,      // ToolTipBase
    pub tooltip_text: Color32,      // ToolTipText
    pub button: Color32,            // Button      — button fill at rest
    pub button_text: Color32,       // ButtonText
    pub highlight: Color32,         // Highlight / Accent — selection + accent
    pub highlighted_text: Color32,  // HighlightedText
    pub link: Color32,              // Link
    pub link_visited: Color32,      // LinkVisited
    pub bright_text: Color32,       // BrightText  — warnings / attention
    pub light: Color32,             // Light  } 3D bevel ramp,
    pub midlight: Color32,          // Midlight} used here for
    pub mid: Color32,               // Mid    } pressed/border
    pub dark: Color32,              // Dark   } shading
    pub shadow: Color32,            // Shadow
}

impl Palette {
    // ---- "Slate Dark"  (Test_colors.py apply_theme, dark branch) ----
    pub fn dark() -> Self {
        Self {
            window:           rgb(15, 23, 42), //
            window_text:      rgb(226, 232, 240), //
            base:             rgb(30, 41, 59), //
            alternate_base:   rgb(51, 65, 85), //
            text:             rgb(226, 232, 240), //
            placeholder_text: rgb(148, 163, 184),
            tooltip_base:     rgb(15, 23, 42), //
            tooltip_text:     rgb(226, 232, 240), //
            button:           rgb(30, 41, 59), //
            button_text:      rgb(226, 232, 240), //
            highlight:        rgb(59, 130, 246), //
            highlighted_text: rgb(255, 255, 255),
            link:             rgb(59, 130, 246), //
            link_visited:     rgb(139, 92, 246), //
            bright_text:      rgb(255, 160, 0), //
            light:            rgb(51, 65, 85), //
            midlight:         rgb(30, 41, 59), //
            mid:              rgb(30, 41, 59), //
            dark:             rgb(2, 6, 23),
            shadow:           rgb(0, 0, 0),
        }
    }

    // ---- "Warm Light"  (Test_colors.py apply_theme, light branch) ----
    pub fn light() -> Self {
        Self {
            window:           rgb(253, 245, 230),
            window_text:      rgb(0, 0, 0),
            base:             rgb(224, 218, 202),
            alternate_base:   rgb(225, 225, 225),
            text:             rgb(0, 0, 0),
            placeholder_text: rgb(120, 120, 120),
            tooltip_base:     rgb(30, 30, 30),
            tooltip_text:     rgb(255, 255, 255),
            button:           rgb(253, 245, 230),
            button_text:      rgb(0, 0, 0),
            highlight:        rgb(0, 120, 215),
            highlighted_text: rgb(255, 255, 255),
            link:             rgb(0, 120, 215),
            link_visited:     rgb(128, 0, 128),
            bright_text:      rgb(220, 38, 38),
            light:            rgb(255, 255, 255),
            midlight:         rgb(240, 240, 240),
            mid:              rgb(200, 200, 200),
            dark:             rgb(160, 160, 160),
            shadow:           rgb(100, 100, 100),
        }
    }

    // ---- "Nord"  (nordtheme.com) ----
    pub fn nord() -> Self {
        Self {
            window:           rgb(46, 52, 64),
            window_text:      rgb(216, 222, 233),
            base:             rgb(59, 66, 82),
            alternate_base:   rgb(67, 76, 94),
            text:             rgb(216, 222, 233),
            placeholder_text: rgb(97, 110, 136),
            tooltip_base:     rgb(46, 52, 64),
            tooltip_text:     rgb(236, 239, 244),
            button:           rgb(59, 66, 82),
            button_text:      rgb(216, 222, 233),
            highlight:        rgb(94, 129, 172),
            highlighted_text: rgb(236, 239, 244),
            link:             rgb(136, 192, 208),
            link_visited:     rgb(180, 142, 173),
            bright_text:      rgb(235, 203, 139),
            light:            rgb(76, 86, 106),
            midlight:         rgb(67, 76, 94),
            mid:              rgb(76, 86, 106),
            dark:             rgb(33, 37, 46),
            shadow:           rgb(20, 23, 28),
        }
    }

    // ---- "Dracula"  (draculatheme.com) ----
    pub fn dracula() -> Self {
        Self {
            window:           rgb(40, 42, 54),
            window_text:      rgb(248, 248, 242),
            base:             rgb(33, 34, 44),
            alternate_base:   rgb(68, 71, 90),
            text:             rgb(248, 248, 242),
            placeholder_text: rgb(98, 114, 164),
            tooltip_base:     rgb(33, 34, 44),
            tooltip_text:     rgb(248, 248, 242),
            button:           rgb(68, 71, 90),
            button_text:      rgb(248, 248, 242),
            highlight:        rgb(189, 147, 249),
            highlighted_text: rgb(40, 42, 54),
            link:             rgb(139, 233, 253),
            link_visited:     rgb(255, 121, 198),
            bright_text:      rgb(255, 184, 108),
            light:            rgb(86, 88, 105),
            midlight:         rgb(68, 71, 90),
            mid:              rgb(98, 114, 164),
            dark:             rgb(25, 26, 33),
            shadow:           rgb(15, 15, 20),
        }
    }

    // ---- "Gruvbox Dark"  (github.com/morhetz/gruvbox) ----
    pub fn gruvbox() -> Self {
        Self {
            window:           rgb(40, 40, 40),
            window_text:      rgb(235, 219, 178),
            base:             rgb(29, 32, 33),
            alternate_base:   rgb(60, 56, 54),
            text:             rgb(235, 219, 178),
            placeholder_text: rgb(146, 131, 116),
            tooltip_base:     rgb(29, 32, 33),
            tooltip_text:     rgb(235, 219, 178),
            button:           rgb(60, 56, 54),
            button_text:      rgb(235, 219, 178),
            highlight:        rgb(250, 189, 47),
            highlighted_text: rgb(40, 40, 40),
            link:             rgb(131, 165, 152),
            link_visited:     rgb(211, 134, 155),
            bright_text:      rgb(254, 128, 25),
            light:            rgb(80, 73, 69),
            midlight:         rgb(60, 56, 54),
            mid:              rgb(102, 92, 84),
            dark:             rgb(29, 32, 33),
            shadow:           rgb(13, 14, 14),
        }
    }

    // ---- "Solarized Dark"  (ethanschoonover.com/solarized) ----
    pub fn solarized_dark() -> Self {
        Self {
            window:           rgb(0, 43, 54),
            window_text:      rgb(131, 148, 150),
            base:             rgb(7, 54, 66),
            alternate_base:   rgb(88, 110, 117),
            text:             rgb(147, 161, 161),
            placeholder_text: rgb(88, 110, 117),
            tooltip_base:     rgb(7, 54, 66),
            tooltip_text:     rgb(147, 161, 161),
            button:           rgb(7, 54, 66),
            button_text:      rgb(131, 148, 150),
            highlight:        rgb(38, 139, 210),
            highlighted_text: rgb(253, 246, 227),
            link:             rgb(42, 161, 152),
            link_visited:     rgb(108, 113, 196),
            bright_text:      rgb(203, 75, 22),
            light:            rgb(88, 110, 117),
            midlight:         rgb(7, 54, 66),
            mid:              rgb(88, 110, 117),
            dark:             rgb(0, 33, 43),
            shadow:           rgb(0, 16, 22),
        }
    }

    // ---- "Solarized Light"  (ethanschoonover.com/solarized) ----
    pub fn solarized_light() -> Self {
        Self {
            window:           rgb(253, 246, 227),
            window_text:      rgb(101, 123, 131),
            base:             rgb(238, 232, 213),
            alternate_base:   rgb(221, 214, 193),
            text:             rgb(88, 110, 117),
            placeholder_text: rgb(147, 161, 161),
            tooltip_base:     rgb(7, 54, 66),
            tooltip_text:     rgb(238, 232, 213),
            button:           rgb(238, 232, 213),
            button_text:      rgb(101, 123, 131),
            highlight:        rgb(38, 139, 210),
            highlighted_text: rgb(253, 246, 227),
            link:             rgb(38, 139, 210),
            link_visited:     rgb(108, 113, 196),
            bright_text:      rgb(220, 50, 47),
            light:            rgb(255, 255, 255),
            midlight:         rgb(238, 232, 213),
            mid:              rgb(147, 161, 161),
            dark:             rgb(207, 201, 180),
            shadow:           rgb(184, 177, 150),
        }
    }

    // ---- "Monokai"  (classic Sublime palette) ----
    pub fn monokai() -> Self {
        Self {
            window:           rgb(39, 40, 34),
            window_text:      rgb(248, 248, 242),
            base:             rgb(30, 31, 28),
            alternate_base:   rgb(73, 72, 62),
            text:             rgb(248, 248, 242),
            placeholder_text: rgb(117, 113, 94),
            tooltip_base:     rgb(30, 31, 28),
            tooltip_text:     rgb(248, 248, 242),
            button:           rgb(73, 72, 62),
            button_text:      rgb(248, 248, 242),
            highlight:        rgb(249, 38, 114),
            highlighted_text: rgb(248, 248, 242),
            link:             rgb(102, 217, 239),
            link_visited:     rgb(174, 129, 255),
            bright_text:      rgb(253, 151, 31),
            light:            rgb(90, 88, 75),
            midlight:         rgb(73, 72, 62),
            mid:              rgb(117, 113, 94),
            dark:             rgb(30, 31, 28),
            shadow:           rgb(18, 19, 16),
        }
    }

    // ---- "One Dark"  (Atom One Dark) ----
    pub fn one_dark() -> Self {
        Self {
            window:           rgb(40, 44, 52),
            window_text:      rgb(171, 178, 191),
            base:             rgb(33, 37, 43),
            alternate_base:   rgb(62, 68, 81),
            text:             rgb(171, 178, 191),
            placeholder_text: rgb(92, 99, 112),
            tooltip_base:     rgb(33, 37, 43),
            tooltip_text:     rgb(171, 178, 191),
            button:           rgb(58, 63, 75),
            button_text:      rgb(171, 178, 191),
            highlight:        rgb(97, 175, 239),
            highlighted_text: rgb(255, 255, 255),
            link:             rgb(86, 182, 194),
            link_visited:     rgb(198, 120, 221),
            bright_text:      rgb(229, 192, 123),
            light:            rgb(75, 82, 99),
            midlight:         rgb(62, 68, 81),
            mid:              rgb(92, 99, 112),
            dark:             rgb(27, 31, 35),
            shadow:           rgb(16, 18, 22),
        }
    }

    // ---- "Catppuccin Mocha"  (github.com/catppuccin) ----
    pub fn catppuccin() -> Self {
        Self {
            window:           rgb(30, 30, 46),
            window_text:      rgb(205, 214, 244),
            base:             rgb(24, 24, 37),
            alternate_base:   rgb(49, 50, 68),
            text:             rgb(205, 214, 244),
            placeholder_text: rgb(108, 112, 134),
            tooltip_base:     rgb(17, 17, 27),
            tooltip_text:     rgb(205, 214, 244),
            button:           rgb(49, 50, 68),
            button_text:      rgb(205, 214, 244),
            highlight:        rgb(203, 166, 247),
            highlighted_text: rgb(17, 17, 27),
            link:             rgb(137, 180, 250),
            link_visited:     rgb(180, 190, 254),
            bright_text:      rgb(250, 179, 135),
            light:            rgb(88, 91, 112),
            midlight:         rgb(69, 71, 90),
            mid:              rgb(69, 71, 90),
            dark:             rgb(17, 17, 27),
            shadow:           rgb(11, 11, 18),
        }
    }
}

// Shape constants (Qt 'Fusion' uses subtle rounding + 1px borders).
const ROUNDING: f32 = 4.0;
const BORDER: f32 = 1.0;

// ----------------------------------------------------------------------------
//  2) ENTRY POINTS
// ----------------------------------------------------------------------------
pub fn style_from(p: Palette) -> Style {
    let mut style = Style::default();
    style.visuals = visuals(&p);
    apply_text_sizes(&mut style);
    apply_spacing(&mut style);
    style
}

// Key under which we stash the active Palette inside egui's context data.
fn palette_id() -> egui::Id {
    egui::Id::new("omniboard_palette")
}

/// Apply a palette AND remember it, so widgets can read the exact Qt roles
/// later via `theme::palette(ui.ctx())`. Call this instead of `set_style`.
///     theme::install(&cc.egui_ctx, Palette::dark());
pub fn install(ctx: &egui::Context, p: Palette) {
    ctx.set_style(style_from(p));
    ctx.data_mut(|d| d.insert_temp(palette_id(), p));
}

/// Fetch the palette installed above. Falls back to dark if none was set.
pub fn palette(ctx: &egui::Context) -> Palette {
    ctx.data(|d| d.get_temp::<Palette>(palette_id()))
        .unwrap_or_else(Palette::dark)
}

pub fn get_palette_str(ctx: &egui::Context, theme_str: &str) {
    let palette = match theme_str {
        "light" => Palette::light(),
        "dark" => Palette::dark(),
        "nord" => Palette::nord(),
        "dracula" => Palette::dracula(),
        "gruvbox" => Palette::gruvbox(),
        "solarized_dark" => Palette::solarized_dark(),
        "solarized_light" => Palette::solarized_light(),
        "monokai" => Palette::monokai(),
        "one_dark" => Palette::one_dark(),
        "catppuccin" => Palette::catppuccin(),
        "custom" => settings::with(|s| s.custom_theme.unwrap_or(Palette::dark())),
        _ => Palette::dark(),
    };
    install(ctx, palette);
}

// ----------------------------------------------------------------------------
//  3) MAP QPalette ROLES -> egui Visuals
//  egui widget states and the Qt role we drive them from:
//     noninteractive -> Window bg + PlaceholderText fg (labels)
//     inactive       -> Button   (button at rest)
//     hovered        -> AlternateBase / Light (a step brighter), Highlight border
//     active         -> Mid (pressed, a step darker), Highlight border
//     open           -> Base
// ----------------------------------------------------------------------------
fn visuals(p: &Palette) -> Visuals {
    let theme = state_machine::with(|sm| sm.get_current_theme()).to_string();
    let mut v = match theme.as_str() {
        "dark" => Visuals::dark(),
        "light" => Visuals::light(),
        "nord" => Visuals::dark(),
        "dracula" => Visuals::dark(),
        "gruvbox" => Visuals::dark(),
        "solarized_dark" => Visuals::dark(),
        "solarized_light" => Visuals::light(),
        "monokai" => Visuals::dark(),
        "one_dark" => Visuals::dark(),
        "catppuccin" => Visuals::dark(),
        _ => Visuals::dark(),
    };
    // Panels / windows / inputs.
    v.panel_fill = p.window;
    v.window_fill = p.window;
    v.extreme_bg_color = p.base; // QLineEdit / text-edit background (Qt 'Base')
    v.faint_bg_color = p.alternate_base; // striped rows
    v.window_rounding = Rounding::same(ROUNDING);
    v.window_stroke = Stroke::new(BORDER, p.dark);

    // Selection + links.
    v.selection.bg_fill = p.highlight.gamma_multiply(0.55);
    v.selection.stroke = Stroke::new(BORDER, p.highlight);
    v.hyperlink_color = p.link;

    // Warnings/errors -> Qt 'BrightText'.
    v.warn_fg_color = p.bright_text;
    v.error_fg_color = p.bright_text;

    let rounding = Rounding::same(ROUNDING);

    // --- noninteractive: labels, separators ---
    v.widgets.noninteractive.bg_fill = p.window;
    v.widgets.noninteractive.weak_bg_fill = p.window;
    v.widgets.noninteractive.bg_stroke = Stroke::new(BORDER, p.mid);
    v.widgets.noninteractive.fg_stroke = Stroke::new(BORDER, p.window_text);
    v.widgets.noninteractive.rounding = rounding;

    // --- inactive: button at rest (Qt 'Button' + 'ButtonText') ---
    v.widgets.inactive.bg_fill = p.button;
    v.widgets.inactive.weak_bg_fill = p.button;
    v.widgets.inactive.bg_stroke = Stroke::new(BORDER, p.mid);
    v.widgets.inactive.fg_stroke = Stroke::new(BORDER, p.button_text);
    v.widgets.inactive.rounding = rounding;
    v.widgets.inactive.expansion = 0.0;

    // --- hovered: one bevel-step brighter (Qt 'AlternateBase'/'Light') ---
    v.widgets.hovered.bg_fill = p.alternate_base;
    v.widgets.hovered.weak_bg_fill = p.alternate_base;
    v.widgets.hovered.bg_stroke = Stroke::new(BORDER, p.highlight);
    v.widgets.hovered.fg_stroke = Stroke::new(BORDER, p.window_text);
    v.widgets.hovered.rounding = rounding;
    v.widgets.hovered.expansion = 1.0;

    // --- active: pressed, one step darker (Qt 'Mid') ---
    v.widgets.active.bg_fill = p.mid;
    v.widgets.active.weak_bg_fill = p.mid;
    v.widgets.active.bg_stroke = Stroke::new(BORDER, p.highlight);
    v.widgets.active.fg_stroke = Stroke::new(BORDER, p.highlighted_text);
    v.widgets.active.rounding = rounding;
    v.widgets.active.expansion = 1.0;

    // --- open: an opened combo box / menu (Qt 'Base') ---
    v.widgets.open.bg_fill = p.base;
    v.widgets.open.weak_bg_fill = p.base;
    v.widgets.open.bg_stroke = Stroke::new(BORDER, p.mid);
    v.widgets.open.fg_stroke = Stroke::new(BORDER, p.text);
    v.widgets.open.rounding = rounding;

    v
}

// ----------------------------------------------------------------------------
//  4) TEXT SIZES  (roughly the px sizes used in the Python stylesheets)
// ----------------------------------------------------------------------------
fn apply_text_sizes(style: &mut Style) {
    use FontFamily::{Monospace, Proportional};
    style.text_styles = [
        (TextStyle::Heading, FontId::new(18.0, Proportional)), // title_label: 18px bold
        (TextStyle::Body, FontId::new(12.0, Proportional)),
        (TextStyle::Button, FontId::new(12.0, Proportional)),
        (TextStyle::Small, FontId::new(11.0, Proportional)), // hex/rgb inputs: 11px
        (TextStyle::Monospace, FontId::new(12.0, Monospace)),
    ]
    .into();
}

// ----------------------------------------------------------------------------
//  5) SPACING
// ----------------------------------------------------------------------------
fn apply_spacing(style: &mut Style) {
    let s = &mut style.spacing;
    s.item_spacing = egui::vec2(8.0, 6.0);
    s.button_padding = egui::vec2(10.0, 6.0);
    s.menu_margin = egui::Margin::same(6.0);
    s.indent = 18.0;
    s.scroll.bar_width = 10.0;
}
