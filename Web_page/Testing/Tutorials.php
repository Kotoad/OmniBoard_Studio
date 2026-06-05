<?php require_once __DIR__ . '/i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $page_title = t('Tutorials', 'page_title', 'OmniBoard Studio - Visual Programming for Microcontrollers'); include 'Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white"><?= t('Tutorials', 'header.title', 'OmniBoard Studio Tutorials') ?></h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto"><?= t('Tutorials', 'header.description', 'Explore our comprehensive tutorials to get the most out of OmniBoard Studio...') ?></p>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row gap-10 flex-grow">

        <aside class="w-full md:w-64 shrink-0 hidden md:block">
            <nav class="sticky top-24 flex flex-col space-y-3 border-l-2 border-slate-800 pl-5">
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">Getting Started</h3>
                <a href="/Tutorials_content/Tutorial_0_linux_based_RPI_variant_en.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Getting Started.0', 'Raspberry Pi Setup') ?></a>
                <a href="/Tutorials_content/Tutorial_0_RPI_PICO_variant_en.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Getting Started.1', 'Raspberry Pi Pico Setup') ?></a>

                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2 mt-6">Core Concepts</h3>
                <a href="/Tutorials_content/Basic_therms.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Core Concepts.0', 'Basic Electronic Principles') ?></a>
                <a href="/Tutorials_content/Blinking_LED.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Core Concepts.1', 'Blinking LED') ?></a>
                <a href="/Tutorials_content/Button_LED.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Core Concepts.2', 'Button controlled LED') ?></a>
                <a href="/Tutorials_content/Timing_LED.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Core Concepts.3', 'Timing LED') ?></a>
                <a href="/Tutorials_content/LED_trafic_light.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Core Concepts.4', 'LED traffic light') ?></a>

                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2 mt-6">Advanced</h3>
                <a href="/Tutorials_content/Tutorial_5_en.php"
                    class="text-sm text-slate-400 hover:text-blue-400 transition-colors"><?= t('Tutorials', 'sidebar.Advanced.0', 'Hardware Interfacing') ?></a>
            </nav>
        </aside>

        <main class="flex-1">
            <section id="tutorials" class="bg-slate-900 py-20 border-t border-slate-800">
                <h2 class="text-3xl font-bold mb-12 text-white"><?= t('Tutorials', 'main_section.title', 'Available Tutorials') ?></h2>
                <div class="grid md:grid-cols-2 gap-6">
                    <?php 
                    $links = [
                        "/Tutorials_content/Tutorial_0_linux_based_RPI_variant_en.php",
                        "/Tutorials_content/Tutorial_0_RPI_PICO_variant_en.php",
                        "/Tutorials_content/Basic_therms.php",
                        "/Tutorials_content/Blinking_LED.php",
                        "/Tutorials_content/Timing_LED.php",
                        "/Tutorials_content/Button_LED.php"
                    ];
                    for ($i = 0; $i < count($links); $i++): 
                    ?>
                    <a href="<?= $links[$i] ?>" class="block p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm hover:border-blue-500 transition-all group">
                        <div class="text-sm font-semibold text-blue-400 mb-2 uppercase tracking-wide"><?= t('Tutorials', "main_section.tutorials_list.{$i}.label") ?></div>
                        <h3 class="text-2xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors"><?= t('Tutorials', "main_section.tutorials_list.{$i}.title") ?></h3>
                        <p class="text-slate-400"><?= t('Tutorials', "main_section.tutorials_list.{$i}.description") ?></p>
                    </a>
                    <?php endfor; ?>
                </div>
            </section>
        </main>

    </div>

    <?php include 'Footer.php'; ?>

</body>
</html>