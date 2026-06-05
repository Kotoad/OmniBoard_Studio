<?php require_once __DIR__ . '/i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $page_title = t('FAQ', 'page_title', 'Frequently Asked Questions - OmniBoard Studio'); include 'Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white"><?= t('FAQ', 'header.title', 'Frequently Asked Questions') ?></h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto"><?= t('FAQ', 'header.description', 'Find answers to common questions about OmniBoard Studio.') ?></p>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="faq" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6 text-center space-y-16">
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400"><?= t('FAQ', 'questions.0.question', 'What is OmniBoard Studio?') ?></h2>
                    <p class="text-slate-400"><?= t('FAQ', 'questions.0.answer', 'OmniBoard Studio is a visual programming environment designed for microcontroller projects...') ?></p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400"><?= t('FAQ', 'questions.1.question', 'Which platforms does OmniBoard Studio support?') ?></h2>
                    <p class="text-slate-400"><?= t('FAQ', 'questions.1.answer', 'Currently, OmniBoard Studio supports Windows and Linux operating systems...') ?></p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400"><?= t('FAQ', 'questions.2.question', 'What hardware is compatible with OmniBoard Studio?') ?></h2>
                    <p class="text-slate-400"><?= t('FAQ', 'questions.2.answer', 'OmniBoard Studio is designed to work with the Raspberry Pi Pico series...') ?></p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400"><?= t('FAQ', 'questions.3.question', 'Is OmniBoard Studio free to use?') ?></h2>
                    <p class="text-slate-400"><?= t('FAQ', 'questions.3.answer', 'Yes, OmniBoard Studio is free to download and use...') ?></p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400"><?= t('FAQ', 'questions.4.question', 'Where can I find tutorials and documentation?') ?></h2>
                    <p class="text-slate-400"><?= t('FAQ', 'questions.4.answer', 'You can find comprehensive tutorials and documentation on our Tutorials page...') ?></p>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>
</html>