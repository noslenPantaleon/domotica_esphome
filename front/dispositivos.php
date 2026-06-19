<?php
session_start();

if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

// 1. Inicializamos las variables por defecto para evitar CUALQUIER Warning
$dispositivos = [];
$error_msg = "";
$response = "";
$http_code = 0;

// 2. Probamos con la URL en inglés. 
// Si en tu main.py el prefijo es singular, cambialo a 'http://127.0.0.1:8000/device/mongo'
$url_dispositivos = 'http://127.0.0.1:8000/devices/mongo'; 

$ch = curl_init($url_dispositivos);
if ($ch === false) {
    $error_msg = "No se pudo inicializar cURL en el servidor PHP.";
} else {
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); 
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $_SESSION['token'],
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    
    // Si cURL falla a nivel de red (ej: FastAPI apagado o URL rota)
    if ($response === false) {
        $error_msg = "Error de conexión cURL: " . curl_error($ch);
    } else {
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    }
    curl_close($ch);
}

// 3. Procesamos la respuesta si no hubo errores de red
if (empty($error_msg)) {
    if ($http_code === 200) {
        $dispositivos = json_decode($response, true);
    } else {
        $result = json_decode($response, true);
        $error_msg = isset($result['detail']) ? $result['detail'] : "FastAPI denegó el acceso (Código HTTP: $http_code).";
    }
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dispositivos IoT - ESPHome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">

    <div class="max-w-5xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div class="flex justify-between items-center border-b pb-4 mb-6">
            <h1 class="text-2xl font-bold text-gray-800">📟 Estado de Dispositivos (MongoDB)</h1>
            <a href="dashboard.php" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition">
                Volver al Dashboard
            </a>
        </div>

        <?php if (!empty($error_msg)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>Error del Sistema:</strong> <?php echo htmlspecialchars($error_msg); ?>
            </div>
            
            <div class="bg-gray-50 p-4 rounded border text-xs font-mono text-gray-600">
                <p class="font-bold mb-1">💡 Tips para solucionar el 404/500 en Dispositivos:</p>
                <p>1. Verifica en tu <span class="bg-gray-200 px-1 rounded">main.py</span> si el prefix es <span class="bg-gray-200 px-1 rounded">"/devices"</span> o <span class="bg-gray-200 px-1 rounded">"/device"</span>.</p>
                <p>2. Si el prefijo es correcto, probá agregando una barra al final de la URL en la línea 13 de este archivo (<span class="bg-gray-200 px-1 rounded">/devices/mongo/</span>).</p>
            </div>
        <?php else: ?>

            <?php if (empty($dispositivos)): ?>
                <p class="text-center text-gray-400 py-8">No se encontraron documentos de dispositivos en MongoDB para tu cuenta o rol.</p>
            <?php else: ?>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <?php foreach ($dispositivos as $disp): ?>
                        <div class="bg-gray-50 border border-gray-200 p-5 rounded-xl shadow-sm hover:shadow-md transition">
                            <div class="flex justify-between items-start mb-3">
                                <h3 class="text-sm font-mono font-bold text-purple-700 bg-purple-50 px-2 py-1 rounded border border-purple-200 select-all">
                                    🆔 <?php echo htmlspecialchars($disp['_id'] ?? $disp['id'] ?? 'ID Desconocido'); ?>
                                </h3>
                                <span class="bg-blue-100 text-blue-800 text-xs px-2.5 py-0.5 rounded-full font-bold">
                                    Client ID: #<?php echo htmlspecialchars($disp['client_id'] ?? '-'); ?>
                                </span>
                            </div>
                            
                            <div class="space-y-2 text-sm text-gray-600">
                                <p>🏷️ <strong>Nombre:</strong> <?php echo htmlspecialchars($disp['name'] ?? 'Dispositivo ESPHome'); ?></p>
                                <p>🔌 <strong>Tipo / Modelo:</strong> <?php echo htmlspecialchars($disp['type'] ?? $disp['model'] ?? 'Genérico'); ?></p>
                                <p>📍 <strong>Ubicación ID (SQL):</strong> <?php echo htmlspecialchars($disp['location_id'] ?? 'No asignada'); ?></p>
                            </div>

                            <div class="mt-4 pt-3 border-t border-gray-200 text-right">
                                <a href="lecturas.php?device_id=<?php echo urlencode($disp['_id'] ?? $disp['id']); ?>" 
                                   class="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800">
                                    Ver lecturas de sensores 📊
                                </a>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>

        <?php endif; ?>
    </div>

</body>
</html>