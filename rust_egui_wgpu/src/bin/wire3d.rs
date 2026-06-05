// Hide the console window in release builds (keep it in debug for logging).
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// OmniBoard Studio — 3D Wiring System showcase (Rust / egui).
//
// A port of `wire3d.py` (PyQt6 + OpenGL) to the egui/glow stack used by the
// sibling 2D demo in `main.rs`. Instead of a GPU pipeline (this machine is an
// Intel HD 4000 with no working Vulkan/wgpu path) the whole scene is rendered
// with egui's 2D `Painter`: a hand-rolled orbit camera projects 3D world points
// to the screen with perspective, and depth is resolved with painter's-algorithm
// sorting (far drawn first). No GLSL, no `unsafe`, no extra dependencies.
//
//   Left-drag    = orbit camera
//   Middle-drag  = pan camera
//   Scroll       = zoom in / out
//   Left-click   = select a node (turns cyan)
//   A            = add a random node
//   W            = connect the last two selected nodes
//   Delete       = remove selected node(s) and their wires
//   R            = reset camera
//   Esc          = quit

use eframe::egui;
use egui::{Align2, Color32, FontId, Pos2, Rect, Stroke, Vec2};
use std::ops::{Add, Mul, Sub};

// ── Minimal 3D vector math ────────────────────────────────────────────────────

#[derive(Clone, Copy, Debug)]
struct Vec3 {
    x: f32,
    y: f32,
    z: f32,
}

impl Vec3 {
    const fn new(x: f32, y: f32, z: f32) -> Self {
        Self { x, y, z }
    }
    fn dot(self, o: Vec3) -> f32 {
        self.x * o.x + self.y * o.y + self.z * o.z
    }
    fn cross(self, o: Vec3) -> Vec3 {
        Vec3::new(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )
    }
    fn length(self) -> f32 {
        self.dot(self).sqrt()
    }
    fn normalized(self) -> Vec3 {
        let len = self.length();
        if len < 1e-8 {
            self
        } else {
            self * (1.0 / len)
        }
    }
    fn lerp(self, o: Vec3, t: f32) -> Vec3 {
        self * (1.0 - t) + o * t
    }
}

impl Add for Vec3 {
    type Output = Vec3;
    fn add(self, o: Vec3) -> Vec3 {
        Vec3::new(self.x + o.x, self.y + o.y, self.z + o.z)
    }
}
impl Sub for Vec3 {
    type Output = Vec3;
    fn sub(self, o: Vec3) -> Vec3 {
        Vec3::new(self.x - o.x, self.y - o.y, self.z - o.z)
    }
}
impl Mul<f32> for Vec3 {
    type Output = Vec3;
    fn mul(self, s: f32) -> Vec3 {
        Vec3::new(self.x * s, self.y * s, self.z * s)
    }
}

// ── Orbit camera ──────────────────────────────────────────────────────────────

/// A point successfully projected from world space onto the screen.
struct Projected {
    pos: Pos2,
    depth: f32,        // camera-space forward distance (sort key; bigger = farther)
    radius_factor: f32, // multiply a world radius by this to get a screen radius
}

/// Spherical orbit camera (mirrors `OrbitCamera` in wire3d.py).
struct OrbitCamera {
    yaw: f32,   // degrees
    pitch: f32, // degrees, clamped to ±88
    distance: f32,
    target: Vec3,
    fov_deg: f32,
}

impl OrbitCamera {
    const NEAR: f32 = 0.05;

    fn new() -> Self {
        Self {
            yaw: -35.0,
            pitch: 30.0,
            distance: 14.0,
            target: Vec3::new(0.0, 0.0, 0.0),
            fov_deg: 45.0,
        }
    }

    fn reset(&mut self) {
        *self = OrbitCamera::new();
    }

    /// Eye position in world space from spherical coordinates.
    fn eye(&self) -> Vec3 {
        let yr = self.yaw.to_radians();
        let pr = self.pitch.to_radians();
        self.target
            + Vec3::new(
                pr.cos() * yr.sin(),
                pr.sin(),
                pr.cos() * yr.cos(),
            ) * self.distance
    }

    /// Orthonormal camera basis: (right, up, forward).
    fn basis(&self) -> (Vec3, Vec3, Vec3) {
        let forward = (self.target - self.eye()).normalized();
        let world_up = Vec3::new(0.0, 1.0, 0.0);
        let mut right = forward.cross(world_up);
        if right.length() < 1e-6 {
            right = Vec3::new(1.0, 0.0, 0.0);
        }
        let right = right.normalized();
        let up = right.cross(forward);
        (right, up, forward)
    }

    /// Project a world point to screen space, or `None` if it is behind the
    /// near plane.
    fn project(&self, p: Vec3, rect: Rect) -> Option<Projected> {
        let eye = self.eye();
        let (right, up, forward) = self.basis();
        let rel = p - eye;
        let cz = rel.dot(forward);
        if cz <= Self::NEAR {
            return None;
        }
        let cx = rel.dot(right);
        let cy = rel.dot(up);
        let focal = (rect.height() * 0.5) / (self.fov_deg.to_radians() * 0.5).tan();
        let center = rect.center();
        let pos = Pos2::new(
            center.x + cx / cz * focal,
            center.y - cy / cz * focal,
        );
        Some(Projected {
            pos,
            depth: cz,
            radius_factor: focal / cz,
        })
    }

    fn orbit(&mut self, dx: f32, dy: f32) {
        self.yaw += dx * 0.45;
        self.pitch = (self.pitch + dy * 0.45).clamp(-88.0, 88.0);
    }

    fn pan(&mut self, dx: f32, dy: f32) {
        let (right, up, _) = self.basis();
        let speed = self.distance * 0.0025;
        self.target = self.target - (right * dx - up * dy) * speed;
    }

    fn zoom(&mut self, scroll_y: f32) {
        if scroll_y == 0.0 {
            return;
        }
        let factor = if scroll_y > 0.0 { 0.9 } else { 1.0 / 0.9 };
        self.distance = (self.distance * factor).clamp(0.5, 300.0);
    }
}

// ── Data model ────────────────────────────────────────────────────────────────

struct Node {
    id: usize,
    pos: Vec3,
    color: Color32,
    radius: f32,
    label: String,
    selected: bool,
}

struct Wire {
    from: usize,
    to: usize,
    color: Color32,
    thickness: f32,
    selected: bool,
}

struct Scene {
    nodes: Vec<Node>,
    wires: Vec<Wire>,
    next_id: usize,
}

impl Scene {
    fn new() -> Self {
        Self {
            nodes: Vec::new(),
            wires: Vec::new(),
            next_id: 0,
        }
    }

    fn demo() -> Self {
        let mut s = Scene::new();
        // Hardware nodes (same layout/colors as wire3d.py's _build_demo_scene).
        let rpi = s.add_node(Vec3::new(0.0, 0.0, 0.0), Color32::from_rgb(51, 153, 255), "Raspberry Pi 4");
        let ard = s.add_node(Vec3::new(4.5, 0.0, 2.0), Color32::from_rgb(51, 217, 89), "Arduino Uno");
        let sen1 = s.add_node(Vec3::new(-3.5, 0.0, 2.5), Color32::from_rgb(255, 153, 38), "Temp Sensor");
        let sen2 = s.add_node(Vec3::new(2.0, 0.0, -4.0), Color32::from_rgb(230, 77, 77), "Motor Driver");
        let hub = s.add_node(Vec3::new(-1.5, 0.0, -3.0), Color32::from_rgb(191, 102, 255), "USB Hub");
        let pwr = s.add_node(Vec3::new(5.5, 0.0, -2.0), Color32::from_rgb(255, 217, 26), "Power Supply");
        let led = s.add_node(Vec3::new(-5.0, 0.0, -1.5), Color32::from_rgb(242, 242, 242), "LED Strip");

        s.add_wire(rpi, ard, Color32::from_rgb(242, 140, 13));
        s.add_wire(rpi, sen1, Color32::from_rgb(51, 230, 102));
        s.add_wire(rpi, sen2, Color32::from_rgb(230, 51, 64));
        s.add_wire(rpi, hub, Color32::from_rgb(102, 179, 255));
        s.add_wire(ard, pwr, Color32::from_rgb(255, 230, 26));
        s.add_wire(ard, sen2, Color32::from_rgb(230, 128, 26));
        s.add_wire(hub, led, Color32::from_rgb(217, 64, 255));
        s.add_wire(pwr, sen2, Color32::from_rgb(255, 102, 102));
        s
    }

    fn add_node(&mut self, pos: Vec3, color: Color32, label: &str) -> usize {
        let id = self.next_id;
        self.next_id += 1;
        self.nodes.push(Node {
            id,
            pos,
            color,
            radius: 0.4,
            label: label.to_string(),
            selected: false,
        });
        id
    }

    fn remove_node(&mut self, id: usize) {
        self.nodes.retain(|n| n.id != id);
        self.wires.retain(|w| w.from != id && w.to != id);
    }

    /// Add a wire; rejects self-loops and duplicates. Returns true on success.
    fn add_wire(&mut self, from: usize, to: usize, color: Color32) -> bool {
        if from == to {
            return false;
        }
        if !self.nodes.iter().any(|n| n.id == from) || !self.nodes.iter().any(|n| n.id == to) {
            return false;
        }
        let exists = self
            .wires
            .iter()
            .any(|w| (w.from == from && w.to == to) || (w.from == to && w.to == from));
        if exists {
            return false;
        }
        self.wires.push(Wire {
            from,
            to,
            color,
            thickness: 0.06,
            selected: false,
        });
        true
    }

    fn deselect_all(&mut self) {
        for n in &mut self.nodes {
            n.selected = false;
        }
        for w in &mut self.wires {
            w.selected = false;
        }
    }

    fn node(&self, id: usize) -> Option<&Node> {
        self.nodes.iter().find(|n| n.id == id)
    }
}

// ── Geometry helpers ──────────────────────────────────────────────────────────

/// Two inner control points for a cubic Bézier wire that droops downward
/// (−Y) proportional to its length, like a hanging cable.
fn wire_control_points(src: Vec3, dst: Vec3) -> [Vec3; 4] {
    let mid = (src + dst) * 0.5;
    let span = (dst - src).length();
    let sag = Vec3::new(0.0, -span * 0.30, 0.0);
    [src, mid + sag, mid + sag, dst]
}

/// Sample `n + 1` points along a cubic Bézier curve.
fn bezier_cubic(p: [Vec3; 4], n: usize) -> Vec<Vec3> {
    (0..=n)
        .map(|i| {
            let t = i as f32 / n as f32;
            // de Casteljau
            let a = p[0].lerp(p[1], t);
            let b = p[1].lerp(p[2], t);
            let c = p[2].lerp(p[3], t);
            let ab = a.lerp(b, t);
            let bc = b.lerp(c, t);
            ab.lerp(bc, t)
        })
        .collect()
}

/// A flat XZ reference grid as world-space line segments.
fn build_grid(half: i32) -> Vec<(Vec3, Vec3)> {
    let mut segs = Vec::new();
    let h = half as f32;
    for i in -half..=half {
        let f = i as f32;
        segs.push((Vec3::new(f, 0.0, -h), Vec3::new(f, 0.0, h)));
        segs.push((Vec3::new(-h, 0.0, f), Vec3::new(h, 0.0, f)));
    }
    segs
}

/// Blend a color toward another by `t` in [0, 1].
fn blend(a: Color32, b: Color32, t: f32) -> Color32 {
    let l = |x: u8, y: u8| (x as f32 * (1.0 - t) + y as f32 * t).round() as u8;
    Color32::from_rgb(l(a.r(), b.r()), l(a.g(), b.g()), l(a.b(), b.b()))
}

// ── App ───────────────────────────────────────────────────────────────────────

/// Something to paint this frame, tagged with a representative depth so the
/// whole scene can be composited back-to-front (painter's algorithm).
enum Drawable {
    Node(usize),
    Wire(usize),
}

struct WireApp {
    scene: Scene,
    camera: OrbitCamera,
    last_selected: Vec<usize>, // node ids, most recent last (kept to length 2)
    info: String,
    rng: u32,
}

impl WireApp {
    fn new() -> Self {
        Self {
            scene: Scene::demo(),
            camera: OrbitCamera::new(),
            last_selected: Vec::new(),
            info: String::new(),
            rng: 0x9E37_79B9,
        }
    }

    /// Tiny xorshift-ish PRNG so we don't pull in the `rand` crate.
    fn rand_f32(&mut self) -> f32 {
        self.rng = self.rng.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
        (self.rng >> 8) as f32 / 16_777_216.0
    }

    fn add_random_node(&mut self) {
        let x = self.rand_f32() * 12.0 - 6.0;
        let z = self.rand_f32() * 12.0 - 6.0;
        let color = Color32::from_rgb(
            (50.0 + self.rand_f32() * 205.0) as u8,
            (50.0 + self.rand_f32() * 205.0) as u8,
            (50.0 + self.rand_f32() * 205.0) as u8,
        );
        const LABELS: [&str; 7] = ["Sensor", "MCU", "Gateway", "Driver", "Relay", "Display", "Module"];
        let label = LABELS[(self.rand_f32() * LABELS.len() as f32) as usize % LABELS.len()];
        self.scene.add_node(Vec3::new(x, 0.0, z), color, label);
        self.info = format!("Added {label}");
    }

    fn connect_last_two(&mut self) {
        if self.last_selected.len() >= 2 {
            let a = self.last_selected[self.last_selected.len() - 2];
            let b = self.last_selected[self.last_selected.len() - 1];
            if self.scene.add_wire(a, b, Color32::from_rgb(230, 180, 60)) {
                self.info = format!("Wire {a} \u{2192} {b}");
            } else {
                self.info = "Already connected / same node".to_string();
            }
        } else {
            self.info = "Select two nodes first".to_string();
        }
    }

    fn delete_selected(&mut self) {
        let ids: Vec<usize> = self
            .scene
            .nodes
            .iter()
            .filter(|n| n.selected)
            .map(|n| n.id)
            .collect();
        for id in &ids {
            self.scene.remove_node(*id);
            self.last_selected.retain(|x| x != id);
        }
        if !ids.is_empty() {
            self.info = format!("Removed {} node(s)", ids.len());
        }
    }

    fn clear_all(&mut self) {
        self.scene = Scene::new();
        self.last_selected.clear();
        self.info = "Scene cleared".to_string();
    }

    fn select_node(&mut self, id: Option<usize>) {
        self.scene.deselect_all();
        if let Some(id) = id {
            if let Some(n) = self.scene.nodes.iter_mut().find(|n| n.id == id) {
                n.selected = true;
            }
            if self.last_selected.last() != Some(&id) {
                self.last_selected.push(id);
            }
            if self.last_selected.len() > 2 {
                let start = self.last_selected.len() - 2;
                self.last_selected.drain(0..start);
            }
        }
    }

    /// Nearest node whose projected disk contains the cursor (×1.3 pick radius).
    fn pick_node(&self, cursor: Pos2, rect: Rect) -> Option<usize> {
        let mut best: Option<(usize, f32)> = None;
        for n in &self.scene.nodes {
            if let Some(p) = self.camera.project(n.pos, rect) {
                let screen_r = (n.radius * 1.3 * p.radius_factor).max(6.0);
                if cursor.distance(p.pos) <= screen_r {
                    if best.map_or(true, |(_, d)| p.depth < d) {
                        best = Some((n.id, p.depth));
                    }
                }
            }
        }
        best.map(|(id, _)| id)
    }

    // ── Sidebar ───────────────────────────────────────────────────────────────

    fn sidebar(&mut self, ctx: &egui::Context) {
        egui::SidePanel::right("panel")
            .exact_width(220.0)
            .show(ctx, |ui| {
                ui.add_space(12.0);
                ui.heading(egui::RichText::new("3D WIRE SYSTEM").color(Color32::from_rgb(0, 212, 255)));
                ui.separator();

                let sel = self.scene.nodes.iter().find(|n| n.selected);
                match sel {
                    Some(n) => {
                        ui.label(egui::RichText::new(format!("Selected: {}", n.label)).strong());
                        ui.label(
                            egui::RichText::new(format!(
                                "pos ({:.1}, {:.1}, {:.1})",
                                n.pos.x, n.pos.y, n.pos.z
                            ))
                            .color(Color32::from_rgb(0, 255, 136))
                            .monospace()
                            .size(11.0),
                        );
                    }
                    None => {
                        ui.label(egui::RichText::new("Nothing selected").weak());
                    }
                }
                if !self.info.is_empty() {
                    ui.label(
                        egui::RichText::new(&self.info)
                            .color(Color32::from_rgb(0, 255, 136))
                            .size(11.0),
                    );
                }

                ui.add_space(8.0);
                ui.separator();
                if ui.button("\u{2795}  Add Node  [A]").clicked() {
                    self.add_random_node();
                }
                if ui.button("\u{1F517}  Connect Last 2  [W]").clicked() {
                    self.connect_last_two();
                }
                if ui.button("\u{1F5D1}  Delete Selected  [Del]").clicked() {
                    self.delete_selected();
                }
                if ui.button("\u{21BA}  Reset Camera  [R]").clicked() {
                    self.camera.reset();
                }
                if ui.button("\u{1F504}  Clear All").clicked() {
                    self.clear_all();
                }

                ui.add_space(8.0);
                ui.separator();
                ui.label(
                    egui::RichText::new(format!(
                        "Nodes : {}\nWires : {}",
                        self.scene.nodes.len(),
                        self.scene.wires.len()
                    ))
                    .monospace()
                    .size(11.0),
                );

                ui.add_space(8.0);
                ui.separator();
                ui.label(
                    egui::RichText::new(
                        "Controls:\n  Left-drag  \u{2192} orbit\n  Mid-drag   \u{2192} pan\n  Scroll     \u{2192} zoom\n  Click      \u{2192} select\n  A          \u{2192} add node\n  W          \u{2192} connect 2\n  Del        \u{2192} remove\n  R          \u{2192} reset cam",
                    )
                    .monospace()
                    .size(10.0)
                    .color(Color32::from_rgb(120, 150, 170)),
                );
            });
    }

    // ── Canvas ──────────────────────────────────────────────────────────────────

    fn canvas(&mut self, ctx: &egui::Context) {
        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(Color32::from_rgb(15, 23, 33)))
            .show(ctx, |ui| {
                let rect = ui.max_rect();
                let resp = ui.allocate_rect(rect, egui::Sense::click_and_drag());

                // ── Camera interaction ──
                let middle_down = ctx.input(|i| i.pointer.middle_down());
                if resp.dragged() {
                    let d = resp.drag_delta();
                    if middle_down {
                        self.camera.pan(d.x, d.y);
                    } else {
                        self.camera.orbit(d.x, d.y);
                    }
                }
                let scroll = ctx.input(|i| i.smooth_scroll_delta.y);
                if resp.hovered() && scroll != 0.0 {
                    self.camera.zoom(scroll);
                }

                // ── Click to pick ──
                if resp.clicked() {
                    let picked = resp
                        .interact_pointer_pos()
                        .and_then(|p| self.pick_node(p, rect));
                    self.select_node(picked);
                    if let Some(id) = picked {
                        if let Some(n) = self.scene.node(id) {
                            self.info = format!("Selected {}", n.label);
                        }
                    }
                }

                // ── Keyboard ──
                let (ka, kw, kdel, kr, kesc) = ctx.input(|i| {
                    (
                        i.key_pressed(egui::Key::A),
                        i.key_pressed(egui::Key::W),
                        i.key_pressed(egui::Key::Delete) || i.key_pressed(egui::Key::Backspace),
                        i.key_pressed(egui::Key::R),
                        i.key_pressed(egui::Key::Escape),
                    )
                });
                if ka {
                    self.add_random_node();
                }
                if kw {
                    self.connect_last_two();
                }
                if kdel {
                    self.delete_selected();
                }
                if kr {
                    self.camera.reset();
                }
                if kesc {
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }

                // ── Render ──
                let painter = ui.painter_at(rect);
                self.draw_grid(&painter, rect);
                self.draw_scene(&painter, rect);
                draw_hud(&painter, rect, self.scene.nodes.len(), self.scene.wires.len());

                if resp.hovered() || resp.dragged() {
                    ctx.request_repaint();
                }
            });
    }

    fn draw_grid(&self, painter: &egui::Painter, rect: Rect) {
        let color = Color32::from_rgb(31, 51, 71);
        for (a, b) in build_grid(12) {
            if let (Some(pa), Some(pb)) = (self.camera.project(a, rect), self.camera.project(b, rect)) {
                painter.line_segment([pa.pos, pb.pos], Stroke::new(1.0, color));
            }
        }
    }

    /// Composite nodes and wires back-to-front by representative depth.
    fn draw_scene(&self, painter: &egui::Painter, rect: Rect) {
        let mut order: Vec<(f32, Drawable)> = Vec::new();

        for (i, n) in self.scene.nodes.iter().enumerate() {
            if let Some(p) = self.camera.project(n.pos, rect) {
                order.push((p.depth, Drawable::Node(i)));
            }
        }
        for (i, w) in self.scene.wires.iter().enumerate() {
            let (Some(a), Some(b)) = (self.scene.node(w.from), self.scene.node(w.to)) else {
                continue;
            };
            let mid = (a.pos + b.pos) * 0.5;
            if let Some(p) = self.camera.project(mid, rect) {
                order.push((p.depth, Drawable::Wire(i)));
            }
        }

        // Farther first.
        order.sort_by(|x, y| y.0.partial_cmp(&x.0).unwrap_or(std::cmp::Ordering::Equal));

        for (_, d) in order {
            match d {
                Drawable::Wire(i) => self.draw_wire(painter, rect, &self.scene.wires[i]),
                Drawable::Node(i) => self.draw_node(painter, rect, &self.scene.nodes[i]),
            }
        }
    }

    fn draw_wire(&self, painter: &egui::Painter, rect: Rect, wire: &Wire) {
        let (Some(src), Some(dst)) = (self.scene.node(wire.from), self.scene.node(wire.to)) else {
            return;
        };
        let spine = bezier_cubic(wire_control_points(src.pos, dst.pos), 28);
        let projected: Vec<Projected> = spine
            .iter()
            .filter_map(|p| self.camera.project(*p, rect))
            .collect();
        let color = if wire.selected {
            blend(wire.color, Color32::WHITE, 0.5)
        } else {
            wire.color
        };
        for seg in projected.windows(2) {
            let depth = (seg[0].depth + seg[1].depth) * 0.5;
            let width = (wire.thickness * 2.0 * (self.camera_focal(rect) / depth)).clamp(1.0, 8.0);
            painter.line_segment([seg[0].pos, seg[1].pos], Stroke::new(width, color));
        }
    }

    fn draw_node(&self, painter: &egui::Painter, rect: Rect, node: &Node) {
        let Some(p) = self.camera.project(node.pos, rect) else {
            return;
        };
        let r = (node.radius * p.radius_factor).max(2.0);

        let base = if node.selected {
            blend(node.color, Color32::from_rgb(0, 128, 255), 0.45)
        } else {
            node.color
        };
        painter.circle_filled(p.pos, r, base);
        // Fake specular: a smaller, lighter circle offset toward the light.
        let hi = blend(base, Color32::WHITE, 0.55);
        let hi_pos = p.pos + Vec2::new(-0.32 * r, -0.34 * r);
        painter.circle_filled(hi_pos, r * 0.42, hi);
        // Rim.
        let rim = if node.selected {
            Stroke::new(2.0, Color32::from_rgb(0, 212, 255))
        } else {
            Stroke::new(1.0, blend(base, Color32::BLACK, 0.4))
        };
        painter.circle_stroke(p.pos, r, rim);
    }

    fn camera_focal(&self, rect: Rect) -> f32 {
        (rect.height() * 0.5) / (self.camera.fov_deg.to_radians() * 0.5).tan()
    }
}

impl eframe::App for WireApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.sidebar(ctx);
        self.canvas(ctx);
    }
}

/// Bottom-right heads-up display showing node / wire counts.
fn draw_hud(painter: &egui::Painter, rect: Rect, nodes: usize, wires: usize) {
    painter.text(
        rect.right_bottom() - Vec2::new(10.0, 10.0),
        Align2::RIGHT_BOTTOM,
        format!("nodes={nodes} wires={wires}"),
        FontId::monospace(11.0),
        Color32::from_rgba_unmultiplied(255, 255, 255, 60),
    );
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 750.0])
            .with_title("3D Wiring System — Rust/egui"),
        renderer: eframe::Renderer::Glow, // glow (OpenGL); see Cargo.toml note.
        ..Default::default()
    };
    eframe::run_native(
        "Wire3D",
        options,
        Box::new(|_cc| Box::new(WireApp::new())),
    )
}
