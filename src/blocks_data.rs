use crate::graph::BlockType;
use crate::state_machine;

pub struct BlockMeta {
    pub color: egui::Color32,
    pub title_key: &'static str,
    pub field_key: &'static str,
    pub description_key: &'static str,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum BlockSubCategory {
    ControlFlow,
    Comparison,
    BoolLogic,
    BasicMath,
    LEDControl,
}

impl BlockSubCategory {
    pub fn header_key(&self) -> &'static str {
        match self {
            BlockSubCategory::ControlFlow => "blocks-library-subcategory-control-flow",
            BlockSubCategory::Comparison => "blocks-library-subcategory-comparison",
            BlockSubCategory::BoolLogic => "blocks-library-subcategory-bool-logic",
            BlockSubCategory::BasicMath => "blocks-library-subcategory-basic-math",
            BlockSubCategory::LEDControl => "blocks-library-subcategory-led-control",
        }
    }
}

impl BlockType {
    pub fn category(&self) -> state_machine::BlocksLibraryTab {
        match self {
            BlockType::Start => state_machine::BlocksLibraryTab::Basic,
            BlockType::End => state_machine::BlocksLibraryTab::Basic,
            BlockType::Timer => state_machine::BlocksLibraryTab::Basic,
            BlockType::Networks => state_machine::BlocksLibraryTab::Basic,
            BlockType::Return => state_machine::BlocksLibraryTab::Basic,
            BlockType::If => state_machine::BlocksLibraryTab::Logic,
            BlockType::While => state_machine::BlocksLibraryTab::Logic,
            BlockType::WhileTrue => state_machine::BlocksLibraryTab::Logic,
            BlockType::For => state_machine::BlocksLibraryTab::Logic,
            BlockType::Switch => state_machine::BlocksLibraryTab::Logic,
            BlockType::Lower => state_machine::BlocksLibraryTab::Logic,
            BlockType::Greater => state_machine::BlocksLibraryTab::Logic,
            BlockType::Equal => state_machine::BlocksLibraryTab::Logic,
            BlockType::NotEqual => state_machine::BlocksLibraryTab::Logic,
            BlockType::GreaterEqual => state_machine::BlocksLibraryTab::Logic,
            BlockType::LowerEqual => state_machine::BlocksLibraryTab::Logic,
            BlockType::Not => state_machine::BlocksLibraryTab::Logic,
            BlockType::And => state_machine::BlocksLibraryTab::Logic,
            BlockType::Nand => state_machine::BlocksLibraryTab::Logic,
            BlockType::Or => state_machine::BlocksLibraryTab::Logic,
            BlockType::Nor => state_machine::BlocksLibraryTab::Logic,
            BlockType::Xor => state_machine::BlocksLibraryTab::Logic,
            BlockType::Xnor => state_machine::BlocksLibraryTab::Logic,
            BlockType::Add => state_machine::BlocksLibraryTab::Math,
            BlockType::Subtract => state_machine::BlocksLibraryTab::Math,
            BlockType::Multiply => state_machine::BlocksLibraryTab::Math,
            BlockType::Divide => state_machine::BlocksLibraryTab::Math,
            BlockType::Modulo => state_machine::BlocksLibraryTab::Math,
            BlockType::Power => state_machine::BlocksLibraryTab::Math,
            BlockType::Root => state_machine::BlocksLibraryTab::Math,
            BlockType::RandomNumber => state_machine::BlocksLibraryTab::Math,
            BlockType::Round => state_machine::BlocksLibraryTab::Math,
            BlockType::Floor => state_machine::BlocksLibraryTab::Math,
            BlockType::Ciel => state_machine::BlocksLibraryTab::Math,
            BlockType::AddOne => state_machine::BlocksLibraryTab::Math,
            BlockType::SubtractOne => state_machine::BlocksLibraryTab::Math,
            BlockType::Button => state_machine::BlocksLibraryTab::IO,
            BlockType::LedOn => state_machine::BlocksLibraryTab::IO,
            BlockType::LedOff => state_machine::BlocksLibraryTab::IO,
            BlockType::LedToggle => state_machine::BlocksLibraryTab::IO,
            BlockType::LedBlink => state_machine::BlocksLibraryTab::IO,
            BlockType::LedPwm => state_machine::BlocksLibraryTab::IO,
            BlockType::RgbLed => state_machine::BlocksLibraryTab::IO,
        }
    }

    pub fn sub_category(&self) -> Option<BlockSubCategory> {
        match self {
            BlockType::If
            | BlockType::While
            | BlockType::WhileTrue
            | BlockType::For
            | BlockType::Switch => Some(BlockSubCategory::ControlFlow),
            BlockType::Lower
            | BlockType::Greater
            | BlockType::Equal
            | BlockType::NotEqual
            | BlockType::GreaterEqual
            | BlockType::LowerEqual => Some(BlockSubCategory::Comparison),
            BlockType::Not
            | BlockType::And
            | BlockType::Nand
            | BlockType::Or
            | BlockType::Nor
            | BlockType::Xor
            | BlockType::Xnor => Some(BlockSubCategory::BoolLogic),
            BlockType::Add
            | BlockType::Subtract
            | BlockType::Multiply
            | BlockType::Divide
            | BlockType::Modulo
            | BlockType::Power
            | BlockType::Root => Some(BlockSubCategory::BasicMath),
            BlockType::LedOn
            | BlockType::LedOff
            | BlockType::LedToggle
            | BlockType::LedBlink
            | BlockType::LedPwm
            | BlockType::RgbLed => Some(BlockSubCategory::LEDControl),
            _ => None,
        }
    }

    pub fn meta(&self) -> BlockMeta {
        match self {
            //MARK: Basic Blocks
            BlockType::Start => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-start",
                field_key: "blocks-library-basic-blocks-tab-start-field",
                description_key: "blocks-library-basic-blocks-tab-start-description",
            },
            BlockType::End => BlockMeta {
                color: egui::Color32::from_rgb(214, 93, 93),
                title_key: "blocks-library-basic-blocks-tab-end",
                field_key: "blocks-library-basic-blocks-tab-end-field",
                description_key: "blocks-library-basic-blocks-tab-end-description",
            },
            BlockType::Timer => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-timer",
                field_key: "blocks-library-basic-blocks-tab-timer-field",
                description_key: "blocks-library-basic-blocks-tab-timer-description",
            },
            BlockType::Networks => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-networks",
                field_key: "blocks-library-basic-blocks-tab-networks-field",
                description_key: "blocks-library-basic-blocks-tab-networks-description",
            },
            BlockType::Return => BlockMeta {
                color: egui::Color32::from_rgb(106, 174, 139),
                title_key: "blocks-library-basic-blocks-tab-return",
                field_key: "blocks-library-basic-blocks-tab-return-field",
                description_key: "blocks-library-basic-blocks-tab-return-description",
            },
            //MARK: Logic Blocks
            BlockType::If => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-if",
                field_key: "blocks-library-logic-blocks-tab-if-field",
                description_key: "blocks-library-logic-blocks-tab-if-description",
            },
            BlockType::While => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-while",
                field_key: "blocks-library-logic-blocks-tab-while-field",
                description_key: "blocks-library-logic-blocks-tab-while-description",
            },
            BlockType::WhileTrue => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-while-true",
                field_key: "blocks-library-logic-blocks-tab-while-true-field",
                description_key: "blocks-library-logic-blocks-tab-while-true-description",
            },
            BlockType::For => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-for",
                field_key: "blocks-library-logic-blocks-tab-for-field",
                description_key: "blocks-library-logic-blocks-tab-for-description",
            },
            BlockType::Switch => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-switch",
                field_key: "blocks-library-logic-blocks-tab-switch-field",
                description_key: "blocks-library-logic-blocks-tab-switch-description",
            },
            BlockType::Lower => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-lower",
                field_key: "blocks-library-logic-blocks-tab-lower-field",
                description_key: "blocks-library-logic-blocks-tab-lower-description",
            },
            BlockType::Greater => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-greater",
                field_key: "blocks-library-logic-blocks-tab-greater-field",
                description_key: "blocks-library-logic-blocks-tab-greater-description",
            },
            BlockType::Equal => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-equal",
                field_key: "blocks-library-logic-blocks-tab-equal-field",
                description_key: "blocks-library-logic-blocks-tab-equal-description",
            },
            BlockType::NotEqual => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-not-equal",
                field_key: "blocks-library-logic-blocks-tab-not-equal-field",
                description_key: "blocks-library-logic-blocks-tab-not-equal-description",
            },
            BlockType::GreaterEqual => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-greater-equal",
                field_key: "blocks-library-logic-blocks-tab-greater-equal-field",
                description_key: "blocks-library-logic-blocks-tab-greater-equal-description",
            },
            BlockType::LowerEqual => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-lower-equal",
                field_key: "blocks-library-logic-blocks-tab-lower-equal-field",
                description_key: "blocks-library-logic-blocks-tab-lower-equal-description",
            },
            BlockType::Not => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-not",
                field_key: "blocks-library-logic-blocks-tab-not-field",
                description_key: "blocks-library-logic-blocks-tab-not-description",
            },
            BlockType::And => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-and",
                field_key: "blocks-library-logic-blocks-tab-and-field",
                description_key: "blocks-library-logic-blocks-tab-and-description",
            },
            BlockType::Nand => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-nand",
                field_key: "blocks-library-logic-blocks-tab-nand-field",
                description_key: "blocks-library-logic-blocks-tab-nand-description",
            },
            BlockType::Or => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-or",
                field_key: "blocks-library-logic-blocks-tab-or-field",
                description_key: "blocks-library-logic-blocks-tab-or-description",
            },
            BlockType::Nor => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-nor",
                field_key: "blocks-library-logic-blocks-tab-nor-field",
                description_key: "blocks-library-logic-blocks-tab-nor-description",
            },
            BlockType::Xor => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-xor",
                field_key: "blocks-library-logic-blocks-tab-xor-field",
                description_key: "blocks-library-logic-blocks-tab-xor-description",
            },
            BlockType::Xnor => BlockMeta {
                color: egui::Color32::from_rgb(122, 155, 201),
                title_key: "blocks-library-logic-blocks-tab-xnor",
                field_key: "blocks-library-logic-blocks-tab-xnor-field",
                description_key: "blocks-library-logic-blocks-tab-xnor-description",
            },
            //MARK: Math Blocks
            BlockType::Add => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-add",
                field_key: "blocks-library-math-blocks-tab-add-field",
                description_key: "blocks-library-math-blocks-tab-add-description",
            },
            BlockType::Subtract => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-subtract",
                field_key: "blocks-library-math-blocks-tab-subtract-field",
                description_key: "blocks-library-math-blocks-tab-subtract-description",
            },
            BlockType::Multiply => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-multiply",
                field_key: "blocks-library-math-blocks-tab-multiply-field",
                description_key: "blocks-library-math-blocks-tab-multiply-description",
            },
            BlockType::Divide => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-divide",
                field_key: "blocks-library-math-blocks-tab-divide-field",
                description_key: "blocks-library-math-blocks-tab-divide-description",
            },
            BlockType::Modulo => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-modulo",
                field_key: "blocks-library-math-blocks-tab-modulo-field",
                description_key: "blocks-library-math-blocks-tab-modulo-description",
            },
            BlockType::Power => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-power",
                field_key: "blocks-library-math-blocks-tab-power-field",
                description_key: "blocks-library-math-blocks-tab-power-description",
            },
            BlockType::Root => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-root",
                field_key: "blocks-library-math-blocks-tab-root-field",
                description_key: "blocks-library-math-blocks-tab-root-description",
            },
            BlockType::RandomNumber => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-random-number",
                field_key: "blocks-library-math-blocks-tab-random-number-field",
                description_key: "blocks-library-math-blocks-tab-random-number-description",
            },
            BlockType::Round => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-round",
                field_key: "blocks-library-math-blocks-tab-round-field",
                description_key: "blocks-library-math-blocks-tab-round-description",
            },
            BlockType::Floor => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-floor",
                field_key: "blocks-library-math-blocks-tab-floor-field",
                description_key: "blocks-library-math-blocks-tab-floor-description",
            },
            BlockType::Ciel => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-ceil",
                field_key: "blocks-library-math-blocks-tab-ceil-field",
                description_key: "blocks-library-math-blocks-tab-ceil-description",
            },
            BlockType::AddOne => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-add-one",
                field_key: "blocks-library-math-blocks-tab-add-one-field",
                description_key: "blocks-library-math-blocks-tab-add-one-description",
            },
            BlockType::SubtractOne => BlockMeta {
                color: egui::Color32::from_rgb(94, 178, 178),
                title_key: "blocks-library-math-blocks-tab-subtract-one",
                field_key: "blocks-library-math-blocks-tab-subtract-one-field",
                description_key: "blocks-library-math-blocks-tab-subtract-one-description",
            },
            //MARK: IO Blocks
            BlockType::Button => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-button",
                field_key: "blocks-library-io-blocks-tab-button-field",
                description_key: "blocks-library-io-blocks-tab-button-description",
            },
            BlockType::LedOn => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-led-on",
                field_key: "blocks-library-io-blocks-tab-led-on-field",
                description_key: "blocks-library-io-blocks-tab-led-on-description",
            },
            BlockType::LedOff => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-led-off",
                field_key: "blocks-library-io-blocks-tab-led-off-field",
                description_key: "blocks-library-io-blocks-tab-led-off-description",
            },
            BlockType::LedToggle => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-led-toggle",
                field_key: "blocks-library-io-blocks-tab-led-toggle-field",
                description_key: "blocks-library-io-blocks-tab-led-toggle-description",
            },
            BlockType::LedBlink => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-led-blink",
                field_key: "blocks-library-io-blocks-tab-led-blink-field",
                description_key: "blocks-library-io-blocks-tab-led-blink-description",
            },
            BlockType::LedPwm => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-led-pwm",
                field_key: "blocks-library-io-blocks-tab-led-pwm-field",
                description_key: "blocks-library-io-blocks-tab-led-pwm-description",
            },
            BlockType::RgbLed => BlockMeta {
                color: egui::Color32::from_rgb(255, 206, 84),
                title_key: "blocks-library-io-blocks-tab-rgb-led",
                field_key: "blocks-library-io-blocks-tab-rgb-led-field",
                description_key: "blocks-library-io-blocks-tab-rgb-led-description",
            },
        }
    }
}
