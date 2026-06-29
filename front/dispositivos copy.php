<?php
session_start();

if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$dispositivos = [];
$locaciones_map = []; 
$error_msg = "";
$debug_locations = "No se ejecutó petición.";
$debug_devices = "No se ejecutó petición.";

// =========================================================================
// 1. PETICIÓN A MYSQL: Traemos el catálogo de locaciones reales
// =========================================================================
$url_locations = 'http://127.0.0.1:8000/locations/'; // Agregamos barra al final por las dudas
$ch_loc = curl_init($url_locations);
if ($ch_loc !== false) {
    curl_setopt($ch_loc, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch_loc, CURLOPT_HTTPGET, true);
    curl_setopt($ch_loc, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $_SESSION['token'],
        'Content-Type: application/json'
    ]);
    $res_loc = curl_exec($ch_loc);
    $code_loc = curl_getinfo($ch_loc, CURLINFO_HTTP_CODE);
    curl_close($ch_loc);

    $debug_locations = "Código: " . $code_loc . " | Respuesta: " . $res_loc;


   if ($code_loc === 200) {
        $locaciones_data = json_decode($res_loc, true);
        if (is_array($locaciones_data)) {
            foreach ($locaciones_data as $loc) {
                $loc_id = $loc['location_id'] ?? $loc['id'] ?? null;
                
                // 🚨 Armando el nombre real usando las columnas de tu MySQL (street y street_number)
                if (isset($loc['street']) && isset($loc['street_number'])) {
                    $loc_name = $loc['street'] . " " . $loc['street_number'];
                } else {
                    $loc_name = $loc['name'] ?? $loc['nombre'] ?? 'Ubicación #' . $loc_id;
                }
                
                if ($loc_id !== null) {
                    $locaciones_map[$loc_id] = $loc_name;
                }
            }
        }
    }
}


// =========================================================================
// 2. PETICIÓN A MONGODB: Apuntamos al endpoint correcto del Router
// =========================================================================
// Modificamos a '/devices/' que es donde Pydantic no rebota con un 422
$url_dispositivos = 'http://127.0.0.1:8000/devices/'; 
$ch = curl_init($url_dispositivos);
if ($ch !== false) {
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); 
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $_SESSION['token'],
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $debug_devices = "Código: " . $http_code . " | Respuesta: " . $response;

    if ($http_code === 200) {
        $decoded = json_decode($response, true);
        // Validamos estrictamente que la respuesta sea una lista de dispositivos válida
        if (is_array($decoded) && !isset($decoded['detail'])) {
            $dispositivos = $decoded;
        } else {
            $error_msg = "La API no devolvió una lista válida de dispositivos.";
        }
    } else {
        $result = json_decode($response, true);
        $error_msg = isset($result['detail']) ? json_encode($result['detail']) : "Error al conectar con FastAPI (Código: $http_code).";
    }
} else {
    $error_msg = "No se pudo inicializar cURL.";
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dispositivos IoT - ESPHome</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">

    

    <div class="max-w-6xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div class="flex justify-between items-center border-b pb-4 mb-6">
            <h1 class="text-2xl font-bold text-gray-800">📟 Panel de Dispositivos (MongoDB Atlas)</h1>
            <a href="dashboard.php" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-semibold transition shadow-sm">
                Volver al Dashboard
            </a>
        </div>

        <?php if (!empty($error_msg)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>Error del Sistema:</strong> <?php echo $error_msg; ?>
            </div>
        <?php else: ?>

            <?php if (empty($dispositivos)): ?>
                <p class="text-center text-gray-400 py-8">No se encontraron documentos de dispositivos válidos en MongoDB.</p>
            <?php else: ?>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <?php foreach ($dispositivos as $disp): ?>
                        <?php if (!is_array($disp)) continue; ?>
                        <div class="bg-gray-50 border border-gray-200 p-5 rounded-xl shadow-sm flex flex-col justify-between">
                            
                            <div>
                                <div class="flex justify-between items-start mb-3">
                                    <h3 class="text-sm font-mono font-bold text-purple-700 bg-purple-50 px-2 py-1 rounded border border-purple-200 select-all">
                                        🆔 <?php echo htmlspecialchars($disp['_id'] ?? $disp['id'] ?? 'Desconocido'); ?>
                                    </h3>
                                    <span class="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full font-bold">
                                        Client ID: #<?php echo htmlspecialchars($disp['client_id'] ?? '-'); ?>
                                    </span>
                                </div>
                                
                                <div class="space-y-1.5 text-sm text-gray-600 mb-4">
                                    <p>🏷️ <strong>Nombre:</strong> <span class="text-gray-900 font-medium"><?php echo htmlspecialchars($disp['device_name'] ?? $disp['name'] ?? 'Dispositivo Sin Nombre'); ?></span></p>
                                    <p>🔌 <strong>Modelo:</strong> <span class="text-gray-900 font-medium"><?php echo htmlspecialchars($disp['device_type'] ?? $disp['type'] ?? 'Genérico'); ?></span></p>
                                    
                                    <p>📍 <strong>Locación:</strong> 
                                        <span class="text-gray-900 font-medium bg-amber-50 text-amber-900 px-2 py-0.5 rounded border border-amber-200 text-xs font-semibold">
                                            <?php 
                                                $loc_raw = $disp['location_id'] ?? $disp['location'] ?? null;
                                                
                                                if ($loc_raw !== null) {
                                                    if (is_array($loc_raw)) {
                                                        $id_desde_array = $loc_raw['id'] ?? $loc_raw['location_id'] ?? null;
                                                        if ($id_desde_array !== null && isset($locaciones_map[$id_desde_array])) {
                                                            echo htmlspecialchars($locaciones_map[$id_desde_array]) . " (ID: #$id_desde_array)";
                                                        } else {
                                                            echo htmlspecialchars($loc_raw['name'] ?? $loc_raw['description'] ?? 'Estructura Compleja');
                                                        }
                                                    } elseif (is_numeric($loc_raw)) {
                                                        if (isset($locaciones_map[$loc_raw])) {
                                                            echo htmlspecialchars($locaciones_map[$loc_raw]) . " (ID: #$loc_raw)";
                                                        } else {
                                                            echo "ID de Locación #$loc_raw (No asignada en MySQL)";
                                                        }
                                                    } else {
                                                        echo htmlspecialchars($loc_raw);
                                                    }
                                                } else {
                                                    echo "ID 0 (Por defecto)";
                                                }
                                            ?>
                                        </span>
                                    </p>

                                    <p>🟢 <strong>Estado General:</strong> 
                                        <span class="px-2 py-0.5 text-xs font-bold rounded-full <?php echo ($disp['overall_state'] ?? '') === 'active' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'; ?>">
                                            <?php echo htmlspecialchars($disp['overall_state'] ?? 'unknown'); ?>
                                        </span>
                                    </p>
                                </div>

                                <div class="mt-4">
                                    <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Lecturas Actuales (MQTT)</h4>
                                    <?php if (empty($disp['sensors'])): ?>
                                        <p class="text-xs text-gray-400 italic bg-gray-100 p-2 rounded">Esperando telemetría...</p>
                                    <?php else: ?>
                                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                            <?php foreach ($disp['sensors'] as $sensor): ?>
                                                <div class="bg-white border border-gray-100 rounded-lg p-3 shadow-inner flex items-center justify-between">
                                                    <div>
                                                        <p class="text-xs font-semibold text-gray-500 truncate">
                                                            📊 <?php echo htmlspecialchars($sensor['sensor_name'] ?? 'Sensor'); ?>
                                                        </p>
                                                        <p class="text-lg font-black text-gray-800 mt-0.5">
                                                            <?php echo htmlspecialchars($sensor['last_value'] ?? '0'); ?> <span class="text-sm font-normal text-gray-500"><?php echo htmlspecialchars($sensor['unit'] ?? ''); ?></span>
                                                        </p>
                                                    </div>
                                                </div>
                                            <?php endforeach; ?>
                                        </div>
                                    <?php endif; ?>
                                </div>
                            </div>

                            <div class="mt-6 pt-3 border-t border-gray-200 text-right">
                                <a href="lecturas.php?device_id=<?php echo urlencode($disp['_id'] ?? $disp['id'] ?? ''); ?>" 
                                   class="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition">
                                    Ver Historial Cronológico 📊
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