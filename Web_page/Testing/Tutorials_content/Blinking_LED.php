<?php require_once __DIR__ . '/../i18n.php'; ?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">

<?php $pageTitle = t('Blinking_LED', 'page_title', 'Blinking LED'); include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?= t('Blinking_LED', 'header.title', 'How to Create a Blinking LED Project') ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            <?= t('Blinking_LED', 'header.description', 'In this tutorial, we will guide you through creating a simple blinking LED project using OmniBoard Studio.') ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Blinking_LED', 'sections.0.title', 'Steps to Create a Blinking LED Project') ?></h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">1</div>
                    <p class="text-slate-300 mt-1"><?= t('Blinking_LED', 'sections.0.steps.0', 'Open OmniBoard Studio and create a new project.') ?></p>
                </div>
                
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">2</div>
                    <p class="text-slate-300 mt-1 py-2"><?= t('Blinking_LED', 'sections.0.steps.1.description', 'Drag and drop the necessary blocks to create a node diagram that turns an LED on and off.') ?></p>
                    <details class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?= t('Blinking_LED', 'sections.0.steps.1.details.summary', 'Try to explore and make the diagram you self or click here and find out one of the solutions.') ?>
                            <span class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?= t('Blinking_LED', 'sections.0.steps.1.details.instructions.0', 'Place Start block.') ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?= t('Blinking_LED', 'sections.0.steps.1.details.instructions.1', 'Connect the Start block to a While True block to create an infinite loop.') ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?= t('Blinking_LED', 'sections.0.steps.1.details.instructions.2', 'Then connect the While True block to a Toggle LED block. This will cause the LED to toggle between on and off states.') ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?= t('Blinking_LED', 'sections.0.steps.1.details.instructions.3', 'Finally connect the Timer block to the Toggle LED block. This will create the desired blinking effect. You can adjust the timer duration to change the blinking speed as you wish. (1000 milliseconds = 1 second)') ?></span>
                            </li>
                        </ul>
                        <figure class="w-full flex flex-col items-center mt-4">
                            <img src="../assets/Blinking_LED_assets/Blinking_LED_Flowchart.png" alt="Blinking LED Blocks" class="rounded-lg border border-slate-700">
                        </figure>
                    </details>
                </div>

                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">3</div>
                    <p class="text-slate-300 mt-1"><?= t('Blinking_LED', 'sections.0.steps.2.description', 'Make the correct circuit') ?></p>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?= t('Blinking_LED', 'sections.0.steps.2.instructions.0', 'Connect the GPIO pin asigned to the LED to the rezistor.') ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?= t('Blinking_LED', 'sections.0.steps.2.instructions.1', 'Connect the positive leg of the LED to a resistor, and then connect the other end of the LED to ground...') ?></span>
                        </li>
                    </ul>
                    <figure class="w-full flex flex-col items-center mt-4">
                        <img src="../assets/Blinking_LED_assets/Blinking_LED_Circuit.png" alt="Blinking LED Circuit" class="rounded-lg border border-slate-700">
                    </figure>
                </div>

                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">4</div>
                    <p class="text-slate-300 mt-1"><?= t('Blinking_LED', 'sections.0.steps.3', 'Compile the code and upload it to your microcontroller.') ?></p>
                </div>
                
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">5</div>
                    <p class="text-slate-300 mt-1"><?= t('Blinking_LED', 'sections.0.steps.4', 'Watch your LED blink on and off at the interval you set with the Timer block!') ?></p>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?= t('Blinking_LED', 'sections.1.title', 'Bonus informations') ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1"><?= t('Blinking_LED', 'sections.1.items.Writen code example', 'Here is an example of simplified the MicroPython code that would be generated by the blocks for a blinking LED project:') ?></span></li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import machine # Needed for controlling the GPIO pins
import time # Needed for creating delays
led = machine.Pin(2, machine.Pin.OUT) # Asign GPIO pin 2 to control the LED as and output
while True: # Create an infinite loop to keep the LED blinking
    togle(led) # Toggle the LED on and off.
                 This is a custom function that would be generated by the blocks. 
                 It would turn the LED on if it's currently off, and turn it off if it's currently on.
    time.sleep(1) # Wait for 1 second before toggling again
                </code></pre>
                
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1"><?= t('Blinking_LED', 'sections.1.items.And here is simplefied code for Python', 'And here is simplefied code for Python') ?></span></li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import time # Needed for creating delays
import RPi.GPIO as GPIO # Needed for controlling the GPIO pins
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(2, GPIO.OUT) # Asign GPIO pin 2 to control the LED as and output
while True: # Create an infinite loop to keep the LED blinking
    togle(pin=2) # Toggle the LED on and off.
                   This is a custom function that would be generated by the blocks. 
                   It would turn the LED on if it's currently off, and turn it off if it's currently on.
    time.sleep(1) # Wait for 1 second before toggling again
                </code></pre>

                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">What is an LED?</span></li>
                <li class="flex items-start gap-3"><span><?= t('Blinking_LED', 'sections.1.items.What is an LED?', 'LED stands for Light Emitting Diode...') ?></span></li>
                
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">In simple terms, what is an LED?</span></li>
                <li class="flex items-start gap-3"><span><?= t('Blinking_LED', 'sections.1.items.In simple terms, what is an LED?', 'An LED can be thought of as a "light bulb" in a circuit...') ?></span></li>
                
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">What is a resistor?</span></li>
                <li class="flex items-start gap-3"><span><?= t('Blinking_LED', 'sections.1.items.What is a resistor?', 'A resistor is an electronic component that limits the flow...') ?></span></li>
                
                <li class="flex items-start gap-3"><span class="text-blue-500 mt-1">In simple terms, what is a resistor?</span></li>
                <li class="flex items-start gap-3"><span><?= t('Blinking_LED', 'sections.1.items.In simple terms, what is a resistor?', 'A resistor can be thought of as a "gatekeeper"...') ?></span></li>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>
</html>