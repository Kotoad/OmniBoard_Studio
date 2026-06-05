<?php require_once __DIR__ . '/../i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $page_title = t('Tutorial_0_RPI_PICO_variant_en', 'page_title', 'Raspberry Pi Pico Setup - OmniBoard Studio'); include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?= t('Tutorial_0_RPI_PICO_variant_en', 'header.title', 'Raspberry Pi Pico Setup') ?>
        </h1>
        <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            <?= t('Tutorial_0_RPI_PICO_variant_en', 'header.description', 'Learn how to flash the latest MicroPython firmware and prepare your board for OmniBoard Studio.') ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.0.title', 'Supported Raspberry Pi Pico Variants:') ?></h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <?php for($i=0; $i<5; $i++): ?>
                <div class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    <?= t('Tutorial_0_RPI_PICO_variant_en', "sections.0.variants.{$i}") ?>
                </div>
                <?php endfor; ?>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.1.title', 'You will need:') ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl">
                <?php for($i=0; $i<3; $i++): ?>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?= t('Tutorial_0_RPI_PICO_variant_en', "sections.1.requirements.{$i}") ?></span>
                </li>
                <?php endfor; ?>
            </ul>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.2.title', 'Steps to set up your Raspberry Pi Pico:') ?></h2>
            <ul class="space-y-4">
                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">1</div>
                    <div class="w-full">
                        <div class="text-slate-300 mt-1"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.2.steps.0.description', 'Download the latest version of MicroPython for your RPI') ?></div>
                        <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                            <?php for($i=0; $i<4; $i++): ?>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?= t('Tutorial_0_RPI_PICO_variant_en', "sections.2.steps.0.links.{$i}") ?></span>
                            </li>
                            <?php endfor; ?>
                        </ul>
                    </div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">2</div>
                    <div class="text-slate-300 mt-1"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.2.steps.1', 'Connect your Raspberry Pi Pico to your computer using the Micro USB cable...') ?></div>
                </div>
                
                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">3</div>
                    <div class="text-slate-300 mt-1"><?= t('Tutorial_0_RPI_PICO_variant_en', 'sections.2.steps.2', 'Copy the downloaded MicroPython firmware file to the Pico\'s root directory...') ?></div>
                </div>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>
</html>