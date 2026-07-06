use egui::{Pos2};
use serde::{Deserialize, Serialize};

use crate::state_machine;

pub struct BlockMeta {
    pub color: egui::Color32,
    pub title_key: &'static str,
    pub field_key: &'static str,
    pub description_key: &'static str,
}

impl BlockKind {
    pub const ALL: [BlockKind; 12] = [
        BlockKind::Basic(BasicBlockData::Start),
        BlockKind::Basic(BasicBlockData::End),
        BlockKind::Logic(LogicBlockData::If),
        BlockKind::Logic(LogicBlockData::Else),
        BlockKind::Logic(LogicBlockData::While),
        BlockKind::Logic(LogicBlockData::For),
        BlockKind::Math(MathBlockData::Add),
        BlockKind::Math(MathBlockData::Subtract),
        BlockKind::Math(MathBlockData::Multiply),
        BlockKind::Math(MathBlockData::Divide),
        BlockKind::IO(IOBlockData::Input),
        BlockKind::IO(IOBlockData::Output),
    ];

    pub fn category(&self) -> state_machine::BlocksLibraryTab {
        match self {
            BlockKind::Basic(_) => state_machine::BlocksLibraryTab::Basic,
            BlockKind::Logic(_) => state_machine::BlocksLibraryTab::Logic,
            BlockKind::Math(_) => state_machine::BlocksLibraryTab::Math,
            BlockKind::IO(_) => state_machine::BlocksLibraryTab::IO,
        }
    }

    pub fn meta(&self) -> BlockMeta {
        match self {
            BlockKind::Basic(BasicBlockData::Start) => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-start",
                field_key: "blocks-library-basic-blocks-tab-start-field",
                description_key: "blocks-library-basic-blocks-tab-start-description",
            },
            BlockKind::Basic(BasicBlockData::End) => BlockMeta {
                color: egui::Color32::from_rgb(214, 93, 93),
                title_key: "blocks-library-basic-blocks-tab-end",
                field_key: "blocks-library-basic-blocks-tab-end-field",
                description_key: "blocks-library-basic-blocks-tab-end-description",
            },
            BlockKind::Logic(LogicBlockData::If) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-if",
                field_key: "blocks-library-logic-blocks-tab-if-field",
                description_key: "blocks-library-logic-blocks-tab-if-description",
            },
            BlockKind::Logic(LogicBlockData::Else) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-else",
                field_key: "blocks-library-logic-blocks-tab-else-field",
                description_key: "blocks-library-logic-blocks-tab-else-description",
            },
            BlockKind::Logic(LogicBlockData::While) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-while",
                field_key: "blocks-library-logic-blocks-tab-while-field",
                description_key: "blocks-library-logic-blocks-tab-while-description",
            },
            BlockKind::Logic(LogicBlockData::For) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-for",
                field_key: "blocks-library-logic-blocks-tab-for-field",
                description_key: "blocks-library-logic-blocks-tab-for-description",
            },
            BlockKind::Math(MathBlockData::Add) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-add",
                field_key: "blocks-library-math-blocks-tab-add-field",
                description_key: "blocks-library-math-blocks-tab-add-description",
            },
            BlockKind::Math(MathBlockData::Subtract) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-subtract",
                field_key: "blocks-library-math-blocks-tab-subtract-field",
                description_key: "blocks-library-math-blocks-tab-subtract-description",
            },
            BlockKind::Math(MathBlockData::Multiply) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-multiply",
                field_key: "blocks-library-math-blocks-tab-multiply-field",
                description_key: "blocks-library-math-blocks-tab-multiply-description",
            },
            BlockKind::Math(MathBlockData::Divide) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-divide",
                field_key: "blocks-library-math-blocks-tab-divide-field",
                description_key: "blocks-library-math-blocks-tab-divide-description",
            },
            BlockKind::IO(IOBlockData::Input) => BlockMeta {
                color: egui::Color32::from_rgb(203, 146, 66),
                title_key: "blocks-library-io-blocks-tab-input",
                field_key: "blocks-library-io-blocks-tab-input-field",
                description_key: "blocks-library-io-blocks-tab-input-description",
            },
            BlockKind::IO(IOBlockData::Output) => BlockMeta {
                color: egui::Color32::from_rgb(203, 146, 66),
                title_key: "blocks-library-io-blocks-tab-output",
                field_key: "blocks-library-io-blocks-tab-output-field",
                description_key: "blocks-library-io-blocks-tab-output-description",
            },
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Block {
    pub id: usize,
    pub pos: egui::Pos2,
    #[serde(skip, default="rect_nothing")]
    pub rect: egui::Rect,
    pub kind: BlockKind,
    #[serde(skip)]
    pub wires: Wires,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, Default)]
pub struct Wires {
    pub from_wires: Vec<Wire>,
    pub to_wires: Vec<Wire>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Wire {
    pub from: usize,
    pub to: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum BlockKind {
    Basic(BasicBlockData),
    Logic(LogicBlockData),
    Math(MathBlockData),
    IO(IOBlockData),
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum BasicBlockData { Start, End }

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum LogicBlockData { If, Else, While, For }

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum MathBlockData { Add, Subtract, Multiply, Divide }

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum IOBlockData { Input, Output }

fn rect_nothing() -> egui::Rect {
    egui::Rect::NOTHING
}

impl Block {

    pub fn new(kind: BlockKind, pos: Pos2, id: usize) -> Self {
        Self { id, pos, kind, rect: egui::Rect::NOTHING, wires: Wires::default() }
    }

    pub fn color(&self) -> egui::Color32 {
        self.kind.meta().color
    }

    pub fn out_port(&self) -> egui::Pos2 { 
        egui::Pos2::new(self.rect.right(), self.rect.center().y)
    }

    pub fn in_port(&self)  -> egui::Pos2 {
        egui::Pos2::new(self.rect.left(), self.rect.center().y)
    }
}