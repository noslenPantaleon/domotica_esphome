<?php
session_start();

// Si ya está logueado, lo mandamos al index/dashboard
if (isset($_SESSION['token'])) {
    header("Location: dashboard.php");
    exit;
}

$error = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // URL de tu backend de FastAPI (ajústala a tu endpoint real de login)
    $url = 'http://127.0.0.1:8000/auth/login'; 
    

    // FastAPI espera los datos en formato x-www-form-urlencoded por el estándar OAuth2
    $data = [
        'username' => $username,
        'password' => $password
    ];

    // Configuración de la petición hacia FastAPI mediante cURL
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/x-www-form-urlencoded'
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $result = json_decode($response, true);

    if ($http_code === 200 && isset($result['access_token'])) {
        // ¡Éxito! Guardamos el token en la sesión de PHP
        $_SESSION['token'] = $result['access_token'];
        $_SESSION['username'] = $username;
        
        // Redirigimos a la página protegida
        header("Location: dashboard.php");
        exit;
    } else {
        // Capturamos el error que mandó FastAPI
        $error = isset($result['detail']) ? $result['detail'] : "Usuario o contraseña incorrectos.";
    }
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - PHP & FastAPI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">

    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center text-gray-800">Iniciar Sesión (PHP)</h2>
        
        <?php if (!empty($error)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-sm">
                <?php echo htmlspecialchars($error); ?>
            </div>
        <?php endif; ?>

        <form action="login.php" method="POST" class="space-y-4">
            <div>
                <label class="block text-gray-700 text-sm font-bold mb-1">Email / Usuario</label>
                <input type="text" name="username" required
                    class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            
            <div>
                <label class="block text-gray-700 text-sm font-bold mb-1">Contraseña</label>
                <input type="password" name="password" required
                    class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>

            <button type="submit" 
                class="w-full bg-green-600 text-white font-bold py-2 px-4 rounded-md hover:bg-green-700 transition duration-200">
                Ingresar
            </button>
        </form>
    </div>

</body>
</html>