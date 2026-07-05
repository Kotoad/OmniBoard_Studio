use crate::visual_editor;
use crate::state_machine;
use crate::translation_manager::LOADER;

use log::debug;
use i18n_embed_fl::fl;

macro_rules! img_src_details {
    ($file:literal) => {
        egui::ImageSource::Bytes {
            uri: std::borrow::Cow::Borrowed(concat!("../resources/images/blocks_details/", $file)),
            bytes: egui::load::Bytes::Static(include_bytes!(concat!("../resources/images/blocks_details/", $file)))
        }
    };
}

impl visual_editor::VisualEditor {

    fn show_basic_blocks_library(&mut self, ui: &mut egui::Ui) {

        let mut current_block_details = state_machine::with(|sm| sm.get_current_basic_block_details());

        egui::SidePanel::left("basic_blocks_library_panel")
            .resizable(true)
            .default_width(100.0)
            .show_inside(ui, |ui| {
                egui::ScrollArea::vertical().auto_shrink([false, false]).show(ui, |ui| {
                    ui.with_layout(egui::Layout::top_down_justified(egui::Align::Center), |ui| {
                        ui.selectable_value(&mut current_block_details, state_machine::BasicBlock::Start, fl!(LOADER, "blocks-library-basic-blocks-tab-start"));
                        ui.selectable_value(&mut current_block_details, state_machine::BasicBlock::End, fl!(LOADER, "blocks-library-basic-blocks-tab-end"));
                    });
                    state_machine::with_mut(|sm| sm.set_current_basic_block_details(current_block_details));
                });
            });
        egui::CentralPanel::default().show_inside(ui, |ui| {
            match current_block_details {
                state_machine::BasicBlock::Start => {
                    ui.vertical(|ui| {
                        ui.heading(fl!(LOADER, "blocks-library-basic-blocks-tab-start"));
                        //ui.image(img_src_details!("start_block.png"));
                        ui.label(fl!(LOADER, "blocks-library-blocks-descriptions-start"));
                        if ui.button(fl!(LOADER, "blocks-library-add-block-button", block_name = fl!(LOADER, "blocks-library-basic-blocks-tab-start"))).clicked() {
                            let block = state_machine::Block::Basic(state_machine::BasicBlock::Start);
                            visual_editor::VisualEditor::add_block(self, block);
                            debug!("Adding Start Block");
                        }
                    });
                }
                state_machine::BasicBlock::End => {
                    ui.vertical(|ui| {
                        ui.heading(fl!(LOADER, "blocks-library-basic-blocks-tab-end"));
                        //ui.image(img_src_details!("end_block.png"));
                        ui.label(fl!(LOADER, "blocks-library-blocks-descriptions-end"));
                        if ui.button(fl!(LOADER, "blocks-library-add-block-button", block_name = fl!(LOADER, "blocks-library-basic-blocks-tab-end"))).clicked() {
                            let block = state_machine::Block::Basic(state_machine::BasicBlock::End);
                            visual_editor::VisualEditor::add_block(self, block);
                            debug!("Adding End Block");
                        }
                    });
                    
                }
            }
        });
    }

    fn show_logic_blocks_library(&mut self, ui: &mut egui::Ui) {
        ui.label("Logic Blocks Library");
    }

    fn show_math_blocks_library(&mut self, ui: &mut egui::Ui) {
        ui.label("Math Blocks Library");
    }

    fn show_io_blocks_library(&mut self, ui: &mut egui::Ui) {
        ui.label("IO Blocks Library");
    }

    fn show_functions_blocks_library(&mut self, ui: &mut egui::Ui) {
        ui.label("Functions Blocks Library");
    }

    pub(crate) fn blocks_library(&mut self, ctx: &egui::Context) {
        
        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("blocks_library"),
            egui::ViewportBuilder::default()
                .with_title(fl!(LOADER, "blocks-library-window-title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {

                    let mut blocks_library_tab = state_machine::with(|sm| sm.get_blocks_library_tab());

                    egui::ScrollArea::horizontal().show(ui, |ui| {
                        ui.horizontal(|ui| {
                            ui.selectable_value(&mut blocks_library_tab, state_machine::BlocksLibraryTab::Basic, fl!(LOADER, "blocks-library-tab-basic"));
                            ui.selectable_value(&mut blocks_library_tab, state_machine::BlocksLibraryTab::Logic, fl!(LOADER, "blocks-library-tab-logic"));
                            ui.selectable_value(&mut blocks_library_tab, state_machine::BlocksLibraryTab::Math, fl!(LOADER, "blocks-library-tab-math"));
                            ui.selectable_value(&mut blocks_library_tab, state_machine::BlocksLibraryTab::IO, fl!(LOADER, "blocks-library-tab-io"));
                            ui.selectable_value(&mut blocks_library_tab, state_machine::BlocksLibraryTab::Functions, fl!(LOADER, "blocks-library-tab-functions"));
                        });
                    });
                    state_machine::with_mut(|sm| sm.set_blocks_library_tab(blocks_library_tab));

                    ui.separator();

                    match blocks_library_tab {
                        state_machine::BlocksLibraryTab::Basic => {
                            self.show_basic_blocks_library(ui);
                        },
                        state_machine::BlocksLibraryTab::Logic => {
                            self.show_logic_blocks_library(ui);
                        },
                        state_machine::BlocksLibraryTab::Math => {
                            self.show_math_blocks_library(ui);
                        },
                        state_machine::BlocksLibraryTab::IO => {
                            self.show_io_blocks_library(ui);
                        },
                        state_machine::BlocksLibraryTab::Functions => {
                            self.show_functions_blocks_library(ui);
                        },
                    }
                });

                if ctx.input(|i| i.viewport().close_requested()) {
                    state_machine::with_mut(|sm| sm.on_close_blocks_library_window());
                }
            }
        );
    }
}

