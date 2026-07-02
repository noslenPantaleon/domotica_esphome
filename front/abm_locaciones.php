<?php
session_start();

// 1. Control de Seguridad
if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$error_msg = "";
$success_msg = "";
$locaciones = [];

// =========================================================================
// 2. PROCESAR EL FORMULARIO DE ALTA (POST hacia FastAPI)
// =========================================================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'crear') {
    $url_create = 'http://127.0.0.1:8000/locations/'; // Tu endpoint de FastAPI
    
    // Armamos el payload con los nombres exactos que espera tu Pydantic en Python
    $data = [
        "country"       => $_POST['country'] ?? 'Argentina',
        "district"      => $_POST['district'] ?? '',
        "street"        => $_POST['street'] ?? '',
        "street_number" => (int)($_POST['street_number'] ?? 0),
        "latitude"      => $_POST['latitude'] ?? '0.0',
        "longitude"     => $_POST['longitude'] ?? '0.0'
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
        $success_msg = "¡Locación guardada con éxito en MySQL!";
    } else {
        $res_decoded = json_decode($response, true);
        $error_msg = $res_decoded['detail'] ?? "Error al guardar (Código HTTP: $http_code)";
        if (is_array($error_msg)) {
            $error_msg = json_encode($error_msg);
        }
    }
}

// =========================================================================
// 3. LEER EL CATÁLOGO ACTUAL (GET desde FastAPI)
// =========================================================================
$url_list = 'http://127.0.0.1:8000/locations/';
$ch_list = curl_init($url_list);
curl_setopt($ch_list, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch_list, CURLOPT_HTTPGET, true);
curl_setopt($ch_list, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);
$res_list = curl_exec($ch_list);
$code_list = curl_getinfo($ch_list, CURLINFO_HTTP_CODE);
curl_close($ch_list);

if ($code_list === 200) {
    $locaciones = json_decode($res_list, true);
} else {
    $error_msg = "No se pudo cargar la lista de locaciones existentes.";
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABM Locaciones - Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen font-sans flex flex-col md:flex-row">

    <div class="bg-slate-900 text-slate-100 w-full md:w-64 flex-shrink-0 flex flex-col shadow-xl">
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
            <span class="text-2xl">🏠</span>
            <div>
                <h1 class="font-bold text-sm uppercase tracking-wider">Domótica IoT</h1>
                <p class="text-xs text-slate-400">Módulo Locaciones</p>
            </div>
        </div>
        <nav class="flex-1 p-4 space-y-1">
            <a href="dashboard.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>📊</span> Dashboard General
            </a>
            <a href="dispositivos.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>📟</span> Panel IoT (MongoDB)
            </a>
            <div class="pt-4 pb-2 px-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Módulos ABM</div>
            <a href="abm_clientes.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>👥</span> Gestionar Clientes
            </a>
            <a href="abm_locaciones.php" class="flex items-center gap-3 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition shadow-sm">
                <span>📍</span> Gestionar Locaciones
            </a>
            <a href="abm_usuarios.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>🔐</span> Administrar Usuarios
            </a>
        </nav>
        <div class="p-4 border-t border-slate-800">
            <a href="logout.php" class="flex items-center justify-center gap-2 w-full bg-red-600/20 text-red-400 py-2 px-4 rounded-lg text-xs font-semibold transition border border-red-500/30">
                <span>🚪</span> Cerrar Sesión
            </a>
        </div>
    </div>

    <div class="flex-1 p-6 md:p-8 overflow-y-auto">
        <div class="border-b pb-4 mb-6">
            <h2 class="text-2xl font-black text-gray-800">📍 Catálogo Estructural de Locaciones</h2>
            <p class="text-sm text-gray-500">Altas y consultas de domicilios físicos en la base de datos relacional MySQL.</p>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Ubicaciones Configuradas</h3>
                
                <?php if (empty($locaciones)): ?>
                    <p class="text-center text-gray-400 py-8 text-sm italic">No hay locaciones cargadas en el sistema relacional.</p>
                <?php else: ?>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-gray-600">
                            <thead class="bg-gray-50 text-gray-700 text-xs uppercase font-bold border-b border-gray-100">
                                <tr>
                                    <th class="p-3">ID</th>
                                    <th class="p-3">Dirección</th>
                                    <th class="p-3">Barrio/Distrito</th>
                                    <th class="p-3">Coordenadas</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <?php foreach ($locaciones as $loc): ?>
                                    <tr class="hover:bg-gray-50/80 transition">
                                        <td class="p-3 font-mono font-bold text-blue-600">#<?php echo htmlspecialchars($loc['location_id'] ?? $loc['id'] ?? '-'); ?></td>
                                        <td class="p-3 font-medium text-gray-900">
                                            <?php echo htmlspecialchars(($loc['street'] ?? '') . " " . ($loc['street_number'] ?? '')); ?>
                                        </td>
                                        <td class="p-3"><?php echo htmlspecialchars($loc['district'] ?? 'Genérico'); ?></td>
                                        <td class="p-3">
                                            <span class="bg-gray-100 text-gray-700 font-mono text-xs px-2 py-0.5 rounded border">
                                                <?php echo htmlspecialchars(round((float)($loc['latitude'] ?? 0), 4) . ", " . round((float)($loc['longitude'] ?? 0), 4)); ?>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Añadir Nueva Dirección</h3>
                
                <form action="abm_locaciones.php" method="POST" class="space-y-4">
                    <input type="hidden" name="action" value="crear">
                    
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Calle</label>
                        <input type="text" name="street" required placeholder="Ej: Caseros" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Altura / Número</label>
                        <input type="number" name="street_number" required placeholder="Ej: 533" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Barrio / Distrito / Partido</label>
                        <input type="text" name="district" required placeholder="Ej: Capital Federal" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">País</label>
                        <input type="text" name="country" value="Argentina" required 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm bg-gray-50 text-gray-500 cursor-not-allowed">
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Latitud</label>
                            <input type="text" name="latitude" value="-34.6037" placeholder="-34.6037" 
                                   class="w-full border border-gray-200 p-2.5 rounded-xl text-sm font-mono focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Longitud</label>
                            <input type="text" name="longitude" value="-58.3816" placeholder="-58.3816" 
                                   class="w-full border border-gray-200 p-2.5 rounded-xl text-sm font-mono focus:outline-none">
                        </div>
                    </div>

                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold text-sm transition shadow-sm mt-2">
                        💾 Guardar en MySQL
                    </button>
                </form>
            </div>

        </div>
    </div>

</body>
</html>