<!DOCTYPE html>
<html lang="en">

<?php $page_title = "Frequently Asked Questions - OmniBoard Studio"; include 'Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">Frequently Asked Questions</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Find answers to common questions about OmniBoard
            Studio.</p>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="faq" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6 text-center space-y-16">
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">What is OmniBoard Studio?</h2>
                    <p class="text-slate-400">OmniBoard Studio is a visual programming environment designed for
                        microcontroller projects. It allows users to create and compile MicroPython code using a
                        drag-and-drop node-based interface.</p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Which platforms does OmniBoard Studio support?
                    </h2>
                    <p class="text-slate-400">Currently, OmniBoard Studio supports Windows and Linux operating systems.
                        We are actively working on expanding support to other platforms in the future.</p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">What hardware is compatible with OmniBoard
                        Studio?</h2>
                    <p class="text-slate-400">OmniBoard Studio is designed to work with the Raspberry Pi Pico series and
                        Raspberry Pi 1 to 5. We plan to add support for more microcontroller platforms and single-board
                        computers in future updates.</p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Is OmniBoard Studio free to use?</h2>
                    <p class="text-slate-400">Yes, OmniBoard Studio is free to download and use. We are committed to
                        providing a powerful and accessible tool for makers, educators, and hobbyists in the
                        microcontroller community.</p>
                </div>
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Where can I find tutorials and documentation?
                    </h2>
                    <p class="text-slate-400">You can find comprehensive tutorials and documentation on our Tutorials
                        page. We cover everything from getting started with hardware setup to advanced node creation and
                        project deployment.</p>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>

</html>