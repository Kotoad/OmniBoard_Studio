<?php
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$display_avatar = null;

if (!empty($_SESSION['user_email'])) {
    // 1. Load config.php to get the exact DATA_DIR path
    $config_file = __DIR__ . '/Admin/config.php';
    if (file_exists($config_file) && !defined('DATA_DIR')) {
        require_once $config_file;
    }

    // 2. Define path and load users.json
    $users_file = defined('DATA_DIR') ? DATA_DIR . 'users.json' : __DIR__ . '/Admin/data/users.json';
    
    if (file_exists($users_file)) {
        $users = json_decode(file_get_contents($users_file), true);
        $email = $_SESSION['user_email'];
        
        // 3. Search for the avatar (GitHub priority, then Google)
        if (isset($users[$email]['providers'])) {
            $providers = $users[$email]['providers'];
            if (!empty($providers['github']['avatar_url'])) {
                $display_avatar = $providers['github']['avatar_url'];
            } elseif (!empty($providers['google']['avatar_url'])) {
                $display_avatar = $providers['google']['avatar_url'];
            }
        }
        
        // Fallback to the top-level avatar field if providers array is missing it
        if (!$display_avatar && !empty($users[$email]['avatar_url'])) {
            $display_avatar = $users[$email]['avatar_url'];
        }
    }
}
?>
<nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
    <div class="w-full mx-auto px-6 py-4 flex justify-between items-center">
        <a href="/" class="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">OmniBoard Studio</a>
        
        <div class="hidden md:flex items-center space-x-6">
            <a href="/#features" class="text-slate-300 hover:text-blue-400 transition-colors">Features</a>
            <a href="/Tutorials.php" class="text-slate-300 hover:text-blue-400 transition-colors">Tutorials</a>
            <a href="/FAQ.php" class="text-slate-300 hover:text-blue-400 transition-colors">FAQ</a>
            <a href="/Download.php" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download App</a>
            
            <div class="pl-4 border-l border-slate-700 flex items-center gap-4">
                <?php if (isset($_SESSION['user_email'])): ?>
                    <a href="/Auth/settings.php" class="text-slate-300 text-sm font-medium hover:text-blue-400 transition-colors flex items-center gap-2">
                        <span class="w-7 h-7 bg-slate-700 rounded-full flex items-center justify-center text-xs font-bold border border-slate-600 text-white overflow-hidden">
                            <?php if ($display_avatar): ?>
                                <img src="<?= htmlspecialchars($display_avatar) ?>" alt="Avatar" class="w-full h-full object-cover">
                            <?php else: ?>
                                <?= strtoupper(substr($_SESSION['user_email'], 0, 1)) ?>
                            <?php endif; ?>
                        </span>
                    </a>
                    <a href="/Auth/logout.php" class="border border-red-800 text-red-400 hover:bg-red-900/30 px-3 py-1.5 rounded text-sm transition-colors">Logout</a>
                <?php else: ?>
                    <a href="/Auth/login.php?provider=github" class="text-slate-300 text-sm hover:text-white transition-colors">GitHub Login</a>
                    <a href="/Auth/login.php?provider=google" class="text-slate-300 text-sm hover:text-white transition-colors">Google Login</a>
                <?php endif; ?>
            </div>
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
            <a href="/Download.php" class="text-slate-300 hover:text-blue-400">Download App</a>
            <hr class="border-slate-700 my-2">
            <?php if (isset($_SESSION['user_email'])): ?>
                <a href="/Auth/settings.php" class="text-slate-300 hover:text-blue-400">Account Settings</a>
                <a href="/Auth/logout.php" class="text-red-400 hover:text-red-300">Logout</a>
            <?php else: ?>
                <a href="/Auth/login.php?provider=github" class="text-slate-300 hover:text-blue-400">GitHub Login</a>
                <a href="/Auth/login.php?provider=google" class="text-slate-300 hover:text-blue-400">Google Login</a>
            <?php endif; ?>
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