<!DOCTYPE html>
<html lang="en">

<?php $pageTitle = 'Button controlled LED Project'; include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            How to Create a Button controlled LED Project
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">In this tutorial, we will guide you through creating a
            simple button controlled LED project using OmniBoard Studio.</p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Steps to Create a Button controlled LED Project</h2>
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
                    <p class="text-slate-300 mt-1">Drag and drop the necessary blocks to create a simple circuit that
                        controls an LED with a button.</p>
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
                                <span>Then connect the While True block to a Button block. This will allow us to check
                                    the state of the button.</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Finally connect the True output of the Button block to a LED ON block. This will
                                    cause the LED to turn on. To the False output connect a LED OFF block. This will
                                    cause the LED to turn off.</span>
                            </li>
                        </ul>
                        <figure class="w-full flex flex-col items-center mt-4">
                            <img src="Button_led/Button_led_Flowchart.png" alt="Button controlled LED Blocks"
                                class="rounded-lg border border-slate-700">
                            <figcaption class="text-sm text-slate-500 mt-2">Example block arrangement for a button
                                controlled LED project.</figcaption>
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
                            <span>Connect the button to the correct GPIO pin on your microcontroller. This will allow
                                the Button block to read the state of the button correctly. Your usual button will have
                                two pairs of pins. You will need to connect one pair to a GPIO pin and the other pair to
                                3.3V.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span>Now you can try to connect the LED from memory because the circuit is the same as in
                                the previous tutorial. Or click to reveal the circuit diagram and instructions.</span>
                        </li>
                        <details
                            class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                            <summary
                                class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                                Click to reveal the circuit diagram and instructions
                                <span
                                    class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                            </summary>

                            <ul
                                class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                                <li class="flex items-start gap-3">
                                    <span class="text-blue-500 mt-1">●</span>
                                    <span>Connect the GPIO pin asigned to the LED to the rezistor.</span>
                                </li>
                                <li class="flex items-start gap-3">
                                    <span class="text-blue-500 mt-1">●</span>
                                    <span>Connect the positive leg of the LED to a resistor, and then connect the other
                                        end of the LED to ground. You can determine which leg is positive and which is
                                        negative by finding the longer leg (positive) and shorter leg (negative) or flat
                                        side of the LED cover (negative).</span>
                                </li>
                                <figure class="w-full flex flex-col items-center mt-4">
                                    <img src="Button_led/Button_led_Circuit.png" alt="Button controlled LED Circuit"
                                        class="rounded-lg border border-slate-700">
                                    <figcaption class="text-sm text-slate-500 mt-2">Example circuit diagram for a button
                                        controlled LED project.</figcaption>
                                </figure>
                            </ul>
                        </details>
                    </ul>
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
                        for a button controlled LED project:</span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
from machine import Pin # Import the Pin class to control GPIO pins
led = Pin(2, Pin.OUT) # Set GPIO pin 2 as an output for the LED
button = Pin(0, Pin.IN, Pin.PULL_UP) # Set GPIO pin 0 as an input for the button with a pull-up resistor
while True: # Start an infinite loop
    if button.value() == 1: # Check if the button is pressed (active high)
        led.value(1) # Turn the LED on
    else: # If the button is not pressed
        led.value(0) # Turn the LED off
                </code></pre>
                <li class="flex items-start gap-3">
                    <span>And here is simplefied code for Python</span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import RPi.GPIO as GPIO # Import the GPIO library to control GPIO pins
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(2, GPIO.OUT) # Set GPIO pin 2 as an output for the LED
GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set GPIO pin 0 as an input for the button with a pull-up resistor
while True: # Start an infinite loop
    if GPIO.input(0) == GPIO.HIGH: # Check if the button is pressed (active high)
        GPIO.output(2, GPIO.HIGH) # Turn the LED on
    else: # If the button is not pressed
        GPIO.output(2, GPIO.LOW) # Turn the LED off
                </code></pre>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>