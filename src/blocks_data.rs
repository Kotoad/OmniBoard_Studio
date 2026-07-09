use crate::state_machine;
use crate::graph::{BlockKind, BasicBlock, LogicBlock, MathBlock, IOBlock};

pub struct BlockMeta {
    pub color: egui::Color32,
    pub title_key: &'static str,
    pub field_key: &'static str,
    pub description_key: &'static str,
}

impl BlockKind {
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
            BlockKind::Basic(BasicBlock::Start) => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-start",
                field_key: "blocks-library-basic-blocks-tab-start-field",
                description_key: "blocks-library-basic-blocks-tab-start-description",
            },
            BlockKind::Basic(BasicBlock::End) => BlockMeta {
                color: egui::Color32::from_rgb(214, 93, 93),
                title_key: "blocks-library-basic-blocks-tab-end",
                field_key: "blocks-library-basic-blocks-tab-end-field",
                description_key: "blocks-library-basic-blocks-tab-end-description",
            },
            BlockKind::Logic(LogicBlock::If) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-if",
                field_key: "blocks-library-logic-blocks-tab-if-field",
                description_key: "blocks-library-logic-blocks-tab-if-description",
            },
            BlockKind::Logic(LogicBlock::Else) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-else",
                field_key: "blocks-library-logic-blocks-tab-else-field",
                description_key: "blocks-library-logic-blocks-tab-else-description",
            },
            BlockKind::Logic(LogicBlock::While) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-while",
                field_key: "blocks-library-logic-blocks-tab-while-field",
                description_key: "blocks-library-logic-blocks-tab-while-description",
            },
            BlockKind::Logic(LogicBlock::For) => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-for",
                field_key: "blocks-library-logic-blocks-tab-for-field",
                description_key: "blocks-library-logic-blocks-tab-for-description",
            },
            BlockKind::Math(MathBlock::Add) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-add",
                field_key: "blocks-library-math-blocks-tab-add-field",
                description_key: "blocks-library-math-blocks-tab-add-description",
            },
            BlockKind::Math(MathBlock::Subtract) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-subtract",
                field_key: "blocks-library-math-blocks-tab-subtract-field",
                description_key: "blocks-library-math-blocks-tab-subtract-description",
            },
            BlockKind::Math(MathBlock::Multiply) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-multiply",
                field_key: "blocks-library-math-blocks-tab-multiply-field",
                description_key: "blocks-library-math-blocks-tab-multiply-description",
            },
            BlockKind::Math(MathBlock::Divide) => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-divide",
                field_key: "blocks-library-math-blocks-tab-divide-field",
                description_key: "blocks-library-math-blocks-tab-divide-description",
            },
            BlockKind::IO(IOBlock::Input) => BlockMeta {
                color: egui::Color32::from_rgb(203, 146, 66),
                title_key: "blocks-library-io-blocks-tab-input",
                field_key: "blocks-library-io-blocks-tab-input-field",
                description_key: "blocks-library-io-blocks-tab-input-description",
            },
            BlockKind::IO(IOBlock::Output) => BlockMeta {
                color: egui::Color32::from_rgb(203, 146, 66),
                title_key: "blocks-library-io-blocks-tab-output",
                field_key: "blocks-library-io-blocks-tab-output-field",
                description_key: "blocks-library-io-blocks-tab-output-description",
            },
        }
    }
}