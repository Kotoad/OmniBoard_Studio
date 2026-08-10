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
pub struct Wire {
    pub from_block: usize,
    pub from_port: u8,
    pub to_block: usize,
    pub to_port: u8
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum BlockKind {
    Basic(BasicBlock),
    Logic(LogicBlock),
    Math(MathBlock),
    IO(IOBlock),
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum ValueRef { Literal(f32), Variable(String) }

impl Default for ValueRef {
    fn default() -> Self {
        ValueRef::Literal(0.0)
    }
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum DeviceRef { Literal(f32), Device(String) }

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
    Pwm
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
pub enum CmpOp { Lower, Greater, #[default] Equal, NotEqual, GreaterEqual, LowerEqual }

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
            conditions: vec![
                Condition {
                    left_value: ValueRef::Literal(0.0),
                    operator: CmpOp::Equal,
                    right_value: ValueRef::Literal(0.0),
                }
            ],
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

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub struct Graph { 
    pub name: String,
    blocks: Vec<Block>,
    wires: Vec<Wire>,
    #[serde(skip)]
    next_block_id: usize,
    #[serde(skip)]
    zoom: f32,
}

pub enum ConnectError {
    SelfWire,
    DuplicateWire,
    FromOccupied,
    ToOccupied,
    NonexistentBlock,
    NoSuchPort,
}

#[derive(Deserialize, Serialize, Debug, Clone, PartialEq)]
pub enum BlockType { Start, End, Timer, Networks, Return, If,
    While, WhileTrue, For, Switch, Lower, Greater, Equal, NotEqual,
    GreaterEqual, LowerEqual, Not, And, Nand, Or, Nor, Xor, Xnor,
    Add, Subtract, Multiply, Divide, Modulo, Power, Root, RandomNumber,
    Round, Floor, Ciel, AddOne, SubtractOne,
    Button, LedOn, LedOff, LedToggle, LedBlink, LedPwm, RgbLed,
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
            BlockType::NotEqual => BlockKind::Logic(LogicBlock::NotEqual(ComparisonData::default())),
            BlockType::GreaterEqual => BlockKind::Logic(LogicBlock::GreaterEqual(ComparisonData::default())),
            BlockType::LowerEqual => BlockKind::Logic(LogicBlock::LowerEqual(ComparisonData::default())),
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
            BlockType::RandomNumber => BlockKind::Math(MathBlock::RandomNumber(RandomNumberData::default())),
            BlockType::Round => BlockKind::Math(MathBlock::Round(RoundFloorCielData::default())),
            BlockType::Floor => BlockKind::Math(MathBlock::Floor(RoundFloorCielData::default())),
            BlockType::Ciel => BlockKind::Math(MathBlock::Ciel(RoundFloorCielData::default())),
            BlockType::AddOne => BlockKind::Math(MathBlock::AddOne(AddSubtractOneData::default())),
            BlockType::SubtractOne => BlockKind::Math(MathBlock::SubtractOne(AddSubtractOneData::default())),
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
            BlockKind::Logic(LogicBlock::If(d))  => d.conditions.len() as u8 + d.has_else as u8,
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
            zoom: 1.0,
        }
    }

    pub fn from_parts(name: impl Into<String>, blocks: Vec<Block>, wires: Vec<Wire>) -> Self {
        let mut graph = Self {
            name: name.into(),
            blocks,
            wires,
            next_block_id: 0,
            zoom: 1.0,
        };
        graph.normalize();
        graph
    }

    pub fn peak_next_block_id(&self) -> usize {
        self.next_block_id
    }

    pub fn set_zoom(&mut self, zoom: f32) {
        self.zoom = zoom;
    }

    pub fn get_zoom(&self) -> f32 {
        self.zoom
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
        self.wires.retain(|w| w.from_block != block_id && w.to_block != block_id);
    }

    pub fn duplicate_block(&mut self, block_id: usize, pos: Point) -> Option<usize> {
        if let Some(block) = self.blocks.iter().find(|b| b.id == block_id) {
            let new_id = self.add_block(block.kind.clone(), pos);
            Some(new_id)
        } else {
            None
        }
    }

    pub fn connect(&mut self, from: (usize, u8), to: (usize, u8)) -> Result<(), ConnectError> {
        let (from_block, from_port) = from;
        let (to_block, to_port) = to;

        if from_block == to_block {
            return Err(ConnectError::SelfWire);
        } else if from_port >= self.block(from_block).map_or(0, |b| b.kind.out_ports()) || to_port >= self.block(to_block).map_or(0, |b| b.kind.in_ports()) {
            return Err(ConnectError::NoSuchPort);
        } else if self.has_outgoing(from) {
            return Err(ConnectError::FromOccupied);
        } else if self.has_incoming(to) {
            return Err(ConnectError::ToOccupied);
        } else if !self.block_exists(from_block) || !self.block_exists(to_block) {
            return Err(ConnectError::NonexistentBlock);
        } else if self.wire_exists(from, to) {
            return Err(ConnectError::DuplicateWire);
        }
        self.wires.push(Wire { from_block, to_block, from_port, to_port });
        Ok(())
    }

    pub fn disconnect(&mut self, from: (usize, u8), to: (usize, u8)) {
        self.wires.retain(|w| !(w.from_block == from.0 && w.from_port == from.1 && w.to_block == to.0 && w.to_port == to.1));
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

    pub fn wire_exists(&self, from: (usize, u8), to: (usize, u8)) -> bool {
        self.wires.iter().any(|w| w.from_block == from.0 && w.from_port == from.1 && w.to_block == to.0 && w.to_port == to.1)
    }

    pub fn has_outgoing(&self, (block_id, port): (usize, u8)) -> bool {
        self.wires.iter().any(|w| w.from_block == block_id && w.from_port == port)
    }

    pub fn has_incoming(&self, (block_id, port): (usize, u8)) -> bool {
        self.wires.iter().any(|w| w.to_block == block_id && w.to_port == port)
    }

    pub fn normalize(&mut self) {
        self.next_block_id = self.blocks.iter().map(|b| b.id).max().map_or(0, |id| id + 1);
        self.zoom = 1.0;
    }
}