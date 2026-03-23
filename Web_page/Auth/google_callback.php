<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Google OAuth callback
// ─────────────────────────────────────────────

ini_set('display_errors', 1);
error_reporting(E_ALL);

session_start();

require_once __DIR__ . '/../Admin/config.php';

// ── Validate state ───────────────────────────────────────────────────────────
if (empty($_GET['state']) || $_GET['state'] !== ($_SESSION['oauth_state'] ?? '')) {
    $_SESSION['oauth_error'] = 'OAuth state mismatch. Please try again.';
    header('Location: /');
    exit;
}
unset($_SESSION['oauth_state']);

if (empty($_GET['code'])) {
    $_SESSION['oauth_error'] = 'Google OAuth did not return an authorisation code.';
    header('Location: /');
    exit;
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
    $_SESSION['oauth_error'] = 'Failed to obtain Google access token.';
    header('Location: /');
    exit;
}

$access_token = $token_data['access_token'];

// ── Fetch user info ──────────────────────────────────────────────────────────
$user_info = _google_get('https://www.googleapis.com/oauth2/v2/userinfo', $access_token);

if (empty($user_info['email']) || empty($user_info['verified_email'])) {
    $_SESSION['oauth_error'] = 'No verified email address found on your Google account.';
    header('Location: /');
    exit;
}

$primary_email = strtolower($user_info['email']);

// ── Load / update users.json ─────────────────────────────────────────────────
$users = _load_users();
$now   = date('c');

if (isset($users[$primary_email])) {
    $users[$primary_email]['last_login']  = $now;
    $users[$primary_email]['avatar_url']  = $user_info['picture'] ?? '';
    $users[$primary_email]['source']      = 'google';
    $users[$primary_email]['google_name'] = $user_info['name'] ?? '';
} else {
    $users[$primary_email] = [
        'email'           => $primary_email,
        'github_username' => '',
        'avatar_url'      => $user_info['picture'] ?? '',
        'google_name'     => $user_info['name'] ?? '',
        'registered_at'   => $now,
        'last_login'      => $now,
        'source'          => 'google',
    ];
}

_save_users($users);

// ── Set session and redirect ─────────────────────────────────────────────────
echo "<h3>OAuth Success, but stopping here to debug file saving:</h3>";
echo "<b>DATA_DIR literal path:</b> " . DATA_DIR . "<br>";
echo "<b>DATA_DIR resolved path:</b> " . realpath(DATA_DIR) . "<br>";
echo "<b>Does directory exist?</b> " . (is_dir(DATA_DIR) ? 'Yes' : 'No') . "<br>";
echo "<b>Is directory writable?</b> " . (is_writable(DATA_DIR) ? 'Yes' : 'No') . "<br>";
echo "<b>Does users.json exist?</b> " . (file_exists(DATA_DIR . 'users.json') ? 'Yes' : 'No') . "<br>";
if (file_exists(DATA_DIR . 'users.json')) {
    echo "<b>Is users.json writable?</b> " . (is_writable(DATA_DIR . 'users.json') ? 'Yes' : 'No') . "<br>";
}
echo "<br><b>User data being saved:</b><br><pre>";
print_r($users);
echo "</pre>";

// Comment out the redirect so you can see this page
$_SESSION['user_email']    = $primary_email;
// header('Location: /');
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
