<?php
session_start();

// 1. Control de Seguridad
if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$error_msg = "";
$success_msg = "";
$dispositivos = [];
$clientes = [];

// =========================================================================
// 2. LEER CATÁLOGO DE CLIENTES (Para el desplegable obligatorio)
// =========================================================================
$url_cli = 'http://127.0.0.1:8000/clients/';
$ch_cli = curl_init($url_cli);
curl_setopt($ch_cli, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch_cli, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);
$res_cli = curl_exec($ch_cli);
$code_cli = curl_getinfo($ch_cli, CURLINFO_HTTP_CODE);
curl_close($ch_cli);

if ($code_cli === 200) {
    $clientes = json_decode($res_cli, true);
}

// =========================================================================
// 3. PROCESAR EL FORMULARIO DE ALTA DE DISPOSITIVO (POST hacia FastAPI)
// =========================================================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'crear') {
    $url_create = 'http://127.0.0.1:8000/devices/'; // Revisa si tu endpoint es /devices/ o /dispositivos/
    
    // Armamos el payload según requiera tu backend de FastAPI para IoT
    $data = [
        "device_id"   => $_POST['device_id'] ?? '',   // Ej: esp32_sala_01
        "name"        => $_POST['name'] ?? '',        // Ej: ESP32 Termostato Principal
        "client_id"   => (int)($_POST['client_id'] ?? 0),
        "type"        => $_POST['type'] ?? 'ESP32',
        "is_connected"=> false
    ];

    $ch = curl_init($url_create);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $_SESSION['token'],
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code === 201 || $http_code === 200) {
        $success_msg = "¡Dispositivo IoT registrado exitosamente en el sistema!";
    } else {
        $res_decoded = json_decode($response, true);
        $debug_error_detail = isset($res_decoded['detail']) ? print_r($res_decoded['detail'], true) : $response;
        $error_msg = "Error del Servidor (Código HTTP: $http_code). <br>
                      <small class='block mt-2 font-mono bg-slate-900 text-yellow-300 p-2 rounded text-left overflow-x-auto'>
                      <strong>Respuesta de FastAPI:</strong> " . htmlspecialchars($debug_error_detail) . "
                      </small>";
    }
}

// =========================================================================
// 4. LEER EL LISTADO DE DISPOSITIVOS REGISTRADOS (GET)
// =========================================================================
$url_dev = 'http://127.0.0.1:8000/devices/';
$ch_dev = curl_init($url_dev);
curl_setopt($ch_dev, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch_dev, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);
$res_dev = curl_exec($ch_dev);
$code_dev = curl_getinfo($ch_dev, CURLINFO_HTTP_CODE);
curl_close($ch_dev);

if ($code_dev === 200) {
    $dispositivos = json_decode($res_dev, true);
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Módulo Dispositivos - Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen font-sans flex flex-col md:flex-row">

    <div class="bg-slate-900 text-slate-100 w-full md:w-64 flex-shrink-0 flex flex-col shadow-xl">
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
            <span class="text-2xl">🏠</span>
            <div>
                <h1 class="font-bold text-sm uppercase tracking-wider">Domótica IoT</h1>
                <p class="text-xs text-slate-400">Módulo Dispositivos</p>
            </div>
        </div>
        <nav class="flex-1 p-4 space-y-1">
            <a href="dashboard.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>📊</span> Dashboard General
            </a>
            <a href="dispositivos.php" class="flex items-center gap-3 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition shadow-sm">
                <span>📟</span> Panel IoT (MongoDB)
            </a>
            <div class="pt-4 pb-2 px-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Módulos ABM</div>
            <a href="abm_clientes.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>👥</span> Gestionar Clientes
            </a>
            <a href="abm_locaciones.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>📍</span> Gestionar Locaciones
            </a>
            <a href="abm_usuarios.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>🔐</span> Administrar Usuarios
            </a>
        </nav>
    </div>

    <div class="flex-1 p-6 md:p-8 overflow-y-auto">
        <div class="border-b pb-4 mb-6">
            <h2 class="text-2xl font-black text-gray-800">📟 Aprovisionamiento de Hardware IoT</h2>
            <p class="text-sm text-gray-500">Vinculación de nodos ESP32/ESP8266 a las cuentas de clientes.</p>
        </div>

        <?php if (!empty($success_msg)): ?>
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-6 shadow-sm">
                <strong>Éxito:</strong> <?php echo $success_msg; ?>
            </div>
        <?php endif; ?>
        <?php if (!empty($error_msg)): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-6 shadow-sm">
                <strong>Atención:</strong> <?php echo $error_msg; ?>
            </div>
        <?php endif; ?>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Dispositivos en Red</h3>
                
                <?php if (empty($dispositivos)): ?>
                    <p class="text-center text-gray-400 py-8 text-sm italic">No hay dispositivos registrados en el backend.</p>
                <?php else: ?>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-gray-600">
                            <thead class="bg-gray-50 text-gray-700 text-xs uppercase font-bold border-b border-gray-100">
                                <tr>
                                    <th class="p-3">Device ID (MQTT/Mongo)</th>
                                    <th class="p-3">Nombre Descriptivo</th>
                                    <th class="p-3">Client ID</th>
                                    <th class="p-3">Tipo</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <?php foreach ($dispositivos as $dev): ?>
                                    <tr class="hover:bg-gray-50/80 transition">
                                        <td class="p-3 font-mono text-sm font-bold text-emerald-600">⚙️ <?php echo htmlspecialchars($dev['device_id'] ?? '-'); ?></td>
                                        <td class="p-3 font-medium text-gray-900"><?php echo htmlspecialchars($dev['name'] ?? 'Sin etiqueta'); ?></td>
                                        <td class="p-3 font-mono font-bold text-xs text-blue-600">#<?php echo htmlspecialchars($dev['client_id'] ?? '-'); ?></td>
                                        <td class="p-3">
                                            <span class="bg-gray-100 text-gray-700 px-2 py-0.5 rounded text-xs font-mono uppercase">
                                                <?php echo htmlspecialchars($dev['type'] ?? 'ESP32'); ?>
                                            </span>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                <?php endif; ?>
            </div>

            <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-fit">
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Aprovisionar Equipo</h3>
                
                <form action="abm_dispositivos.php" method="POST" class="space-y-4">
                    <input type="hidden" name="action" value="crear">
                    
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Device ID (Clave en MQTT)</label>
                        <input type="text" name="device_id" required placeholder="Ej: esp32_sala_01" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                        <small class="text-[10px] text-gray-400 block mt-1">Debe coincidir con el ID que publica tu placa de hardware.</small>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre Descriptivo</label>
                        <input type="text" name="name" required placeholder="Ej: Sensor Temperatura Comedor" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Asignar a Cliente</label>
                        <select name="client_id" required class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white">
                            <option value="">-- Seleccionar Propietario --</option>
                            <?php foreach ($clientes as $cli): ?>
                                <option value="<?php echo htmlspecialchars($cli['id'] ?? $cli['client_id']); ?>">
                                    <?php echo htmlspecialchars($cli['name']); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Tipo de Hardware</label>
                        <select name="type" class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white">
                            <option value="ESP32">ESP32 NodeMCU</option>
                            <option value="ESP8266">ESP8266 / Sonoff</option>
                            <option value="Raspberry">Raspberry Pi Gateway</option>
                            <option value="Virtual">Simulador Virtual MQTT</option>
                        </select>
                    </div>

                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold text-sm transition shadow-sm mt-2">
                        💾 Registrar Dispositivo
                    </button>
                </form>
            </div>

        </div>
    </div>

</body>
</html>