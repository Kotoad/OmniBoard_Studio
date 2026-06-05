<?php require_once __DIR__ . '/../i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $page_title = t('Basic_therms', 'page_title', 'Basic Electronics & Circuit Diagrams'); include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?= t('Basic_therms', 'header.title', 'Basic Electronics & Circuit Diagrams') ?>
        </h1>
        <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            <?= t('Basic_therms', 'header.description', 'Understand essential electrical quantities, symbols, and wiring principles before building projects.') ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Basic_therms', 'sections.0.title', 'Electrical and Magnetic Quantities') ?></h2>
            <p class="text-slate-300 mb-4"><?= t('Basic_therms', 'sections.0.description.0', 'Before diving into building circuits, it\'s important to understand some fundamental electrical and magnetic quantities...') ?></p>
            <p class="text-slate-300 mb-4"><?= t('Basic_therms', 'sections.0.description.1', 'Here are some of the key electrical and magnetic quantities you should be familiar with:') ?></p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span>Electric Quantities:</span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric charge</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric charge', 'A fundamental property of matter that causes it to experience a force...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric voltage</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric voltage', 'In electrical terms is a potential difference between two points in a circuit...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric current</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric current', 'The flow of electric charge through a conductor...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric resistance</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric resistance', 'The opposition to the flow of electric current...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric power</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric power', 'The rate at which electrical energy is transferred or consumed...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric conductance</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric conductance', 'The reciprocal of resistance...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric energy</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric energy', 'The capacity to do work...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric capacity</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric capacity', 'The ability of a system to store electric charge...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Electric inductance</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Electric Quantities.Electric inductance', 'The property of a conductor that opposes changes in current...') ?></span></li>
                    </ul>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span>Magnetic Quantities:</span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic flux</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic flux', 'The total magnetic field passing through a given area...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic field strength</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic field strength', 'The intensity of a magnetic field...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic permeability</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic permeability', 'The ability of a material to support the formation of a magnetic field...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic reluctance</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic reluctance', 'The opposition to the creation of a magnetic field...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic energy</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic energy', 'The energy stored in a magnetic field...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic force</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic force', 'The force exerted by a magnetic field...') ?></span></li>
                        
                        <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Magnetic moment</span></li>
                        <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.0.categories.Magnetic Quantities.Magnetic moment', 'A measure of the strength and orientation of a magnet\'s magnetic field...') ?></span></li>
                    </ul>
                </li>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Basic_therms', 'sections.1.title', 'Common Electrical Terms and Symbols') ?></h2>
            <p class="text-slate-300 mb-4"><?= t('Basic_therms', 'sections.1.description.0', 'In addition to understanding the fundamental electrical and magnetic quantities...') ?></p>
            <p class="text-slate-300 mb-4"><?= t('Basic_therms', 'sections.1.description.1', 'Here are some common electrical terms and symbols you should know:') ?></p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Ground</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Ground', 'A reference point in an electrical circuit from which voltages are measured...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Ground_Symbol.png" alt="Ground Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Power Supply</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Power Supply', 'A source of electrical power for the circuit...') ?></span></li>
                <div class="w-full flex justify-center gap-12 mt-4">
                    <figure class="flex flex-col items-center">
                        <img src="../assets/Basic_therms_assets/Power_Supply_Symbol_DC.png" alt="Power Supply Symbol DC" class="max-w-full h-auto">
                    </figure>
                    <figure class="flex flex-col items-center">
                        <img src="../assets/Basic_therms_assets/Power_Supply_Symbol_AC.png" alt="Power Supply Symbol AC" class="max-w-full h-auto">
                    </figure>
                </div>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Pin symbol</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Pin symbol', 'A symbol representing a connection point on a your RPI by number') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Pin_Connection_Symbol.png" alt="Pin Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Resistor</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Resistor', 'A component that resists the flow of electric current...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Resistor_Symbol.png" alt="Resistor Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Capacitor</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Capacitor', 'A component that stores and releases electrical energy...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Capacitor_Symbol.png" alt="Capacitor Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Inductor</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Inductor', 'A component that stores energy in a magnetic field...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Inductor_Symbol.png" alt="Inductor Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Diode</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Diode', 'A component that allows current to flow in one direction only...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Diode_Symbol.png" alt="Diode Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">LED diode</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.LED diode', 'A type of diode that emits light when current flows through it...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/LED_Symbol.png" alt="LED Symbol" class="max-w-full h-auto">
                </figure>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">Transistor</span></li>
                <li class="flex items-start gap-3"><span><?= t('Basic_therms', 'sections.1.terms.Transistor', 'A semiconductor device used to amplify or switch electronic signals...') ?></span></li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="../assets/Basic_therms_assets/Transistor_Symbol.png" alt="Transistor Symbol" class="max-w-full h-auto">
                </figure>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>
</html>