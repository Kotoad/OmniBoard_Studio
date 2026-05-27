// OmniBoard Studio — minimal Rust / egui / wgpu node-graph demo.
//
// Mirrors the core of the real app: draggable "blocks" on a pannable canvas,
// connected by bezier "wires" between output→input ports, with a sidebar that
// adds blocks and generates Python for a Raspberry Pi.
//
// Rendering goes through wgpu: eframe is built with default features off and
// the `wgpu` feature on, and we explicitly request `Renderer::Wgpu` below.
//
//   Left-drag a block            = move it
//   Right-click output port,
//     release on an input port    = create a wire
//   Middle-drag                  = pan the canvas

use eframe::egui;
use egui::{Color32, Pos2, Rect, Stroke, Vec2};

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1000.0, 700.0])
            .with_title("OmniBoard — Rust/egui/wgpu Node Demo"),
        renderer: eframe::Renderer::Glow, // <- render egui through OpenGL (glow)
        ..Default::default()
    };
    eframe::run_native(
        "OmniBoard",
        options,
        Box::new(|cc| {
            // Report the OpenGL renderer glow is using (should be the Intel GPU,
            // not a software rasterizer).
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
    pos: Pos2,
    width: f32,
    height: f32,
}

impl Block {
    fn new(id: usize, kind: &'static str, pos: Pos2) -> Self {
        Self { id, kind, pos, width: 110.0, height: 50.0 }
    }

    fn rect(&self) -> Rect {
        Rect::from_min_size(self.pos, Vec2::new(self.width, self.height))
    }

    fn color(&self) -> Color32 {
        match self.kind {
            "Start" => Color32::from_rgb(106, 174, 139),
            "End"   => Color32::from_rgb(220, 80, 80),
            "Timer" => Color32::from_rgb(122, 155, 201),
            "GPIO"  => Color32::from_rgb(200, 150, 80),
            "Print" => Color32::from_rgb(150, 100, 200),
            _       => Color32::from_rgb(200, 180, 60),
        }
    }

    /// Centre of the right-side output port.
    fn out_port(&self) -> Pos2 {
        let r = self.rect();
        Pos2::new(r.right(), r.center().y)
    }

    /// Centre of the left-side input port.
    fn in_port(&self) -> Pos2 {
        let r = self.rect();
        Pos2::new(r.left(), r.center().y)
    }
}

#[derive(Clone)]
struct Wire {
    from: usize, // block id
    to: usize,
}

// ── App ─────────────────────────────────────────────────────────────────────

struct NodeApp {
    blocks: Vec<Block>,
    wires: Vec<Wire>,
    next_id: usize,
    dragging: Option<usize>,
    drag_offset: Vec2,
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
            Block::new(1, "Timer", Pos2::new(230.0, 200.0)),
            Block::new(2, "GPIO", Pos2::new(400.0, 140.0)),
            Block::new(3, "Print", Pos2::new(400.0, 270.0)),
            Block::new(4, "End", Pos2::new(570.0, 200.0)),
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
            dragging: None,
            drag_offset: Vec2::ZERO,
            wire_from: None,
            log: vec!["Ready — egui on wgpu.".into()],
            canvas_offset: Vec2::ZERO,
            panning: false,
            pan_start: Pos2::ZERO,
        }
    }

    fn block_at(&self, pos: Pos2) -> Option<usize> {
        let p = pos - self.canvas_offset;
        self.blocks.iter().rev().find(|b| b.rect().contains(p)).map(|b| b.id)
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
                "Timer" => { lines.push("    time.sleep(1)".into()); any = true; }
                "GPIO"  => { lines.push("    GPIO.output(18, True)".into()); any = true; }
                "Print" => { lines.push("    print('Hello from Omniboard')".into()); any = true; }
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
                    let pos = Pos2::new(100.0 + (id as f32 * 20.0), 100.0);
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
                .max_height(220.0)
                .stick_to_bottom(true)
                .show(ui, |ui| {
                    for entry in &self.log {
                        ui.label(egui::RichText::new(entry).monospace().size(11.0));
                    }
                });

            ui.separator();
            ui.small("LMB drag = move block");
            ui.small("RMB on port = start wire");
            ui.small("MMB drag = pan canvas");
        });

        // ── Canvas ───────────────────────────────────────────────────────────
        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(Color32::from_rgb(15, 22, 33)))
            .show(ctx, |ui| {
                let canvas_rect = ui.max_rect();
                let _response = ui.allocate_rect(canvas_rect, egui::Sense::click_and_drag());

                let pointer = ctx.input(|i| i.pointer.hover_pos());
                let lmb_down = ctx.input(|i| i.pointer.primary_down());
                let rmb_pressed = ctx.input(|i| i.pointer.secondary_pressed());
                let rmb_released = ctx.input(|i| i.pointer.secondary_released());
                let mmb = ctx.input(|i| i.pointer.middle_down());

                // Pan with middle mouse button.
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

                if let Some(pos) = pointer {
                    // Begin / continue dragging a block.
                    if lmb_down && self.dragging.is_none() {
                        if let Some(id) = self.block_at(pos) {
                            let block_pos = self.blocks[id].pos;
                            self.dragging = Some(id);
                            self.drag_offset = block_pos - (pos - self.canvas_offset);
                        }
                    }
                    if !lmb_down {
                        self.dragging = None;
                    }
                    if let Some(id) = self.dragging {
                        self.blocks[id].pos = pos - self.canvas_offset + self.drag_offset;
                        ctx.request_repaint();
                    }

                    // Wire creation: press near an output port, release on an input port.
                    if rmb_pressed {
                        for b in &self.blocks {
                            let port = b.out_port() + self.canvas_offset;
                            if pos.distance(port) < 14.0 {
                                self.wire_from = Some(b.id);
                                break;
                            }
                        }
                    }
                    if rmb_released {
                        if let Some(from) = self.wire_from {
                            for b in &self.blocks {
                                let port = b.in_port() + self.canvas_offset;
                                if pos.distance(port) < 14.0 && b.id != from {
                                    let dup = self.wires.iter().any(|w| w.from == from && w.to == b.id);
                                    if !dup {
                                        self.wires.push(Wire { from, to: b.id });
                                        self.log.push(format!("Wire: {from} -> {}", b.id));
                                    }
                                    break;
                                }
                            }
                            self.wire_from = None;
                        }
                    }
                }

                let painter = ui.painter_at(canvas_rect);

                // ── Grid ────────────────────────────────────────────────────
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

                // ── Wires ───────────────────────────────────────────────────
                for wire in &self.wires {
                    if let (Some(from_b), Some(to_b)) = (
                        self.blocks.iter().find(|b| b.id == wire.from),
                        self.blocks.iter().find(|b| b.id == wire.to),
                    ) {
                        let p0 = from_b.out_port() + self.canvas_offset;
                        let p1 = to_b.in_port() + self.canvas_offset;
                        let ctrl = ((p1.x - p0.x) * 0.5).max(40.0);
                        let c0 = Pos2::new(p0.x + ctrl, p0.y);
                        let c1 = Pos2::new(p1.x - ctrl, p1.y);
                        // Cubic bezier as a 16-segment polyline.
                        let pts: Vec<Pos2> = (0..=16)
                            .map(|i| {
                                let t = i as f32 / 16.0;
                                let a = p0.lerp(c0, t);
                                let b = c0.lerp(c1, t);
                                let c = c1.lerp(p1, t);
                                let ab = a.lerp(b, t);
                                let bc = b.lerp(c, t);
                                ab.lerp(bc, t)
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

                // Live wire being dragged.
                if let (Some(from_id), Some(pos)) = (self.wire_from, pointer) {
                    if let Some(b) = self.blocks.iter().find(|b| b.id == from_id) {
                        let p0 = b.out_port() + self.canvas_offset;
                        painter.line_segment([p0, pos], Stroke::new(2.0, Color32::from_rgb(255, 200, 60)));
                    }
                }

                // ── Blocks ──────────────────────────────────────────────────
                for block in &self.blocks {
                    let rect = block.rect().translate(self.canvas_offset);
                    let shadow = rect.translate(Vec2::new(3.0, 4.0));
                    painter.rect_filled(shadow, 4.0, Color32::from_rgba_unmultiplied(0, 0, 0, 100));
                    painter.rect_filled(rect, 4.0, block.color());
                    painter.rect_stroke(rect, 4.0, Stroke::new(2.0, Color32::from_rgba_unmultiplied(255, 255, 255, 80)));

                    painter.text(
                        rect.center(),
                        egui::Align2::CENTER_CENTER,
                        block.kind,
                        egui::FontId::proportional(13.0),
                        Color32::WHITE,
                    );

                    let op = block.out_port() + self.canvas_offset;
                    painter.circle_filled(op, 6.0, Color32::WHITE);
                    painter.circle_stroke(op, 6.0, Stroke::new(1.5, Color32::BLACK));

                    let ip = block.in_port() + self.canvas_offset;
                    painter.circle_filled(ip, 6.0, Color32::from_rgb(180, 220, 200));
                    painter.circle_stroke(ip, 6.0, Stroke::new(1.5, Color32::BLACK));
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
