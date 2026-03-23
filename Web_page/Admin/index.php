<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Admin Dashboard
// ─────────────────────────────────────────────

session_start();

require_once __DIR__ . '/config.php';

// ── Session timeout ───────────────────────────────────────────────────────────
if (isset($_SESSION['admin_logged_in'])) {
    if (time() - ($_SESSION['admin_last_activity'] ?? 0) > ADMIN_SESSION_LIFETIME) {
        session_unset();
        session_destroy();
        session_start();
        $_SESSION['login_error'] = 'Session expired. Please log in again.';
    } else {
        $_SESSION['admin_last_activity'] = time();
    }
}

// ── CSRF token ────────────────────────────────────────────────────────────────
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// ── Logout ────────────────────────────────────────────────────────────────────
if (isset($_GET['logout'])) {
    session_unset();
    session_destroy();
    header('Location: /Admin/');
    exit;
}

// ── Login handler ─────────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username'])) {
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $_POST['csrf_token'] ?? '')) {
        $_SESSION['login_error'] = 'Invalid request token.';
    } elseif (
        $_POST['username'] === ADMIN_USERNAME &&
        password_verify($_POST['password'], ADMIN_PASSWORD_HASH)
    ) {
        session_regenerate_id(true);
        $_SESSION['admin_logged_in']      = true;
        $_SESSION['admin_last_activity']  = time();
        $_SESSION['csrf_token']           = bin2hex(random_bytes(32));
        header('Location: /Admin/');
        exit;
    } else {
        $_SESSION['login_error'] = 'Invalid username or password.';
    }
}

// ── Show login page if not authenticated ──────────────────────────────────────
if (empty($_SESSION['admin_logged_in'])) {
    $error = $_SESSION['login_error'] ?? '';
    unset($_SESSION['login_error']);
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login – OmniBoard Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center">
    <div class="w-full max-w-sm bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-center text-blue-400 mb-2">OmniBoard Studio</h1>
        <p class="text-slate-400 text-center text-sm mb-8">Admin Dashboard</p>
        <?php if ($error): ?>
            <div class="mb-5 bg-red-900/40 border border-red-700 text-red-300 text-sm rounded-lg px-4 py-3">
                <?= htmlspecialchars($error) ?>
            </div>
        <?php endif; ?>
        <form method="POST">
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <div class="mb-4">
                <label class="block text-sm text-slate-400 mb-1" for="username">Username</label>
                <input id="username" name="username" type="text" autocomplete="username" required
                    class="w-full bg-slate-700 border border-slate-600 text-slate-100 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                    placeholder="admin">
            </div>
            <div class="mb-6">
                <label class="block text-sm text-slate-400 mb-1" for="password">Password</label>
                <input id="password" name="password" type="password" autocomplete="current-password" required
                    class="w-full bg-slate-700 border border-slate-600 text-slate-100 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <button type="submit"
                class="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-lg transition-colors">
                Sign In
            </button>
        </form>
    </div>
</body>
</html>
    <?php
    exit;
}

// ═════════════════════════════════════════════════════════════════════════════
//  AUTHENTICATED – collect data for all tabs
// ═════════════════════════════════════════════════════════════════════════════

// ── Helper: cURL fetch returning decoded JSON ─────────────────────────────────
function api_get(string $url, array $headers = [], int $timeout = 10): array|false
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_TIMEOUT        => $timeout,
        CURLOPT_USERAGENT      => 'OmniBoard-Admin/1.0',
        CURLOPT_FOLLOWLOCATION => true,
    ]);
    $response = curl_exec($ch);
    $err      = curl_errno($ch);
    curl_close($ch);
    if ($err || $response === false) {
        return false;
    }
    $decoded = json_decode($response, true);
    return is_array($decoded) ? $decoded : false;
}

function api_post(string $url, array $headers = [], array $payload = [], int $timeout = 15): array|false
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_TIMEOUT        => $timeout,
        CURLOPT_USERAGENT      => 'OmniBoard-Admin/1.0',
        CURLOPT_FOLLOWLOCATION => true,
    ]);
    $response = curl_exec($ch);
    $err      = curl_errno($ch);
    curl_close($ch);
    
    if ($err || $response === false) {
        return false;
    }
    
    $decoded = json_decode($response, true);
    return is_array($decoded) ? $decoded : false;
}

function github_headers(): array
{
    $h = ['Accept: application/vnd.github+json', 'X-GitHub-Api-Version: 2022-11-28'];
    if (GITHUB_TOKEN !== 'REPLACE_WITH_YOUR_GITHUB_PERSONAL_TOKEN') {
        $h[] = 'Authorization: Bearer ' . GITHUB_TOKEN;
    }
    return $h;
}

// ── Load local JSON files ─────────────────────────────────────────────────────
function load_json_file(string $path): array
{
    if (!file_exists($path)) {
        return [];
    }
    $data = json_decode(file_get_contents($path), true);
    return is_array($data) ? $data : [];
}

$app_starts = load_json_file(DATA_DIR . 'app_starts.json');
$users_map  = load_json_file(DATA_DIR . 'users.json');
$local_releases = load_json_file(DATA_DIR . 'releases.json');
$users      = array_values($users_map);

// Sort app_starts descending by timestamp
usort($app_starts, fn($a, $b) => strcmp($b['timestamp'] ?? '', $a['timestamp'] ?? ''));

// ── GitHub repo data ──────────────────────────────────────────────────────────
$gh_repo    = api_get('https://api.github.com/repos/' . GITHUB_REPO, github_headers());
$gh_commits = api_get('https://api.github.com/repos/' . GITHUB_REPO . '/commits?per_page=10', github_headers());
$gh_issues  = api_get('https://api.github.com/repos/' . GITHUB_REPO . '/issues?state=open&per_page=20', github_headers());
$gh_tags    = api_get('https://api.github.com/repos/' . GITHUB_REPO . '/tags?per_page=30', github_headers());

// ── PostHog configured? ───────────────────────────────────────────────────────
$posthog_configured = !empty(POSTHOG_PERSONAL_API_KEY) && !empty(POSTHOG_PROJECT_ID);

$ph_trends   = null;
$ph_pages    = null;
$ph_sessions = null;

if ($posthog_configured) {
    $ph_headers = [
        'Authorization: Bearer ' . POSTHOG_PERSONAL_API_KEY,
        'Content-Type: application/json',
    ];

    $query_url = POSTHOG_API_HOST . '/api/projects/' . POSTHOG_PROJECT_ID . '/query/';

    // 7-day pageview trend
    $ph_trends = api_post($query_url, $ph_headers, [
        'query' => [
            'kind'      => 'TrendsQuery',
            'series'    => [['kind' => 'EventsNode', 'event' => '$pageview']],
            'dateRange' => ['date_from' => '-7d']
        ]
    ]);

    // Top pages
    $ph_pages = api_post($query_url, $ph_headers, [
        'query' => [
            'kind'            => 'TrendsQuery',
            'series'          => [['kind' => 'EventsNode', 'event' => '$pageview']],
            'breakdownFilter' => ['breakdown' => '$current_url', 'breakdown_type' => 'event'],
            'dateRange'       => ['date_from' => '-7d']
        ]
    ]);

    // Sessions count (unique sessions in last 7 days)
    $ph_sessions = api_post($query_url, $ph_headers, [
        'query' => [
            'kind'      => 'TrendsQuery',
            'series'    => [['kind' => 'EventsNode', 'event' => '$pageview', 'math' => 'unique_session']],
            'dateRange' => ['date_from' => '-7d']
        ]
    ]);
}

// ── App usage aggregates ───────────────────────────────────────────────────────
$starts_by_platform = [];
$starts_by_version  = [];
$unique_ids         = [];

foreach ($app_starts as $s) {
    $p = $s['platform'] ?? 'unknown';
    $v = $s['version']  ?? 'unknown';
    $starts_by_platform[$p] = ($starts_by_platform[$p] ?? 0) + 1;
    $starts_by_version[$v]  = ($starts_by_version[$v]  ?? 0) + 1;
    if (!empty($s['anonymous_id'])) {
        $unique_ids[$s['anonymous_id']] = true;
    }
}
arsort($starts_by_version);

// ── Users by source ───────────────────────────────────────────────────────────
$users_by_source = ['github' => 0, 'google' => 0, 'other' => 0];
foreach ($users as $u) {
    $src = $u['source'] ?? 'other';
    if (isset($users_by_source[$src])) {
        $users_by_source[$src]++;
    } else {
        $users_by_source['other']++;
    }
}

// ── Server info ────────────────────────────────────────────────────────────────
$disk_total = @disk_total_space('/') ?: @disk_total_space('C:\\') ?: 0;
$disk_free  = @disk_free_space('/')  ?: @disk_free_space('C:\\')  ?: 0;
$disk_used  = $disk_total - $disk_free;

function human_bytes(int $bytes): string
{
    if ($bytes >= 1073741824) return round($bytes / 1073741824, 2) . ' GB';
    if ($bytes >= 1048576)    return round($bytes / 1048576,    2) . ' MB';
    if ($bytes >= 1024)       return round($bytes / 1024,       2) . ' KB';
    return $bytes . ' B';
}

$starts_file_size = file_exists(DATA_DIR . 'app_starts.json') ? filesize(DATA_DIR . 'app_starts.json') : 0;
$users_file_size  = file_exists(DATA_DIR . 'users.json')      ? filesize(DATA_DIR . 'users.json')      : 0;

// ── GitHub OAuth URL ─────────────────────────────────────────────────────────
$gh_oauth_state         = bin2hex(random_bytes(16));
$_SESSION['oauth_state'] = $gh_oauth_state;
$github_oauth_url = 'https://github.com/login/oauth/authorize?client_id='
    . urlencode(GITHUB_CLIENT_ID)
    . '&scope=user:email&state=' . urlencode($gh_oauth_state);

// ── Google OAuth URL ─────────────────────────────────────────────────────────
$google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth?'
    . http_build_query([
        'client_id'     => GOOGLE_CLIENT_ID,
        'redirect_uri'  => 'https://omniboardstudio.cz/Auth/google_callback.php',
        'response_type' => 'code',
        'scope'         => 'openid email profile',
        'state'         => $gh_oauth_state,
        'access_type'   => 'online',
    ]);

// ── JSON data for charts (passed to JS) ──────────────────────────────────────
$chart_platform_labels = array_keys($starts_by_platform);
$chart_platform_data   = array_values($starts_by_platform);
$chart_version_labels  = array_slice(array_keys($starts_by_version), 0, 10);
$chart_version_data    = array_slice(array_values($starts_by_version), 0, 10);
$chart_users_labels    = array_keys($users_by_source);
$chart_users_data      = array_values($users_by_source);

// PostHog trend chart data
$ph_trend_labels = [];
$ph_trend_data   = [];
$ph_res = $ph_trends['results'] ?? $ph_trends['result'] ?? null;

if ($ph_res && isset($ph_res[0]['data'])) {
    $ph_trend_labels = $ph_res[0]['labels'] ?? [];
    $ph_trend_data   = $ph_res[0]['data']   ?? [];
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard – OmniBoard Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
    <style type="text/tailwindcss">
        @layer base {
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { @apply bg-slate-900; }
            ::-webkit-scrollbar-thumb { @apply bg-slate-600 rounded-full; }
            ::-webkit-scrollbar-thumb:hover { @apply bg-slate-500; }
        }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

<!-- ── Top Nav ──────────────────────────────────────────────────────────────── -->
<nav class="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
    <div class="max-w-screen-xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <span class="text-blue-400 font-bold text-xl">OmniBoard Studio</span>
            <span class="text-slate-500 text-sm hidden sm:inline">/ Admin</span>
        </div>
        <div class="flex items-center gap-4">
            <span class="text-slate-400 text-sm hidden md:inline" id="live-clock"></span>
            <a href="?logout=1"
               class="text-sm text-red-400 hover:text-red-300 border border-red-800 hover:border-red-700 px-3 py-1.5 rounded-lg transition-colors">
                Logout
            </a>
        </div>
    </div>
</nav>

<!-- ── Tab Nav ──────────────────────────────────────────────────────────────── -->
<div class="bg-slate-800 border-b border-slate-700 sticky top-14 z-40">
    <div class="max-w-screen-xl mx-auto px-4 overflow-x-auto">
        <div class="flex gap-1 py-1 whitespace-nowrap" id="tab-nav">
            <?php
            $tabs = [
                'overview'  => 'Overview',
                'analytics' => 'Analytics',
                'releases'  => 'Releases',
                'appusage'  => 'App Usage',
                'users'     => 'Users',
                'github'    => 'GitHub',
                'server'    => 'Server',
            ];
            foreach ($tabs as $id => $label):
            ?>
            <button data-tab="<?= $id ?>"
                class="tab-btn px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors text-slate-400 hover:text-slate-100"
                onclick="switchTab('<?= $id ?>')">
                <?= $label ?>
            </button>
            <?php endforeach; ?>
        </div>
    </div>
</div>

<!-- ── Main Content ──────────────────────────────────────────────────────────── -->
<main class="max-w-screen-xl mx-auto px-4 py-8">

<!-- ════════════════════  OVERVIEW  ════════════════════ -->
<div id="tab-overview" class="tab-content">
    <h2 class="text-2xl font-bold mb-6 text-white">Overview</h2>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <?php
        $gh_stars   = $gh_repo['stargazers_count'] ?? '–';
        $latest_ver = 'v0.22.15';
        if (is_array($gh_tags) && !empty($gh_tags)) {
            $latest_ver = $gh_tags[0]['name'] ?? $latest_ver;
        }
        $stats_cards = [
            ['label' => 'App Starts',       'value' => number_format(count($app_starts)), 'color' => 'text-blue-400'],
            ['label' => 'Registered Users', 'value' => number_format(count($users)),      'color' => 'text-green-400'],
            ['label' => 'GitHub Stars',     'value' => is_numeric($gh_stars) ? number_format($gh_stars) : $gh_stars, 'color' => 'text-yellow-400'],
            ['label' => 'Unique Installs',  'value' => number_format(count($unique_ids)), 'color' => 'text-purple-400'],
            ['label' => 'Latest Version',   'value' => $latest_ver,                       'color' => 'text-slate-100'],
        ];
        foreach ($stats_cards as $card):
        ?>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1"><?= $card['label'] ?></p>
            <p class="<?= $card['color'] ?> text-2xl font-bold"><?= htmlspecialchars((string)$card['value']) ?></p>
        </div>
        <?php endforeach; ?>
    </div>

    <!-- Quick Links -->
    <div class="grid md:grid-cols-3 gap-4 mb-8">
        <a href="https://eu.posthog.com" target="_blank"
           class="flex items-center gap-3 bg-slate-800 border border-slate-700 hover:border-blue-600 rounded-xl p-4 transition-colors group">
            <div class="w-10 h-10 bg-blue-600/20 rounded-lg flex items-center justify-center text-blue-400 text-xl group-hover:bg-blue-600/30 transition-colors">&#128202;</div>
            <div>
                <p class="font-semibold text-slate-100">PostHog Dashboard</p>
                <p class="text-slate-400 text-xs">eu.posthog.com</p>
            </div>
        </a>
        <a href="https://github.com/<?= GITHUB_REPO ?>" target="_blank"
           class="flex items-center gap-3 bg-slate-800 border border-slate-700 hover:border-blue-600 rounded-xl p-4 transition-colors group">
            <div class="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center text-white text-xl group-hover:bg-slate-600 transition-colors">&#9733;</div>
            <div>
                <p class="font-semibold text-slate-100">GitHub Repository</p>
                <p class="text-slate-400 text-xs"><?= GITHUB_REPO ?></p>
            </div>
        </a>
        <a href="https://scarf.sh" target="_blank"
           class="flex items-center gap-3 bg-slate-800 border border-slate-700 hover:border-blue-600 rounded-xl p-4 transition-colors group">
            <div class="w-10 h-10 bg-purple-600/20 rounded-lg flex items-center justify-center text-purple-400 text-xl group-hover:bg-purple-600/30 transition-colors">&#128273;</div>
            <div>
                <p class="font-semibold text-slate-100">Scarf.sh Downloads</p>
                <p class="text-slate-400 text-xs">omniboard.gateway.scarf.sh</p>
            </div>
        </a>
    </div>

    <!-- Recent App Starts -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700">
            <h3 class="font-semibold text-slate-100">Recent App Starts</h3>
            <p class="text-slate-400 text-sm">Last 10 recorded launches</p>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                    <tr>
                        <th class="px-4 py-3 text-left">Timestamp</th>
                        <th class="px-4 py-3 text-left">Version</th>
                        <th class="px-4 py-3 text-left">Platform</th>
                        <th class="px-4 py-3 text-left">Anonymous ID</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-700/50">
                    <?php
                    $recent = array_slice($app_starts, 0, 10);
                    if (empty($recent)):
                    ?>
                    <tr><td colspan="4" class="px-4 py-6 text-center text-slate-500">No app starts recorded yet.</td></tr>
                    <?php else: foreach ($recent as $s): ?>
                    <tr class="hover:bg-slate-700/30 transition-colors">
                        <td class="px-4 py-3 text-slate-300 font-mono text-xs"><?= htmlspecialchars($s['timestamp'] ?? '') ?></td>
                        <td class="px-4 py-3"><span class="bg-blue-900/40 text-blue-300 text-xs px-2 py-0.5 rounded"><?= htmlspecialchars($s['version'] ?? '–') ?></span></td>
                        <td class="px-4 py-3 text-slate-300"><?= htmlspecialchars(ucfirst($s['platform'] ?? '–')) ?></td>
                        <td class="px-4 py-3 font-mono text-slate-400 text-xs"><?= htmlspecialchars(substr($s['anonymous_id'] ?? '–', 0, 16)) ?>…</td>
                    </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- ════════════════════  ANALYTICS  ════════════════════ -->
<div id="tab-analytics" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">Analytics</h2>

    <?php if (!$posthog_configured): ?>
    <div class="bg-yellow-900/30 border border-yellow-700 rounded-xl px-6 py-5 mb-6">
        <p class="text-yellow-300 font-semibold mb-1">PostHog not configured</p>
        <p class="text-yellow-200/70 text-sm">Add <code class="bg-yellow-900/50 px-1 rounded">POSTHOG_PERSONAL_API_KEY</code> and <code class="bg-yellow-900/50 px-1 rounded">POSTHOG_PROJECT_ID</code> to <code class="bg-yellow-900/50 px-1 rounded">Admin/config.php</code> to enable this section.</p>
    </div>
    <?php else: ?>

    <!-- Info Row -->
    <div class="flex flex-wrap gap-3 mb-6">
        <span class="bg-slate-800 border border-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded-lg">Host: <?= POSTHOG_API_HOST ?></span>
        <span class="bg-slate-800 border border-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded-lg font-mono">Key: <?= substr(POSTHOG_PROJECT_KEY, 0, 12) ?>…</span>
        <span class="bg-slate-800 border border-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded-lg">Project ID: <?= POSTHOG_PROJECT_ID ?></span>
        <a href="<?= POSTHOG_API_HOST ?>/project/<?= POSTHOG_PROJECT_ID ?>/insights" target="_blank"
           class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3 py-1.5 rounded-lg transition-colors">Open PostHog &rarr;</a>
    </div>

    <?php if ($ph_trends === false): ?>
    <div class="bg-red-900/30 border border-red-700 rounded-xl px-6 py-4 mb-6">
        <p class="text-red-300 text-sm">Failed to fetch data from PostHog API. Check that your API key and project ID are correct.</p>
    </div>
    <?php else: ?>

    <!-- 7-day pageview chart -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
        <h3 class="font-semibold text-slate-100 mb-4">Pageviews – Last 7 Days</h3>
        <?php if (empty($ph_trend_data)): ?>
        <p class="text-slate-400 text-sm">No pageview data returned from PostHog.</p>
        <p class="text-slate-400 text-sm"><?= $ph_trend_data ?></p>
        <?php else: ?>
        <canvas id="phTrendChart" height="80"></canvas>
        <?php endif; ?>
    </div>

    <!-- Top pages table -->
    <?php if ($ph_pages && !empty($ph_pages['results'] ?? $ph_pages['result'])): ?>
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden mb-6">
        <div class="px-6 py-4 border-b border-slate-700">
            <h3 class="font-semibold text-slate-100">Top Pages (Last 7 Days)</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                    <tr>
                        <th class="px-4 py-3 text-left">Page URL</th>
                        <th class="px-4 py-3 text-right">Pageviews</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-700/50">
                    <?php
                    $sorted_pages = $ph_pages['results'] ?? $ph_pages['result'] ?? [];
                    usort($sorted_pages, fn($a, $b) => array_sum($b['data'] ?? []) <=> array_sum($a['data'] ?? []));
                    foreach (array_slice($sorted_pages, 0, 15) as $page):
                        $url   = $page['breakdown_value'] ?? $page['label'] ?? '–';
                        $count = array_sum($page['data'] ?? []);
                    ?>
                    <tr class="hover:bg-slate-700/30">
                        <td class="px-4 py-2.5 text-slate-300 text-xs font-mono truncate max-w-md"><?= htmlspecialchars($url) ?></td>
                        <td class="px-4 py-2.5 text-right text-blue-300 font-semibold"><?= number_format($count) ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
    <?php endif; ?>

    <?php endif; // ph_trends check ?>
    <?php endif; // posthog_configured check ?>
</div>

<!-- ════════════════════  RELEASES  ════════════════════ -->
<div id="tab-releases" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">Local Server Releases</h2>

    <?php 
    $latest = !empty($local_releases) ? $local_releases[0] : null; 
    if ($latest): 
    ?>
    <div class="bg-blue-900/20 border border-blue-700 rounded-xl px-6 py-4 mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
            <p class="text-blue-300 text-sm uppercase tracking-widest mb-1">Current Live Version</p>
            <p class="text-white text-3xl font-bold"><?= htmlspecialchars($latest['version']) ?></p>
            <p class="text-slate-400 text-sm mt-1">Released: <?= htmlspecialchars($latest['date']) ?></p>
        </div>
        <div class="flex flex-col gap-2 text-sm">
            <a href="<?= htmlspecialchars($latest['windows_file']) ?>"
               class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors text-center">Windows .exe</a>
            <a href="<?= htmlspecialchars($latest['linux_file']) ?>"
               class="bg-slate-700 hover:bg-slate-600 text-slate-100 px-4 py-2 rounded-lg transition-colors text-center">Linux .tar.gz</a>
        </div>
    </div>
    <?php endif; ?>

    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="font-semibold text-slate-100">All Hosted Versions</h3>
            <span class="text-xs text-slate-400 font-mono">Source: data/releases.json</span>
        </div>
        
        <?php if (empty($local_releases)): ?>
        <p class="px-6 py-4 text-slate-400 text-sm">No versions found in releases.json.</p>
        <?php else: ?>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                    <tr>
                        <th class="px-4 py-3 text-left">Version</th>
                        <th class="px-4 py-3 text-left">Date</th>
                        <th class="px-4 py-3 text-left">Windows</th>
                        <th class="px-4 py-3 text-left">Linux</th>
                        <th class="px-4 py-3 text-left">Notes</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-700/50">
                    <?php foreach ($local_releases as $i => $release):
                        $is_latest = ($i === 0);
                    ?>
                    <tr class="hover:bg-slate-700/30 transition-colors">
                        <td class="px-4 py-3">
                            <span class="font-semibold text-slate-100"><?= htmlspecialchars($release['version']) ?></span>
                            <?php if ($is_latest): ?>
                            <span class="ml-2 bg-blue-700 text-blue-100 text-xs px-1.5 py-0.5 rounded">latest</span>
                            <?php endif; ?>
                        </td>
                        <td class="px-4 py-3 text-slate-400 text-xs">
                            <?= htmlspecialchars($release['date']) ?>
                        </td>
                        <td class="px-4 py-3">
                            <?php if (!empty($release['windows_file'])): ?>
                            <a href="<?= htmlspecialchars($release['windows_file']) ?>" class="text-blue-400 hover:text-blue-300 text-xs">.exe</a>
                            <?php else: ?>
                            <span class="text-slate-600 text-xs">–</span>
                            <?php endif; ?>
                        </td>
                        <td class="px-4 py-3">
                            <?php if (!empty($release['linux_file'])): ?>
                            <a href="<?= htmlspecialchars($release['linux_file']) ?>" class="text-blue-400 hover:text-blue-300 text-xs">.tar.gz</a>
                            <?php else: ?>
                            <span class="text-slate-600 text-xs">–</span>
                            <?php endif; ?>
                        </td>
                        <td class="px-4 py-3 text-slate-400 text-xs truncate max-w-xs">
                            <?= htmlspecialchars($release['notes'] ?? '') ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>

<!-- ════════════════════  APP USAGE  ════════════════════ -->
<div id="tab-appusage" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">App Usage</h2>

    <!-- Summary cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <?php $summary_cards = [
            ['label' => 'Total Starts',    'value' => number_format(count($app_starts))],
            ['label' => 'Unique Installs', 'value' => number_format(count($unique_ids))],
            ['label' => 'Windows Starts',  'value' => number_format($starts_by_platform['windows'] ?? 0)],
            ['label' => 'Linux Starts',    'value' => number_format($starts_by_platform['linux'] ?? 0)],
        ]; foreach ($summary_cards as $c): ?>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1"><?= $c['label'] ?></p>
            <p class="text-white text-2xl font-bold"><?= $c['value'] ?></p>
        </div>
        <?php endforeach; ?>
    </div>

    <!-- Charts row -->
    <div class="grid md:grid-cols-2 gap-6 mb-8">
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 class="font-semibold text-slate-100 mb-4">By Platform</h3>
            <?php if (empty($starts_by_platform)): ?>
            <p class="text-slate-400 text-sm">No data yet.</p>
            <?php else: ?>
            <canvas id="platformChart" height="200"></canvas>
            <?php endif; ?>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 class="font-semibold text-slate-100 mb-4">By Version (Top 10)</h3>
            <?php if (empty($starts_by_version)): ?>
            <p class="text-slate-400 text-sm">No data yet.</p>
            <?php else: ?>
            <canvas id="versionChart" height="200"></canvas>
            <?php endif; ?>
        </div>
    </div>

    <!-- Filters + Table -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700 flex flex-wrap items-center gap-4">
            <h3 class="font-semibold text-slate-100">All Entries</h3>
            <div class="flex flex-wrap gap-3 ml-auto">
                <select id="filterPlatform" onchange="filterTable()"
                    class="bg-slate-700 border border-slate-600 text-slate-100 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option value="">All Platforms</option>
                    <?php foreach (array_keys($starts_by_platform) as $p): ?>
                    <option value="<?= htmlspecialchars($p) ?>"><?= htmlspecialchars(ucfirst($p)) ?></option>
                    <?php endforeach; ?>
                </select>
                <select id="filterVersion" onchange="filterTable()"
                    class="bg-slate-700 border border-slate-600 text-slate-100 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option value="">All Versions</option>
                    <?php foreach (array_keys($starts_by_version) as $v): ?>
                    <option value="<?= htmlspecialchars($v) ?>"><?= htmlspecialchars($v) ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm" id="startsTable">
                <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                    <tr>
                        <th class="px-4 py-3 text-left">#</th>
                        <th class="px-4 py-3 text-left">Timestamp</th>
                        <th class="px-4 py-3 text-left">Version</th>
                        <th class="px-4 py-3 text-left">Platform</th>
                        <th class="px-4 py-3 text-left">Anonymous ID</th>
                        <th class="px-4 py-3 text-left">IP Hash</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-700/50" id="startsTableBody">
                    <?php if (empty($app_starts)): ?>
                    <tr><td colspan="6" class="px-4 py-8 text-center text-slate-500">No app starts recorded yet.</td></tr>
                    <?php else: foreach ($app_starts as $i => $s): ?>
                    <tr class="hover:bg-slate-700/30 transition-colors starts-row"
                        data-platform="<?= htmlspecialchars($s['platform'] ?? '') ?>"
                        data-version="<?= htmlspecialchars($s['version'] ?? '') ?>">
                        <td class="px-4 py-2.5 text-slate-500 text-xs"><?= $i + 1 ?></td>
                        <td class="px-4 py-2.5 text-slate-300 font-mono text-xs"><?= htmlspecialchars($s['timestamp'] ?? '') ?></td>
                        <td class="px-4 py-2.5"><span class="bg-blue-900/40 text-blue-300 text-xs px-2 py-0.5 rounded"><?= htmlspecialchars($s['version'] ?? '–') ?></span></td>
                        <td class="px-4 py-2.5 text-slate-300"><?= htmlspecialchars(ucfirst($s['platform'] ?? '–')) ?></td>
                        <td class="px-4 py-2.5 font-mono text-slate-400 text-xs"><?= htmlspecialchars(substr($s['anonymous_id'] ?? '–', 0, 12)) ?>…</td>
                        <td class="px-4 py-2.5 font-mono text-slate-500 text-xs"><?= htmlspecialchars($s['ip_hash'] ?? '–') ?></td>
                    </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>
        </div>
        <!-- Pagination -->
        <div class="px-6 py-4 border-t border-slate-700 flex flex-wrap items-center justify-between gap-3">
            <span class="text-slate-400 text-sm" id="paginationInfo"></span>
            <div class="flex gap-2">
                <button onclick="changePage(-1)" class="bg-slate-700 hover:bg-slate-600 text-slate-100 text-sm px-3 py-1.5 rounded-lg transition-colors">Prev</button>
                <button onclick="changePage(1)"  class="bg-slate-700 hover:bg-slate-600 text-slate-100 text-sm px-3 py-1.5 rounded-lg transition-colors">Next</button>
            </div>
        </div>
    </div>
</div>

<!-- ════════════════════  USERS  ════════════════════ -->
<div id="tab-users" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">Users</h2>

    <div class="grid md:grid-cols-3 gap-4 mb-8">
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">Total Users</p>
            <p class="text-white text-2xl font-bold"><?= number_format(count($users)) ?></p>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">GitHub OAuth</p>
            <p class="text-white text-2xl font-bold"><?= number_format($users_by_source['github']) ?></p>
        </div>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">Google OAuth</p>
            <p class="text-white text-2xl font-bold"><?= number_format($users_by_source['google']) ?></p>
        </div>
    </div>

    <div class="grid md:grid-cols-2 gap-6 mb-8">
        <!-- Users by source chart -->
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 class="font-semibold text-slate-100 mb-4">Users by Source</h3>
            <?php if (empty($users)): ?>
            <p class="text-slate-400 text-sm">No registered users yet.</p>
            <?php else: ?>
            <canvas id="usersChart" height="200"></canvas>
            <?php endif; ?>
        </div>

        <!-- OAuth URL generators -->
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 class="font-semibold text-slate-100 mb-4">OAuth Login URLs</h3>
            <div class="mb-4">
                <p class="text-slate-400 text-xs uppercase tracking-widest mb-2">GitHub Login URL</p>
                <div class="bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-xs text-slate-300 break-all select-all">
                    <?= htmlspecialchars($github_oauth_url) ?>
                </div>
            </div>
            <div>
                <p class="text-slate-400 text-xs uppercase tracking-widest mb-2">Google Login URL</p>
                <div class="bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-xs text-slate-300 break-all select-all">
                    <?= htmlspecialchars($google_oauth_url) ?>
                </div>
            </div>
            <p class="text-slate-500 text-xs mt-3">Note: state tokens are single-use. Regenerate the page for fresh URLs.</p>
        </div>
    </div>

    <!-- Users table -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="font-semibold text-slate-100">Registered Users</h3>
            <button onclick="exportUsersCSV()"
                class="bg-green-700 hover:bg-green-600 text-white text-sm px-4 py-2 rounded-lg transition-colors">
                Export CSV
            </button>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm" id="usersTable">
                <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                    <tr>
                        <th class="px-4 py-3 text-left">Email</th>
                        <th class="px-4 py-3 text-left">Source</th>
                        <th class="px-4 py-3 text-left">GitHub Username</th>
                        <th class="px-4 py-3 text-left">Registered</th>
                        <th class="px-4 py-3 text-left">Last Login</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-700/50">
                    <?php if (empty($users)): ?>
                    <tr><td colspan="5" class="px-4 py-8 text-center text-slate-500">No users registered yet.</td></tr>
                    <?php else: foreach ($users as $u): ?>
                    <tr class="hover:bg-slate-700/30 transition-colors">
                        <td class="px-4 py-3 text-slate-200"><?= htmlspecialchars($u['email'] ?? '–') ?></td>
                        <td class="px-4 py-3">
                            <?php $src = $u['source'] ?? 'other';
                            $src_cls = $src === 'github' ? 'bg-slate-700 text-slate-200' : ($src === 'google' ? 'bg-blue-900/40 text-blue-300' : 'bg-slate-700 text-slate-400');
                            ?>
                            <span class="text-xs px-2 py-0.5 rounded <?= $src_cls ?>"><?= htmlspecialchars(ucfirst($src)) ?></span>
                        </td>
                        <td class="px-4 py-3 text-slate-300">
                            <?php if (!empty($u['github_username'])): ?>
                            <a href="https://github.com/<?= htmlspecialchars($u['github_username']) ?>"
                               target="_blank" class="hover:text-blue-400"><?= htmlspecialchars($u['github_username']) ?></a>
                            <?php else: ?>
                            <span class="text-slate-600">–</span>
                            <?php endif; ?>
                        </td>
                        <td class="px-4 py-3 text-slate-400 text-xs font-mono"><?= htmlspecialchars(substr($u['registered_at'] ?? '–', 0, 10)) ?></td>
                        <td class="px-4 py-3 text-slate-400 text-xs font-mono"><?= htmlspecialchars(substr($u['last_login'] ?? '–', 0, 10)) ?></td>
                    </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- ════════════════════  GITHUB  ════════════════════ -->
<div id="tab-github" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">GitHub</h2>

    <?php if ($gh_repo === false): ?>
    <div class="bg-red-900/30 border border-red-700 rounded-xl px-6 py-4 mb-6">
        <p class="text-red-300 text-sm">Failed to fetch repository data from GitHub API. Rate limit may be exceeded – add a GitHub token to config.php.</p>
    </div>
    <?php else: ?>

    <!-- Repo stat cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <?php $gh_stats = [
            ['label' => 'Stars',        'value' => number_format($gh_repo['stargazers_count'] ?? 0), 'color' => 'text-yellow-400'],
            ['label' => 'Forks',        'value' => number_format($gh_repo['forks_count']       ?? 0), 'color' => 'text-blue-400'],
            ['label' => 'Watchers',     'value' => number_format($gh_repo['watchers_count']     ?? 0), 'color' => 'text-green-400'],
            ['label' => 'Open Issues',  'value' => number_format($gh_repo['open_issues_count']  ?? 0), 'color' => 'text-red-400'],
            ['label' => 'Language',     'value' => $gh_repo['language'] ?? '–',                        'color' => 'text-purple-400'],
        ]; foreach ($gh_stats as $c): ?>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1"><?= $c['label'] ?></p>
            <p class="<?= $c['color'] ?> text-xl font-bold"><?= htmlspecialchars($c['value']) ?></p>
        </div>
        <?php endforeach; ?>
    </div>

    <!-- Repo info row -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl px-6 py-4 mb-6 flex flex-wrap gap-4 items-center">
        <div>
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">Repository</p>
            <a href="<?= htmlspecialchars($gh_repo['html_url'] ?? '#') ?>" target="_blank"
               class="text-blue-400 hover:text-blue-300 font-semibold"><?= htmlspecialchars($gh_repo['full_name'] ?? GITHUB_REPO) ?></a>
        </div>
        <?php if (!empty($gh_repo['license']['name'])): ?>
        <div>
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">License</p>
            <p class="text-slate-200"><?= htmlspecialchars($gh_repo['license']['name']) ?></p>
        </div>
        <?php endif; ?>
        <?php if (!empty($gh_repo['clone_url'])): ?>
        <div class="flex-1">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1">Clone URL</p>
            <code class="text-slate-300 text-xs bg-slate-900 px-3 py-1.5 rounded"><?= htmlspecialchars($gh_repo['clone_url']) ?></code>
        </div>
        <?php endif; ?>
    </div>

    <?php endif; ?>

    <!-- Recent Commits -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden mb-6">
        <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="font-semibold text-slate-100">Recent Commits</h3>
            <a href="https://github.com/<?= GITHUB_REPO ?>/commits" target="_blank"
               class="text-sm text-blue-400 hover:text-blue-300">View all &rarr;</a>
        </div>
        <?php if ($gh_commits === false): ?>
        <p class="px-6 py-4 text-red-400 text-sm">Failed to fetch commits from GitHub API.</p>
        <?php elseif (empty($gh_commits)): ?>
        <p class="px-6 py-4 text-slate-400 text-sm">No commits found.</p>
        <?php else: ?>
        <ul class="divide-y divide-slate-700/50">
            <?php foreach ($gh_commits as $commit):
                $msg    = $commit['commit']['message'] ?? '–';
                $msg    = explode("\n", $msg)[0]; // first line only
                $author = $commit['commit']['author']['name'] ?? '–';
                $date   = substr($commit['commit']['author']['date'] ?? '', 0, 10);
                $sha    = substr($commit['sha'] ?? '', 0, 7);
                $url    = $commit['html_url'] ?? '#';
            ?>
            <li class="px-6 py-3 flex items-start gap-4 hover:bg-slate-700/30 transition-colors">
                <div class="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                <div class="flex-1 min-w-0">
                    <a href="<?= htmlspecialchars($url) ?>" target="_blank"
                       class="text-slate-100 hover:text-blue-400 transition-colors truncate block">
                        <?= htmlspecialchars($msg) ?>
                    </a>
                    <p class="text-slate-500 text-xs mt-0.5"><?= htmlspecialchars($author) ?> &middot; <?= htmlspecialchars($date) ?> &middot;
                        <span class="font-mono"><?= htmlspecialchars($sha) ?></span>
                    </p>
                </div>
            </li>
            <?php endforeach; ?>
        </ul>
        <?php endif; ?>
    </div>

    <!-- Open Issues -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="font-semibold text-slate-100">Open Issues</h3>
            <a href="https://github.com/<?= GITHUB_REPO ?>/issues" target="_blank"
               class="text-sm text-blue-400 hover:text-blue-300">View all &rarr;</a>
        </div>
        <?php if ($gh_issues === false): ?>
        <p class="px-6 py-4 text-red-400 text-sm">Failed to fetch issues from GitHub API.</p>
        <?php elseif (empty($gh_issues)): ?>
        <p class="px-6 py-4 text-slate-400 text-sm">No open issues.</p>
        <?php else: ?>
        <ul class="divide-y divide-slate-700/50">
            <?php foreach ($gh_issues as $issue):
                $labels = array_map(fn($l) => $l['name'] ?? '', $issue['labels'] ?? []);
            ?>
            <li class="px-6 py-3 hover:bg-slate-700/30 transition-colors">
                <div class="flex items-start gap-3">
                    <span class="text-green-400 mt-0.5 flex-shrink-0">&#9711;</span>
                    <div class="flex-1 min-w-0">
                        <a href="<?= htmlspecialchars($issue['html_url'] ?? '#') ?>" target="_blank"
                           class="text-slate-100 hover:text-blue-400 transition-colors">
                            <?= htmlspecialchars($issue['title'] ?? '–') ?>
                        </a>
                        <p class="text-slate-500 text-xs mt-0.5">
                            #<?= $issue['number'] ?? '' ?> &middot; <?= htmlspecialchars($issue['user']['login'] ?? '–') ?>
                            &middot; <?= htmlspecialchars(substr($issue['created_at'] ?? '', 0, 10)) ?>
                            <?php foreach ($labels as $lbl): ?>
                            <span class="ml-1 bg-slate-700 text-slate-300 text-xs px-1.5 py-0.5 rounded"><?= htmlspecialchars($lbl) ?></span>
                            <?php endforeach; ?>
                        </p>
                    </div>
                </div>
            </li>
            <?php endforeach; ?>
        </ul>
        <?php endif; ?>
    </div>
</div>

<!-- ════════════════════  SERVER  ════════════════════ -->
<div id="tab-server" class="tab-content hidden">
    <h2 class="text-2xl font-bold mb-6 text-white">Server</h2>

    <!-- Server info cards -->
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <?php $server_info = [
            ['label' => 'PHP Version',    'value' => PHP_VERSION],
            ['label' => 'Server Software','value' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'],
            ['label' => 'Operating System','value' => PHP_OS_FAMILY . ' (' . PHP_OS . ')'],
            ['label' => 'Server Timezone','value' => date_default_timezone_get()],
            ['label' => 'Current Time',   'value' => date('Y-m-d H:i:s T')],
            ['label' => 'Memory Usage',   'value' => function_exists('memory_get_usage') ? human_bytes(memory_get_usage(true)) . ' / ' . human_bytes((int)ini_get('memory_limit') * 1024 * 1024) : 'N/A'],
        ]; foreach ($server_info as $c): ?>
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-5">
            <p class="text-slate-400 text-xs uppercase tracking-widest mb-1"><?= $c['label'] ?></p>
            <p class="text-slate-100 font-semibold text-sm break-all"><?= htmlspecialchars($c['value']) ?></p>
        </div>
        <?php endforeach; ?>
    </div>

    <!-- Disk space -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
        <h3 class="font-semibold text-slate-100 mb-4">Disk Space</h3>
        <?php if ($disk_total > 0):
            $pct = round($disk_used / $disk_total * 100);
            $bar_cls = $pct > 90 ? 'bg-red-500' : ($pct > 70 ? 'bg-yellow-500' : 'bg-blue-500');
        ?>
        <div class="flex justify-between text-sm text-slate-300 mb-2">
            <span>Used: <?= human_bytes($disk_used) ?></span>
            <span>Free: <?= human_bytes($disk_free) ?></span>
            <span>Total: <?= human_bytes($disk_total) ?></span>
        </div>
        <div class="w-full bg-slate-700 rounded-full h-3">
            <div class="<?= $bar_cls ?> h-3 rounded-full transition-all" style="width: <?= $pct ?>%"></div>
        </div>
        <p class="text-slate-400 text-xs mt-2"><?= $pct ?>% used</p>
        <?php else: ?>
        <p class="text-slate-400 text-sm">Disk space information not available.</p>
        <?php endif; ?>
    </div>

    <!-- Data files -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden mb-6">
        <div class="px-6 py-4 border-b border-slate-700">
            <h3 class="font-semibold text-slate-100">Data Files</h3>
        </div>
        <table class="w-full text-sm">
            <thead class="text-slate-400 text-xs uppercase tracking-wider bg-slate-900/50">
                <tr>
                    <th class="px-4 py-3 text-left">File</th>
                    <th class="px-4 py-3 text-left">Size</th>
                    <th class="px-4 py-3 text-left">Entries</th>
                    <th class="px-4 py-3 text-left">Exists</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/50">
                <tr class="hover:bg-slate-700/30">
                    <td class="px-4 py-3 font-mono text-slate-300 text-xs">data/app_starts.json</td>
                    <td class="px-4 py-3 text-slate-300"><?= human_bytes($starts_file_size) ?></td>
                    <td class="px-4 py-3 text-slate-300"><?= number_format(count($app_starts)) ?></td>
                    <td class="px-4 py-3">
                        <span class="text-xs px-2 py-0.5 rounded <?= file_exists(DATA_DIR . 'app_starts.json') ? 'bg-green-900/40 text-green-300' : 'bg-slate-700 text-slate-400' ?>">
                            <?= file_exists(DATA_DIR . 'app_starts.json') ? 'Yes' : 'No' ?>
                        </span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-700/30">
                    <td class="px-4 py-3 font-mono text-slate-300 text-xs">data/users.json</td>
                    <td class="px-4 py-3 text-slate-300"><?= human_bytes($users_file_size) ?></td>
                    <td class="px-4 py-3 text-slate-300"><?= number_format(count($users)) ?></td>
                    <td class="px-4 py-3">
                        <span class="text-xs px-2 py-0.5 rounded <?= file_exists(DATA_DIR . 'users.json') ? 'bg-green-900/40 text-green-300' : 'bg-slate-700 text-slate-400' ?>">
                            <?= file_exists(DATA_DIR . 'users.json') ? 'Yes' : 'No' ?>
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- PHP extensions -->
    <div class="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 class="font-semibold text-slate-100 mb-4">Loaded PHP Extensions</h3>
        <div class="flex flex-wrap gap-2">
            <?php foreach (get_loaded_extensions() as $ext): ?>
            <span class="bg-slate-700 text-slate-300 text-xs px-2.5 py-1 rounded"><?= htmlspecialchars($ext) ?></span>
            <?php endforeach; ?>
        </div>
    </div>
</div>

</main>

<!-- ── JavaScript ───────────────────────────────────────────────────────────── -->
<script>
// ── Clock ────────────────────────────────────────────────────────────────────
(function updateClock() {
    const el = document.getElementById('live-clock');
    if (el) el.textContent = new Date().toLocaleString('en-GB', { hour12: false });
    setTimeout(updateClock, 1000);
})();

// ── Tab switching ────────────────────────────────────────────────────────────
const tabContents = document.querySelectorAll('.tab-content');
const tabButtons  = document.querySelectorAll('.tab-btn');

function switchTab(id) {
    tabContents.forEach(el => el.classList.add('hidden'));
    tabButtons.forEach(btn => {
        btn.classList.remove('text-blue-400', 'border-b-2', 'border-blue-500', 'text-slate-100');
        btn.classList.add('text-slate-400');
    });

    const target = document.getElementById('tab-' + id);
    if (target) target.classList.remove('hidden');

    const activeBtn = document.querySelector(`[data-tab="${id}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('text-slate-400');
        activeBtn.classList.add('text-blue-400', 'border-b-2', 'border-blue-500', 'text-slate-100');
    }

    // Lazy-init charts only when tab is shown
    if (id === 'analytics')  initAnalyticsCharts();
    if (id === 'appusage')   initAppUsageCharts();
    if (id === 'users')      initUsersChart();

    // Store active tab in URL hash for persistence
    history.replaceState(null, '', '#' + id);
}

// Activate default tab
const initialTab = (location.hash.slice(1) in {overview:1,analytics:1,releases:1,appusage:1,users:1,github:1,server:1})
    ? location.hash.slice(1)
    : 'overview';
switchTab(initialTab);

// ── Chart.js defaults ─────────────────────────────────────────────────────────
Chart.defaults.color           = '#94a3b8'; // slate-400
Chart.defaults.borderColor     = '#334155'; // slate-700
Chart.defaults.font.family     = 'ui-sans-serif, system-ui, sans-serif';

let platformChartInst, versionChartInst, usersChartInst, phTrendChartInst;

// ── PostHog trend chart ───────────────────────────────────────────────────────
function initAnalyticsCharts() {
    if (phTrendChartInst) return;
    const ctx = document.getElementById('phTrendChart');
    if (!ctx) return;

    const labels = <?= json_encode($ph_trend_labels) ?>;
    const data   = <?= json_encode($ph_trend_data) ?>;
    if (!labels.length) return;

    phTrendChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Pageviews',
                data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: '#1e293b' } },
                y: { beginAtZero: true, grid: { color: '#1e293b' } }
            }
        }
    });
}

// ── App usage charts ──────────────────────────────────────────────────────────
function initAppUsageCharts() {
    if (platformChartInst && versionChartInst) return;

    const pCtx = document.getElementById('platformChart');
    if (pCtx) {
        platformChartInst = new Chart(pCtx, {
            type: 'doughnut',
            data: {
                labels: <?= json_encode($chart_platform_labels) ?>,
                datasets: [{
                    data: <?= json_encode($chart_platform_data) ?>,
                    backgroundColor: ['#3b82f6','#22c55e','#a855f7','#f59e0b'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    const vCtx = document.getElementById('versionChart');
    if (vCtx) {
        versionChartInst = new Chart(vCtx, {
            type: 'bar',
            data: {
                labels: <?= json_encode($chart_version_labels) ?>,
                datasets: [{
                    label: 'Starts',
                    data: <?= json_encode($chart_version_data) ?>,
                    backgroundColor: '#3b82f6',
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#1e293b' } },
                    y: { grid: { display: false } }
                }
            }
        });
    }
}

// ── Users chart ───────────────────────────────────────────────────────────────
function initUsersChart() {
    if (usersChartInst) return;
    const ctx = document.getElementById('usersChart');
    if (!ctx) return;

    usersChartInst = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: <?= json_encode($chart_users_labels) ?>,
            datasets: [{
                data: <?= json_encode($chart_users_data) ?>,
                backgroundColor: ['#6366f1','#3b82f6','#94a3b8'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// ── App starts pagination & filter ───────────────────────────────────────────
let currentPage     = 1;
const rowsPerPage   = 50;
let filteredRows    = [];

function filterTable() {
    const platform = document.getElementById('filterPlatform')?.value ?? '';
    const version  = document.getElementById('filterVersion')?.value  ?? '';
    const allRows  = Array.from(document.querySelectorAll('.starts-row'));

    filteredRows = allRows.filter(row => {
        const matchP = !platform || row.dataset.platform === platform;
        const matchV = !version  || row.dataset.version  === version;
        return matchP && matchV;
    });

    currentPage = 1;
    renderPage();
}

function renderPage() {
    const allRows = Array.from(document.querySelectorAll('.starts-row'));
    allRows.forEach(r => r.classList.add('hidden'));

    const rows  = filteredRows.length ? filteredRows : allRows;
    const start = (currentPage - 1) * rowsPerPage;
    const end   = start + rowsPerPage;
    rows.slice(start, end).forEach(r => r.classList.remove('hidden'));

    const info = document.getElementById('paginationInfo');
    if (info) {
        const total = rows.length;
        info.textContent = total
            ? `Showing ${start + 1}–${Math.min(end, total)} of ${total}`
            : 'No results';
    }
}

function changePage(dir) {
    const rows  = filteredRows.length ? filteredRows : Array.from(document.querySelectorAll('.starts-row'));
    const pages = Math.ceil(rows.length / rowsPerPage);
    currentPage = Math.max(1, Math.min(currentPage + dir, pages));
    renderPage();
}

// Init pagination when the App Usage tab is first opened
document.querySelector('[data-tab="appusage"]')?.addEventListener('click', () => {
    if (!filteredRows.length) {
        filteredRows = Array.from(document.querySelectorAll('.starts-row'));
        renderPage();
    }
}, { once: true });

// Also init if starting on that tab
if (initialTab === 'appusage') {
    filteredRows = Array.from(document.querySelectorAll('.starts-row'));
    renderPage();
    initAppUsageCharts();
}

// ── Export users CSV ─────────────────────────────────────────────────────────
function exportUsersCSV() {
    const table = document.getElementById('usersTable');
    if (!table) return;
    const rows  = Array.from(table.querySelectorAll('tr'));
    const csv   = rows.map(row =>
        Array.from(row.querySelectorAll('th,td'))
            .map(cell => '"' + cell.innerText.replace(/"/g, '""') + '"')
            .join(',')
    ).join('\r\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'omniboard_users_' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
</script>
</body>
</html>
