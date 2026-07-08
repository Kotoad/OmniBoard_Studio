use i18n_embed::{
    fluent::{ FluentLanguageLoader, fluent_language_loader },
    DesktopLanguageRequester, LanguageLoader,
};
use rust_embed::RustEmbed;
use once_cell::sync::Lazy;

#[derive(RustEmbed)]
#[folder = "i18n/"]
struct TranslationManager;

pub static LOADER: Lazy<FluentLanguageLoader> = Lazy::new(|| {
    let loader = fluent_language_loader!();
    loader.load_languages(&TranslationManager, &[loader.fallback_language().clone()]).unwrap();
    loader
});

pub fn init() {
    let requested = DesktopLanguageRequester::requested_languages();
    let _ = i18n_embed::select(&*LOADER, &TranslationManager, &requested);
}

pub fn switch_language(language: &str) {
    if let Ok(id) = language.parse() {
        let _ = i18n_embed::select(&*LOADER, &TranslationManager, &[id]);
    }
}

#[cfg(test)]
pub fn all_languages_loader() -> (FluentLanguageLoader, Vec<unic_langid::LanguageIdentifier>) {
    let loader = fluent_language_loader!();
    let languages = loader.available_languages(&TranslationManager).unwrap();
    loader.load_languages(&TranslationManager, &languages).unwrap();
    (loader, languages)
}