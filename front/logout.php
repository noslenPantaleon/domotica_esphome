<?php
// 1. Inicializa la sesión actual para poder manipularla
session_start();

// 2. Desvincula todas las variables de la sesión ($_SESSION['token'], etc.)
session_unset();

// 3. Destruye la sesión por completo en el servidor
session_destroy();

// 4. Redirige al usuario al formulario de login
header("Location: login.php");
exit;
?>