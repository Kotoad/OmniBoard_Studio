// Hide the console window in release builds (keep it in debug for logging).
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// OmniBoard Studio — minimal Rust / egui / wgpu node-graph demo.
//
// Draggable "blocks" on a pannable canvas, connected by bezier "wires" between
// output→input ports, with a sidebar that adds blocks and generates Python.
//
// Unlike a pure painter-drawn canvas, each block here is a real `egui::Area`
// hosting *interactive* widgets — text inputs, numeric selectors, combo boxes
// and checkboxes. The painter is only used for the non-interactive scenery
// (grid, wires, ports).
//
//   Drag a block's title bar         = move it
//   Type / click inside a block      = edit its widgets
//   Right-click output port,
//     release on an input port        = create a wire
//   Middle-drag                      = pan the canvas

use eframe::egui;
use egui::{Color32, Pos2, Rect, Stroke, Vec2};

/// GPIO pins offered by the combo box on a GPIO block.
const GPIO_PINS: [u8; 6] = [17, 18, 22, 23, 24, 27];

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1000.0, 700.0])
            .with_title("OmniBoard — Rust/egui/wgpu Node Demo"),
        renderer: eframe::Renderer::Glow, // render egui through OpenGL (glow)
        ..Default::default()
    };
    eframe::run_native(
        "OmniBoard",
        options,
        Box::new(|cc| {
            if let Some(gl) = &cc.gl {
                use eframe::glow::HasContext as _;
                let renderer = unsafe { gl.get_parameter_string(eframe::glow::RENDERER) };
                eprintln!("OpenGL renderer: {renderer}");
            }
            Box::new(NodeApp::new())
        }),
    )
}

// ── Data ────────────────────────────────────────────────────────────────────

#[derive(Clone)]
struct Block {
    id: usize,
    kind: &'static str,
    pos: Pos2, // canvas-space top-left (pan offset added at draw time)

    // ── per-block interactive widget state ──
    text: String,    // Print: the message
    seconds: i32,    // Timer: delay
    pin_idx: usize,  // GPIO: index into GPIO_PINS
    high: bool,      // GPIO: drive high / low

    // Last on-screen rect (filled in each frame after the Area lays out).
    // Used to anchor wires and ports. Starts as an estimate.
    screen_rect: Rect,
}

impl Block {
    fn new(id: usize, kind: &'static str, pos: Pos2) -> Self {
        Self {
            id,
            kind,
            pos,
            text: "Hello from OmniBoard".to_string(),
            seconds: 1,
            pin_idx: 1, // pin 18
            high: true,
            screen_rect: Rect::from_min_size(pos, Vec2::new(170.0, 80.0)),
        }
    }

    fn header_color(&self) -> Color32 {
        match self.kind {
            "Start" => Color32::from_rgb(106, 174, 139),
            "End" => Color32::from_rgb(220, 80, 80),
            "Timer" => Color32::from_rgb(122, 155, 201),
            "GPIO" => Color32::from_rgb(200, 150, 80),
            "Print" => Color32::from_rgb(150, 100, 200),
            _ => Color32::from_rgb(200, 180, 60),
        }
    }

    /// Centre of the right-side output port (screen coords).
    fn out_port(&self) -> Pos2 {
        Pos2::new(self.screen_rect.right(), self.screen_rect.center().y)
    }

    /// Centre of the left-side input port (screen coords).
    fn in_port(&self) -> Pos2 {
        Pos2::new(self.screen_rect.left(), self.screen_rect.center().y)
    }
}

#[derive(Clone)]
struct Wire {
    from: usize,
    to: usize,
}

// ── App ─────────────────────────────────────────────────────────────────────

struct NodeApp {
    blocks: Vec<Block>,
    wires: Vec<Wire>,
    next_id: usize,
    wire_from: Option<usize>,
    log: Vec<String>,
    canvas_offset: Vec2,
    panning: bool,
    pan_start: Pos2,
}

impl NodeApp {
    fn new() -> Self {
        let blocks = vec![
            Block::new(0, "Start", Pos2::new(60.0, 200.0)),
            Block::new(1, "Timer", Pos2::new(260.0, 200.0)),
            Block::new(2, "GPIO", Pos2::new(470.0, 120.0)),
            Block::new(3, "Print", Pos2::new(470.0, 320.0)),
            Block::new(4, "End", Pos2::new(700.0, 220.0)),
        ];
        let wires = vec![
            Wire { from: 0, to: 1 },
            Wire { from: 1, to: 2 },
            Wire { from: 1, to: 3 },
            Wire { from: 2, to: 4 },
            Wire { from: 3, to: 4 },
        ];
        Self {
            blocks,
            wires,
            next_id: 5,
            wire_from: None,
            log: vec!["Ready — interactive widgets on egui/glow.".into()],
            canvas_offset: Vec2::ZERO,
            panning: false,
            pan_start: Pos2::ZERO,
        }
    }

    fn generate_code(&self) -> String {
        let mut lines = vec![
            "import time".to_string(),
            "import RPi.GPIO as GPIO".to_string(),
            "".to_string(),
            "def main():".to_string(),
        ];
        let mut any = false;
        for b in &self.blocks {
            match b.kind {
                "Timer" => {
                    lines.push(format!("    time.sleep({})", b.seconds));
                    any = true;
                }
                "GPIO" => {
                    lines.push(format!(
                        "    GPIO.output({}, {})",
                        GPIO_PINS[b.pin_idx],
                        if b.high { "True" } else { "False" }
                    ));
                    any = true;
                }
                "Print" => {
                    lines.push(format!("    print({:?})", b.text));
                    any = true;
                }
                _ => {}
            }
        }
        if !any {
            lines.push("    pass".into());
        }
        lines.push("".into());
        lines.push("main()".into());
        lines.join("\n")
    }
}

impl eframe::App for NodeApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // ── Sidebar ──────────────────────────────────────────────────────────
        egui::SidePanel::left("sidebar").exact_width(180.0).show(ctx, |ui| {
            ui.add_space(10.0);
            ui.heading("Blocks");
            ui.separator();

            let kinds: &[&'static str] = &["Start", "Timer", "GPIO", "Print", "End"];
            for kind in kinds {
                if ui.button(format!("+ {kind}")).clicked() {
                    let id = self.next_id;
                    self.next_id += 1;
                    let pos = Pos2::new(120.0 + (id as f32 * 18.0), 120.0);
                    self.blocks.push(Block::new(id, kind, pos));
                    self.log.push(format!("Added {kind} block (id={id})"));
                }
            }

            ui.separator();
            ui.heading("Actions");
            if ui.button("Clear all").clicked() {
                self.blocks.clear();
                self.wires.clear();
                self.next_id = 0;
                self.log.push("Canvas cleared.".into());
            }
            if ui.button("Generate Code").clicked() {
                let code = self.generate_code();
                self.log.push("-- Generated --".into());
                for line in code.lines() {
                    self.log.push(line.to_string());
                }
            }

            ui.separator();
            ui.heading("Log");
            egui::ScrollArea::vertical()
                .max_height(200.0)
                .stick_to_bottom(true)
                .show(ui, |ui| {
                    for entry in &self.log {
                        ui.label(egui::RichText::new(entry).monospace().size(11.0));
                    }
                });

            ui.separator();
            ui.small("Drag title bar = move block");
            ui.small("Click inside   = edit widgets");
            ui.small("RMB on port    = start wire");
            ui.small("MMB drag       = pan canvas");
        });

        // ── Canvas ───────────────────────────────────────────────────────────
        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(Color32::from_rgb(15, 22, 33)))
            .show(ctx, |ui| {
                let canvas_rect = ui.max_rect();
                let _bg = ui.allocate_rect(canvas_rect, egui::Sense::click_and_drag());

                let pointer = ctx.input(|i| i.pointer.hover_pos());
                let rmb_pressed = ctx.input(|i| i.pointer.secondary_pressed());
                let rmb_released = ctx.input(|i| i.pointer.secondary_released());
                let mmb = ctx.input(|i| i.pointer.middle_down());

                // ── Pan with middle mouse button ─────────────────────────────
                if mmb {
                    if let Some(p) = pointer {
                        if !self.panning {
                            self.panning = true;
                            self.pan_start = p;
                        } else {
                            self.canvas_offset += p - self.pan_start;
                            self.pan_start = p;
                        }
                    }
                } else {
                    self.panning = false;
                }

                // ── Grid (background painter) ────────────────────────────────
                let painter = ui.painter_at(canvas_rect);
                let grid_color = Color32::from_rgba_unmultiplied(255, 255, 255, 12);
                let step = 32.0;
                let ox = self.canvas_offset.x.rem_euclid(step);
                let oy = self.canvas_offset.y.rem_euclid(step);
                let mut x = canvas_rect.left() + ox;
                while x < canvas_rect.right() {
                    painter.line_segment(
                        [Pos2::new(x, canvas_rect.top()), Pos2::new(x, canvas_rect.bottom())],
                        Stroke::new(1.0, grid_color),
                    );
                    x += step;
                }
                let mut y = canvas_rect.top() + oy;
                while y < canvas_rect.bottom() {
                    painter.line_segment(
                        [Pos2::new(canvas_rect.left(), y), Pos2::new(canvas_rect.right(), y)],
                        Stroke::new(1.0, grid_color),
                    );
                    y += step;
                }

                // ── Blocks as interactive Areas ──────────────────────────────
                // Each block is its own Area, pinned to its (panned) position.
                // We drive the position ourselves via the title-bar drag, so
                // panning and dragging both stay under our control.
                for i in 0..self.blocks.len() {
                    let screen_pos = self.blocks[i].pos + self.canvas_offset;
                    let area_id = egui::Id::new(("block", self.blocks[i].id));
                    let header_color = self.blocks[i].header_color();
                    let block = &mut self.blocks[i];

                    let area = egui::Area::new(area_id)
                        .fixed_pos(screen_pos)
                        .constrain_to(canvas_rect) // keep blocks off the sidebar
                        .order(egui::Order::Middle)
                        .show(ctx, |ui| {
                            egui::Frame::none()
                                .fill(Color32::from_rgb(35, 44, 58))
                                .rounding(6.0)
                                .stroke(Stroke::new(1.0, Color32::from_white_alpha(40)))
                                .inner_margin(egui::Margin::same(0.0))
                                .show(ui, |ui| {
                                    ui.set_width(170.0);

                                    // ── Title bar = drag handle ──────────────
                                    let title = egui::Frame::none()
                                        .fill(header_color)
                                        .rounding(egui::Rounding {
                                            nw: 6.0,
                                            ne: 6.0,
                                            sw: 0.0,
                                            se: 0.0,
                                        })
                                        .inner_margin(egui::Margin::symmetric(8.0, 5.0))
                                        .show(ui, |ui| {
                                            ui.set_width(170.0 - 16.0);
                                            ui.add(
                                                egui::Label::new(
                                                    egui::RichText::new(block.kind)
                                                        .strong()
                                                        .color(Color32::WHITE),
                                                )
                                                .selectable(false),
                                            );
                                        });
                                    let drag = ui.interact(
                                        title.response.rect,
                                        area_id.with("drag"),
                                        egui::Sense::drag(),
                                    );
                                    if drag.dragged() {
                                        block.pos += drag.drag_delta();
                                    }
                                    if drag.hovered() {
                                        ui.ctx().set_cursor_icon(egui::CursorIcon::Grab);
                                    }

                                    // ── Body: interactive widgets per kind ───
                                    egui::Frame::none()
                                        .inner_margin(egui::Margin::same(8.0))
                                        .show(ui, |ui| {
                                            ui.set_width(170.0 - 16.0);
                                            match block.kind {
                                                "Print" => {
                                                    ui.label("Message:");
                                                    ui.text_edit_singleline(&mut block.text);
                                                }
                                                "Timer" => {
                                                    ui.horizontal(|ui| {
                                                        ui.label("Wait:");
                                                        ui.add(
                                                            egui::DragValue::new(&mut block.seconds)
                                                                .clamp_range(0..=60)
                                                                .suffix(" s"),
                                                        );
                                                    });
                                                }
                                                "GPIO" => {
                                                    egui::ComboBox::from_id_source(
                                                        area_id.with("pin"),
                                                    )
                                                    .selected_text(format!(
                                                        "Pin {}",
                                                        GPIO_PINS[block.pin_idx]
                                                    ))
                                                    .show_ui(ui, |ui| {
                                                        for (idx, pin) in
                                                            GPIO_PINS.iter().enumerate()
                                                        {
                                                            ui.selectable_value(
                                                                &mut block.pin_idx,
                                                                idx,
                                                                format!("Pin {pin}"),
                                                            );
                                                        }
                                                    });
                                                    ui.checkbox(&mut block.high, "Drive HIGH");
                                                }
                                                "Start" => {
                                                    ui.label(
                                                        egui::RichText::new("entry point")
                                                            .italics()
                                                            .weak(),
                                                    );
                                                }
                                                "End" => {
                                                    ui.label(
                                                        egui::RichText::new("stop")
                                                            .italics()
                                                            .weak(),
                                                    );
                                                }
                                                _ => {}
                                            }
                                        });
                                });
                        });

                    // Record the on-screen rect for wire/port anchoring.
                    self.blocks[i].screen_rect = area.response.rect;
                }

                // ── Wire creation (right-click drag between ports) ───────────
                if let Some(pos) = pointer {
                    if rmb_pressed {
                        for b in &self.blocks {
                            if pos.distance(b.out_port()) < 14.0 {
                                self.wire_from = Some(b.id);
                                break;
                            }
                        }
                    }
                    if rmb_released {
                        if let Some(from) = self.wire_from.take() {
                            for b in &self.blocks {
                                if pos.distance(b.in_port()) < 14.0 && b.id != from {
                                    let dup =
                                        self.wires.iter().any(|w| w.from == from && w.to == b.id);
                                    if !dup {
                                        self.wires.push(Wire { from, to: b.id });
                                        self.log.push(format!("Wire: {from} -> {}", b.id));
                                    }
                                    break;
                                }
                            }
                        }
                    }
                }

                // ── Wires (background painter, drawn behind the block Areas) ──
                for wire in &self.wires {
                    if let (Some(from_b), Some(to_b)) = (
                        self.blocks.iter().find(|b| b.id == wire.from),
                        self.blocks.iter().find(|b| b.id == wire.to),
                    ) {
                        let p0 = from_b.out_port();
                        let p1 = to_b.in_port();
                        let ctrl = ((p1.x - p0.x) * 0.5).max(40.0);
                        let c0 = Pos2::new(p0.x + ctrl, p0.y);
                        let c1 = Pos2::new(p1.x - ctrl, p1.y);
                        let pts: Vec<Pos2> = (0..=16)
                            .map(|i| {
                                let t = i as f32 / 16.0;
                                let a = p0.lerp(c0, t);
                                let b = c0.lerp(c1, t);
                                let c = c1.lerp(p1, t);
                                a.lerp(b, t).lerp(b.lerp(c, t), t)
                            })
                            .collect();
                        for seg in pts.windows(2) {
                            painter.line_segment(
                                [seg[0], seg[1]],
                                Stroke::new(2.5, Color32::from_rgb(80, 200, 160)),
                            );
                        }
                    }
                }

                // ── Ports + live wire (foreground, so they sit on top) ───────
                let top = ctx.layer_painter(egui::LayerId::new(
                    egui::Order::Foreground,
                    egui::Id::new("ports"),
                ));
                for b in &self.blocks {
                    let op = b.out_port();
                    top.circle_filled(op, 6.0, Color32::WHITE);
                    top.circle_stroke(op, 6.0, Stroke::new(1.5, Color32::BLACK));
                    let ip = b.in_port();
                    top.circle_filled(ip, 6.0, Color32::from_rgb(180, 220, 200));
                    top.circle_stroke(ip, 6.0, Stroke::new(1.5, Color32::BLACK));
                }
                if let (Some(from_id), Some(pos)) = (self.wire_from, pointer) {
                    if let Some(b) = self.blocks.iter().find(|b| b.id == from_id) {
                        top.line_segment(
                            [b.out_port(), pos],
                            Stroke::new(2.0, Color32::from_rgb(255, 200, 60)),
                        );
                    }
                }

                // ── HUD ──────────────────────────────────────────────────────
                painter.text(
                    canvas_rect.right_bottom() - Vec2::new(10.0, 10.0),
                    egui::Align2::RIGHT_BOTTOM,
                    format!("blocks={} wires={}", self.blocks.len(), self.wires.len()),
                    egui::FontId::monospace(11.0),
                    Color32::from_rgba_unmultiplied(255, 255, 255, 60),
                );
            });
    }
}
