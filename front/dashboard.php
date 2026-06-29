<?php
// 1. PRIMERO LA LÓGICA: Validamos sesión y traemos los datos de FastAPI
session_start();

if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$url_me = 'http://127.0.0.1:8000/auth/me';

$ch = curl_init($url_me);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPGET, true);

curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code === 200) {
    $user_data = json_decode($response, true);
} else {
    session_destroy();
    header("Location: login.php?error=session_expirada");
    exit;
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Domótica ESPHome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">

    <nav class="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
        <h1 class="text-xl font-bold tracking-wide">🏠 Sistema de Domótica</h1>
        <div class="flex items-center space-x-4">
            <span class="text-sm bg-blue-700 px-3 py-1 rounded-full border border-blue-400">
                Rol: <?php echo htmlspecialchars($user_data['role']); ?>
            </span>
            <a href="logout.php" class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm font-semibold transition">
                Cerrar Sesión
            </a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        
        <div class="border-b pb-4 mb-6">
            <h2 class="text-2xl font-bold text-gray-800">
                ¡Bienvenido, <?php echo htmlspecialchars($user_data['email']); ?>!
            </h2>
            <p class="text-gray-500 text-sm mt-1">Has ingresado correctamente al panel de control.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <?php if ($user_data['role'] === 'admin'): ?>
                <div class="border border-gray-200 p-5 rounded-lg hover:shadow-md transition">
                    <h3 class="text-lg font-semibold text-blue-600 mb-2">👥 Gestión de Clientes</h3>
                    <p class="text-gray-600 text-sm mb-4">Administra los clientes cargados en el sistema MySQL.</p>
                    <a href="clientes.php" class="inline-block text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        Ir a Clientes
                    </a>
                </div>
            <?php endif; ?>

            <div class="border border-gray-200 p-5 rounded-lg hover:shadow-md transition">
                <h3 class="text-lg font-semibold text-green-600 mb-2">📟 Dispositivos IoT (ESPHome)</h3>
                <p class="text-gray-600 text-sm mb-4">Monitorea tus dispositivos enlazados con MongoDB.</p>
                <a href="dispositivos.php" class="inline-block text-sm bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    Ver Dispositivos
                </a>
            </div>

        </div>

    </main>

</body>
</html>