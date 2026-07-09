use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Debug, Clone, Copy, PartialEq, Default)]
pub struct Point { pub x: f32, pub y: f32}

impl Point {
    pub fn translate(&mut self, dx: f32, dy: f32) {
        self.x += dx;
        self.y += dy;
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct Block { pub id: usize, pub pos: Point, pub kind: BlockKind }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct Wire { pub from: usize, pub to: usize }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq,)]
pub enum BlockKind { Basic(BasicBlock), Logic(LogicBlock), Math(MathBlock), IO(IOBlock) }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum BasicBlock { Start, End }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum LogicBlock { If, Else, While, For }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum MathBlock { Add, Subtract, Multiply, Divide }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum IOBlock { Input, Output }

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct Graph { 
    pub name: String,
    blocks: Vec<Block>,
    wires: Vec<Wire>,
    #[serde(skip)]
    next_block_id: usize,
}

pub enum ConnectError {
    SelfWire,
    DuplicateWire,
    FromOccupied,
    ToOccupied,
    NonexistentBlock,
}

impl BlockKind {
    pub const ALL: [BlockKind; 12] = [
        BlockKind::Basic(BasicBlock::Start),
        BlockKind::Basic(BasicBlock::End),
        BlockKind::Logic(LogicBlock::If),
        BlockKind::Logic(LogicBlock::Else),
        BlockKind::Logic(LogicBlock::While),
        BlockKind::Logic(LogicBlock::For),
        BlockKind::Math(MathBlock::Add),
        BlockKind::Math(MathBlock::Subtract),
        BlockKind::Math(MathBlock::Multiply),
        BlockKind::Math(MathBlock::Divide),
        BlockKind::IO(IOBlock::Input),
        BlockKind::IO(IOBlock::Output),
    ];
}

impl Graph {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            blocks: Vec::new(),
            wires: Vec::new(),
            next_block_id: 0,
        }
    }

    pub fn from_parts(name: impl Into<String>, blocks: Vec<Block>, wires: Vec<Wire>) -> Self {
        let mut graph = Self {
            name: name.into(),
            blocks,
            wires,
            next_block_id: 0,
        };
        graph.normalize();
        graph
    }

    pub fn peak_next_block_id(&self) -> usize {
        self.next_block_id
    }

    pub fn add_block(&mut self, kind: BlockKind, pos: Point) -> usize {
        let id = self.next_block_id;
        self.next_block_id += 1;
        let block = Block { id, pos, kind };
        self.blocks.push(block);
        id
    }

    pub fn delete_block(&mut self, block_id: usize) {
        self.blocks.retain(|b| b.id != block_id);
        self.wires.retain(|w| w.from != block_id && w.to != block_id);
    }

    pub fn duplicate_block(&mut self, block_id: usize, pos: Point) -> Option<usize> {
        if let Some(block) = self.blocks.iter().find(|b| b.id == block_id) {
            let new_id = self.add_block(block.kind.clone(), pos);
            Some(new_id)
        } else {
            None
        }
    }

    pub fn connect(&mut self, from: usize, to: usize) -> Result<(), ConnectError> {
        if from == to {
            return Err(ConnectError::SelfWire);
        } else if self.has_outgoing(from) {
            return Err(ConnectError::FromOccupied);
        } else if self.has_incoming(to) {
            return Err(ConnectError::ToOccupied);
        } else if !self.block_exists(from) || !self.block_exists(to) {
            return Err(ConnectError::NonexistentBlock);
        } else if self.wire_exists(from, to) {
            return Err(ConnectError::DuplicateWire);
        }
        self.wires.push(Wire { from, to });
        Ok(())
    }

    pub fn disconnect(&mut self, from: usize, to: usize) {
        self.wires.retain(|w| !(w.from == from && w.to == to));
    }

    pub fn block(&self, id: usize) -> Option<&Block> {
        self.blocks.iter().find(|b| b.id == id)
    }

    pub fn blocks(&self) -> &Vec<Block> {
        &self.blocks
    }

    pub fn blocks_mut(&mut self) -> impl Iterator<Item = &mut Block> {
        self.blocks.iter_mut()
    }

    pub fn wires(&self) -> &Vec<Wire> {
        &self.wires
    }

    pub fn block_exists(&self, id: usize) -> bool {
        self.blocks.iter().any(|b| b.id == id)
    }

    pub fn wire_exists(&self, from: usize, to: usize) -> bool {
        self.wires.iter().any(|w| w.from == from && w.to == to)
    }

    pub fn has_outgoing(&self, block_id: usize) -> bool {
        self.wires.iter().any(|w| w.from == block_id)
    }

    pub fn has_incoming(&self, block_id: usize) -> bool {
        self.wires.iter().any(|w| w.to == block_id)
    }

    pub fn normalize(&mut self) {
        self.next_block_id = self.blocks.iter().map(|b| b.id).max().map_or(0, |id| id + 1);
    }
}