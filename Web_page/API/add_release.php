<?php
require_once __DIR__ . '/../Admin/config.php';

// ── Handle new release submission ───────────────────────────────────────────

$headers = getallheaders();
$auth_header = $headers['Authorization'] ?? '';
$expected_token = 'Bearer ' . ($_ENV['ACTION_API_TOKEN'] ?? 'UNSET');

if ($expected_token === 'Bearer UNSET' || $auth_header !== $expected_token) {
    http_response_code(403);
    die('Forbidden: Invalid API token.');
}

$data = json_decode(file_get_contents('php://input'), true);
if (!$data || empty($data['version'])) {
    http_response_code(400);
    die('Bad Request: Missing required fields (version, url).');
}

try {
    $stmt = $pdo->prepare("
        INSERT INTO releases (version, release_date, windows_file, linux_file, notes) 
        VALUES (?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE 
        release_date=?, windows_file=?, linux_file=?, notes=?
    ");

    $stmt->execute([
        $data['version'], $data['date'], $data['windows_file'], $data['linux_file'], $data['notes'],
        // These are the values used if the version already exists (Update)
        $data['date'], $data['windows_file'], $data['linux_file'], $data['notes']
    ]);

    echo "Release added/updated successfully.";
} catch (PDOException $e) {
    http_response_code(500);
    die('Internal Server Error: ' . $e->getMessage());
}