<?php
session_start();

// Si no hay token guardado en la sesión, redirige al login
if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

// URL apuntando al endpoint correcto en inglés con barra final
$url_clientes = 'http://127.0.0.1:8000/clients/'; 

$ch = curl_init($url_clientes);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPGET, true);

// Forzamos a cURL a seguir redirecciones por si FastAPI tira un 307
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); 

curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$clientes = [];
$error_msg = "";

if ($http_code === 200) {
    $clientes = json_decode($response, true);
} else {
    $result = json_decode($response, true);
    $error_msg = isset($result['detail']) ? $result['detail'] : "No se pudieron cargar los clientes (Error $http_code).";
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestión de Clientes</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">

    <div class="max-w-5xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div class="flex justify-between items-center border-b pb-4 mb-6">
            <h1 class="text-2xl font-bold text-gray-800">👥 Listado de Clientes (MySQL)</h1>
            <a href="dashboard.php" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition">
                Volver al Dashboard
            </a>
        </div>

        <?php if (!empty($error_msg)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>Error de Servidor:</strong> <?php echo htmlspecialchars($error_msg); ?>
            </div>
        <?php else: ?>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-200 text-gray-700 uppercase text-xs tracking-wider">
                            <th class="p-3 border-b">ID</th>
                            <th class="p-3 border-b">Nombre</th>
                            <th class="p-3 border-b">Email</th>
                            <th class="p-3 border-b">Teléfono</th>
                            <th class="p-3 border-b">Estado</th>
                        </tr>
                    </thead>
                    <tbody class="text-gray-600 text-sm divide-y divide-gray-100">
                        <?php if (empty($clientes)): ?>
                            <tr>
                                <td colspan="5" class="p-4 text-center text-gray-400">No hay clientes registrados en la base de datos.</td>
                            </tr>
                        <?php else: ?>
                            <?php foreach ($clientes as $c): ?>
                                <tr class="hover:bg-gray-50 transition">
                                    <td class="p-3 font-mono font-bold text-gray-900">
                                        <?php echo htmlspecialchars($c['client_id'] ?? $c['id'] ?? '-'); ?>
                                    </td>
                                    
                                    <td class="p-3 font-semibold text-gray-800">
                                        <?php echo htmlspecialchars($c['name'] ?? $c['nombre'] ?? 'Sin Nombre'); ?>
                                    </td>
                                    
                                    <td class="p-3">
                                        <?php echo htmlspecialchars($c['email'] ?? '-'); ?>
                                    </td>
                                    
                                    <td class="p-3">
                                        <?php echo htmlspecialchars($c['phone'] ?? $c['telefono'] ?? '-'); ?>
                                    </td>
                                    
                                    <td class="p-3">
                                        <?php 
                                        // Verifica si viene 'active' o 'is_active', sino asume true por defecto
                                        $estado = $c['active'] ?? $c['is_active'] ?? $c['activo'] ?? true; 
                                        ?>
                                        <span class="px-2 py-1 text-xs rounded-full font-bold <?php echo $estado ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'; ?>">
                                            <?php echo $estado ? 'Activo' : 'Inactivo'; ?>
                                        </span>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>

</body>
</html>