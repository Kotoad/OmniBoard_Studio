<!DOCTYPE html>
<html lang="en">

<?php $page_title = "LED traffic light - OmniBoard Studio Tutorial"; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php';?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center border-b border-slate-800">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            How to make a simple LED traffic light
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">In this tutorial, we will guide you through creating a
            simple LED traffic light project using OmniBoard Studio.</p>
    </header>

    <hr class="border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Steps to Create a simple LED traffic light</h2>
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
                    <p class="text-slate-300 mt-1">Drag and drop three LED blocks onto the canvas to represent the red,
                        yellow, and green lights.
                    </p>
                    <p class="text-slate-300 mt-1">
                        You will need at least three LED blocks to represent the red, yellow, and green lights of the
                        traffic light, a way to control the timing of the lights, and a way to loop the sequence. You
                        can use a combination of LED blocks, timer blocks, and loop blocks to achieve this.
                    </p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            Try to figure out how to connect the blocks to create the traffic light sequence on your
                            own! If you need a hint, click here.
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul 
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>
                                    Use the Start and While True blocks to create a loop that will run indefinitely.
                                </span>
                            </li>
                        </ul>
                    </details>
                </div>
        </section>
    </main>


</body>

</html>