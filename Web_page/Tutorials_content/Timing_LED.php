<!DOCTYPE html>
<html lang="en">

<?php $page_title = "Timing LED Tutorial - OmniBoard Studio"; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">Timing LED Tutorial</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Learn how to create a simple timing LED project using
            OmniBoard Studio.</p>
    </header>

    <hr class="border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Steps to Create a Timing LED Project</h2>
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
                        turns an LED on and off with different timing intervals.</p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            Try to explore and make the diagram yourself or click here to find out one of the solutions.
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
                                <span>Connect the Start block to a While True block. This will create an infinite loop
                                    that allows the LED to keep blinking.</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Connect the ¨While True block to a Timer block. Set the timer duration to your
                                    desired interval (e.g., 1000 milliseconds for 1 second).</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Connect the Timer block to a LED ON block. The timer will control the time it will
                                    take for the LED to turn ON</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Then connect the LED ON block to another timer. Here you can also set the duration
                                    to whatever you want</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>Connect the second Timer block to a LED OFF block. This will control how long the
                                    LED stays ON before it turns OFF.</span>
                            </li>
                        </ul>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <p class="text-slate-300 mt-1">Make the correct circuit</p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            Try to make the circuit from memory becouse it's the same as the circuit for blinking LED or
                            click here to see the solutuon
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
                                <span>Connect the positive leg of the LED to a resistor, and then connect the other end
                                    of the LED to ground. You can determine which leg is positive and which is negative
                                    by finding the longer leg (positive) and shorter leg (negative) or flat side of the
                                    LED cover (negative).</span>
                            </li>
                            <figure class="w-full flex flex-col items-center mt-4">
                                <img src="Blinking_LED/Blinking_LED_Circuit.png" alt="Timind LED circiut"
                                    class="rounded-lg border border-slate-700">
                                <figcaption class="text-sm text-slate-500 mt-2">Example circuit diagram for timing LED
                                    project.</figcaption>
                            </figure>
                        </ul>
                    </details>
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
import time # Import the time module for timing functions
led = Pin(15, Pin.OUT) # Set GPIO pin 15 as an output for the LED
while True: # Start an infinite loop
    led.value(1) # Turn the LED on
    time.sleep(1) # Wait for 1 second
    led.value(0) # Turn the LED off
    time.sleep(1) # Wait for 1 second
                </code></pre>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">And here is simplified code for Python:</span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import RPi.GPIO as GPIO # Import the RPi.GPIO library to control GPIO pins
import time # Import the time module for timing functions
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(15, GPIO.OUT) # Set GPIO pin 15 as an output for the LED
while True: # Start an infinite loop
    GPIO.output(15, GPIO.HIGH) # Turn the LED on
    time.sleep(1) # Wait for 1 second
    GPIO.output(15, GPIO.LOW) # Turn the LED off
    time.sleep(1) # Wait for 1 second
                </code></pre>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>