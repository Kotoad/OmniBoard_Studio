<?php require_once __DIR__ . '/../i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $pageTitle = t('Tutorial_0_linux_based_RPI_variant_en', 'page_title', 'Linux-based Raspberry Pi Setup'); include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center border-b border-slate-800">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?= t('Tutorial_0_linux_based_RPI_variant_en', 'header.title', 'How to set up a Linux-based Raspberry Pi') ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            <?= t('Tutorial_0_linux_based_RPI_variant_en', 'header.description', 'In this tutorial, we will guide you through setting up a Linux-based Raspberry Pi for use with OmniBoard Studio.') ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.0.title', 'RPI models:') ?></h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <?php for($i=0; $i<14; $i++): ?>
                <div class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    <?= t('Tutorial_0_linux_based_RPI_variant_en', "sections.0.models.{$i}") ?>
                </div>
                <?php endfor; ?>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.1.title', 'You will need:') ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl">
                <?php for($i=0; $i<4; $i++): ?>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?= t('Tutorial_0_linux_based_RPI_variant_en', "sections.1.requirements.{$i}") ?></span>
                </li>
                <?php endfor; ?>
            </ul>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.2.title', 'Steps to set up your Raspberry Pi:') ?></h2>
            <div class="space-y-4">
                <?php for($i=0; $i<11; $i++): ?>
                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30"><?= $i+1 ?></div>
                    <div class="text-slate-300 mt-1"><?= t('Tutorial_0_linux_based_RPI_variant_en', "sections.2.steps.{$i}") ?></div>
                </div>
                <?php endfor; ?>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">12</div>
                    <div class="text-slate-300 mt-1">
                        <span class="font-bold text-white"><?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.2.steps.11.description', 'First time configuration and connection') ?></span>
                        <ul class="mt-4 space-y-3 pl-4 border-l-2 border-slate-700">
                            <?php for($j=0; $j<5; $j++): ?>
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <?= t('Tutorial_0_linux_based_RPI_variant_en', "sections.2.steps.11.instructions.{$j}") ?>
                            </li>
                            <?php endfor; ?>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="mt-8 p-4 bg-blue-900/20 border border-blue-800 rounded-lg text-blue-200 text-sm">
                <?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.2.notes.0', 'Red LED indicates power and green LED indicates reading/writing to the MicroSD card.') ?>
            </div>
            <div class="mt-8 p-4 bg-blue-900/20 border border-blue-800 rounded-lg text-blue-200 text-sm">
                <?= t('Tutorial_0_linux_based_RPI_variant_en', 'sections.2.notes.1', '*W means what this RPI model has WiFi built-in...') ?><br>
            </div>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>
</html>