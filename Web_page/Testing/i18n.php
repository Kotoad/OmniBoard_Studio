<?php
// Set session cookie to last 30 days before starting the session
$session_lifetime = 60 * 60 * 24 * 30; // 30 days

// 1. Tell the server not to delete the session file for 30 days
ini_set('session.gc_maxlifetime', $session_lifetime);

// 2. Determine cookie domain dynamically to support localhost testing and production
$current_host = $_SERVER['HTTP_HOST'];
$cookie_domain = ($current_host === 'localhost') ? 'localhost' : '.omniboardstudio.cz';

// 3. Set cookie parameters including wildcard domain (note the leading dot)
session_set_cookie_params([
    'lifetime' => $session_lifetime,
    'path'     => '/',
    'domain'   => $cookie_domain,
    'secure'   => ($current_host !== 'localhost'), // Requires HTTPS in production
    'httponly' => true,
    'samesite' => 'Lax'
]);

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// 4. Sliding Expiration: Force the browser to reset the cookie timer to 30 days from right NOW
setcookie(
    session_name(),
    session_id(),
    [
        'expires'  => time() + $session_lifetime, 
        'path'     => '/',
        'domain'   => $cookie_domain,
        'secure'   => ($current_host !== 'localhost'),
        'httponly' => true,
        'samesite' => 'Lax'
    ]
);

$allowed_langs = ['en', 'cs']; 

// 1. Check if the user is explicitly changing the language via URL
if (isset($_GET['lang']) && in_array($_GET['lang'], $allowed_langs)) {
    $_SESSION['lang'] = $_GET['lang'];
    // Save the preference in a cookie for 30 days
    setcookie('lang', $_GET['lang'], time() + (86400 * 30), "/"); 
}

// 2. Determine the current language: Session -> Cookie -> Default ('en')
if (isset($_SESSION['lang'])) {
    $current_lang = $_SESSION['lang'];
} elseif (isset($_COOKIE['lang']) && in_array($_COOKIE['lang'], $allowed_langs)) {
    $current_lang = $_COOKIE['lang'];
    // Restore it to the session for quicker access during this request
    $_SESSION['lang'] = $current_lang; 
} else {
    $current_lang = 'en';
}

// 3. Load the corresponding JSON file
$json_file = __DIR__ . "/Translations/{$current_lang}.json";

if (file_exists($json_file)) {
    $translations = json_decode(file_get_contents($json_file), true);
} else {
    $translations = []; 
}

// 4. Helper function to fetch translation text
function t($page, $key_path, $default = '') {
    global $translations;
    
    $keys = explode('.', $key_path);
    $value = $translations[$page] ?? [];
    
    foreach ($keys as $k) {
        if (isset($value[$k])) {
            $value = $value[$k];
        } else {
            return $default; 
        }
    }
    
    return is_string($value) ? $value : $default;
}
?>