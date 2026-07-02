<?php
session_start();

if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

// Validamos que venga un device_id por la URL
$device_id = isset($_GET['device_id']) ? $_GET['device_id'] : '';

if (empty($device_id)) {
    die("Error: No se especificó un ID de dispositivo válido.");
}

$readings = [];
$error_msg = "";
$http_code = 0;

// Apuntamos al endpoint de históricos que definimos en tu router.py
// Pasamos el limit=100 para traer las últimas 100 lecturas
$url_readings = "http://127.0.0.1:8000/devices/mongo/" . urlencode($device_id) . "/readings?limit=100"; 

$ch = curl_init($url_readings);
if ($ch === false) {
    $error_msg = "No se pudo inicializar cURL.";
} else {
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $_SESSION['token'],
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    
    if ($response === false) {
        $error_msg = "Error de conexión cURL: " . curl_error($ch);
    } else {
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    }
    curl_close($ch);
}

if (empty($error_msg)) {
    if ($http_code === 200) {
        $readings = json_decode($response, true);
    } else {
        $result = json_decode($response, true);
        $error_msg = isset($result['detail']) ? $result['detail'] : "Error al traer el historial (Código HTTP: $http_code).";
    }
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historial de Lecturas - Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">

    <div class="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md">
        
        <div class="flex justify-between items-center border-b pb-4 mb-6">
            <div>
                <h1 class="text-2xl font-bold text-gray-800">📊 Historial Cronológico (Time-Series)</h1>
                <p class="text-sm text-purple-700 font-mono mt-1">Dispositivo: <?php echo htmlspecialchars($device_id); ?></p>
            </div>
            <a href="dispositivos.php" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-semibold transition">
                Volver a Dispositivos
            </a>
        </div>

        <?php if (!empty($error_msg)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>Error:</strong> <?php echo htmlspecialchars($error_msg); ?>
            </div>
        <?php else: ?>

            <?php if (empty($readings)): ?>
                <div class="text-center py-12 text-gray-400">
                    <p class="text-lg">No hay registros históricos para este dispositivo en MongoDB.</p>
                    <p class="text-xs mt-1">Las lecturas aparecerán a medida que el ESP32 publique datos por MQTT.</p>
                </div>
            <?php else: ?>
                
                <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                    <table class="min-w-full divide-y divide-gray-200 text-sm">
                        <thead class="bg-gray-50 text-gray-700 font-bold uppercase tracking-wider text-xs">
                            <tr>
                                <th class="px-6 py-3 text-left">Fecha y Hora (Servidor)</th>
                                <th class="px-6 py-3 text-left">Componente / Sensor</th>
                                <th class="px-6 py-3 text-left">Tipo</th>
                                <th class="px-6 py-3 text-right">Lectura</th>
                                <th class="px-6 py-3 text-center">Calidad</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 bg-white text-gray-600">
                            <?php foreach ($readings as $r): ?>
                                <tr class="hover:bg-gray-50 transition">
                                    <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                                        <?php 
                                            // Formateamos el timestamp ISO de MongoDB a algo legible en Latam (DD/MM/AAAA HH:MM:SS)
                                            echo date('d/m/Y H:i:s', strtotime($r['timestamp'])); 
                                        ?>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap font-mono text-xs text-indigo-600">
                                        <?php echo htmlspecialchars($r['sensor_name']); ?>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap capitalize text-xs">
                                        <?php echo htmlspecialchars($r['sensor_type']); ?>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-right font-bold text-gray-900">
                                        <?php echo htmlspecialchars($r['value']); ?> <span class="text-xs font-normal text-gray-400"><?php echo htmlspecialchars($r['unit']); ?></span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-center">
                                        <span class="px-2 py-0.5 text-xs font-bold rounded-full <?php echo ($r['quality'] ?? 'good') === 'good' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'; ?>">
                                            <?php echo htmlspecialchars($r['quality'] ?? 'good'); ?>
                                        </span>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

            <?php endif; ?>

        <?php endif; ?>
    </div>

</body>
</html>