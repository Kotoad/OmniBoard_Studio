<nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
    <div class="w-full mx-auto px-6 py-4 flex justify-between items-center">

        <a href="/index.php" class="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">OmniBoard
            Studio</a>
        <div class="hidden md:flex items-center space-x-8">
            <a href="/index.php#features" class="text-slate-300 hover:text-blue-400 transition-colors">Features</a>
            <a href="/Tutorials.php" class="text-slate-300 hover:text-blue-400 transition-colors">Tutorials</a>
            <a href="/FAQ.php" class="text-slate-300 hover:text-blue-400 transition-colors">FAQ</a>
            <a href="/Download.php"
                class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download App</a>
        </div>

        <button id="menu-btn" class="md:hidden text-slate-300 focus:outline-none">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            </svg>
        </button>
    </div>

    <div id="mobile-menu" class="hidden md:hidden bg-slate-800 border-t border-slate-700">
        <div class="flex flex-col p-6 space-y-4">
            <a href="/index.php" class="text-slate-300 hover:text-blue-400">Home</a>
            <a href="/Tutorials.php" class="text-slate-300 hover:text-blue-400">Tutorials</a>
            <a href="/Download.php" class="text-slate-300 hover:text-blue-400">Download</a>
            <a href="/FAQ.php" class="text-slate-300 hover:text-blue-400">FAQ</a>
            <a href="/Contact.php" class="text-slate-300 hover:text-blue-400">Contact</a>
        </div>
    </div>
</nav>

<script>
const btn = document.getElementById('menu-btn');
const menu = document.getElementById('mobile-menu');

btn.addEventListener('click', () => {
    menu.classList.toggle('hidden');
});
</script>