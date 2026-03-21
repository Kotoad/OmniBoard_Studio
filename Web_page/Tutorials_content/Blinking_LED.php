<!DOCTYPE html>
<html lang="en">

<?php $pageTitle = 'Blinking LED'; include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            How to Create a Blinking LED Project
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            In this tutorial, we will guide you through creating a simple blinking LED project using OmniBoard Studio.
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Steps to Create a Blinking LED Project</h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <p class="text-slate-300 mt-1">Open OmniBoard Studio and create a new project.</p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <p class="text-slate-300 mt-1 py-2">Drag and drop the necessary blocks to create a node diagram that
                        turns an LED on and off.</p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            Try to explore and make the diagram you self or click here and find out one of the
                            solutions.
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Place Start block.</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Connect the Start block to a While True block to create an infinite loop.</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Then connect the While True block to a Toggle LED block. This will cause the LED
                                    to toggle between on and off states.</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Finally connect the Timer block to the Toggle LED block. This will create the
                                    desired blinking effect. You can adjust the timer duration to change the blinking
                                    speed as you wish. (1000 milliseconds = 1 second)</span>
                            </li>
                        </ul>
                        <figure class="w-full flex flex-col items-center mt-4">
                            <img src="Blinking_LED/Blinking_LED_Flowchart.png" alt="Blinking LED Blocks"
                                class="rounded-lg border border-slate-700">
                            <figcaption class="text-sm text-slate-500 mt-2">Example block arrangement for a blinking LED
                                project.</figcaption>
                        </figure>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <p class="text-slate-300 mt-1">Make the correct circuit</p>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span>Connect the GPIO pin asigned to the LED to the rezistor.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span>Connect the positive leg of the LED to a resistor, and then connect the other end of
                                the LED to ground. You can determine which leg is positive and which is negative by
                                finding the longer leg (positive) and shorter leg (negative) or flat side of the LED
                                cover (negative).</span>
                        </li>
                    </ul>
                    <figure class="w-full flex flex-col items-center mt-4">
                        <img src="Blinking_LED/Blinking_LED_Circuit.png" alt="Blinking LED Circuit"
                            class="rounded-lg border border-slate-700">
                        <figcaption class="text-sm text-slate-500 mt-2">Example circuit for a blinking LED project.
                        </figcaption>
                    </figure>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        4</div>
                    <p class="text-slate-300 mt-1">Compile the code and upload it to your microcontroller.</p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        5</div>
                    <p class="text-slate-300 mt-1">Watch your LED blink on and off at the interval you set with the
                        Timer block!</p>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Bonus informations</h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Writen code example</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>Here is an example of simplified the MicroPython code that would be generated by the blocks
                        for a blinking LED project:</span>
                </li>
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
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">And here is simplefied code for Python:</span>
                </li>
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
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">What is an LED?</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>LED stands for Light Emitting Diode. It is a semiconductor device that emits light when an
                        electric current passes through it. LEDs are widely used in electronic circuits for indication
                        and display purposes due to their efficiency, long lifespan, and low power consumption.</span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">In simple terms, what is an LED?</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>
                        An LED can be thought of as a "light bulb" in a circuit. When electricity flows through it, it
                        produces light, making it useful for visual indicators and displays in electronic projects.
                    </span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">What is a resistor?</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A resistor is an electronic component that limits the flow of electric current in a circuit.
                        It is used to protect components like LEDs from receiving too much current, which can damage
                        them. Resistors are essential for controlling the amount of current that flows through different
                        parts of a circuit.</span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">In simple terms, what is a resistor?</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A resistor can be thought of as a "gatekeeper" in a circuit that controls how much electricity
                        flows through it. It helps ensure that components like LEDs receive the right amount of current
                        to function properly without getting damaged.</span>
                </li>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>