use egui::{Pos2};
use serde::{Deserialize, Serialize};

use crate::{state_machine};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub id: usize,
    pub pos: egui::Pos2,
    #[serde(skip, default="rect_nothing")]
    pub rect: egui::Rect,
    pub kind: BlockKind,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Wire {
    pub from: usize,
    pub to: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BlockKind {
    Basic(BasicBlockData),
    Logic(LogicBlockData),
    Math(MathBlockData),
    IO(IOBlockData),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BasicBlockData { Start, End }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum LogicBlockData { If, Else, While, For }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MathBlockData { Add, Subtract, Multiply, Divide }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IOBlockData { Input, Output }

fn rect_nothing() -> egui::Rect {
    egui::Rect::NOTHING
}

impl Block {

    pub fn new(block_kind: state_machine::Block, pos: Pos2, id: usize) -> Self {
        let kind = match block_kind {
            state_machine::Block::Basic(state_machine::BasicBlock::Start) => BlockKind::Basic(BasicBlockData::Start),
            state_machine::Block::Basic(state_machine::BasicBlock::End) => BlockKind::Basic(BasicBlockData::End),
            state_machine::Block::Logic(state_machine::LogicBlock::If) => BlockKind::Logic(LogicBlockData::If),
            state_machine::Block::Logic(state_machine::LogicBlock::Else) => BlockKind::Logic(LogicBlockData::Else),
            state_machine::Block::Logic(state_machine::LogicBlock::While) => BlockKind::Logic(LogicBlockData::While),
            state_machine::Block::Logic(state_machine::LogicBlock::For) => BlockKind::Logic(LogicBlockData::For),
            state_machine::Block::Math(state_machine::MathBlock::Add) => BlockKind::Math(MathBlockData::Add),
            state_machine::Block::Math(state_machine::MathBlock::Subtract) => BlockKind::Math(MathBlockData::Subtract),
            state_machine::Block::Math(state_machine::MathBlock::Multiply) => BlockKind::Math(MathBlockData::Multiply),
            state_machine::Block::Math(state_machine::MathBlock::Divide) => BlockKind::Math(MathBlockData::Divide),
            state_machine::Block::IO(state_machine::IOBlock::Input) => BlockKind::IO(IOBlockData::Input),
            state_machine::Block::IO(state_machine::IOBlock::Output) => BlockKind::IO(IOBlockData::Output),
        };
        Self { id, pos, kind, rect: egui::Rect::NOTHING }
    }

    pub fn color(&self) -> egui::Color32 {
        match self.kind {
            BlockKind::Basic(BasicBlockData::Start) => egui::Color32::from_rgb(106, 174, 139),
            BlockKind::Basic(BasicBlockData::End) => egui::Color32::from_rgb(214, 93, 93),
            BlockKind::Logic(LogicBlockData::If) => egui::Color32::from_rgb(122, 155, 201),
            BlockKind::Logic(LogicBlockData::Else) => egui::Color32::from_rgb(122, 155, 201),
            BlockKind::Logic(LogicBlockData::While) => egui::Color32::from_rgb(122, 155, 201),
            BlockKind::Logic(LogicBlockData::For) => egui::Color32::from_rgb(122, 155, 201),
            BlockKind::Math(MathBlockData::Add) => egui::Color32::from_rgb(94, 178, 178),
            BlockKind::Math(MathBlockData::Subtract) => egui::Color32::from_rgb(94, 178, 178),
            BlockKind::Math(MathBlockData::Multiply) => egui::Color32::from_rgb(94, 178, 178),
            BlockKind::Math(MathBlockData::Divide) => egui::Color32::from_rgb(94, 178, 178),
            BlockKind::IO(IOBlockData::Input) => egui::Color32::from_rgb(203, 146, 66),
            BlockKind::IO(IOBlockData::Output) => egui::Color32::from_rgb(203, 146, 66),
        }
    }

    pub fn out_port(&self) -> egui::Pos2 { 
        egui::Pos2::new(self.rect.right(), self.rect.center().y)
    }

    pub fn in_port(&self)  -> egui::Pos2 {
        egui::Pos2::new(self.rect.left(), self.rect.center().y)
    }
}