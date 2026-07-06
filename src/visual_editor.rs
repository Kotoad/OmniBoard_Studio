use egui::{Color32, Pos2, RichText, Sense, Stroke, Vec2};
use i18n_embed_fl::fl;
use serde::{Deserialize, Serialize};
use log::{debug, error};

use crate::{blocks_data, state_machine};
use crate::translation_manager::LOADER;

const MAGIC: &[u8; 4] = b"OMNI";
const FORMAT_VERSION: u16 = 1;

#[derive(Clone, Copy)]
struct RunState {
    current: usize,
    deadline: f64,
}

pub(crate) struct VisualEditor {
    blocks: Vec<blocks_data::Block>,
    wires: Vec<blocks_data::Wire>,
    next_block_id: usize,

    wire_from: Option<usize>,
    selected: Option<usize>,
    run: Option<RunState>,

    canvas_offset: Vec2,
    pan_start: Pos2,
    panning: bool,
    
    snap_to_grid: bool,
    dirty: bool,
    context_wire: Option<(usize, usize)>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
struct GraphFile {
    blocks: Vec<blocks_data::Block>,
    wires: Vec<blocks_data::Wire>,
    next_block_id: usize,
}

//MARK: - Grapgic helpers
fn wire_points(from: Pos2, to: Pos2) -> Vec<Pos2> {
    let ctrl = ((to.x - from.x) * 0.5).max(40.0);
    let c0 = Pos2::new(from.x + ctrl, from.y);
    let c1 = Pos2::new(to.x - ctrl, to.y);
    (0..=24)
        .map(|i| {
            let t = i as f32 / 24.0;
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

fn encode_graph(file: &GraphFile) -> Result<Vec<u8>, String> {
    let payload = bincode::serde::encode_to_vec(file, bincode::config::standard()).map_err(|e| e.to_string())?;
    let mut out = Vec::with_capacity(6 + payload.len());
    out.extend_from_slice(MAGIC);
    out.extend_from_slice(&FORMAT_VERSION.to_le_bytes());
    out.extend_from_slice(&payload);
    Ok(out)
}

fn decode_graph(bytes: &[u8]) -> Result<GraphFile, String> {
    if bytes.len() < 6 || &bytes[..4] != MAGIC {
        return Err("Invalid file format".to_string());
    }
    let version = u16::from_le_bytes([bytes[4], bytes[5]]);
    if version != FORMAT_VERSION {
        return Err(format!(
            "Unsupported file version: {} (expected {})",
            version, FORMAT_VERSION
        ));
    }
    bincode::serde::decode_from_slice::<GraphFile, _>(&bytes[6..], bincode::config::standard())
        .map(|(file, _len)| file)
        .map_err(|e| e.to_string())
}

impl VisualEditor {
    pub(crate) fn new() -> Self {
        Self {
            blocks: Vec::new(),
            wires: Vec::new(),
            next_block_id: 0,

            wire_from: None,
            selected: None,
            run: None,

            canvas_offset: Vec2::ZERO,
            pan_start: Pos2::ZERO,
            panning: false,

            snap_to_grid: false,

            dirty: false,
            context_wire: None,
        }
    }

    //MARK: - Helpers
    fn block(&self, id: usize) -> Option<&blocks_data::Block> {
        self.blocks.iter().find(|b| b.id == id)
    }

    pub fn is_dirty(&self) -> bool {
        self.dirty
    }

    fn delete_block(&mut self, id: usize) {
        self.blocks.retain(|b| b.id != id);
        self.wires.retain(|w| w.from != id && w.to != id);
        self.blocks.iter_mut().for_each(|b| {
            b.wires.from_wires.retain(|w| w.from != id && w.to != id);
            b.wires.to_wires.retain(|w| w.from != id && w.to != id);
        });
        if self.selected == Some(id) {
            self.selected = None;
        }
        if self.run.map(|r| r.current) == Some(id) {
            self.run = None;
        }
        self.dirty = true;
    }

    fn duplicate_block(&mut self, id: usize) {
        if let Some(src) = self.block(id) {
            let mut copy = src.clone();
            copy.id = self.next_block_id;
            copy.pos += Vec2::new(20.0, 20.0);
            copy.rect = egui::Rect::NOTHING;
            copy.wires = blocks_data::Wires::default();
            self.next_block_id += 1;
            self.blocks.push(copy);
            self.dirty = true;
        }
    }

    pub fn save(&mut self, path: &std::path::Path) {
        let file = GraphFile {
            blocks: self.blocks.clone(),
            wires: self.wires.clone(),
            next_block_id: self.next_block_id,
        };
        match encode_graph(&file)
            .and_then(|bytes| std::fs::write(path, bytes).map_err(|e| e.to_string()))
        {
            Ok(()) => {debug!("Graph saved to {}", path.display()); self.dirty = false},
            Err(e) => error!("Failed to save graph: {}", e),
        }

        #[cfg(debug_assertions)]
        {
            let json_path = path.with_extension("omni.json");
            match serde_json::to_string_pretty(&file)
                .map_err(|e| e.to_string())
                .and_then(|json| std::fs::write(&json_path, json).map_err(|e| e.to_string()))
            {
                Ok(()) => {debug!("Graph saved to {}", json_path.display()); self.dirty = false},
                Err(e) => error!("Failed to save graph: {}", e),
            }
        }
    }

    pub fn load(&mut self, path: &std::path::Path) {
        if path.extension().and_then(|e| e.to_str()) == Some("omni") {
            match std::fs::read(path)
                .map_err(|e| e.to_string())
                .and_then(|bytes| decode_graph(&bytes))
            {
                Ok(file) => {
                    self.blocks = file.blocks;
                    self.wires = file.wires;
                    self.next_block_id = file.next_block_id;
                    self.selected = None;
                    self.run = None;
                    self.wire_from = None;
                    self.dirty = false;
                    debug!("Graph loaded from {}", path.display());
                }
                Err(e) => error!("Failed to load graph: {}", e),
            }
        } else if path.extension().and_then(|e| e.to_str()) == Some("json") {
            match std::fs::read_to_string(path)
                .map_err(|e| e.to_string())
                .and_then(|json| serde_json::from_str::<GraphFile>(&json).map_err(|e| e.to_string()))
            {
                Ok(file) => {
                    self.blocks = file.blocks;
                    self.wires = file.wires;
                    self.next_block_id = file.next_block_id;
                    self.selected = None;
                    self.run = None;
                    self.wire_from = None;
                    self.dirty = false;
                    debug!("Graph loaded from {}", path.display());
                }
                Err(e) => error!("Failed to load graph: {}", e),
            }
        }
    }

    pub fn add_block(&mut self, block_kind: blocks_data::BlockKind) {
        let id = self.next_block_id;
        self.next_block_id += 1;
        let pos = Pos2::new(100.0 + (id as f32 * 20.0), 100.0);
        let block = blocks_data::Block::new(block_kind, pos, id);
        self.blocks.push(block);
        self.dirty = true;
    }


    //MARK: - GUI
    pub(crate) fn show_visual_editor(&mut self, ctx: &egui::Context) {
        egui::CentralPanel::default().show(ctx, |ui| {
            let canvas_rect = ui.max_rect();
            let _response = ui.allocate_rect(canvas_rect, egui::Sense::click_and_drag());

            let pointer = ui.input(|i| i.pointer.hover_pos());
            let rmb_pressed = ui.input(|i| i.pointer.secondary_pressed());
            let rmb_released = ui.input(|i| i.pointer.secondary_released());
            let mmb_pressed = ui.input(|i| i.pointer.middle_down());

            //MARK: - Handle events
            if mmb_pressed {
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

            //MARK: - Draw grid
            let painter = ui.painter_at(canvas_rect);

            let pal = state_machine::with(|sm| sm.get_current_palette());

            let grid_size = 25.0;
            let ox = self.canvas_offset.x.rem_euclid(grid_size);
            let oy = self.canvas_offset.y.rem_euclid(grid_size);
            let mut x = canvas_rect.left() + ox;

            while x < canvas_rect.right() {
                painter.line_segment(
                    [Pos2::new(x, canvas_rect.top()), Pos2::new(x, canvas_rect.bottom())],
                    Stroke::new(1.0, pal.mid),
                );
                x += grid_size;
            }

            let mut y = canvas_rect.top() + oy;

            while y < canvas_rect.bottom() {
                painter.line_segment(
                    [Pos2::new(canvas_rect.left(), y), Pos2::new(canvas_rect.right(), y)],
                    Stroke::new(1.0, pal.mid),
                );
                y += grid_size;
            }

            //MARK: - Draw blocks
            let offset = self.canvas_offset;
            let selected = self.selected;
            let run_current = self.run.map(|r| r.current);
            let snap = self.snap_to_grid;
            let mut pending_delete: Option<usize> = None;
            let mut pending_duplicate: Option<usize> = None;
            let mut pending_select: Option<usize> = None;

            for block in &mut self.blocks{
                let area = egui::Area::new(egui::Id::new(("block", block.id)))
                    .fixed_pos(block.pos + offset)
                    .movable(false)
                    .constrain(false)
                    .order(egui::Order::Middle);

                let resp = area.show(ctx, |ui| {
                    ui.set_clip_rect(canvas_rect);
                    ui.set_max_width(190.0);

                    let outline = if run_current == Some(block.id) {
                        Stroke::new(3.0, Color32::from_rgb(255, 210, 80))
                    } else if selected == Some(block.id) {
                        Stroke::new(2.5, Color32::WHITE)
                    } else {
                        Stroke::new(2.0, blocks_data::Block::color(block))
                    };

                    let shell = egui::Frame::none()
                        .fill(Color32::from_rgb(18, 18, 22))
                        .stroke(outline)
                        .rounding(6.0)
                        .inner_margin(egui::Margin::ZERO)
                        .show(ui, |ui| {
                            ui.set_min_width(170.0);
                            ui.spacing_mut().item_spacing.y = 0.0;

                            let header = egui::Frame::none()
                                .fill(blocks_data::Block::color(block))
                                .rounding(egui::Rounding { nw: 5.0, ne: 5.0, sw: 0.0, se: 0.0 })
                                .inner_margin(egui::Margin::symmetric(8.0, 5.0))
                                .show(ui, |ui| {
                                    ui.set_min_width(170.0);
                                    ui.horizontal(|ui| {
                                        let block_kind = LOADER.get(block.kind.meta().title_key);
                                        ui.label(RichText::new(block_kind).color(Color32::WHITE).strong());

                                        ui.with_layout(
                                            egui::Layout::right_to_left(egui::Align::Center),
                                            |ui| {
                                                ui.label(
                                                RichText::new(format!("#{}", block.id))
                                                        .small()
                                                        .color(Color32::from_white_alpha(140)),
                                                );
                                            }
                                        );
                                    });
                                });

                                let header_drag = header.response.interact(Sense::click_and_drag());
                                if header_drag.dragged_by(egui::PointerButton::Primary) {
                                    block.pos += header_drag.drag_delta();
                                    ui.ctx().set_cursor_icon(egui::CursorIcon::Grabbing);
                                    self.dirty = true;
                                } else if header_drag.hovered() {
                                    ui.ctx().set_cursor_icon(egui::CursorIcon::Grab);
                                }
                                if header_drag.drag_stopped_by(egui::PointerButton::Primary) && snap {
                                    block.pos = Pos2::new(
                                        (block.pos.x /  grid_size).round() * grid_size,
                                        (block.pos.y /  grid_size).round() * grid_size,
                                    );
                                }
                                if header_drag.clicked() {
                                    pending_select = Some(block.id);
                                }
                                header_drag.context_menu(|ui| {
                                    if ui.button(fl!(LOADER, "main-gui-block-context-menu-duplicate")).clicked() {
                                        pending_duplicate = Some(block.id);
                                        ui.close_menu();
                                    }
                                    if ui.button(fl!(LOADER, "main-gui-block-context-menu-delete")).clicked() {
                                        pending_delete = Some(block.id);
                                        ui.close_menu();
                                    }
                                });

                                egui::Frame::none()
                                    .inner_margin(egui::Margin::same(8.0))
                                    .show(ui, |ui| {
                                        ui.spacing_mut().item_spacing.y = 4.0;
                                        ui.label(RichText::new(LOADER.get(block.kind.meta().field_key)).color(Color32::from_white_alpha(200)));
                                    })
                        });
                    let rect = shell.response.rect;
                    let painter = ui.painter();
                    let op = Pos2::new(rect.right(), rect.center().y);
                    let ip = Pos2::new(rect.left(), rect.center().y);
                    let out_hot = pointer.is_some_and(|p| p.distance(op) < 16.0);
                    let in_hot = pointer.is_some_and(|p| p.distance(ip) < 16.0);
                    painter.circle_filled(op, if out_hot { 7.0 } else { 5.0 }, Color32::WHITE);
                    painter.circle_stroke(op, if out_hot { 7.0 } else { 5.0 }, Stroke::new(1.5, Color32::BLACK));
                    painter.circle_filled(ip, if in_hot { 7.0 } else { 5.0 }, Color32::from_rgb(180, 220, 200));
                    painter.circle_stroke(ip, if in_hot { 7.0 } else { 5.0 }, Stroke::new(1.5, Color32::BLACK));
                });

                block.rect = resp.response.rect
            }

            if let Some(id) = pending_select {
                self.selected = Some(id);
            }
            if let Some(id) = pending_delete {
                self.delete_block(id);
            }
            if let Some(id) = pending_duplicate {
                self.duplicate_block(id);
            }

            //MARK: - Wire events
            let mut grabbed_port = false;
            if let Some(pos) = pointer {
                if rmb_pressed {
                    for block in &self.blocks {
                        if pos.distance(block.out_port()) < 16.0 {
                            if block.wires.from_wires.is_empty() {
                                self.wire_from = Some(block.id);
                                grabbed_port = true;
                                break;
                            }
                        }
                    }
                }
                if rmb_released {
                    if let Some(from) = self.wire_from.take() {
                        let from_idx = self.blocks.iter().position(|b| b.id == from);
                        for to_idx in 0..self.blocks.len() {
                            if self.blocks[to_idx].id != from && pos.distance(self.blocks[to_idx].in_port()) < 16.0 {
                                let to_id = self.blocks[to_idx].id;
                                let dup = self.wires.iter().any(|w| w.from == from && w.to == to_id);
                                if !dup {
                                    let wire = blocks_data::Wire { from, to: to_id };
                                    self.wires.push(wire.clone());
                                    if let Some(from_idx) = from_idx {
                                        self.blocks[from_idx].wires.from_wires.push(wire.clone());
                                    }
                                    self.blocks[to_idx].wires.to_wires.push(wire.clone());
                                    self.dirty = true;
                                }
                                break;
                            }
                        }
                    }
                }
            }

            //MARK: - Draw wires
            let mut hovered_wire: Option<usize> = None;
            let mut wire_paths: Vec<Vec<Pos2>> = Vec::with_capacity(self.wires.len());
            for (i, wire) in self.wires.iter().enumerate() {
                let path = match (self.block(wire.from), self.block(wire.to)) {
                    (Some(from), Some(to)) => wire_points(from.out_port(), to.in_port()),
                    _ => Vec::new(),
                };
                if hovered_wire.is_none() {
                    if let Some(p) = pointer {
                        if !path.is_empty() && canvas_rect.contains(p) && dist_to_polyline(p, &path) < 6.0 {
                            hovered_wire = Some(i);
                        }
                    }
                }
                wire_paths.push(path);
            }
            if _response.secondary_clicked() && !grabbed_port {
                self.context_wire = hovered_wire.map(|i| (self.wires[i].from, self.wires[i].to));
            }
            _response.context_menu(|ui| {
                if let Some((from, to)) = self.context_wire {
                    if ui.button(fl!(LOADER, "main-gui-wire-context-menu-delete")).clicked() {
                        self.wires.retain(|w| !(w.from == from && w.to == to));
                        self.blocks.iter_mut().for_each(|b| {
                            b.wires.from_wires.retain(|w| !(w.from == from && w.to == to));
                            b.wires.to_wires.retain(|w| !(w.from == from && w.to == to));
                        });
                        ui.close_menu();
                    }
                }
            });
            let wire_painter = ctx
                .layer_painter(egui::LayerId::new(
                    egui::Order::Background,
                    egui::Id::new("wires"),
                ))
                .with_clip_rect(canvas_rect);
            for (i, path) in wire_paths.iter().enumerate() {
                let (width, color) = if hovered_wire == Some(i) {
                    (4.0, Color32::from_rgb(255, 100, 100))
                } else {
                    (2.5, Color32::from_rgb(80, 200, 160))
                };
                for seg in path.windows(2) {
                    wire_painter.line_segment([seg[0], seg[1]], Stroke::new(width, color));
                }
            }

            let fg = ctx
                .layer_painter(egui::LayerId::new(
                    egui::Order::Foreground,
                    egui::Id::new("overlay"),
                ))
                .with_clip_rect(canvas_rect);
            if let (Some(from), Some(pos)) = (self.wire_from, pointer) {
                if let Some(block) = self.blocks.iter().find(|b| b.id == from) {
                    for seg in wire_points(block.out_port(), pos).windows(2) {
                        fg.line_segment([seg[0], seg[1]], Stroke::new(2.5, Color32::from_rgb(255, 100, 60)));
                    }
                }
            }
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;
    use crate::{blocks_data::{BasicBlockData, Block, BlockKind, Wire, Wires}, translation_manager};

    fn block(id: usize, x: f32, y: f32, kind: BlockKind) -> Block {
        Block {
            id,
            pos: Pos2::new(x, y),
            rect: egui::Rect::NOTHING,
            kind,
            wires: Wires::default(),
        }
    }

    #[test]
    fn all_block_meta_keys_exist() {
        let (loader, langs) = translation_manager::all_languages_loader();
        for lang in &langs {
            let ids: std::collections::HashSet<String> =
                loader.with_message_iter(lang, |iter| iter.map(|m| m.id.name.to_string()).collect());
            for kind in blocks_data::BlockKind::ALL {
                let m = kind.meta();
                for key in &[m.title_key, m.field_key, m.description_key] {
                    assert!(ids.contains(*key), "Missing i18n key: {} in language {}", key, lang);
                }
            }
        }
    }

    #[test]
    fn empty_graph_round_trips() {
        let graph = GraphFile {blocks: vec![], wires: vec![], next_block_id: 0};
        assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
    }

    #[test]
    fn simple_graph_round_trips() {
        let graph = GraphFile {
            blocks: vec![
                block(0, 10.0, 20.0, BlockKind::Basic(BasicBlockData::Start)),
                block(1, 30.0, 40.0, BlockKind::Basic(BasicBlockData::End)),
            ],
            wires: vec![Wire { from: 0, to: 1 }],
            next_block_id: 2,
        };
        assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
    }

    #[test]
    fn bad_magic_rejected() { assert!(decode_graph(b"JUNKdata").is_err()); }

    #[test]
    fn truncated_rejected() { assert!(decode_graph(b"OMN").is_err()); }

    #[test]
    fn future_version_rejected() {
        let mut bytes = encode_graph(&GraphFile { blocks: vec![], wires: vec![], next_block_id: 0 }).unwrap();
        bytes[4..6].copy_from_slice(&99u16.to_le_bytes());
        let err = decode_graph(&bytes).unwrap_err();
        assert!(err.contains("Unsupported file version"));
    }

    fn arbitrary_block() -> impl Strategy<Value = BlockKind> {
        use crate::blocks_data::{BasicBlockData::*, LogicBlockData::*, MathBlockData::*, IOBlockData::*};
        prop_oneof![
            Just(BlockKind::Basic(Start)),
            Just(BlockKind::Basic(End)),
            Just(BlockKind::Logic(If)),
            Just(BlockKind::Logic(Else)),
            Just(BlockKind::Logic(While)),
            Just(BlockKind::Logic(For)),
            Just(BlockKind::Math(Add)),
            Just(BlockKind::Math(Subtract)),
            Just(BlockKind::Math(Multiply)),
            Just(BlockKind::Math(Divide)),
            Just(BlockKind::IO(Input)),
            Just(BlockKind::IO(Output))
        ]
    }

    fn arbitrary_graph() -> impl Strategy<Value = GraphFile> {
        (
            prop::collection::vec((any::<usize>(), -1e6f32..1e6, -1e6f32..1e6, arbitrary_block()), 0..40),
            prop::collection::vec((any::<usize>(), any::<usize>()), 0..40),
            any::<usize>(),
        ).prop_map(|(bs, ws, next)| GraphFile {
            blocks: bs.into_iter().map(|(id, x, y, kind)| block(id, x, y, kind)).collect(),
            wires: ws.into_iter().map(|(from, to)| Wire { from, to }).collect(),
            next_block_id: next,
        })
    }

    proptest! {
        #[test]
        fn any_graph_round_trips(graph in arbitrary_graph()) {
            prop_assert_eq!(decode_graph(&encode_graph(&graph).unwrap()).unwrap(), graph);
        }

        #[test]
        fn garbage_never_panics(bytes in prop::collection::vec(any::<u8>(), 0..512)) {
            let _ = decode_graph(&bytes);
        }
    }
}  