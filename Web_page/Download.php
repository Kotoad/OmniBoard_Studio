<!DOCTYPE html>
<html lang="en">

<?php 
$page_title = "Download OmniBoard Studio - Visual Programming Environment"; 
include 'Head.php';

// Load local releases
$releases_file = __DIR__ . '/data/releases.json';
$releases = file_exists($releases_file) ? json_decode(file_get_contents($releases_file), true) : [];
$latest_release = !empty($releases) ? $releases[0] : null;
$previous_releases = count($releases) > 1 ? array_slice($releases, 1) : [];
?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">Download OmniBoard Studio</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Get the latest version of OmniBoard Studio for your platform. All files are hosted securely on our servers.</p>
    </header>

    <main class="w-full py-10 flex-grow">
        <?php if ($latest_release): ?>
        <section id="latest-download" class="max-w-5xl mx-auto px-6 mb-20">
            <h2 class="text-3xl font-bold mb-8 text-center text-white">Latest Version (<?= htmlspecialchars($latest_release['version']) ?>)</h2>
            <div class="grid md:grid-cols-2 gap-8">
                <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Windows</h2>
                    <p class="text-slate-400 mb-6">Download the Windows installer to get started quickly.</p>
                    <a href="<?= htmlspecialchars($latest_release['windows_file']) ?>" download
                        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download for Windows</a>
                </div>
                <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Linux</h2>
                    <p class="text-slate-400 mb-6">Get the Linux version of OmniBoard Studio for your GNU/Linux systems.</p>
                    <a href="<?= htmlspecialchars($latest_release['linux_file']) ?>" download
                        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download for Linux</a>
                </div>
            </div>
        </section>
        <?php else: ?>
            <p class="text-center text-slate-400">No releases available at the moment.</p>
        <?php endif; ?>

        <?php if (!empty($previous_releases)): ?>
        <section id="previous-versions" class="max-w-5xl mx-auto px-6 mb-20">
            <h2 class="text-2xl font-bold mb-6 text-white border-b border-slate-700 pb-2">Previous Versions</h2>
            <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                            <tr>
                                <th class="px-6 py-4">Version</th>
                                <th class="px-6 py-4">Release Date</th>
                                <th class="px-6 py-4">Windows</th>
                                <th class="px-6 py-4">Linux</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-700/50">
                            <?php foreach ($previous_releases as $release): ?>
                            <tr class="hover:bg-slate-700/30 transition-colors">
                                <td class="px-6 py-4 font-semibold text-slate-200"><?= htmlspecialchars($release['version']) ?></td>
                                <td class="px-6 py-4 text-slate-400"><?= htmlspecialchars($release['date']) ?></td>
                                <td class="px-6 py-4">
                                    <?php if (!empty($release['windows_file'])): ?>
                                        <a href="<?= htmlspecialchars($release['windows_file']) ?>" class="text-blue-400 hover:text-blue-300 download">.exe</a>
                                    <?php else: ?>
                                        <span class="text-slate-600">-</span>
                                    <?php endif; ?>
                                </td>
                                <td class="px-6 py-4">
                                    <?php if (!empty($release['linux_file'])): ?>
                                        <a href="<?= htmlspecialchars($release['linux_file']) ?>" class="text-blue-400 hover:text-blue-300 download">.tar.gz</a>
                                    <?php else: ?>
                                        <span class="text-slate-600">-</span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        <?php endif; ?>
    </main>

    <?php include 'Footer.php'; ?>
</body>
</html>