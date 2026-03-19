<!DOCTYPE html>
<html lang="en">

<?php $page_title = "Download OmniBoard Studio - Visual Programming Environment"; include 'Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">Download OmniBoard Studio</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Get the latest version of OmniBoard Studio for your
            platform. Follow the instructions below to install and start building your projects.</p>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="download" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6">
                <h2 class="text-3xl font-bold mb-12 text-center text-white">Available Downloads</h2>
                <div class="grid md:grid-cols-2 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                        <h2 class="text-2xl font-semibold mb-4 text-blue-400">Windows</h2>
                        <p class="text-slate-400 mb-6">Download the Windows installer to get started quickly.</p>
                        <a href="https://omniboardstudio.cz/downloads/OmniBoard_Online_Installer.exe" download
                            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download
                            for Windows</a>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                        <h2 class="text-2xl font-semibold mb-4 text-blue-400">Linux</h2>
                        <p class="text-slate-400 mb-6">Get the Linux version of OmniBoard Studio for your GNU/Linux
                            systems.</p>
                        <a href="https://omniboardstudio.cz/downloads/install.sh" download
                            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download
                            for Linux</a>
                    </div>
                </div>
                <div class="mt-20 text-center">
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Other Platforms</h2>
                    <p class="text-slate-400 mb-6">We are actively working on expanding support to other platforms. Stay
                        tuned for updates!</p>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>

</html>