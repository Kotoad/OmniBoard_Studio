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

    $stmt = $pdo->prepare("
        INSERT INTO app_starts (started_at, version, platform, ip_hash, anonymous_id, starts)
        VALUES (?, ?, ?, ?, ?, 1)
        ON DUPLICATE KEY UPDATE
        started_at=VALUES(started_at), version=VALUES(version), platform=VALUES(platform), ip_hash=VALUES(ip_hash), anonymous_id=VALUES(anonymous_id), starts = starts + 1
    ");
    $stmt->execute([date('c'), $version, $platform, $ip_hash, $anonymous_id]);
}

// ── Return the dynamic release manifest ──────────────────────────────────────

$stmt = $pdo->prepare("SELECT * FROM releases ORDER BY id DESC");
$stmt->execute();
$releases = $stmt->fetchAll();

$latest_release = $releases[0] ?? null;


if (!empty($latest_release)) {
    // Create absolute URLs if relative paths are used in the JSON
    $domain = "https://omniboardstudio.cz"; 
    echo json_encode([
        'tag_name' => $latest_release['version'],
        'assets'   => [
            [
                'name'         => 'OmniBoard_Online_Installer.exe',
                'download_url' => $domain . $latest_release['windows_file'],
            ],
            [
                'name'         => 'OmniBoard_Studio_Linux.tar.gz',
                'download_url' => $domain . $latest_release['linux_file'],
            ],
        ],
    ]);
} else {
    // Fallback if JSON is missing
    echo json_encode(['error' => 'No releases found on server']);
}