use egui::{
    self, FontId, Rounding, Ui, TextFormat
};
use egui::text::LayoutJob;

pub fn file_button_simple(ui: &mut Ui, filename: &str, created: &str, last_modified: &str) -> egui::Response {

    let mut job = LayoutJob::default();

    job.append(
        &format!("{filename}\t"),
        0.0,
        TextFormat {
            font_id: FontId::proportional(14.0),
            color: ui.visuals().text_color(),
            ..Default::default()
        },
    );

    job.append(
        &format!("{created} | {last_modified}"),
        0.0,
        TextFormat {
            font_id: FontId::proportional(10.0),
            color: ui.visuals().weak_text_color(),
            ..Default::default()
        },
    );
    
    // min_size makes the button fill the panel width and have a fixed height.
    ui.add_sized(
        [ui.available_width(), 28.0],
        egui::Button::new(job).rounding(Rounding::same(6.0)),
    )
}