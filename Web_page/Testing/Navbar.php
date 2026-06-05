<?php
require_once __DIR__ . '/i18n.php';

//require_once __DIR__ . '/Admin/config.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

/*$display_avatar = null;

$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$stmt->execute([$_SESSION['user_email'] ?? '']);
$user = $stmt->fetch();*/

if ($user) {
    $providers = json_decode($user['providers'], true) ?? [];
    if (isset($providers['github']['avatar_url'])) {
        $display_avatar = $providers['github']['avatar_url'];
    } elseif (isset($providers['google']['avatar_url'])) {
        $display_avatar = $providers['google']['avatar_url'];
    } else {
        $display_avatar = null;
    }
}


?>
<nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
    <div class="w-full mx-auto px-6 py-4 flex justify-between items-center">
        <a href="/" class="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors"><?= t('Navbar', 'brand', 'OmniBoard Studio') ?></a>
        
        <div class="hidden md:flex items-center space-x-6">
            <a href="/#features" class="text-slate-300 hover:text-blue-400 transition-colors"><?= t('Navbar', 'links.0', 'Features') ?></a>
            <a href="/Tutorials.php" class="text-slate-300 hover:text-blue-400 transition-colors"><?= t('Navbar', 'links.1', 'Tutorials') ?></a>
            <a href="/FAQ.php" class="text-slate-300 hover:text-blue-400 transition-colors"><?= t('Navbar', 'links.2', 'FAQ') ?></a>
            <a href="/Download.php" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors"><?= t('Navbar', 'links.3', 'Download App') ?></a>
            
            <div class="flex items-center gap-2 border-l border-slate-700 pl-4">
                <a href="?lang=en" class="<?= $current_lang === 'en' ? 'text-white font-bold' : 'text-slate-400' ?> hover:text-white transition-colors text-sm">EN</a>
                <span class="text-slate-600">|</span>
                <a href="?lang=cs" class="<?= $current_lang === 'cs' ? 'text-white font-bold' : 'text-slate-400' ?> hover:text-white transition-colors text-sm">CS</a>
            </div>

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
                    <a href="/Auth/logout.php" class="border border-red-800 text-red-400 hover:bg-red-900/30 px-3 py-1.5 rounded text-sm transition-colors"><?= t('Navbar', 'auth.logged_in.1', 'Logout') ?></a>
                <?php else: ?>
                    <a href="/Auth/login_page.php" class="border border-slate-700 text-slate-300 hover:bg-slate-800 px-3 py-1.5 rounded text-sm transition-colors"><?= t('Navbar', 'auth.logged_out', 'Login / Register') ?></a>
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
            <a href="/index.php" class="text-slate-300 hover:text-blue-400"><?= t('Navbar', 'mobile_menu.0', 'Home') ?></a>
            <a href="/Tutorials.php" class="text-slate-300 hover:text-blue-400"><?= t('Navbar', 'mobile_menu.1', 'Tutorials') ?></a>
            <a href="/Download.php" class="text-slate-300 hover:text-blue-400"><?= t('Navbar', 'mobile_menu.2', 'Download App') ?></a>
            <hr class="border-slate-700 my-2">
            <?php if (isset($_SESSION['user_email'])): ?>
                <a href="/Auth/settings.php" class="text-slate-300 hover:text-blue-400"><?= t('Navbar', 'auth.logged_in.0', 'Account Settings') ?></a>
                <a href="/Auth/logout.php" class="text-red-400 hover:text-red-300"><?= t('Navbar', 'auth.logged_in.1', 'Logout') ?></a>
            <?php else: ?>
                <a href="/Auth/login_page.php" class="text-slate-300 hover:text-blue-400"><?= t('Navbar', 'auth.logged_out', 'Login / Register') ?></a>
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