<?php
session_start();
unset($_SESSION['user_email']);
unset($_SESSION['oauth_success']);
header('Location: /');
exit;
?>