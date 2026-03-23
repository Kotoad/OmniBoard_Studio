<?php

// Load .env variables manually
$envFile = __DIR__ . '/.env'; // Ensure this points to where the .env file is located
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        // Ignore comments
        if (strpos(trim($line), '#') === 0) continue;
        
        // Split variable name and value
        list($name, $value) = explode('=', $line, 2);
        $name = trim($name);
        $value = trim($value);
        
        // Remove quotes if they exist around the value
        $value = trim($value, '"\'');
        
        // Inject into the environment
        if (!array_key_exists($name, $_SERVER) && !array_key_exists($name, $_ENV)) {
            putenv(sprintf('%s=%s', $name, $value));
            $_ENV[$name] = $value;
            $_SERVER[$name] = $value;
        }
    }
}

// ─────────────────────────────────────────────
//  OmniBoard Studio – Admin Configuration
// ─────────────────────────────────────────────

// PostHog REST API credentials (server-side only)
// Get your personal API key from: https://eu.posthog.com/settings/user-api-keys
define('POSTHOG_PERSONAL_API_KEY', $_ENV['POSTHOG_PERSONAL_API_KEY'] ?? '');
define('POSTHOG_PROJECT_ID',       $_ENV['POSTHOG_PROJECT_ID'] ?? '');   // numeric, e.g. 12345

// PostHog project settings (used for JS snippet & API base)
define('POSTHOG_API_HOST',    'https://eu.posthog.com');
define('POSTHOG_PROJECT_KEY', $_ENV['POSTHOG_PROJECT_KEY'] ?? '');  // alphanumeric, e.g. phc_abc123def456

// GitHub API token (optional – raises rate limit from 60 to 5000 req/h)
// Create at: https://github.com/settings/tokens  (public_repo scope is enough)
define('GITHUB_TOKEN', $_ENV['TOKEN_GITHUB'] ?? '');
define('GITHUB_REPO',  'Kotoad/APP_PyQt');

// GitHub OAuth application credentials
// Register at: https://github.com/settings/applications/new
// Callback URL: https://omniboardstudio.cz/Auth/github_callback.php
define('GITHUB_CLIENT_ID',     $_ENV['CLIENT_ID_GITHUB'] ?? '');
define('GITHUB_CLIENT_SECRET', $_ENV['CLIENT_SECRET_GITHUB'] ?? '');

// Google OAuth application credentials
// Create at: https://console.cloud.google.com/apis/credentials
// Callback URL: https://omniboardstudio.cz/Auth/google_callback.php
define('GOOGLE_CLIENT_ID',     $_ENV['GOOGLE_CLIENT_ID'] ?? '');
define('GOOGLE_CLIENT_SECRET', $_ENV['GOOGLE_CLIENT_SECRET'] ?? '');

// Admin login credentials
// Username stored in plain text; password stored as bcrypt hash.
// Default password: changeme123  – change this before deploying!
// To regenerate: php -r "echo password_hash('your_password', PASSWORD_BCRYPT);"
define('ADMIN_USERNAME',      $_ENV['ADMIN_USERNAME'] ?? 'admin');
define('ADMIN_PASSWORD_HASH', $_ENV['ADMIN_PASSWORD_HASH'] ?? '');

// Data directory (writable by the web server)
define('DATA_DIR', __DIR__ . '/../data/');

// Secret salt used for IP anonymisation in app_starts.json
// Set this to a long random string. Must never change once data has been collected.
define('IP_HASH_SALT', $_ENV['IP_HASH_SALT'] ?? '');

// Session lifetime in seconds (4 hours)
define('ADMIN_SESSION_LIFETIME', 4 * 60 * 60);
