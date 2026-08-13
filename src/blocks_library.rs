use crate::blocks_data::BlockSubCategory;
use crate::graph::BlockType;
use crate::state_machine;
use crate::translation_manager::LOADER;
use crate::visual_editor;

use egui::RichText;
use i18n_embed_fl::fl;
use log::debug;

#[allow(unused_macros)]
macro_rules! img_src_details {
    ($file:literal) => {
        egui::ImageSource::Bytes {
            uri: std::borrow::Cow::Borrowed(concat!("../resources/images/blocks_details/", $file)),
            bytes: egui::load::Bytes::Static(include_bytes!(concat!(
                "../resources/images/blocks_details/",
                $file
            ))),
        }
    };
}

fn show_block_details(
    editor: &mut visual_editor::VisualEditor,
    ui: &mut egui::Ui,
    block_kind: &BlockType,
) {
    let pal = state_machine::with(|sm| sm.get_current_palette());
    let block_title = LOADER.get(block_kind.meta().title_key);
    //let block_image = block_kind.meta().image;
    let block_description = LOADER.get(block_kind.meta().description_key);
    ui.vertical(|ui| {
        ui.heading(
            RichText::new(block_title.clone())
                .color(pal.text)
                .size(20.0)
                .strong(),
        );
        ui.separator();
        ui.heading(
            RichText::new(fl!(LOADER, "blocks-library-block-image-heading"))
                .color(pal.text)
                .size(18.0)
                .strong(),
        );
        //ui.image(img_src_details!(block_image));
        ui.separator();
        ui.heading(
            RichText::new(fl!(LOADER, "blocks-library-block-details-heading"))
                .color(pal.text)
                .size(18.0)
                .strong(),
        );
        ui.label(RichText::new(block_description).color(pal.text).size(16.0));
        if ui
            .button(fl!(
                LOADER,
                "blocks-library-add-block-button",
                block_name = block_title
            ))
            .clicked()
        {
            editor.add_block(block_kind.default_kind());
            debug!("Adding Block: {:?}", block_kind);
        }
    });
}

impl visual_editor::VisualEditor {
    fn show_blocks_library_tab(&mut self, ui: &mut egui::Ui, tab: state_machine::BlocksLibraryTab) {
        let kinds: Vec<BlockType> = BlockType::ALL
            .iter()
            .filter(|k| k.category() == tab)
            .cloned()
            .collect();

        if kinds.is_empty() {
            ui.label(fl!(LOADER, "blocks-library-tab-empty"));
            return;
        }

        let mut current_block = state_machine::with(|sm| sm.get_current_block());

        if current_block.category() != tab {
            match tab {
                state_machine::BlocksLibraryTab::Basic => {
                    current_block = state_machine::with(|sm| sm.get_current_basic_block())
                }
                state_machine::BlocksLibraryTab::Logic => {
                    current_block = state_machine::with(|sm| sm.get_current_logic_block())
                }
                state_machine::BlocksLibraryTab::Math => {
                    current_block = state_machine::with(|sm| sm.get_current_math_block())
                }
                state_machine::BlocksLibraryTab::IO => {
                    current_block = state_machine::with(|sm| sm.get_current_io_block())
                }
                _ => {}
            }
        }

        egui::SidePanel::left("blocks_library_panel")
            .resizable(true)
            .default_width(100.0)
            .show_inside(ui, |ui| {
                egui::ScrollArea::vertical()
                    .auto_shrink([false, false])
                    .show(ui, |ui| {
                        ui.with_layout(
                            egui::Layout::top_down_justified(egui::Align::Center),
                            |ui| {
                                let mut rendered: Vec<BlockSubCategory> = Vec::new();
                                for kind in kinds.iter() {
                                    match kind.sub_category() {
                                        None => {
                                            ui.selectable_value(
                                                &mut current_block,
                                                *kind,
                                                LOADER.get(kind.meta().title_key),
                                            );
                                        }
                                        Some(sub) => {
                                            if rendered.contains(&sub) {
                                                continue;
                                            }
                                            rendered.push(sub);
                                            egui::CollapsingHeader::new(
                                                LOADER.get(sub.header_key()),
                                            )
                                            .default_open(false)
                                            .show(
                                                ui,
                                                |ui| {
                                                    for kind in kinds
                                                        .iter()
                                                        .filter(|k| k.sub_category() == Some(sub))
                                                    {
                                                        ui.selectable_value(
                                                            &mut current_block,
                                                            *kind,
                                                            LOADER.get(kind.meta().title_key),
                                                        );
                                                    }
                                                },
                                            );
                                        }
                                    }
                                }
                            },
                        );
                        state_machine::with_mut(|sm| sm.set_current_block(current_block));
                    });
            });
        egui::CentralPanel::default().show_inside(ui, |ui| {
            show_block_details(self, ui, &current_block);
        });
    }

    pub(crate) fn blocks_library(&mut self, ctx: &egui::Context) {
        ctx.show_viewport_immediate(
            egui::ViewportId::from_hash_of("blocks_library"),
            egui::ViewportBuilder::default()
                .with_title(fl!(LOADER, "blocks-library-window-title"))
                .with_inner_size([600.0, 400.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    let mut blocks_library_tab =
                        state_machine::with(|sm| sm.get_blocks_library_tab());

                    egui::ScrollArea::horizontal().show(ui, |ui| {
                        ui.horizontal(|ui| {
                            ui.selectable_value(
                                &mut blocks_library_tab,
                                state_machine::BlocksLibraryTab::Basic,
                                fl!(LOADER, "blocks-library-tab-basic"),
                            );
                            ui.selectable_value(
                                &mut blocks_library_tab,
                                state_machine::BlocksLibraryTab::Logic,
                                fl!(LOADER, "blocks-library-tab-logic"),
                            );
                            ui.selectable_value(
                                &mut blocks_library_tab,
                                state_machine::BlocksLibraryTab::Math,
                                fl!(LOADER, "blocks-library-tab-math"),
                            );
                            ui.selectable_value(
                                &mut blocks_library_tab,
                                state_machine::BlocksLibraryTab::IO,
                                fl!(LOADER, "blocks-library-tab-io"),
                            );
                            ui.selectable_value(
                                &mut blocks_library_tab,
                                state_machine::BlocksLibraryTab::Functions,
                                fl!(LOADER, "blocks-library-tab-functions"),
                            );
                        });
                    });
                    state_machine::with_mut(|sm| sm.set_blocks_library_tab(blocks_library_tab));

                    ui.separator();

                    self.show_blocks_library_tab(ui, blocks_library_tab);
                });

                if ctx.input(|i| i.viewport().close_requested()) {
                    state_machine::with_mut(|sm| sm.on_close_blocks_library_window());
                }
            },
        );
    }
}
