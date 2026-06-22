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

// Small helper so the colour table below reads like the Python QColor(r,g,b).
const fn rgb(r: u8, g: u8, b: u8) -> Color32 {
    Color32::from_rgb(r, g, b)
}

// ----------------------------------------------------------------------------
//  1) THE PALETTE  — one field per Qt QPalette.ColorRole used in Test_colors.py
// ----------------------------------------------------------------------------
#[derive(Clone, Copy)] // needed so it can be stored in egui's context data
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

    /// True if this is a dark theme — used to pick egui's base Visuals.
    fn is_dark(&self) -> bool {
        // crude luminance check on the window colour
        let c = self.window;
        (c.r() as u32 + c.g() as u32 + c.b() as u32) < 384
    }
}

// Shape constants (Qt 'Fusion' uses subtle rounding + 1px borders).
const ROUNDING: f32 = 4.0;
const BORDER: f32 = 1.0;

// ----------------------------------------------------------------------------
//  2) ENTRY POINTS
// ----------------------------------------------------------------------------
pub fn style() -> Style {
    style_from(Palette::dark())
}

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
    let mut v = if p.is_dark() {
        Visuals::dark()
    } else {
        Visuals::light()
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
