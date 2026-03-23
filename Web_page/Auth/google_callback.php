<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Google OAuth callback
// ─────────────────────────────────────────────

ini_set('display_errors', 1);
error_reporting(E_ALL);

session_start();

echo "<h3>Session Debug</h3>";
echo "Session ID: " . session_id() . "<br>";
echo "Cookies received by server:<br><pre>";
print_r($_COOKIE);
echo "</pre><hr>";

require_once __DIR__ . '/../Admin/config.php';

// ── Validate state ───────────────────────────────────────────────────────────
if (empty($_GET['state']) || $_GET['state'] !== ($_SESSION['oauth_state'] ?? '')) {
    $received = $_GET['state'] ?? 'None';
    $expected = $_SESSION['oauth_state'] ?? 'None';
    die("OAuth state mismatch. Received state: " . htmlspecialchars($received) . " | Expected: " . htmlspecialchars($expected));
}
unset($_SESSION['oauth_state']);

if (empty($_GET['code'])) {
    die('Google OAuth did not return an authorisation code.');
}

$protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$redirect_uri = $protocol . '://' . $_SERVER['HTTP_HOST'] . '/Auth/google_callback.php';

// ── Exchange code for access token ───────────────────────────────────────────
$token_data = _google_post('https://oauth2.googleapis.com/token', [
    'code'          => $_GET['code'],
    'client_id'     => GOOGLE_CLIENT_ID,
    'client_secret' => GOOGLE_CLIENT_SECRET,
    'redirect_uri'  => $redirect_uri,
    'grant_type'    => 'authorization_code',
]);

if (empty($token_data['access_token'])) {
    echo "<h3>Failed to obtain Google access token. Raw response:</h3><pre>";
    print_r($token_data);
    die("</pre>");
}

$access_token = $token_data['access_token'];

// ── Fetch user info ──────────────────────────────────────────────────────────
$user_info = _google_get('https://www.googleapis.com/oauth2/v2/userinfo', $access_token);

if (empty($user_info['email']) || empty($user_info['verified_email'])) {
    echo "<h3>No verified email address found. Raw user info:</h3><pre>";
    print_r($user_info);
    die("</pre>");
}

$primary_email = strtolower($user_info['email']);

// ── Load / update users.json ─────────────────────────────────────────────────
$users = _load_users();
$now   = date('c');

// Identify the account: Use active session if linking, otherwise use Google email
$account_key = $_SESSION['user_email'] ?? $primary_email;

if (!isset($users[$account_key])) {
    // Brand new user registration
    $users[$account_key] = [
        'email'         => $account_key,
        'registered_at' => $now,
        'last_login'    => $now,
        'providers'     => []
    ];
} else {
    // Existing user login
    $users[$account_key]['last_login'] = $now;
}

// Ensure the providers array exists (for migrating older accounts)
if (!isset($users[$account_key]['providers'])) {
    $users[$account_key]['providers'] = [];
}

// Save specific Google data into the providers sub-array
$users[$account_key]['providers']['google'] = [
    'email'       => $primary_email,
    'google_name' => $user_info['name'] ?? '',
    'avatar_url'  => $user_info['picture'] ?? '',
    'linked_at'   => $users[$account_key]['providers']['google']['linked_at'] ?? $now
];

// Maintain top-level fields for Admin dashboard backwards compatibility
$users[$account_key]['source'] = 'multiple'; 
$users[$account_key]['google_name'] = $user_info['name'] ?? '';
$users[$account_key]['avatar_url'] = $user_info['picture'] ?? '';

_save_users($users);

// Set session and redirect to the new Settings page
$_SESSION['user_email'] = $account_key;
header('Location: /Auth/settings.php');
exit;
// ── Helpers ──────────────────────────────────────────────────────────────────
function _google_post(string $url, array $fields): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($fields),
        CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}

function _google_get(string $url, string $token): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ['Authorization: Bearer ' . $token],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}

function _load_users(): array
{
    $file = DATA_DIR . 'users.json';
    if (!file_exists($file)) {
        return [];
    }
    $data = json_decode(file_get_contents($file), true);
    return is_array($data) ? $data : [];
}

function _save_users(array $users): void
{
    if (!is_dir(DATA_DIR)) {
        if (!mkdir(DATA_DIR, 0777, true)) {
            die("Fatal Error: Cannot create the directory: " . DATA_DIR . " - Check permissions.");
        }
    }
    
    $file = DATA_DIR . 'users.json';
    $tmp  = $file . '.tmp';
    
    $writeResult = file_put_contents($tmp, json_encode($users, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);
    if ($writeResult === false) {
        die("Fatal Error: Cannot write to temporary file: " . $tmp . " - Check permissions.");
    }
    
    if (!rename($tmp, $file)) {
        die("Fatal Error: Cannot rename " . $tmp . " to " . $file . " - Check permissions.");
    }
}
