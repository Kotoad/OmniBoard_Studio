<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Version endpoint
//  Returns the current release JSON and, when
//  optional params are present, logs the app start.
// ─────────────────────────────────────────────

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once __DIR__ . '/../Admin/config.php';

// ── Optional telemetry parameters sent by the app ───────────────────────────
$version      = substr(preg_replace('/[^a-zA-Z0-9._\-]/', '', $_REQUEST['v']  ?? ''), 0, 32);
$platform     = in_array($_REQUEST['p'] ?? '', ['windows', 'linux', 'macos'], true)
                    ? $_REQUEST['p']
                    : '';
$anonymous_id = substr(preg_replace('/[^a-zA-Z0-9\-]/', '', $_REQUEST['id'] ?? ''), 0, 64);

// Only log when at least one telemetry param was supplied
if ($version !== '' || $platform !== '' || $anonymous_id !== '') {
    $raw_ip  = $_SERVER['HTTP_CF_CONNECTING_IP']
            ?? $_SERVER['HTTP_X_FORWARDED_FOR']
            ?? $_SERVER['REMOTE_ADDR']
            ?? '';
    $raw_ip  = trim(explode(',', $raw_ip)[0]);
    $ip_hash = substr(hash('sha256', $raw_ip . IP_HASH_SALT), 0, 12);

    $entry = [
        'timestamp'    => date('c'),
        'version'      => $version ?: 'unknown',
        'platform'     => $platform ?: 'unknown',
        'ip_hash'      => $ip_hash,
        'anonymous_id' => $anonymous_id,
    ];

    $file    = DATA_DIR . 'app_starts.json';
    $entries = [];

    if (file_exists($file)) {
        $raw = file_get_contents($file);
        if ($raw !== false) {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) {
                $entries = $decoded;
            }
        }
    }

    $entries[] = $entry;

    if (count($entries) > 10000) {
        $entries = array_slice($entries, -10000);
    }

    if (!is_dir(DATA_DIR)) {
        mkdir(DATA_DIR, 0755, true);
    }

    $tmp = $file . '.tmp';
    if (file_put_contents($tmp, json_encode($entries, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX) !== false) {
        rename($tmp, $file);
    }
}

// ── Return the dynamic release manifest ──────────────────────────────────────
$releases_file = DATA_DIR . 'releases.json';
$releases = file_exists($releases_file) ? json_decode(file_get_contents($releases_file), true) : [];

if (!empty($releases)) {
    $latest = $releases[0];
    // Create absolute URLs if relative paths are used in the JSON
    $domain = "https://omniboardstudio.cz"; 
    echo json_encode([
        'tag_name' => $latest['version'],
        'assets'   => [
            [
                'name'         => 'OmniBoard_Online_Installer.exe',
                'download_url' => $domain . $latest['windows_file'],
            ],
            [
                'name'         => 'OmniBoard_Studio_Linux.tar.gz',
                'download_url' => $domain . $latest['linux_file'],
            ],
        ],
    ]);
} else {
    // Fallback if JSON is missing
    echo json_encode(['error' => 'No releases found on server']);
}