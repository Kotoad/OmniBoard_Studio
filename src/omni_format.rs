pub mod v1 {
    use serde::Deserialize;

    #[derive(Deserialize)]
    pub struct Meta {
        pub created: Option<chrono::DateTime<chrono::Utc>>,
        pub modified: Option<chrono::DateTime<chrono::Utc>>,
    }

    #[derive(Deserialize)]
    pub struct Pos2 {
        pub x: f32,
        pub y: f32,
    }

    #[derive(Deserialize)]
    pub enum BlockKind {
        Basic(BasicBlock),
        Logic(LogicBlock),
        Math(MathBlock),
        IO(IOBlock),
    }

    #[derive(Deserialize)]
    pub enum BasicBlock {
        Start,
        End,
    }
    #[derive(Deserialize)]
    pub enum LogicBlock {
        If,
        Else,
        While,
        For,
    }
    #[derive(Deserialize)]
    pub enum MathBlock {
        Add,
        Subtract,
        Multiply,
        Divide,
    }
    #[derive(Deserialize)]
    pub enum IOBlock {
        Input,
        Output,
    }

    #[derive(Deserialize)]
    pub struct Block {
        pub id: usize,
        pub pos: Pos2,
        pub kind: BlockKind,
    }

    #[derive(Deserialize)]
    pub struct Wire {
        pub from: usize,
        pub to: usize,
    }

    #[derive(Deserialize)]
    pub struct Graph {
        pub blocks: Vec<Block>,
        pub wires: Vec<Wire>,
    }

    #[derive(Deserialize)]
    pub struct GraphFile {
        pub meta: Meta,
        pub graphs: Vec<Graph>,
        pub next_block_id: usize,
    }
}

pub mod v2 {
    use serde::Deserialize;

    #[derive(Deserialize)]
    pub struct Meta {
        pub format_version: u16,
        pub created: Option<chrono::DateTime<chrono::Utc>>,
        pub modified: Option<chrono::DateTime<chrono::Utc>>,
    }

    #[derive(Deserialize)]
    pub struct Pos2 {
        pub x: f32,
        pub y: f32,
    }

    #[derive(Deserialize)]
    pub enum BlockKind {
        Basic(BasicBlock),
        Logic(LogicBlock),
        Math(MathBlock),
        IO(IOBlock),
    }

    #[derive(Deserialize)]
    pub enum BasicBlock {
        Start,
        End,
    }
    #[derive(Deserialize)]
    pub enum LogicBlock {
        If,
        Else,
        While,
        For,
    }
    #[derive(Deserialize)]
    pub enum MathBlock {
        Add,
        Subtract,
        Multiply,
        Divide,
    }
    #[derive(Deserialize)]
    pub enum IOBlock {
        Input,
        Output,
    }

    #[derive(Deserialize)]
    pub struct Block {
        pub id: usize,
        pub pos: Pos2,
        pub kind: BlockKind,
    }

    #[derive(Deserialize)]
    pub struct Wire {
        pub from: usize,
        pub to: usize,
    }

    #[derive(Deserialize)]
    pub struct Graph {
        pub name: String,
        pub blocks: Vec<Block>,
        pub wires: Vec<Wire>,
    }

    #[derive(Deserialize)]
    pub struct GraphFile {
        pub meta: Meta,
        pub graphs: Vec<Graph>,
    }
}
