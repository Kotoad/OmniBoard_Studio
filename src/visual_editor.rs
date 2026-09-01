use chrono::{DateTime, Utc};
use egui::emath::TSTransform;
use egui::{Color32, Pos2, RichText, Sense, Stroke, Vec2};
use i18n_embed_fl::fl;
use log::{debug, error};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::graph::{
    BasicBlock, Block, BlockKind, ButtonData, DeviceDef, ForData, Graph, IOBlock, IfData,
    LedBlinkData, LogicBlock, MathBlock, MathData, Point, VariableDef, WhileData, Wire,
};
use crate::omni_format::{v1, v2};
use crate::theme;
use crate::translation_manager::LOADER;

const MAGIC: &[u8; 4] = b"OMNI";
const FORMAT_VERSION: u16 = 3;
const VERSION_LEN: usize = std::mem::size_of::<u16>();
const HEADER_LEN: usize = MAGIC.len() + VERSION_LEN;

const ZOOM_MIN: f32 = 0.5;
const ZOOM_MAX: f32 = 3.0;
const ZOOM_SPEED: f32 = 0.001;

const GRID_SIZE: f32 = 25.0;
const GRID_WIDTH: f32 = 1.0;

const BLOCK_BORDER_BASE: f32 = 2.0;
const BLOCK_BORDER_SELECTED: f32 = 2.5;
const BLOCK_BORDER_RUNNING: f32 = 3.0;
const BLOCK_MARGIN_X: f32 = 8.0;
const BLOCK_MARGIN_Y: f32 = 5.0;
const HEADER_CORNER_RADIUS: f32 = 6.0;
const SHELL_CORNER_RADIUS: f32 = 5.0;
const BLOCK_MINIMUM_WIDTH: f32 = 175.0;

const PORT_RADIUS: f32 = 5.0;
const PORT_RADIUS_HOVER: f32 = 7.0;
const PORT_BORDER: f32 = 1.5;
const PORT_HITBOX_RADIUS: f32 = 16.0;

const WIRE_HOVER_THRESHOLD: f32 = 6.0;
const WIRE_SEGMENTS: u32 = 24;

#[derive(Clone, Copy)]
struct RunState {
    current: usize,
    #[allow(dead_code)]
    deadline: f64,
}

#[derive(Default)]
struct BlockInteraction {
    select: Option<usize>,
    delete: Option<usize>,
    duplicate: Option<usize>,
    drag: Option<(usize, Vec2)>,
    drag_stop: Option<usize>,
}

pub(crate) struct VisualEditor {
    graphs: Vec<Graph>,
    graph_index: usize,

    run: Option<RunState>,
    cameras: Vec<Camera>,
    interaction: Interaction,
    wire_caches: Vec<WireCache>,

    snap_to_grid: bool,
    dirty: bool,
    created: Option<DateTime<Utc>>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Default, Clone)]
struct GraphFile {
    meta: Meta,
    graphs: Vec<Graph>,
    variables: Vec<VariableDef>,
    devices: Vec<DeviceDef>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Default, Clone)]
struct Meta {
    format_version: u16,
    created: Option<DateTime<Utc>>,
    modified: Option<DateTime<Utc>>,
}

//MARK: - Wire caching
#[derive(Clone)]
struct CachedWire {
    from: Pos2,
    to: Pos2,
    points: Vec<Pos2>,
    bounds: egui::Rect,
    stamp: u64,
}

#[derive(Default, Clone)]
struct WireCache {
    entries: HashMap<(usize, u8), CachedWire>,
    frame: u64,
}

impl CachedWire {
    fn build(from: Pos2, to: Pos2, stamp: u64) -> Self {
        let points = wire_points(from, to);
        let bounds = egui::Rect::from_points(&points);
        Self {
            from,
            to,
            points,
            bounds,
            stamp,
        }
    }
}

impl WireCache {
    fn begin_frame(&mut self) {
        self.frame = self.frame.wrapping_add(1);
    }

    fn ensure(&mut self, key: (usize, u8), from: Pos2, to: Pos2) -> &CachedWire {
        let entry = self
            .entries
            .entry(key)
            .or_insert_with(|| CachedWire::build(from, to, self.frame));
        if entry.from != from || entry.to != to {
            *entry = CachedWire::build(from, to, self.frame);
        } else {
            entry.stamp = self.frame;
        }
        entry
    }

    fn end_frame(&mut self, live_wires: usize) {
        if self.entries.len() > live_wires {
            self.entries.retain(|_, e| e.stamp == self.frame);
        }
    }
}

//MARK: - Camera
#[derive(Clone, Copy)]
struct Camera {
    offset: Vec2,
    pan_start: Pos2,
    zoom: f32,
    panning: bool,
}

impl Default for Camera {
    fn default() -> Self {
        Self {
            offset: Vec2::ZERO,
            pan_start: Pos2::ZERO,
            zoom: 1.0,
            panning: false,
        }
    }
}

impl Camera {
    fn transform(&self) -> TSTransform {
        TSTransform::new(self.offset, self.zoom)
    }

    fn pan(&mut self, pointer: Option<Pos2>, active: bool) {
        if !active {
            self.panning = false;
            return;
        }

        let Some(p) = pointer else {
            return;
        };
        if self.panning {
            self.offset += p - self.pan_start;
        } else {
            self.panning = true;
        }
        self.pan_start = p;
    }

    fn zoom_at(&mut self, pointer: Pos2, scroll_y: f32) {
        let new_zoom = (self.zoom * (scroll_y * ZOOM_SPEED).exp()).clamp(ZOOM_MIN, ZOOM_MAX);
        let world = self.transform().inverse() * pointer;
        self.offset = pointer.to_vec2() - new_zoom * world.to_vec2();
        self.zoom = new_zoom;
    }
}

#[derive(Default)]
struct Interaction {
    selected: Option<usize>,
    wire_from: Option<(usize, u8)>,
    context_wire: Option<(usize, u8, usize, u8)>,
}
//MARK: - Helpers
fn out_port(rect: &egui::Rect, port: u8) -> egui::Pos2 {
    egui::Pos2::new(
        rect.right() + (BLOCK_BORDER_BASE / 2.0),
        rect.top() + (GRID_SIZE * 2.0) - BLOCK_BORDER_BASE + (port as f32) * GRID_SIZE,
    )
}

pub fn in_port(rect: &egui::Rect, port: u8) -> egui::Pos2 {
    egui::Pos2::new(
        rect.left() - (BLOCK_BORDER_BASE / 2.0),
        rect.top() + (GRID_SIZE * 2.0) - BLOCK_BORDER_BASE + (port as f32) * GRID_SIZE,
    )
}

fn out_port_screen(rect: &egui::Rect, port: u8, zoom: f32) -> Pos2 {
    Pos2::new(
        rect.right() + (BLOCK_BORDER_BASE / 2.0) * zoom,
        rect.top() + ((GRID_SIZE * 2.0) - BLOCK_BORDER_BASE + port as f32 * GRID_SIZE) * zoom,
    )
}

fn in_port_screen(rect: &egui::Rect, port: u8, zoom: f32) -> Pos2 {
    Pos2::new(
        rect.left() - (BLOCK_BORDER_BASE / 2.0) * zoom,
        rect.top() + ((GRID_SIZE * 2.0) - BLOCK_BORDER_BASE + port as f32 * GRID_SIZE) * zoom,
    )
}

fn wire_points(from: Pos2, to: Pos2) -> Vec<Pos2> {
    let ctrl = ((to.x - from.x) * 0.5).max(40.0);
    let c0 = Pos2::new(from.x + ctrl, from.y);
    let c1 = Pos2::new(to.x - ctrl, to.y);
    (0..=WIRE_SEGMENTS)
        .map(|i| {
            let t = i as f32 / WIRE_SEGMENTS as f32;
            let ab = from.lerp(c0, t).lerp(c0.lerp(c1, t), t);
            let bc = c0.lerp(c1, t).lerp(c1.lerp(to, t), t);
            ab.lerp(bc, t)
        })
        .collect()
}

fn dist_to_segment(p: Pos2, a: Pos2, b: Pos2) -> f32 {
    let ab = b - a;
    let len2 = ab.length_sq();
    if len2 <= f32::EPSILON {
        return p.distance(a);
    }
    let t = ((p - a).dot(ab) / len2).clamp(0.0, 1.0);
    p.distance(a + ab * t)
}

fn dist_to_polyline(p: Pos2, pts: &[Pos2]) -> f32 {
    pts.windows(2)
        .map(|s| dist_to_segment(p, s[0], s[1]))
        .fold(f32::INFINITY, f32::min)
}

fn draw_grid(
    painter: &egui::Painter,
    rect: egui::Rect,
    offset: Vec2,
    zoom: f32,
    grid_color: Color32,
) {
    let zoom_grid_size = GRID_SIZE * zoom;
    let ox = (offset.x - rect.left()).rem_euclid(zoom_grid_size);
    let oy = (offset.y - rect.top()).rem_euclid(zoom_grid_size);
    let mut x = rect.left() + ox;

    while x < rect.right() {
        painter.line_segment(
            [Pos2::new(x, rect.top()), Pos2::new(x, rect.bottom())],
            Stroke::new(GRID_WIDTH, grid_color),
        );
        x += zoom_grid_size;
    }

    let mut y = rect.top() + oy;

    while y < rect.bottom() {
        painter.line_segment(
            [Pos2::new(rect.left(), y), Pos2::new(rect.right(), y)],
            Stroke::new(GRID_WIDTH, grid_color),
        );
        y += zoom_grid_size;
    }
}

fn snap_font_size(size: f32, pixels_per_point: f32) -> f32 {
    (size * pixels_per_point).round().max(1.0) / pixels_per_point
}

//MARK: - File encoding/decoding
fn encode_graph(file: &GraphFile) -> Result<Vec<u8>, String> {
    let payload = bincode::serde::encode_to_vec(file, bincode::config::standard())
        .map_err(|e| e.to_string())?;
    let mut out = Vec::with_capacity(HEADER_LEN + payload.len());
    out.extend_from_slice(MAGIC);
    out.extend_from_slice(&FORMAT_VERSION.to_le_bytes());
    out.extend_from_slice(&payload);
    Ok(out)
}

impl From<v1::GraphFile> for GraphFile {
    fn from(v1_graph_file: v1::GraphFile) -> Self {
        Self {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: v1_graph_file.meta.created,
                modified: v1_graph_file.meta.modified,
            },
            graphs: v1_graph_file
                .graphs
                .into_iter()
                .enumerate()
                .map(|(i, g)| {
                    Graph::from_parts(
                        format!("Graph {}", i),
                        g.blocks
                            .iter()
                            .map(|b| Block {
                                id: b.id,
                                pos: Point {
                                    x: b.pos.x,
                                    y: b.pos.y,
                                },
                                kind: match &b.kind {
                                    v1::BlockKind::Basic(b) => BlockKind::Basic(match b {
                                        v1::BasicBlock::Start => BasicBlock::Start,
                                        v1::BasicBlock::End => BasicBlock::End,
                                    }),
                                    v1::BlockKind::Logic(b) => BlockKind::Logic(match b {
                                        v1::LogicBlock::If => LogicBlock::If(IfData::default()),
                                        v1::LogicBlock::Else => LogicBlock::If(IfData::default()),
                                        v1::LogicBlock::While => {
                                            LogicBlock::While(WhileData::default())
                                        }
                                        v1::LogicBlock::For => LogicBlock::For(ForData::default()),
                                    }),
                                    v1::BlockKind::Math(b) => BlockKind::Math(match b {
                                        v1::MathBlock::Add => MathBlock::Add(MathData::default()),
                                        v1::MathBlock::Subtract => {
                                            MathBlock::Subtract(MathData::default())
                                        }
                                        v1::MathBlock::Multiply => {
                                            MathBlock::Multiply(MathData::default())
                                        }
                                        v1::MathBlock::Divide => {
                                            MathBlock::Divide(MathData::default())
                                        }
                                    }),
                                    v1::BlockKind::IO(b) => BlockKind::IO(match b {
                                        v1::IOBlock::Input => {
                                            IOBlock::Button(ButtonData::default())
                                        }
                                        v1::IOBlock::Output => {
                                            IOBlock::LedBlink(LedBlinkData::default())
                                        }
                                    }),
                                },
                            })
                            .collect(),
                        g.wires
                            .into_iter()
                            .map(|w| Wire {
                                from_block: w.from,
                                from_port: 0,
                                to_block: w.to,
                                to_port: 0,
                            })
                            .collect(),
                    )
                })
                .collect(),
            variables: Vec::new(),
            devices: Vec::new(),
        }
    }
}

impl From<v2::GraphFile> for GraphFile {
    fn from(v2_graph_file: v2::GraphFile) -> Self {
        Self {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: v2_graph_file.meta.created,
                modified: v2_graph_file.meta.modified,
            },
            graphs: v2_graph_file
                .graphs
                .into_iter()
                .map(|g| {
                    Graph::from_parts(
                        g.name,
                        g.blocks
                            .into_iter()
                            .map(|b| Block {
                                id: b.id,
                                pos: Point {
                                    x: b.pos.x,
                                    y: b.pos.y,
                                },
                                kind: match b.kind {
                                    v2::BlockKind::Basic(b) => BlockKind::Basic(match b {
                                        v2::BasicBlock::Start => BasicBlock::Start,
                                        v2::BasicBlock::End => BasicBlock::End,
                                    }),
                                    v2::BlockKind::Logic(b) => BlockKind::Logic(match b {
                                        v2::LogicBlock::If => LogicBlock::If(IfData::default()),
                                        v2::LogicBlock::Else => LogicBlock::If(IfData::default()),
                                        v2::LogicBlock::While => {
                                            LogicBlock::While(WhileData::default())
                                        }
                                        v2::LogicBlock::For => LogicBlock::For(ForData::default()),
                                    }),
                                    v2::BlockKind::Math(b) => BlockKind::Math(match b {
                                        v2::MathBlock::Add => MathBlock::Add(MathData::default()),
                                        v2::MathBlock::Subtract => {
                                            MathBlock::Subtract(MathData::default())
                                        }
                                        v2::MathBlock::Multiply => {
                                            MathBlock::Multiply(MathData::default())
                                        }
                                        v2::MathBlock::Divide => {
                                            MathBlock::Divide(MathData::default())
                                        }
                                    }),
                                    v2::BlockKind::IO(b) => BlockKind::IO(match b {
                                        v2::IOBlock::Input => {
                                            IOBlock::Button(ButtonData::default())
                                        }
                                        v2::IOBlock::Output => {
                                            IOBlock::LedBlink(LedBlinkData::default())
                                        }
                                    }),
                                },
                            })
                            .collect(),
                        g.wires
                            .into_iter()
                            .map(|w| Wire {
                                from_block: w.from,
                                from_port: 0,
                                to_block: w.to,
                                to_port: 0,
                            })
                            .collect(),
                    )
                })
                .collect(),
            variables: Vec::new(),
            devices: Vec::new(),
        }
    }
}

fn parse_header(bytes: &[u8]) -> Result<(u16, &[u8]), String> {
    if bytes.len() < HEADER_LEN || &bytes[..MAGIC.len()] != MAGIC {
        return Err("Invalid file format".to_string());
    }
    let version = u16::from_le_bytes([bytes[4], bytes[5]]);
    Ok((version, &bytes[HEADER_LEN..]))
}

fn decode_payload<T: for<'de> Deserialize<'de>>(payload: &[u8]) -> Result<T, String> {
    bincode::serde::decode_from_slice::<T, _>(payload, bincode::config::standard())
        .map(|(file, _len)| file)
        .map_err(|e| e.to_string())
}

fn decode_graph(bytes: &[u8]) -> Result<GraphFile, String> {
    let (version, payload) = parse_header(bytes)?;
    match version {
        1 => decode_payload::<v1::GraphFile>(payload).map(GraphFile::from),
        2 => decode_payload::<v2::GraphFile>(payload).map(GraphFile::from),
        3 => decode_payload::<GraphFile>(payload).map(|mut f| {
            f.graphs.iter_mut().for_each(Graph::normalize);
            f
        }),
        v if v > FORMAT_VERSION => Err(format!(
            "This file was saved by a newer version of OmniBoard Studio (format {v}). Please update the app."
        )),
        v => Err(format!("Unknown file version: {v}")),
    }
}

//MARK: - VisualEditor implementation
impl VisualEditor {
    pub(crate) fn new() -> Self {
        Self {
            graphs: vec![Graph::new("Graph 0")],
            graph_index: 0,

            run: None,
            cameras: vec![Camera::default()],
            interaction: Interaction::default(),
            wire_caches: vec![WireCache::default()],

            snap_to_grid: false,
            dirty: false,
            created: Option::<DateTime<Utc>>::None,
        }
    }

    //MARK: - Block management
    pub fn is_dirty(&self) -> bool {
        self.dirty
    }

    pub fn add_block(&mut self, block_kind: BlockKind) {
        let pos = Point {
            x: 100.0 + Graph::peek_next_block_id(&self.graphs[self.graph_index]) as f32 * 20.0,
            y: 100.0,
        };
        Graph::add_block(&mut self.graphs[self.graph_index], block_kind, pos);
        self.dirty = true;
    }

    fn delete_block(&mut self, id: usize) {
        Graph::delete_block(&mut self.graphs[self.graph_index], id);
        if self.interaction.selected == Some(id) {
            self.interaction.selected = None;
        }
        if self.run.map(|r| r.current) == Some(id) {
            self.run = None;
        }
        self.dirty = true;
    }

    fn duplicate_block(&mut self, id: usize) {
        if Graph::block_exists(&self.graphs[self.graph_index], id) {
            let pos = self.graphs[self.graph_index]
                .blocks()
                .iter()
                .find(|b| b.id == id)
                .map(|b| Point {
                    x: b.pos.x + 20.0,
                    y: b.pos.y + 20.0,
                })
                .unwrap_or(Point { x: 100.0, y: 100.0 });
            Graph::duplicate_block(&mut self.graphs[self.graph_index], id, pos);
            self.dirty = true;
        }
    }

    fn move_block(&mut self, id: usize, delta: Vec2) {
        self.graphs[self.graph_index].translate_block(id, delta.x, delta.y);
        self.dirty = true;
    }

    fn snap_block_to_grid(&mut self, id: usize) {
        if !self.snap_to_grid {
            return;
        }

        if let Some(block) = self.graphs[self.graph_index].block(id) {
            let x = (block.pos.x / GRID_SIZE).round() * GRID_SIZE;
            let y = (block.pos.y / GRID_SIZE).round() * GRID_SIZE;
            self.graphs[self.graph_index].set_block_pos(id, x, y);
            self.dirty = true;
        }
    }

    fn handle_zoom(&mut self, ui: &egui::Ui, response: &egui::Response, pointer: Option<Pos2>) {
        if !response.hovered() {
            return;
        };
        let scroll_y = ui.input(|i| i.smooth_scroll_delta.y);
        if scroll_y == 0.0 {
            return;
        };
        let Some(p) = pointer else {
            return;
        };

        self.cameras[self.graph_index].zoom_at(p, scroll_y);
    }

    //MARK: - File management
    pub fn save(&mut self, path: &std::path::Path) {
        let temp = path.with_extension("omni.tmp");
        if self.created.is_none() {
            self.created = Some(Utc::now());
        }
        let file = GraphFile {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: self.created,
                modified: Some(Utc::now()),
            },
            graphs: self.graphs.clone(),
            variables: Vec::new(),
            devices: Vec::new(),
        };
        match encode_graph(&file)
            .and_then(|bytes| std::fs::write(&temp, bytes).map_err(|e| e.to_string()))
        {
            Ok(()) => {
                debug!("Graph saved to {}", path.display());
                if let Err(e) = std::fs::rename(&temp, path) {
                    error!("Failed to rename temp file: {}", e);
                } else {
                    debug!("Temp file renamed to {}", path.display());
                    self.dirty = false
                }
            }
            Err(e) => {
                error!("Failed to save graph: {}", e);
            }
        }

        #[cfg(debug_assertions)]
        {
            let json_path = path.with_extension("omni.json");
            match serde_json::to_string_pretty(&file)
                .map_err(|e| e.to_string())
                .and_then(|json| std::fs::write(&json_path, json).map_err(|e| e.to_string()))
            {
                Ok(()) => {
                    debug!("Graph saved to {}", json_path.display());
                }
                Err(e) => error!("Failed to save graph: {}", e),
            }
        }
    }

    fn ok_load(&mut self, file: GraphFile) {
        self.graphs = file.graphs.clone();
        if self.graphs.is_empty() {
            self.graphs
                .push(Graph::from_parts("Graph 0", Vec::new(), Vec::new()));
        }
        self.cameras = vec![Camera::default(); self.graphs.len()];
        self.wire_caches = vec![WireCache::default(); self.graphs.len()];
        self.graph_index = 0;
        self.graphs.iter_mut().for_each(Graph::normalize);
        self.interaction = Interaction::default();
        self.run = None;
        self.dirty = false;
        self.created = file.meta.created;
    }

    pub fn load(&mut self, path: &std::path::Path) {
        if path.extension().and_then(|e| e.to_str()) == Some("omni") {
            match std::fs::read(path)
                .map_err(|e| e.to_string())
                .and_then(|bytes| decode_graph(&bytes))
            {
                Ok(file) => {
                    self.ok_load(file);
                    debug!("Graph loaded from {}", path.display());
                }
                Err(e) => error!("Failed to load graph: {}", e),
            }
        } else if path.extension().and_then(|e| e.to_str()) == Some("json") {
            match std::fs::read_to_string(path)
                .map_err(|e| e.to_string())
                .and_then(|json| {
                    serde_json::from_str::<GraphFile>(&json).map_err(|e| e.to_string())
                }) {
                Ok(file) => {
                    self.ok_load(file);
                    debug!("Graph loaded from {}", path.display());
                }
                Err(e) => error!("Failed to load graph: {}", e),
            }
        }
    }

    //MARK: - Draw blocks
    fn draw_blocks(
        &self,
        pointer: Option<egui::Pos2>,
        canvas_rect: egui::Rect,
        ctx: &egui::Context,
        rects: &mut HashMap<usize, egui::Rect>,
    ) -> BlockInteraction {
        let selected = self.interaction.selected;
        let run_current = self.run.map(|r| r.current);
        let over_canvas = pointer.is_some_and(|p| canvas_rect.contains(p));
        let mut interaction = BlockInteraction::default();
        let transform = self.cameras[self.graph_index].transform();

        for block in self.graphs[self.graph_index].blocks() {
            let area = egui::Area::new(egui::Id::new(("block", block.id)))
                .fixed_pos(transform * Pos2::new(block.pos.x, block.pos.y))
                .movable(false)
                .constrain(false)
                .interactable(over_canvas)
                .order(egui::Order::Middle);

            let resp = area.show(ctx, |ui| {
                let title = LOADER.get(block.kind.block_type().meta().title_key);
                let field = LOADER.get(block.kind.block_type().meta().field_key);
                let id = format!("#{}", block.id);
                let zoom = self.cameras[self.graph_index].zoom;
                let pixels_per_point = ui.ctx().pixels_per_point();

                for font in ui.style_mut().text_styles.values_mut() {
                    font.size = snap_font_size(font.size * zoom, pixels_per_point);
                }

                let body = egui::TextStyle::Body.resolve(ui.style());
                let small = egui::TextStyle::Small.resolve(ui.style());
                let text_w = |ui: &egui::Ui, s: &str, font: egui::FontId| {
                    ui.fonts_mut(|f| {
                        f.layout_no_wrap(s.to_owned(), font, Color32::WHITE)
                            .rect
                            .width()
                    })
                };

                let gap = ui.spacing().item_spacing.x * zoom;

                let header_w = text_w(ui, &title, body.clone())
                    + gap
                    + text_w(ui, &id, small)
                    + (BLOCK_MARGIN_X * 2.0) * zoom;
                let content_w = text_w(ui, &field, body.clone()) + (BLOCK_MARGIN_X * 2.0) * zoom;
                let world_w = header_w.max(content_w) / zoom;
                let block_w =
                    ((world_w / GRID_SIZE).ceil() * GRID_SIZE).max(BLOCK_MINIMUM_WIDTH) * zoom;

                ui.set_clip_rect(canvas_rect);

                let outline = if run_current == Some(block.id) {
                    Stroke::new(BLOCK_BORDER_RUNNING * zoom, Color32::from_rgb(255, 210, 80))
                } else if selected == Some(block.id) {
                    Stroke::new(BLOCK_BORDER_SELECTED * zoom, Color32::WHITE)
                } else {
                    Stroke::new(
                        BLOCK_BORDER_BASE * zoom,
                        block.kind.block_type().meta().color,
                    )
                };

                let shell = egui::Frame::new()
                    .fill(Color32::from_rgb(18, 18, 22))
                    .stroke(outline)
                    .corner_radius(SHELL_CORNER_RADIUS * zoom)
                    .inner_margin(egui::Margin::ZERO)
                    .show(ui, |ui| {
                        ui.set_min_width(block_w - (BLOCK_BORDER_BASE * 2.0) * zoom);
                        ui.set_max_width(block_w - (BLOCK_BORDER_BASE * 2.0) * zoom);
                        ui.spacing_mut().item_spacing.y = 0.0;

                        let header = egui::Frame::new()
                            .fill(block.kind.block_type().meta().color)
                            .corner_radius(egui::CornerRadius {
                                nw: (HEADER_CORNER_RADIUS * zoom).round() as u8,
                                ne: (HEADER_CORNER_RADIUS * zoom).round() as u8,
                                sw: 0,
                                se: 0,
                            })
                            .inner_margin(egui::vec2(
                                BLOCK_MARGIN_X * zoom,
                                BLOCK_MARGIN_Y * zoom,
                            ))
                            .show(ui, |ui| {
                                ui.set_min_width(
                                    block_w
                                        - (BLOCK_MARGIN_X * 2.0 + BLOCK_BORDER_BASE * 2.0) * zoom,
                                );
                                ui.horizontal(|ui| {
                                    let block_kind =
                                        LOADER.get(block.kind.block_type().meta().title_key);
                                    ui.label(
                                        RichText::new(block_kind).color(Color32::WHITE).strong(),
                                    );

                                    ui.with_layout(
                                        egui::Layout::right_to_left(egui::Align::Center),
                                        |ui| {
                                            ui.label(
                                                RichText::new(format!("#{}", block.id))
                                                    .small()
                                                    .color(Color32::from_white_alpha(140)),
                                            );
                                        },
                                    );
                                });
                            });

                        let header_drag = header.response.interact(Sense::click_and_drag());
                        if header_drag.dragged_by(egui::PointerButton::Primary) {
                            interaction.drag = Some((block.id, header_drag.drag_delta() / zoom));
                            ui.ctx().set_cursor_icon(egui::CursorIcon::Grabbing);
                        } else if header_drag.hovered() {
                            ui.ctx().set_cursor_icon(egui::CursorIcon::Grab);
                        }
                        if header_drag.drag_stopped_by(egui::PointerButton::Primary) {
                            interaction.drag_stop = Some(block.id);
                        }
                        if header_drag.clicked() {
                            interaction.select = Some(block.id);
                        }
                        header_drag.context_menu(|ui| {
                            if ui
                                .button(fl!(LOADER, "main-gui-block-context-menu-duplicate"))
                                .clicked()
                            {
                                interaction.duplicate = Some(block.id);
                                ui.close();
                            }
                            if ui
                                .button(fl!(LOADER, "main-gui-block-context-menu-delete"))
                                .clicked()
                            {
                                interaction.delete = Some(block.id);
                                ui.close();
                            }
                        });

                        //MARK: - Block content
                        egui::Frame::new()
                            .inner_margin(egui::Margin::same((BLOCK_MARGIN_X * zoom).round() as i8))
                            .show(ui, |ui| {
                                let ports_count =
                                    block.kind.out_ports().max(block.kind.in_ports()) as f32;
                                ui.set_min_height(
                                    (ports_count + 1.0) * GRID_SIZE * zoom
                                        - ((BLOCK_MARGIN_Y * 2.0) * zoom)
                                        - (BLOCK_BORDER_BASE * 2.0) * zoom,
                                );
                                ui.spacing_mut().item_spacing.y = 4.0 * zoom;
                                ui.with_layout(egui::Layout::top_down(egui::Align::Center), |ui| {
                                    ui.label(
                                        RichText::new(
                                            LOADER.get(block.kind.block_type().meta().field_key),
                                        )
                                        .color(Color32::from_white_alpha(200)),
                                    );
                                });
                            });
                    });

                //MARK: - Draw ports
                let rect = shell.response.rect;
                let painter = ui.painter();
                let out_ports: Vec<Pos2> = (0..block.kind.out_ports())
                    .map(|i| out_port_screen(&rect, i, zoom))
                    .collect();
                let in_ports: Vec<Pos2> = (0..block.kind.in_ports())
                    .map(|i| in_port_screen(&rect, i, zoom))
                    .collect();

                for port in out_ports.iter() {
                    let out_hot =
                        pointer.is_some_and(|p| p.distance(*port) < PORT_HITBOX_RADIUS * zoom);
                    painter.circle_filled(
                        *port,
                        if out_hot {
                            PORT_RADIUS_HOVER * zoom
                        } else {
                            PORT_RADIUS * zoom
                        },
                        Color32::WHITE,
                    );
                    painter.circle_stroke(
                        *port,
                        if out_hot {
                            PORT_RADIUS_HOVER * zoom
                        } else {
                            PORT_RADIUS * zoom
                        },
                        Stroke::new(PORT_BORDER * zoom, Color32::BLACK),
                    );
                }
                for port in in_ports.iter() {
                    let in_hot =
                        pointer.is_some_and(|p| p.distance(*port) < PORT_HITBOX_RADIUS * zoom);
                    painter.circle_filled(
                        *port,
                        if in_hot {
                            PORT_RADIUS_HOVER * zoom
                        } else {
                            PORT_RADIUS * zoom
                        },
                        Color32::from_rgb(180, 220, 200),
                    );
                    painter.circle_stroke(
                        *port,
                        if in_hot {
                            PORT_RADIUS_HOVER * zoom
                        } else {
                            PORT_RADIUS * zoom
                        },
                        Stroke::new(PORT_BORDER * zoom, Color32::BLACK),
                    );
                }
            });
            rects.insert(block.id, transform.inverse() * resp.response.rect);
        }

        interaction
    }

    fn handle_wire_interaction(
        &mut self,
        pointer: Option<egui::Pos2>,
        rmb_pressed: bool,
        rmb_released: bool,
        rects: &HashMap<usize, egui::Rect>,
    ) -> bool {
        let mut grabbed_port = false;

        if let Some(pos) = pointer {
            let world_ptr = self.cameras[self.graph_index].transform().inverse() * pos;
            if rmb_pressed {
                let graph = &self.graphs[self.graph_index];
                for block in graph.blocks() {
                    let Some(rect) = rects.get(&block.id) else {
                        continue;
                    };
                    for port in 0..block.kind.out_ports() {
                        if world_ptr.distance(out_port(rect, port)) < PORT_HITBOX_RADIUS
                            && !graph.has_outgoing((block.id, port))
                        {
                            self.interaction.wire_from = Some((block.id, port));
                            grabbed_port = true;
                            break;
                        }
                    }
                }
            }
            if rmb_released {
                if let Some(from) = self.interaction.wire_from.take() {
                    let graph = &mut self.graphs[self.graph_index];
                    let to = graph.blocks().iter().find_map(|b| {
                        let r = rects.get(&b.id)?;
                        (0..b.kind.in_ports())
                            .find(|&port| world_ptr.distance(in_port(r, port)) < PORT_HITBOX_RADIUS)
                            .map(|port| (b.id, port))
                    });
                    debug!(
                        "Wire released from block {} port {} to {:?}",
                        from.0, from.1, to
                    );
                    if let Some((to, in_ports)) = to {
                        if graph.connect(from, (to, in_ports)).is_ok() {
                            self.dirty = true;
                            debug!(
                                "Connected wire from block {} port {} to block {} port {}",
                                from.0, from.1, to, in_ports
                            );
                        }
                    }
                }
            }
        }
        grabbed_port
    }

    //MARK: - Draw wires
    fn draw_wires(
        &mut self,
        ctx: &egui::Context,
        pointer: Option<egui::Pos2>,
        canvas_rect: egui::Rect,
        rects: &HashMap<usize, egui::Rect>,
        response: &egui::Response,
        grabbed_port: bool,
    ) {
        let graph = &self.graphs[self.graph_index];
        let cache = &mut self.wire_caches[self.graph_index];
        let transform = self.cameras[self.graph_index].transform();

        cache.begin_frame();

        let mut hovered: Option<(usize, u8)> = None;
        let pointer_world = pointer
            .filter(|p| canvas_rect.contains(*p))
            .map(|p| self.cameras[self.graph_index].transform().inverse() * p);
        let threshold = WIRE_HOVER_THRESHOLD / self.cameras[self.graph_index].zoom;

        for wire in graph.wires() {
            let (Some(from_rect), Some(to_rect)) =
                (rects.get(&wire.from_block), rects.get(&wire.to_block))
            else {
                continue;
            };

            let key = (wire.from_block, wire.from_port);
            let entry = cache.ensure(
                key,
                out_port(from_rect, wire.from_port),
                in_port(to_rect, wire.to_port),
            );

            if hovered.is_none() {
                if let Some(wp) = pointer_world {
                    if entry.bounds.expand(threshold).contains(wp)
                        && dist_to_polyline(wp, &entry.points) < threshold
                    {
                        hovered = Some(key);
                    }
                }
            }
        }

        cache.end_frame(graph.wires().len());

        let wire_layer = egui::LayerId::new(egui::Order::Background, egui::Id::new("wires"));
        ctx.set_transform_layer(wire_layer, transform);
        let mut wire_painter = ctx.layer_painter(wire_layer);
        wire_painter.set_clip_rect(transform.inverse() * canvas_rect);

        if response.secondary_clicked() && !grabbed_port {
            self.interaction.context_wire =
                hovered.and_then(|i| graph.successor(i).map(|to| (i.0, i.1, to.0, to.1)));
        }

        let context_wire = self.interaction.context_wire;
        let mut disconnect: Option<(usize, u8, usize, u8)> = None;

        if context_wire.is_some() {
            response.context_menu(|ui| {
                if let Some(w) = context_wire {
                    if ui
                        .button(fl!(LOADER, "main-gui-wire-context-menu-delete"))
                        .clicked()
                    {
                        disconnect = Some(w);
                        ui.close();
                    }
                }
            });
        }

        for wire in graph.wires() {
            let key = (wire.from_block, wire.from_port);
            let Some(entry) = cache.entries.get(&key) else {
                continue;
            };

            let (width, color) = if hovered == Some(key) {
                (4.0_f32, Color32::from_rgb(255, 100, 100))
            } else {
                (2.5_f32, Color32::from_rgb(80, 200, 160))
            };

            for seg in entry.points.windows(2) {
                wire_painter.line_segment([seg[0], seg[1]], Stroke::new(width, color));
            }
        }

        let fg = ctx
            .layer_painter(egui::LayerId::new(
                egui::Order::Foreground,
                egui::Id::new("overlay"),
            ))
            .with_clip_rect(canvas_rect);
        if let (Some(from), Some(pos)) = (self.interaction.wire_from, pointer) {
            if let Some(rect) = rects.get(&from.0) {
                for seg in wire_points(transform * out_port(rect, from.1), pos).windows(2) {
                    fg.line_segment(
                        [seg[0], seg[1]],
                        Stroke::new(2.5_f32, Color32::from_rgb(255, 100, 60)),
                    );
                }
            }
        }

        if let Some((from_block, from_port, to_block, to_port)) = disconnect {
            self.graphs[self.graph_index].disconnect((from_block, from_port), (to_block, to_port));
            self.interaction.context_wire = None;
            self.dirty = true;
        }
    }

    //MARK: - GUI
    pub(crate) fn show_visual_editor(&mut self, ui: &mut egui::Ui) {
        egui::CentralPanel::default().show(ui, |ui| {
            let canvas_rect = ui.max_rect();
            let response = ui.allocate_rect(canvas_rect, egui::Sense::click_and_drag());

            let pointer = ui.input(|i| i.pointer.hover_pos());
            let rmb_pressed = ui.input(|i| i.pointer.secondary_pressed());
            let rmb_released = ui.input(|i| i.pointer.secondary_released());
            let mmb_pressed = ui.input(|i| i.pointer.middle_down());

            let painter = ui.painter();
            let pal = theme::palette(ui.ctx());

            let mut rects: HashMap<usize, egui::Rect> = HashMap::new();

            self.cameras[self.graph_index].pan(pointer, mmb_pressed);

            self.handle_zoom(ui, &response, pointer);

            draw_grid(
                painter,
                canvas_rect,
                self.cameras[self.graph_index].offset,
                self.cameras[self.graph_index].zoom,
                pal.mid,
            );

            let interaction = self.draw_blocks(pointer, canvas_rect, ui.ctx(), &mut rects);

            if let Some(id) = interaction.select {
                self.interaction.selected = Some(id);
            }
            if let Some((id, delta)) = interaction.drag {
                self.move_block(id, delta);
            }
            if let Some(id) = interaction.drag_stop {
                self.snap_block_to_grid(id);
            }
            if let Some(id) = interaction.duplicate {
                self.duplicate_block(id);
            }
            if let Some(id) = interaction.delete {
                self.delete_block(id);
            }

            let grabbed_port =
                self.handle_wire_interaction(pointer, rmb_pressed, rmb_released, &rects);

            self.draw_wires(ui.ctx(), pointer, canvas_rect, &rects, &response, grabbed_port);
        });
    }
}

//MARK: - Tests
#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph::{BasicBlock, Block, BlockKind, BlockType, Wire};
    use crate::translation_manager;
    use proptest::prelude::*;

    //MARK: - Geometry helpers
    const EPS: f32 = 1e-4;

    fn approx_eq(a: f32, b: f32) {
        assert!(
            (a - b).abs() < EPS,
            "Expected {} to be approximately equal to {}",
            a,
            b
        );
    }

    fn rect(x: f32, y: f32, w: f32, h: f32) -> egui::Rect {
        egui::Rect::from_min_size(egui::Pos2::new(x, y), egui::Vec2::new(w, h))
    }

    //MARK: - Geometry tests
    #[test]
    fn dist_to_segment_is_zero() {
        approx_eq(
            dist_to_segment(
                Pos2::new(5.0, 5.0),
                Pos2::new(0.0, 0.0),
                Pos2::new(10.0, 10.0),
            ),
            0.0,
        );
    }

    #[test]
    fn dist_to_segment_is_perpendicular() {
        approx_eq(
            dist_to_segment(
                Pos2::new(0.0, 3.0),
                Pos2::new(-1.0, 0.0),
                Pos2::new(1.0, 0.0),
            ),
            3.0,
        );
    }

    #[test]
    fn dist_to_segment_clamps_past_enpoints() {
        approx_eq(
            dist_to_segment(
                Pos2::new(5.0, 0.0),
                Pos2::new(0.0, 0.0),
                Pos2::new(1.0, 0.0),
            ),
            4.0,
        );
    }

    #[test]
    fn dist_to_segment_handles_degenerate_segment() {
        approx_eq(
            dist_to_segment(Pos2::new(3.0, 4.0), Pos2::ZERO, Pos2::ZERO),
            5.0,
        );
    }

    #[test]
    fn dist_to_polyline_takes_minimum() {
        let pts = [
            Pos2::new(0.0, 0.0),
            Pos2::new(10.0, 0.0),
            Pos2::new(10.0, 10.0),
        ];
        approx_eq(dist_to_polyline(Pos2::new(11.0, 5.0), &pts), 1.0);
    }

    #[test]
    fn dist_to_polyline_of_degenerate_inputs() {
        assert!(dist_to_polyline(Pos2::ZERO, &[]).is_infinite());
        assert!(dist_to_polyline(Pos2::ZERO, &[Pos2::new(1.0, 1.0)]).is_infinite());
    }

    #[test]
    fn wire_points_has_more_segments_than_points() {
        assert_eq!(
            wire_points(Pos2::ZERO, Pos2::new(100.0, 50.0)).len(),
            WIRE_SEGMENTS as usize + 1
        );
    }

    #[test]
    fn wire_points_starts_and_ends_at_correct_points() {
        let (from, to) = (Pos2::new(10.0, 20.0), Pos2::new(30.0, 40.0));
        let pts = wire_points(from, to);
        approx_eq(pts[0].x, from.x);
        approx_eq(pts[0].y, from.y);
        approx_eq(pts[pts.len() - 1].x, to.x);
        approx_eq(pts[pts.len() - 1].y, to.y);
    }

    #[test]
    fn wire_points_flat_horizontal() {
        for p in wire_points(Pos2::new(0.0, 7.0), Pos2::new(100.0, 7.0)) {
            approx_eq(p.y, 7.0);
        }
    }

    #[test]
    fn ports_are_on_opposite_edges() {
        let r = rect(100.0, 200.0, 175.0, 100.0);
        let out_port = out_port(&r, 0).x;
        let in_port = in_port(&r, 0).x;

        assert!(
            out_port > r.right(),
            "Out port {out_port} is not on the right edge of the block {r:?}"
        );
        assert!(
            in_port < r.left(),
            "In port {in_port} is not on the left edge of the block {r:?}"
        );

        approx_eq(out_port - r.right(), r.left() - in_port);
    }

    #[test]
    fn ports_are_spaced_one_grid_apart() {
        let r = rect(100.0, 200.0, 175.0, 100.0);
        approx_eq(out_port(&r, 1).y - out_port(&r, 0).y, GRID_SIZE);
        approx_eq(out_port(&r, 3).y - out_port(&r, 2).y, GRID_SIZE);
    }

    #[test]
    fn matching_ports_have_same_row() {
        let r = rect(100.0, 200.0, 175.0, 100.0);
        for i in 0..4 {
            approx_eq(out_port(&r, i).y, in_port(&r, i).y);
        }
    }

    //MARK: - i18n tests
    #[test]
    fn all_block_meta_keys_exist() {
        let (loader, langs) = translation_manager::all_languages_loader();
        for lang in &langs {
            let ids: std::collections::HashSet<String> = loader
                .with_message_iter(lang, |iter| iter.map(|m| m.id.name.to_string()).collect());
            for kind in BlockType::ALL {
                let m = kind.meta();
                for key in &[m.title_key, m.field_key, m.description_key] {
                    assert!(
                        ids.contains(*key),
                        "Missing i18n key: {} in language {}",
                        key,
                        lang
                    );
                }
            }
        }
    }

    #[test]
    fn zoom_keeps_the_point_under_the_cursor_fixed() {
        let mut cam = Camera::default();
        let pointer = Pos2::new(400.0, 300.0);
        let before = cam.transform().inverse() * pointer;
        cam.zoom_at(pointer, 120.0);
        let after = cam.transform().inverse() * pointer;
        approx_eq(before.x, after.x);
        approx_eq(before.y, after.y);
    }

    #[test]
    fn cameras_stay_paired_with_graphs() {
        let editor = VisualEditor::new();
        assert_eq!(editor.cameras.len(), editor.graphs.len());
    }

    //MARK: - Graph load/save tests
    fn block(id: usize, x: f32, y: f32, kind: BlockKind) -> Block {
        Block {
            id,
            pos: Point { x, y },
            kind,
        }
    }

    fn v1_v2_fixture_graph() -> GraphFile {
        const IN_V1_V2: &[BlockType] = &[
            BlockType::Start,
            BlockType::End,
            BlockType::If,
            BlockType::If,
            BlockType::While,
            BlockType::For,
            BlockType::Add,
            BlockType::Subtract,
            BlockType::Multiply,
            BlockType::Divide,
            BlockType::Button,
            BlockType::LedBlink,
        ];

        let blocks: Vec<Block> = IN_V1_V2
            .iter()
            .enumerate()
            .map(|(i, t)| {
                block(
                    i,
                    i as f32 * 37.5 - 100.25,
                    -(i as f32) * 12.5 + 3.75,
                    t.default_kind(),
                )
            })
            .collect();

        GraphFile {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: Option::<DateTime<Utc>>::None,
                modified: Option::<DateTime<Utc>>::None,
            },
            graphs: vec![Graph::from_parts(
                "Graph 0",
                blocks.clone(),
                vec![
                    Wire {
                        from_block: 2,
                        from_port: 0,
                        to_block: 5,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 5,
                        from_port: 0,
                        to_block: 3,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 3,
                        from_port: 0,
                        to_block: 4,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 4,
                        from_port: 0,
                        to_block: 6,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 6,
                        from_port: 0,
                        to_block: 7,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 7,
                        from_port: 0,
                        to_block: 1,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 1,
                        from_port: 0,
                        to_block: 0,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 0,
                        from_port: 0,
                        to_block: 2,
                        to_port: 0,
                    },
                ],
            )],
            variables: Vec::new(),
            devices: Vec::new(),
        }
    }

    fn fixture_graph() -> GraphFile {
        let blocks: Vec<Block> = BlockType::ALL
            .iter()
            .enumerate()
            .map(|(i, kind)| {
                block(
                    i,
                    i as f32 * 37.5 - 100.25,
                    -(i as f32) * 12.5 + 3.75,
                    kind.default_kind(),
                )
            })
            .collect();
        GraphFile {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: Option::<DateTime<Utc>>::None,
                modified: Option::<DateTime<Utc>>::None,
            },
            graphs: vec![Graph::from_parts(
                "Graph 0",
                blocks.clone(),
                vec![
                    Wire {
                        from_block: 2,
                        from_port: 0,
                        to_block: 5,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 5,
                        from_port: 0,
                        to_block: 3,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 3,
                        from_port: 0,
                        to_block: 4,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 4,
                        from_port: 0,
                        to_block: 6,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 6,
                        from_port: 0,
                        to_block: 7,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 7,
                        from_port: 0,
                        to_block: 1,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 1,
                        from_port: 0,
                        to_block: 0,
                        to_port: 0,
                    },
                    Wire {
                        from_block: 0,
                        from_port: 0,
                        to_block: 2,
                        to_port: 0,
                    },
                ],
            )],
            variables: Vec::new(),
            devices: Vec::new(),
        }
    }

    #[test]
    fn empty_graph_round_trips() {
        let graph = GraphFile {
            meta: Meta::default(),
            graphs: vec![],
            variables: Vec::new(),
            devices: Vec::new(),
        };
        assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
    }

    #[test]
    fn simple_graph_round_trips() {
        let graph = GraphFile {
            meta: Meta {
                format_version: FORMAT_VERSION,
                created: Option::<DateTime<Utc>>::None,
                modified: Option::<DateTime<Utc>>::None,
            },
            graphs: vec![Graph::from_parts(
                "Graph 0",
                vec![
                    block(0, 10.0, 20.0, BlockKind::Basic(BasicBlock::Start)),
                    block(1, 30.0, 40.0, BlockKind::Basic(BasicBlock::End)),
                ],
                vec![Wire {
                    from_block: 0,
                    from_port: 0,
                    to_block: 1,
                    to_port: 0,
                }],
            )],
            variables: Vec::new(),
            devices: Vec::new(),
        };
        assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
    }

    #[test]
    #[ignore = "one-time generator: cargo test generate_fixture -- --ignored --nocapture"]
    fn generate_fixture() {
        std::fs::create_dir_all(concat!(env!("CARGO_MANIFEST_DIR"), "/tests/fixtures")).unwrap();
        std::fs::write(
            format!(
                "{}/tests/fixtures/v{}_fixture.omni",
                env!("CARGO_MANIFEST_DIR"),
                FORMAT_VERSION
            ),
            encode_graph(&fixture_graph()).unwrap(),
        )
        .unwrap();
    }

    #[test]
    fn v1_fixture_loads() {
        let bytes = include_bytes!("../tests/fixtures/v1_fixture.omni");
        let graph = decode_graph(bytes).unwrap();
        assert_eq!(graph, v1_v2_fixture_graph());
    }

    #[test]
    fn v2_fixture_loads() {
        let bytes = include_bytes!("../tests/fixtures/v2_fixture.omni");
        let graph = decode_graph(bytes).unwrap();
        assert_eq!(graph, v1_v2_fixture_graph());
    }

    #[test]
    fn bad_magic_rejected() {
        assert!(decode_graph(b"JUNKdata").is_err());
    }

    #[test]
    fn truncated_rejected() {
        assert!(decode_graph(b"OMN").is_err());
    }

    #[test]
    fn future_version_rejected() {
        let mut bytes = encode_graph(&GraphFile {
            meta: Meta::default(),
            graphs: vec![],
            variables: Vec::new(),
            devices: Vec::new(),
        })
        .unwrap();
        for v in [(FORMAT_VERSION + 1), (FORMAT_VERSION + 2)] {
            bytes[4..6].copy_from_slice(&v.to_le_bytes());
            let err = decode_graph(&bytes).unwrap_err();
            assert!(
                err.contains("newer version"),
                "version {v}: got: error: {err}"
            );
        }
    }

    #[test]
    fn version_zero_rejected() {
        let mut bytes = encode_graph(&GraphFile {
            meta: Meta::default(),
            graphs: vec![],
            variables: Vec::new(),
            devices: Vec::new(),
        })
        .unwrap();
        bytes[4..6].copy_from_slice(&0u16.to_le_bytes());
        assert!(decode_graph(&bytes)
            .unwrap_err()
            .contains("Unknown file version"));
    }

    fn arbitrary_block() -> impl Strategy<Value = BlockKind> {
        use crate::graph::BlockType;
        prop_oneof![
            Just(BlockType::Start.default_kind()),
            Just(BlockType::End.default_kind()),
            Just(BlockType::Timer.default_kind()),
            Just(BlockType::Networks.default_kind()),
            Just(BlockType::Return.default_kind()),
            Just(BlockType::If.default_kind()),
            Just(BlockType::While.default_kind()),
            Just(BlockType::WhileTrue.default_kind()),
            Just(BlockType::For.default_kind()),
            Just(BlockType::Switch.default_kind()),
            Just(BlockType::Lower.default_kind()),
            Just(BlockType::Greater.default_kind()),
            Just(BlockType::Equal.default_kind()),
            Just(BlockType::NotEqual.default_kind()),
            Just(BlockType::GreaterEqual.default_kind()),
            Just(BlockType::LowerEqual.default_kind()),
            Just(BlockType::Not.default_kind()),
            Just(BlockType::And.default_kind()),
            Just(BlockType::Nand.default_kind()),
            Just(BlockType::Or.default_kind()),
            Just(BlockType::Nor.default_kind()),
            Just(BlockType::Xor.default_kind()),
            Just(BlockType::Xnor.default_kind()),
            Just(BlockType::Add.default_kind()),
            Just(BlockType::Subtract.default_kind()),
            Just(BlockType::Multiply.default_kind()),
            Just(BlockType::Divide.default_kind()),
            Just(BlockType::Modulo.default_kind()),
            Just(BlockType::Power.default_kind()),
            Just(BlockType::Root.default_kind()),
            Just(BlockType::RandomNumber.default_kind()),
            Just(BlockType::Round.default_kind()),
            Just(BlockType::Floor.default_kind()),
            Just(BlockType::Ciel.default_kind()),
            Just(BlockType::AddOne.default_kind()),
            Just(BlockType::SubtractOne.default_kind()),
            Just(BlockType::Button.default_kind()),
            Just(BlockType::LedOn.default_kind()),
            Just(BlockType::LedOff.default_kind()),
            Just(BlockType::LedToggle.default_kind()),
            Just(BlockType::LedBlink.default_kind()),
            Just(BlockType::LedPwm.default_kind()),
            Just(BlockType::RgbLed.default_kind()),
        ]
    }

    fn arbitrary_graph() -> impl Strategy<Value = GraphFile> {
        (
            prop::collection::vec(
                (
                    any::<usize>(),
                    -1e6f32..1e6,
                    -1e6f32..1e6,
                    arbitrary_block(),
                ),
                0..40,
            ),
            prop::collection::vec((any::<usize>(), any::<usize>()), 0..40),
        )
            .prop_map(|(bs, ws)| GraphFile {
                meta: Meta {
                    format_version: FORMAT_VERSION,
                    created: Option::<DateTime<Utc>>::None,
                    modified: Option::<DateTime<Utc>>::None,
                },
                graphs: vec![Graph::from_parts(
                    "Graph 0",
                    bs.into_iter()
                        .map(|(id, x, y, kind)| block(id, x, y, kind))
                        .collect(),
                    ws.into_iter()
                        .map(|(from_block, to_block)| Wire {
                            from_block,
                            from_port: 0,
                            to_block,
                            to_port: 0,
                        })
                        .collect(),
                )],
                variables: Vec::new(),
                devices: Vec::new(),
            })
    }

    //MARK: - Property-based tests
    proptest! {
        #[test]
        fn any_graph_round_trips(graph in arbitrary_graph()) {
            prop_assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
        }

        #[test]
        fn garbage_never_panics(bytes in prop::collection::vec(any::<u8>(), 0..512)) {
            let _ = decode_graph(&bytes);
        }

         #[test]
        fn dist_to_segment_never_exceeds_endpoint_distance(
            px in -1e4f32..1e4, py in -1e4f32..1e4,
            ax in -1e4f32..1e4, ay in -1e4f32..1e4,
            bx in -1e4f32..1e4, by in -1e4f32..1e4,
        ) {
            let (p, a, b) = (Pos2::new(px, py), Pos2::new(ax, ay), Pos2::new(bx, by));
            let d = dist_to_segment(p, a, b);
            prop_assert!(d >= 0.0);
            prop_assert!(d <= p.distance(a).min(p.distance(b)) + 1e-2);
        }

        #[test]
        fn dist_to_segment_is_symmetric(
            px in -1e4f32..1e4, py in -1e4f32..1e4,
            ax in -1e4f32..1e4, ay in -1e4f32..1e4,
            bx in -1e4f32..1e4, by in -1e4f32..1e4,
        ) {
            let (p, a, b) = (Pos2::new(px, py), Pos2::new(ax, ay), Pos2::new(bx, by));
            prop_assert!((dist_to_segment(p, a, b) - dist_to_segment(p, b, a)).abs() < 1e-2);
        }

        #[test]
        fn wire_points_never_produces_nan(
            fx in -1e4f32..1e4, fy in -1e4f32..1e4,
            tx in -1e4f32..1e4, ty in -1e4f32..1e4,
        ) {
            for p in wire_points(Pos2::new(fx, fy), Pos2::new(tx, ty)) {
                prop_assert!(p.x.is_finite() && p.y.is_finite());
            }
        }
    }
}
