use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Debug, Clone, Copy, PartialEq, Default)]
pub struct Point {
    pub x: f32,
    pub y: f32,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct Block {
    pub id: usize,
    pub pos: Point,
    pub kind: BlockKind,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct Wire {
    pub from_block: usize,
    pub from_port: u8,
    pub to_block: usize,
    pub to_port: u8,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum BlockKind {
    Basic(BasicBlock),
    Logic(LogicBlock),
    Math(MathBlock),
    IO(IOBlock),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum ValueRef {
    Literal(f32),
    Variable(String),
}

impl Default for ValueRef {
    fn default() -> Self {
        ValueRef::Literal(0.0)
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum DeviceRef {
    Literal(f32),
    Device(String),
}

impl Default for DeviceRef {
    fn default() -> Self {
        DeviceRef::Literal(0.0)
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct VariableDef {
    pub name: String,
    pub value: f32,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct DeviceDef {
    pub name: String,
    pub device_type: DeviceType,
    pub pin: u8,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum DeviceType {
    Output,
    Input,
    Button,
    Pwm,
}

//MARK: Basic Blocks
#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum BasicBlock {
    Start,
    End,
    Timer(TimerData),
    Networks(NetworksData),
    Return(ReturnData),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct TimerData {
    pub duration: f32,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct NetworksData {
    pub branches: u8,
}

impl Default for NetworksData {
    fn default() -> Self {
        Self { branches: 2 }
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct ReturnData {
    pub value: ValueRef,
}

//MARK: Logic Blocks
#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum LogicBlock {
    If(IfData),
    While(WhileData),
    WhileTrue,
    For(ForData),
    Switch(SwitchData),
    Lower(ComparisonData),
    Greater(ComparisonData),
    Equal(ComparisonData),
    NotEqual(ComparisonData),
    GreaterEqual(ComparisonData),
    LowerEqual(ComparisonData),
    Not(NotData),
    And(BoolComparisonData),
    Nand(BoolComparisonData),
    Or(BoolComparisonData),
    Nor(BoolComparisonData),
    Xor(BoolComparisonData),
    Xnor(BoolComparisonData),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub enum CmpOp {
    Lower,
    Greater,
    #[default]
    Equal,
    NotEqual,
    GreaterEqual,
    LowerEqual,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct Case {
    pub value: ValueRef,
    pub has_block: bool,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct Condition {
    pub left_value: ValueRef,
    pub operator: CmpOp,
    pub right_value: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct IfData {
    pub conditions: Vec<Condition>,
    pub has_else: bool,
}

impl Default for IfData {
    fn default() -> Self {
        Self {
            conditions: vec![Condition {
                left_value: ValueRef::Literal(0.0),
                operator: CmpOp::Equal,
                right_value: ValueRef::Literal(0.0),
            }],
            has_else: true,
        }
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct WhileData {
    pub condition: Condition,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct ForData {
    pub start: ValueRef,
    pub end: ValueRef,
    pub step: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct SwitchData {
    pub value: ValueRef,
    pub cases: Vec<Case>,
    pub has_default: bool,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct ComparisonData {
    pub left_value: ValueRef,
    pub right_value: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct NotData {
    pub value: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct BoolComparisonData {
    pub values: Vec<ValueRef>,
}

//MARK: Math Blocks
#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum MathBlock {
    Add(MathData),
    Subtract(MathData),
    Multiply(MathData),
    Divide(MathData),
    Modulo(MathData),
    Power(PowerData),
    Root(RootData),
    RandomNumber(RandomNumberData),
    Round(RoundFloorCielData),
    Floor(RoundFloorCielData),
    Ciel(RoundFloorCielData),
    AddOne(AddSubtractOneData),
    SubtractOne(AddSubtractOneData),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct MathData {
    pub result: ValueRef,
    pub value_1: ValueRef,
    pub value_2: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct PowerData {
    pub base: ValueRef,
    pub exponent: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct RootData {
    pub value: ValueRef,
    pub degree: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct RandomNumberData {
    pub min: ValueRef,
    pub max: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct RoundFloorCielData {
    pub value: ValueRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct AddSubtractOneData {
    pub value: ValueRef,
}

//MARK: IO Blocks
#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum IOBlock {
    Button(ButtonData),
    LedOn(LedControlData),
    LedOff(LedControlData),
    LedToggle(LedControlData),
    LedBlink(LedBlinkData),
    LedPwm(LedPwmData),
    RgbLed(RgbLedData),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct ButtonData {
    pub pressed: bool,
    pub controlled_value: DeviceRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct LedControlData {
    pub state: bool,
    pub controlled_value: DeviceRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct LedBlinkData {
    pub blink_duration: f32,
    pub controlled_value: DeviceRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct LedPwmData {
    pub pwm_value: ValueRef,
    pub controlled_value: DeviceRef,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Default)]
pub struct RgbLedData {
    pub red: ValueRef,
    pub green: ValueRef,
    pub blue: ValueRef,
    pub controlled_value: DeviceRef,
}

#[derive(Deserialize, Serialize, Debug, Clone)]
pub struct Graph {
    pub name: String,
    blocks: Vec<Block>,
    wires: Vec<Wire>,
    #[serde(skip)]
    next_block_id: usize,
    #[serde(skip)]
    block_index: std::collections::HashMap<usize, usize>,
    #[serde(skip)]
    out_wire: std::collections::HashMap<(usize, u8), (usize, u8)>, // (from_block, from_port) -> (to_block, to_port)
    #[serde(skip)]
    in_wire: std::collections::HashMap<(usize, u8), (usize, u8)>, // (to_block, to_port) -> (from_block, from_port
}

impl PartialEq for Graph {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.blocks == other.blocks && self.wires == other.wires
    }
}

pub enum ConnectError {
    SelfWire,
    DuplicateWire,
    FromOccupied,
    ToOccupied,
    NonexistentBlock,
    NoSuchPort,
}

#[derive(Deserialize, Serialize, Debug, Clone, Copy, PartialEq)]
pub enum BlockType {
    Start,
    End,
    Timer,
    Networks,
    Return,
    If,
    While,
    WhileTrue,
    For,
    Switch,
    Lower,
    Greater,
    Equal,
    NotEqual,
    GreaterEqual,
    LowerEqual,
    Not,
    And,
    Nand,
    Or,
    Nor,
    Xor,
    Xnor,
    Add,
    Subtract,
    Multiply,
    Divide,
    Modulo,
    Power,
    Root,
    RandomNumber,
    Round,
    Floor,
    Ciel,
    AddOne,
    SubtractOne,
    Button,
    LedOn,
    LedOff,
    LedToggle,
    LedBlink,
    LedPwm,
    RgbLed,
}

//MARK: Implementations
impl BlockType {
    pub const ALL: [BlockType; 43] = [
        BlockType::Start,
        BlockType::End,
        BlockType::Timer,
        BlockType::Networks,
        BlockType::Return,
        BlockType::If,
        BlockType::While,
        BlockType::WhileTrue,
        BlockType::For,
        BlockType::Switch,
        BlockType::Lower,
        BlockType::Greater,
        BlockType::Equal,
        BlockType::NotEqual,
        BlockType::GreaterEqual,
        BlockType::LowerEqual,
        BlockType::Not,
        BlockType::And,
        BlockType::Nand,
        BlockType::Or,
        BlockType::Nor,
        BlockType::Xor,
        BlockType::Xnor,
        BlockType::Add,
        BlockType::Subtract,
        BlockType::Multiply,
        BlockType::Divide,
        BlockType::Modulo,
        BlockType::Power,
        BlockType::Root,
        BlockType::RandomNumber,
        BlockType::Round,
        BlockType::Floor,
        BlockType::Ciel,
        BlockType::AddOne,
        BlockType::SubtractOne,
        BlockType::Button,
        BlockType::LedOn,
        BlockType::LedOff,
        BlockType::LedToggle,
        BlockType::LedBlink,
        BlockType::LedPwm,
        BlockType::RgbLed,
    ];

    pub fn default_kind(&self) -> BlockKind {
        match self {
            BlockType::Start => BlockKind::Basic(BasicBlock::Start),
            BlockType::End => BlockKind::Basic(BasicBlock::End),
            BlockType::Timer => BlockKind::Basic(BasicBlock::Timer(TimerData::default())),
            BlockType::Networks => BlockKind::Basic(BasicBlock::Networks(NetworksData::default())),
            BlockType::Return => BlockKind::Basic(BasicBlock::Return(ReturnData::default())),
            BlockType::If => BlockKind::Logic(LogicBlock::If(IfData::default())),
            BlockType::While => BlockKind::Logic(LogicBlock::While(WhileData::default())),
            BlockType::WhileTrue => BlockKind::Logic(LogicBlock::WhileTrue),
            BlockType::For => BlockKind::Logic(LogicBlock::For(ForData::default())),
            BlockType::Switch => BlockKind::Logic(LogicBlock::Switch(SwitchData::default())),
            BlockType::Lower => BlockKind::Logic(LogicBlock::Lower(ComparisonData::default())),
            BlockType::Greater => BlockKind::Logic(LogicBlock::Greater(ComparisonData::default())),
            BlockType::Equal => BlockKind::Logic(LogicBlock::Equal(ComparisonData::default())),
            BlockType::NotEqual => {
                BlockKind::Logic(LogicBlock::NotEqual(ComparisonData::default()))
            }
            BlockType::GreaterEqual => {
                BlockKind::Logic(LogicBlock::GreaterEqual(ComparisonData::default()))
            }
            BlockType::LowerEqual => {
                BlockKind::Logic(LogicBlock::LowerEqual(ComparisonData::default()))
            }
            BlockType::Not => BlockKind::Logic(LogicBlock::Not(NotData::default())),
            BlockType::And => BlockKind::Logic(LogicBlock::And(BoolComparisonData::default())),
            BlockType::Nand => BlockKind::Logic(LogicBlock::Nand(BoolComparisonData::default())),
            BlockType::Or => BlockKind::Logic(LogicBlock::Or(BoolComparisonData::default())),
            BlockType::Nor => BlockKind::Logic(LogicBlock::Nor(BoolComparisonData::default())),
            BlockType::Xor => BlockKind::Logic(LogicBlock::Xor(BoolComparisonData::default())),
            BlockType::Xnor => BlockKind::Logic(LogicBlock::Xnor(BoolComparisonData::default())),
            BlockType::Add => BlockKind::Math(MathBlock::Add(MathData::default())),
            BlockType::Subtract => BlockKind::Math(MathBlock::Subtract(MathData::default())),
            BlockType::Multiply => BlockKind::Math(MathBlock::Multiply(MathData::default())),
            BlockType::Divide => BlockKind::Math(MathBlock::Divide(MathData::default())),
            BlockType::Modulo => BlockKind::Math(MathBlock::Modulo(MathData::default())),
            BlockType::Power => BlockKind::Math(MathBlock::Power(PowerData::default())),
            BlockType::Root => BlockKind::Math(MathBlock::Root(RootData::default())),
            BlockType::RandomNumber => {
                BlockKind::Math(MathBlock::RandomNumber(RandomNumberData::default()))
            }
            BlockType::Round => BlockKind::Math(MathBlock::Round(RoundFloorCielData::default())),
            BlockType::Floor => BlockKind::Math(MathBlock::Floor(RoundFloorCielData::default())),
            BlockType::Ciel => BlockKind::Math(MathBlock::Ciel(RoundFloorCielData::default())),
            BlockType::AddOne => BlockKind::Math(MathBlock::AddOne(AddSubtractOneData::default())),
            BlockType::SubtractOne => {
                BlockKind::Math(MathBlock::SubtractOne(AddSubtractOneData::default()))
            }
            BlockType::Button => BlockKind::IO(IOBlock::Button(ButtonData::default())),
            BlockType::LedOn => BlockKind::IO(IOBlock::LedOn(LedControlData::default())),
            BlockType::LedOff => BlockKind::IO(IOBlock::LedOff(LedControlData::default())),
            BlockType::LedToggle => BlockKind::IO(IOBlock::LedToggle(LedControlData::default())),
            BlockType::LedBlink => BlockKind::IO(IOBlock::LedBlink(LedBlinkData::default())),
            BlockType::LedPwm => BlockKind::IO(IOBlock::LedPwm(LedPwmData::default())),
            BlockType::RgbLed => BlockKind::IO(IOBlock::RgbLed(RgbLedData::default())),
        }
    }
}

impl BlockKind {
    pub fn out_ports(&self) -> u8 {
        match self {
            BlockKind::Basic(BasicBlock::End) => 0,
            BlockKind::Basic(BasicBlock::Networks(NetworksData { branches })) => *branches,
            BlockKind::Basic(_) => 1,
            BlockKind::Logic(LogicBlock::If(d)) => d.conditions.len() as u8 + d.has_else as u8,
            BlockKind::Logic(LogicBlock::Switch(d)) => d.cases.len() as u8 + d.has_default as u8,
            BlockKind::Logic(LogicBlock::While(_d)) => 3,
            BlockKind::Logic(LogicBlock::For(_d)) => 2,
            BlockKind::Logic(LogicBlock::Lower(_d)) => 2,
            BlockKind::Logic(LogicBlock::Greater(_d)) => 2,
            BlockKind::Logic(LogicBlock::Equal(_d)) => 2,
            BlockKind::Logic(LogicBlock::NotEqual(_d)) => 2,
            BlockKind::Logic(LogicBlock::GreaterEqual(_d)) => 2,
            BlockKind::Logic(LogicBlock::LowerEqual(_d)) => 2,
            BlockKind::Logic(_) => 1,
            BlockKind::Math(_) => 1,
            BlockKind::IO(IOBlock::Button(_)) => 2,
            BlockKind::IO(_) => 1,
        }
    }

    pub fn in_ports(&self) -> u8 {
        match self {
            BlockKind::Basic(BasicBlock::Start) => 0,
            BlockKind::Basic(_) => 1,
            BlockKind::Logic(_) => 1,
            BlockKind::Math(_) => 1,
            BlockKind::IO(_) => 1,
        }
    }

    pub fn block_type(&self) -> BlockType {
        match self {
            BlockKind::Basic(BasicBlock::Start) => BlockType::Start,
            BlockKind::Basic(BasicBlock::End) => BlockType::End,
            BlockKind::Basic(BasicBlock::Timer(_)) => BlockType::Timer,
            BlockKind::Basic(BasicBlock::Networks(_)) => BlockType::Networks,
            BlockKind::Basic(BasicBlock::Return(_)) => BlockType::Return,
            BlockKind::Logic(LogicBlock::If(_)) => BlockType::If,
            BlockKind::Logic(LogicBlock::While(_)) => BlockType::While,
            BlockKind::Logic(LogicBlock::WhileTrue) => BlockType::WhileTrue,
            BlockKind::Logic(LogicBlock::For(_)) => BlockType::For,
            BlockKind::Logic(LogicBlock::Switch(_)) => BlockType::Switch,
            BlockKind::Logic(LogicBlock::Lower(_)) => BlockType::Lower,
            BlockKind::Logic(LogicBlock::Greater(_)) => BlockType::Greater,
            BlockKind::Logic(LogicBlock::Equal(_)) => BlockType::Equal,
            BlockKind::Logic(LogicBlock::NotEqual(_)) => BlockType::NotEqual,
            BlockKind::Logic(LogicBlock::GreaterEqual(_)) => BlockType::GreaterEqual,
            BlockKind::Logic(LogicBlock::LowerEqual(_)) => BlockType::LowerEqual,
            BlockKind::Logic(LogicBlock::Not(_)) => BlockType::Not,
            BlockKind::Logic(LogicBlock::And(_)) => BlockType::And,
            BlockKind::Logic(LogicBlock::Nand(_)) => BlockType::Nand,
            BlockKind::Logic(LogicBlock::Or(_)) => BlockType::Or,
            BlockKind::Logic(LogicBlock::Nor(_)) => BlockType::Nor,
            BlockKind::Logic(LogicBlock::Xor(_)) => BlockType::Xor,
            BlockKind::Logic(LogicBlock::Xnor(_)) => BlockType::Xnor,
            BlockKind::Math(MathBlock::Add(_)) => BlockType::Add,
            BlockKind::Math(MathBlock::Subtract(_)) => BlockType::Subtract,
            BlockKind::Math(MathBlock::Multiply(_)) => BlockType::Multiply,
            BlockKind::Math(MathBlock::Divide(_)) => BlockType::Divide,
            BlockKind::Math(MathBlock::Modulo(_)) => BlockType::Modulo,
            BlockKind::Math(MathBlock::Power(_)) => BlockType::Power,
            BlockKind::Math(MathBlock::Root(_)) => BlockType::Root,
            BlockKind::Math(MathBlock::RandomNumber(_)) => BlockType::RandomNumber,
            BlockKind::Math(MathBlock::Round(_)) => BlockType::Round,
            BlockKind::Math(MathBlock::Floor(_)) => BlockType::Floor,
            BlockKind::Math(MathBlock::Ciel(_)) => BlockType::Ciel,
            BlockKind::Math(MathBlock::AddOne(_)) => BlockType::AddOne,
            BlockKind::Math(MathBlock::SubtractOne(_)) => BlockType::SubtractOne,
            BlockKind::IO(IOBlock::Button(_)) => BlockType::Button,
            BlockKind::IO(IOBlock::LedOn(_)) => BlockType::LedOn,
            BlockKind::IO(IOBlock::LedOff(_)) => BlockType::LedOff,
            BlockKind::IO(IOBlock::LedToggle(_)) => BlockType::LedToggle,
            BlockKind::IO(IOBlock::LedBlink(_)) => BlockType::LedBlink,
            BlockKind::IO(IOBlock::LedPwm(_)) => BlockType::LedPwm,
            BlockKind::IO(IOBlock::RgbLed(_)) => BlockType::RgbLed,
        }
    }
}

//MARK: Graph Implementation
impl Graph {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            blocks: Vec::new(),
            wires: Vec::new(),
            next_block_id: 0,
            block_index: std::collections::HashMap::new(),
            out_wire: std::collections::HashMap::new(),
            in_wire: std::collections::HashMap::new(),
        }
    }

    pub fn from_parts(name: impl Into<String>, blocks: Vec<Block>, wires: Vec<Wire>) -> Self {
        let mut graph = Self {
            name: name.into(),
            blocks,
            wires,
            next_block_id: 0,
            block_index: std::collections::HashMap::new(),
            out_wire: std::collections::HashMap::new(),
            in_wire: std::collections::HashMap::new(),
        };
        graph.normalize();
        graph
    }

    //MARK: Block Management
    pub fn peek_next_block_id(&self) -> usize {
        self.next_block_id
    }

    pub fn add_block(&mut self, kind: BlockKind, pos: Point) -> usize {
        let id = self.next_block_id;
        self.next_block_id += 1;
        let block = Block { id, pos, kind };
        self.blocks.push(block);
        self.block_index.insert(id, self.blocks.len() - 1);
        #[cfg(debug_assertions)]
        self.assert_block_index_consistent();
        #[cfg(debug_assertions)]
        self.assert_wire_index_consistent();
        id
    }

    pub fn delete_block(&mut self, block_id: usize) {
        self.blocks.retain(|b| b.id != block_id);
        self.out_wire
            .retain(|k, v| k.0 != block_id && v.0 != block_id);
        self.in_wire
            .retain(|k, v| k.0 != block_id && v.0 != block_id);
        self.wires
            .retain(|w| w.from_block != block_id && w.to_block != block_id);

        self.rebuild_block_index();
        #[cfg(debug_assertions)]
        self.assert_block_index_consistent();
        #[cfg(debug_assertions)]
        self.assert_wire_index_consistent();
    }

    pub fn duplicate_block(&mut self, block_id: usize, pos: Point) -> Option<usize> {
        let kind = self.block(block_id)?.kind.clone();
        Some(self.add_block(kind, pos))
    }

    pub fn block(&self, id: usize) -> Option<&Block> {
        self.block_index
            .get(&id)
            .and_then(|&index| self.blocks.get(index))
    }

    pub fn blocks(&self) -> &Vec<Block> {
        &self.blocks
    }

    pub fn set_block_pos(&mut self, id: usize, x: f32, y: f32) {
        if let Some(block) = self
            .block_index
            .get(&id)
            .and_then(|&index| self.blocks.get_mut(index))
        {
            block.pos = Point { x, y };
        }
    }

    pub fn translate_block(&mut self, id: usize, dx: f32, dy: f32) {
        if let Some(block) = self
            .block_index
            .get(&id)
            .and_then(|&index| self.blocks.get_mut(index))
        {
            block.pos.x += dx;
            block.pos.y += dy;
        }
    }

    pub fn block_exists(&self, id: usize) -> bool {
        self.block_index.contains_key(&id)
    }

    //MARK: Wire Management
    pub fn connect(&mut self, from: (usize, u8), to: (usize, u8)) -> Result<(), ConnectError> {
        let (from_block, from_port) = from;
        let (to_block, to_port) = to;

        if !self.block_exists(from_block) || !self.block_exists(to_block) {
            return Err(ConnectError::NonexistentBlock);
        } else if self.wire_exists(from, to) {
            return Err(ConnectError::DuplicateWire);
        } else if from_block == to_block {
            return Err(ConnectError::SelfWire);
        } else if from_port >= self.block(from_block).map_or(0, |b| b.kind.out_ports())
            || to_port >= self.block(to_block).map_or(0, |b| b.kind.in_ports())
        {
            return Err(ConnectError::NoSuchPort);
        } else if self.has_outgoing(from) {
            return Err(ConnectError::FromOccupied);
        } else if self.has_incoming(to) {
            return Err(ConnectError::ToOccupied);
        }
        self.out_wire.insert(from, to);
        self.in_wire.insert(to, from);
        self.wires.push(Wire {
            from_block,
            to_block,
            from_port,
            to_port,
        });
        #[cfg(debug_assertions)]
        self.assert_wire_index_consistent();
        Ok(())
    }

    pub fn disconnect(&mut self, from: (usize, u8), to: (usize, u8)) {
        if self.out_wire.get(&from) == Some(&to) {
            self.out_wire.remove(&from);
            self.in_wire.remove(&to);
        }
        self.wires.retain(|w| {
            !(w.from_block == from.0
                && w.from_port == from.1
                && w.to_block == to.0
                && w.to_port == to.1)
        });
        #[cfg(debug_assertions)]
        self.assert_wire_index_consistent();
    }

    pub fn wires(&self) -> &Vec<Wire> {
        &self.wires
    }

    pub fn wire_exists(&self, from: (usize, u8), to: (usize, u8)) -> bool {
        self.out_wire.get(&from) == Some(&to) && self.in_wire.get(&to) == Some(&from)
    }

    pub fn has_outgoing(&self, (block_id, port): (usize, u8)) -> bool {
        self.out_wire.contains_key(&(block_id, port))
    }

    pub fn has_incoming(&self, (block_id, port): (usize, u8)) -> bool {
        self.in_wire.contains_key(&(block_id, port))
    }

    #[allow(dead_code)]
    pub fn successor(&self, from: (usize, u8)) -> Option<(usize, u8)> {
        self.out_wire.get(&from).copied()
    }

    #[allow(dead_code)]
    pub fn predecessor(&self, to: (usize, u8)) -> Option<(usize, u8)> {
        self.in_wire.get(&to).copied()
    }

    #[allow(dead_code)]
    pub fn out_edges(&self, block: usize) -> impl Iterator<Item = (u8, (usize, u8))> + '_ {
        let out_ports = self.block(block).unwrap().kind.out_ports();
        (0..out_ports).filter_map(move |port| self.successor((block, port)).map(|t| (port, t)))
    }

    //MARK: Graph Normalization
    pub fn normalize(&mut self) {
        self.next_block_id = self
            .blocks
            .iter()
            .map(|b| b.id)
            .max()
            .map_or(0, |id| id.saturating_add(1));

        self.rebuild_block_index();

        self.repair_wires();

        #[cfg(debug_assertions)]
        self.assert_block_index_consistent();
        #[cfg(debug_assertions)]
        self.assert_wire_index_consistent();
    }

    pub fn rebuild_block_index(&mut self) {
        self.block_index.clear();
        for (index, block) in self.blocks.iter().enumerate() {
            self.block_index.insert(block.id, index);
        }
    }

    pub fn repair_wires(&mut self) {
        self.out_wire.clear();
        self.in_wire.clear();
        let old_wires = std::mem::take(&mut self.wires);
        let mut repaired_wires = Vec::with_capacity(old_wires.len());

        for w in old_wires {
            let out_port_valid = self
                .block(w.from_block)
                .is_some_and(|b| w.from_port < b.kind.out_ports());
            let in_port_valid = self
                .block(w.to_block)
                .is_some_and(|b| w.to_port < b.kind.in_ports());
            let out_port_free = !self.out_wire.contains_key(&(w.from_block, w.from_port));
            let in_port_free = !self.in_wire.contains_key(&(w.to_block, w.to_port));
            let blocks_exist = self.block_exists(w.from_block) && self.block_exists(w.to_block);

            if out_port_valid && in_port_valid && out_port_free && in_port_free && blocks_exist {
                self.out_wire
                    .insert((w.from_block, w.from_port), (w.to_block, w.to_port));
                self.in_wire
                    .insert((w.to_block, w.to_port), (w.from_block, w.from_port));
                repaired_wires.push(w);
            }
        }

        self.wires = repaired_wires;
    }

    #[cfg(debug_assertions)]
    fn assert_block_index_consistent(&self) {
        debug_assert_eq!(self.block_index.len(), self.blocks.len());
        for (&id, &i) in &self.block_index {
            debug_assert_eq!(self.blocks.get(i).map(|b| b.id), Some(id));
        }
    }

    #[cfg(debug_assertions)]
    fn assert_wire_index_consistent(&self) {
        debug_assert_eq!(self.wires.len(), self.out_wire.len());
        debug_assert_eq!(self.wires.len(), self.in_wire.len());
        for w in &self.wires {
            debug_assert_eq!(
                self.out_wire.get(&(w.from_block, w.from_port)),
                Some(&(w.to_block, w.to_port))
            );
            debug_assert_eq!(
                self.in_wire.get(&(w.to_block, w.to_port)),
                Some(&(w.from_block, w.from_port))
            );
        }
    }
}

#[cfg(test)]
impl Graph {
    fn block_scan(&self, id: usize) -> Option<&Block> {
        self.blocks.iter().find(|b| b.id == id)
    }

    fn has_outgoing_wire(&self, (block_id, port): (usize, u8)) -> bool {
        self.wires
            .iter()
            .any(|w| w.from_block == block_id && w.from_port == port)
    }

    fn has_incoming_wire(&self, (block_id, port): (usize, u8)) -> bool {
        self.wires
            .iter()
            .any(|w| w.to_block == block_id && w.to_port == port)
    }

    fn has_wire(&self, from: (usize, u8), to: (usize, u8)) -> bool {
        self.wires.iter().any(|w| {
            w.from_block == from.0
                && w.from_port == from.1
                && w.to_block == to.0
                && w.to_port == to.1
        })
    }

    fn successor_scan(&self, (block_id, port): (usize, u8)) -> Option<(usize, u8)> {
        self.wires
            .iter()
            .find(|w| w.from_block == block_id && w.from_port == port)
            .map(|w| (w.to_block, w.to_port))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    #[derive(Debug, Clone)]
    enum Op {
        Add(usize),
        Delete(usize),
        Connect((usize, u8), (usize, u8)),
        Disconnect((usize, u8), (usize, u8)),
    }

    //MARK: Test Helpers
    const KINDS: [BlockType; 4] = [
        BlockType::Start,
        BlockType::End,
        BlockType::Timer,
        BlockType::If,
    ];

    fn graph_with(kinds: &[BlockType]) -> (Graph, Vec<usize>) {
        let mut graph = Graph::new("test");
        let ids = kinds
            .iter()
            .enumerate()
            .map(|(i, kind)| {
                graph.add_block(
                    kind.default_kind(),
                    Point {
                        x: i as f32 * 50.0,
                        y: 0.0,
                    },
                )
            })
            .collect();
        (graph, ids)
    }

    fn block(id: usize, kind: BlockType) -> Block {
        Block {
            id,
            pos: Point::default(),
            kind: kind.default_kind(),
        }
    }

    fn wire(from: (usize, u8), to: (usize, u8)) -> Wire {
        Wire {
            from_block: from.0,
            from_port: from.1,
            to_block: to.0,
            to_port: to.1,
        }
    }

    //MARK: Block Index
    #[test]
    fn block_lookup_matches_scan() {
        let (graph, ids) = graph_with(&[BlockType::Start, BlockType::Timer, BlockType::End]);

        for id in ids {
            assert_eq!(graph.block(id), graph.block_scan(id));
            assert!(graph.block_exists(id));
        }
        assert_eq!(graph.block(404), graph.block_scan(404));
        assert!(!graph.block_exists(404));
    }

    #[test]
    fn deleting_a_middle_block_keeps_lookups_correct() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer; 4]);

        graph.delete_block(ids[1]);

        assert_eq!(graph.block(ids[1]), None);
        assert!(!graph.block_exists(ids[1]));
        for id in [ids[0], ids[2], ids[3]] {
            assert_eq!(graph.block(id), graph.block_scan(id));
            assert_eq!(graph.block(id).map(|b| b.id), Some(id));
        }
    }

    #[test]
    fn deleting_a_block_removes_its_wires_and_index_entries() {
        let (mut graph, ids) = graph_with(&[BlockType::Start, BlockType::Timer, BlockType::End]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());
        assert!(graph.connect((ids[1], 0), (ids[2], 0)).is_ok());

        graph.delete_block(ids[1]);

        assert!(graph.wires().is_empty());
        assert_eq!(graph.successor((ids[0], 0)), None);
        assert_eq!(graph.predecessor((ids[2], 0)), None);
        assert!(!graph.has_outgoing((ids[0], 0)));
        assert!(!graph.has_incoming((ids[2], 0)));
    }

    #[test]
    fn block_ids_are_not_reused_after_a_delete() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer]);

        graph.delete_block(ids[1]);
        let new_id = graph.add_block(BlockType::Timer.default_kind(), Point::default());

        assert!(!ids.contains(&new_id));
        assert_eq!(graph.block(new_id).map(|b| b.id), Some(new_id));
    }

    #[test]
    fn duplicate_block_copies_the_kind_under_a_new_id() {
        let (mut graph, ids) = graph_with(&[BlockType::If]);

        let copy = graph
            .duplicate_block(ids[0], Point { x: 10.0, y: 10.0 })
            .expect("source block exists");

        assert_ne!(copy, ids[0]);
        assert_eq!(
            graph.block(copy).map(|b| &b.kind),
            graph.block(ids[0]).map(|b| &b.kind)
        );
        assert_eq!(graph.duplicate_block(404, Point::default()), None);
    }

    //MARK: Connect
    #[test]
    fn connect_rejects_nonexistent_blocks() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer]);

        assert!(matches!(
            graph.connect((404, 0), (ids[0], 0)),
            Err(ConnectError::NonexistentBlock)
        ));
        assert!(matches!(
            graph.connect((ids[0], 0), (404, 0)),
            Err(ConnectError::NonexistentBlock)
        ));
        assert!(graph.wires().is_empty());
    }

    #[test]
    fn connect_checks_existence_before_ports() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer]);

        // Port 9 does not exist either, but the missing block is reported first.
        assert!(matches!(
            graph.connect((404, 9), (ids[0], 0)),
            Err(ConnectError::NonexistentBlock)
        ));
    }

    #[test]
    fn connect_rejects_a_self_wire() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer]);

        assert!(matches!(
            graph.connect((ids[0], 0), (ids[0], 0)),
            Err(ConnectError::SelfWire)
        ));
        assert!(graph.wires().is_empty());
    }

    #[test]
    fn connect_rejects_a_duplicate_wire() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        assert!(matches!(
            graph.connect((ids[0], 0), (ids[1], 0)),
            Err(ConnectError::DuplicateWire)
        ));
        assert_eq!(graph.wires().len(), 1);
    }

    #[test]
    fn connect_rejects_ports_the_block_does_not_have() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer]);

        assert!(matches!(
            graph.connect((ids[0], 1), (ids[1], 0)),
            Err(ConnectError::NoSuchPort)
        ));
        assert!(matches!(
            graph.connect((ids[0], 0), (ids[1], 1)),
            Err(ConnectError::NoSuchPort)
        ));
    }

    #[test]
    fn connect_rejects_an_occupied_source_port() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        assert!(matches!(
            graph.connect((ids[0], 0), (ids[2], 0)),
            Err(ConnectError::FromOccupied)
        ));
        assert_eq!(graph.wires().len(), 1);
    }

    #[test]
    fn connect_rejects_an_occupied_target_port() {
        let (mut graph, ids) = graph_with(&[BlockType::If, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        assert!(matches!(
            graph.connect((ids[0], 1), (ids[1], 0)),
            Err(ConnectError::ToOccupied)
        ));
        assert_eq!(graph.wires().len(), 1);
    }

    //MARK: Disconnect
    #[test]
    fn disconnect_removes_the_wire_and_frees_both_ports() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        graph.disconnect((ids[0], 0), (ids[1], 0));

        assert!(graph.wires().is_empty());
        assert!(!graph.has_outgoing((ids[0], 0)));
        assert!(!graph.has_incoming((ids[1], 0)));
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());
    }

    #[test]
    fn disconnect_of_an_unknown_wire_is_a_noop() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        graph.disconnect((ids[0], 0), (ids[2], 0));
        graph.disconnect((404, 0), (ids[1], 0));

        assert_eq!(graph.wires().len(), 1);
        assert_eq!(graph.successor((ids[0], 0)), Some((ids[1], 0)));
        assert_eq!(graph.predecessor((ids[1], 0)), Some((ids[0], 0)));
    }

    //MARK: Adjacency
    #[test]
    fn successor_and_predecessor_are_inverses() {
        let (mut graph, ids) = graph_with(&[BlockType::Timer, BlockType::Timer]);
        assert!(graph.connect((ids[0], 0), (ids[1], 0)).is_ok());

        assert_eq!(graph.successor((ids[0], 0)), Some((ids[1], 0)));
        assert_eq!(graph.predecessor((ids[1], 0)), Some((ids[0], 0)));
        assert_eq!(graph.successor((ids[1], 0)), None);
        assert_eq!(graph.predecessor((ids[0], 0)), None);
    }

    #[test]
    fn out_edges_lists_only_connected_ports() {
        let (mut graph, ids) = graph_with(&[BlockType::If, BlockType::Timer]);
        assert!(graph.connect((ids[0], 1), (ids[1], 0)).is_ok());

        let edges: Vec<(u8, (usize, u8))> = graph.out_edges(ids[0]).collect();

        assert_eq!(edges, vec![(1, (ids[1], 0))]);
    }

    //MARK: Load Path
    #[test]
    fn from_parts_builds_the_indices() {
        let graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::Timer), block(1, BlockType::Timer)],
            vec![wire((0, 0), (1, 0))],
        );

        assert_eq!(graph.block(1).map(|b| b.id), Some(1));
        assert!(graph.block_exists(0));
        assert!(graph.has_outgoing((0, 0)));
        assert!(graph.has_incoming((1, 0)));
        assert_eq!(graph.successor((0, 0)), Some((1, 0)));
        assert_eq!(graph.predecessor((1, 0)), Some((0, 0)));
    }

    #[test]
    fn normalize_sets_the_next_id_past_the_highest_loaded_id() {
        let graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::Timer), block(7, BlockType::Timer)],
            Vec::new(),
        );

        assert_eq!(graph.peek_next_block_id(), 8);
    }

    #[test]
    fn repair_drops_wires_to_missing_blocks() {
        let graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::Timer)],
            vec![wire((0, 0), (99, 0))],
        );

        assert!(graph.wires().is_empty());
        assert!(!graph.has_outgoing((0, 0)));
    }

    #[test]
    fn repair_drops_wires_on_ports_the_block_does_not_have() {
        let graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::Timer), block(1, BlockType::Timer)],
            vec![wire((0, 3), (1, 0)), wire((0, 0), (1, 3))],
        );

        assert!(graph.wires().is_empty());
    }

    #[test]
    fn repair_keeps_the_first_wire_leaving_a_contested_port() {
        let graph = Graph::from_parts(
            "loaded",
            vec![
                block(0, BlockType::If),
                block(1, BlockType::Timer),
                block(2, BlockType::Timer),
            ],
            vec![wire((0, 0), (1, 0)), wire((0, 0), (2, 0))],
        );

        assert_eq!(graph.wires().len(), 1);
        assert_eq!(graph.successor((0, 0)), Some((1, 0)));
    }

    #[test]
    fn repair_keeps_the_first_wire_entering_a_contested_port() {
        let graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::If), block(1, BlockType::Timer)],
            vec![wire((0, 0), (1, 0)), wire((0, 1), (1, 0))],
        );

        assert_eq!(graph.wires().len(), 1);
        assert_eq!(graph.predecessor((1, 0)), Some((0, 0)));
    }

    #[test]
    fn normalize_is_idempotent() {
        let mut graph = Graph::from_parts(
            "loaded",
            vec![block(0, BlockType::If), block(1, BlockType::Timer)],
            vec![
                wire((0, 0), (1, 0)),
                wire((0, 0), (1, 0)),
                wire((0, 1), (99, 0)),
            ],
        );
        let once = graph.clone();

        graph.normalize();

        assert_eq!(graph, once);
        assert_eq!(graph.successor((0, 0)), once.successor((0, 0)));
        assert_eq!(graph.peek_next_block_id(), once.peek_next_block_id());
    }

    //MARK: Property-based Tests
    const MAX_PROBE_ID: usize = 12;
    const MAX_PROBE_PORT: u8 = 6;

    fn arb_port() -> impl Strategy<Value = (usize, u8)> {
        (0..8usize, 0..4u8)
    }

    fn arb_op() -> impl Strategy<Value = Op> {
        prop_oneof![
            3 => (0..KINDS.len()).prop_map(Op::Add),
            1 => (0..8usize).prop_map(Op::Delete),
            3 => (arb_port(), arb_port()).prop_map(|(from, to)| Op::Connect(from, to)),
            1 => (arb_port(), arb_port()).prop_map(|(from, to)| Op::Disconnect(from, to)),
        ]
    }

    fn apply(graph: &mut Graph, op: &Op) {
        match *op {
            Op::Add(kind) => {
                graph.add_block(KINDS[kind].default_kind(), Point::default());
            }
            Op::Delete(id) => graph.delete_block(id),
            Op::Connect(from, to) => {
                let _ = graph.connect(from, to);
            }
            Op::Disconnect(from, to) => graph.disconnect(from, to),
        }
    }

    /// Every indexed answer must equal the answer a linear scan would have given,
    /// and the two wire maps must stay mutual inverses of `wires`.
    fn check_indices(graph: &Graph) -> Result<(), TestCaseError> {
        prop_assert_eq!(graph.blocks().len(), graph.block_index.len());
        prop_assert_eq!(graph.wires().len(), graph.out_wire.len());
        prop_assert_eq!(graph.wires().len(), graph.in_wire.len());

        for w in graph.wires() {
            let from = (w.from_block, w.from_port);
            let to = (w.to_block, w.to_port);
            prop_assert_eq!(graph.successor(from), Some(to));
            prop_assert_eq!(graph.predecessor(to), Some(from));
            prop_assert!(graph.wire_exists(from, to));
        }

        for id in 0..MAX_PROBE_ID {
            prop_assert_eq!(graph.block(id), graph.block_scan(id));
            prop_assert_eq!(graph.block_exists(id), graph.block_scan(id).is_some());

            for port in 0..MAX_PROBE_PORT {
                let probe = (id, port);
                prop_assert_eq!(graph.has_outgoing(probe), graph.has_outgoing_wire(probe));
                prop_assert_eq!(graph.has_incoming(probe), graph.has_incoming_wire(probe));
                prop_assert_eq!(graph.successor(probe), graph.successor_scan(probe));
            }
        }

        for from_id in 0..MAX_PROBE_ID {
            for to_id in 0..MAX_PROBE_ID {
                let (from, to) = ((from_id, 0), (to_id, 0));
                prop_assert_eq!(graph.wire_exists(from, to), graph.has_wire(from, to));
            }
        }

        Ok(())
    }

    proptest! {
        #[test]
        fn indices_agree_with_linear_scans(ops in prop::collection::vec(arb_op(), 0..40)) {
            let mut graph = Graph::new("proptest");
            check_indices(&graph)?;

            for op in &ops {
                apply(&mut graph, op);
                check_indices(&graph)?;
            }
        }

        #[test]
        fn connect_adds_exactly_one_wire_or_changes_nothing(
            ops in prop::collection::vec(arb_op(), 0..30),
            from in arb_port(),
            to in arb_port(),
        ) {
            let mut graph = Graph::new("proptest");
            for op in &ops {
                apply(&mut graph, op);
            }
            let before = graph.wires().clone();

            let connected = graph.connect(from, to).is_ok();

            if connected {
                prop_assert_eq!(graph.wires().len(), before.len() + 1);
                prop_assert_eq!(graph.successor(from), Some(to));
            } else {
                prop_assert_eq!(graph.wires(), &before);
            }
            check_indices(&graph)?;
        }

        #[test]
        fn from_parts_repairs_arbitrary_wires(
            block_count in 0..6usize,
            raw_wires in prop::collection::vec((0..8usize, 0..4u8, 0..8usize, 0..4u8), 0..10),
        ) {
            let blocks = (0..block_count)
                .map(|id| block(id, KINDS[id % KINDS.len()]))
                .collect();
            let wires = raw_wires
                .into_iter()
                .map(|(fb, fp, tb, tp)| wire((fb, fp), (tb, tp)))
                .collect();

            let graph = Graph::from_parts("loaded", blocks, wires);

            check_indices(&graph)?;
            for w in graph.wires() {
                let from = graph.block(w.from_block).expect("wire source survived repair");
                let to = graph.block(w.to_block).expect("wire target survived repair");
                prop_assert!(w.from_port < from.kind.out_ports());
                prop_assert!(w.to_port < to.kind.in_ports());
            }
        }
    }
}
