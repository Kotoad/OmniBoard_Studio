<?php
// Web_page/Auth/login.php

// 1. Force the canonical domain (Must match your GitHub/Google Callback exactly)
$canonical_domain = 'omniboardstudio.cz'; // Change to 'www.omniboardstudio.cz' if you prefer WWW

if ($_SERVER['HTTP_HOST'] !== 'localhost' && $_SERVER['HTTP_HOST'] !== $canonical_domain) {
    $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
    header('Location: ' . $protocol . '://' . $canonical_domain . $_SERVER['REQUEST_URI']);
    exit;
}

// 2. Now it is safe to start the session
session_start();
require_once __DIR__ . '/../Admin/config.php';

$provider = $_GET['provider'] ?? '';

// Generate CSRF state token
$state = bin2hex(random_bytes(16));
$_SESSION['oauth_state'] = $state;

if ($provider === 'github') {
    $url = 'https://github.com/login/oauth/authorize?client_id=' 
         . urlencode(GITHUB_CLIENT_ID) 
         . '&scope=user:email&state=' . urlencode($state);
    header('Location: ' . $url);
    exit;
} elseif ($provider === 'google') {
    $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
    $redirect_uri = $protocol . '://' . $_SERVER['HTTP_HOST'] . '/Auth/google_callback.php';

    $url = 'https://accounts.google.com/o/oauth2/v2/auth?' . http_build_query([
        'client_id'     => GOOGLE_CLIENT_ID,
        'redirect_uri'  => $redirect_uri,
        'response_type' => 'code',
        'scope'         => 'openid email profile',
        'state'         => $state,
        'access_type'   => 'online',
    ]);
    header('Location: ' . $url);
    exit;
}

echo "Invalid provider.";
?>