<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – GitHub OAuth callback
// ─────────────────────────────────────────────

session_start();

require_once __DIR__ . '/../Admin/config.php';

// ── Validate state to prevent CSRF ──────────────────────────────────────────
if (empty($_GET['state']) || $_GET['state'] !== ($_SESSION['oauth_state'] ?? '')) {
    $_SESSION['oauth_error'] = 'OAuth state mismatch. Please try again.';
    header('Location: /');
    exit;
}
unset($_SESSION['oauth_state']);

if (empty($_GET['code'])) {
    $_SESSION['oauth_error'] = 'GitHub OAuth did not return an authorisation code.';
    header('Location: /');
    exit;
}

// ── Exchange code for access token ──────────────────────────────────────────
$token_response = _github_post('https://github.com/login/oauth/access_token', [
    'client_id'     => GITHUB_CLIENT_ID,
    'client_secret' => GITHUB_CLIENT_SECRET,
    'code'          => $_GET['code'],
]);

if (empty($token_response['access_token'])) {
    $_SESSION['oauth_error'] = 'Failed to obtain GitHub access token.';
    header('Location: /');
    exit;
}

$access_token = $token_response['access_token'];

// ── Fetch authenticated user info ────────────────────────────────────────────
$user = _github_get('https://api.github.com/user', $access_token);
if (empty($user['login'])) {
    $_SESSION['oauth_error'] = 'Failed to fetch GitHub user info.';
    header('Location: /');
    exit;
}

// ── Fetch verified primary email ─────────────────────────────────────────────
$emails       = _github_get('https://api.github.com/user/emails', $access_token);
$primary_email = '';

if (is_array($emails)) {
    foreach ($emails as $email_entry) {
        if (!empty($email_entry['primary']) && !empty($email_entry['verified'])) {
            $primary_email = strtolower($email_entry['email']);
            break;
        }
    }
    // Fall back to any verified email
    if ($primary_email === '') {
        foreach ($emails as $email_entry) {
            if (!empty($email_entry['verified'])) {
                $primary_email = strtolower($email_entry['email']);
                break;
            }
        }
    }
}

if ($primary_email === '') {
    $_SESSION['oauth_error'] = 'No verified email address found on your GitHub account.';
    header('Location: /');
    exit;
}

// ── Load / update users.json ─────────────────────────────────────────────────
$users = _load_users();
$now   = date('c');

// Identify the account: Use active session if linking, otherwise use GitHub email
$account_key = $_SESSION['user_email'] ?? $primary_email;

if (!isset($users[$account_key])) {
    $users[$account_key] = [
        'email'         => $account_key,
        'registered_at' => $now,
        'last_login'    => $now,
        'providers'     => []
    ];
} else {
    $users[$account_key]['last_login'] = $now;
}

// Ensure the providers array exists (for migrating older accounts)
if (!isset($users[$account_key]['providers'])) {
    $users[$account_key]['providers'] = [];
}

// Save specific GitHub data
$users[$account_key]['providers']['github'] = [
    'email'           => $primary_email,
    'github_username' => $user_info['login'] ?? '',
    'avatar_url'      => $user_info['avatar_url'] ?? '',
    'linked_at'       => $users[$account_key]['providers']['github']['linked_at'] ?? $now
];

// Maintain top-level fields for Admin dashboard backwards compatibility
$users[$account_key]['source'] = 'multiple';
$users[$account_key]['github_username'] = $user_info['login'] ?? '';
$users[$account_key]['avatar_url'] = $user_info['avatar_url'] ?? '';

_save_users($users);

// Set session and redirect to the new Settings page
$_SESSION['user_email'] = $account_key;
header('Location: /Auth/settings.php');
exit;

// ── Helpers ──────────────────────────────────────────────────────────────────
function _github_post(string $url, array $fields): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($fields),
        CURLOPT_HTTPHEADER     => [
            'Accept: application/json',
            'User-Agent: OmniBoard-Studio/1.0',
        ],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}

function _github_get(string $url, string $token): mixed
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $token,
            'Accept: application/vnd.github+json',
            'User-Agent: OmniBoard-Studio/1.0',
        ],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '[]', true);
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
        mkdir(DATA_DIR, 0755, true);
    }
    $file = DATA_DIR . 'users.json';
    $tmp  = $file . '.tmp';
    file_put_contents($tmp, json_encode($users, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);
    rename($tmp, $file);
}
