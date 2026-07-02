<?php
session_start();

// 1. Control de Seguridad
if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$error_msg = "";
$success_msg = "";
$clientes = [];
$locaciones = [];

// =========================================================================
// 2. LEER PRIMERO EL CATÁLOGO DE LOCACIONES (Para el desplegable del Formulario)
// =========================================================================
$url_loc = 'http://127.0.0.1:8000/locations/';
$ch_loc = curl_init($url_loc);
curl_setopt($ch_loc, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch_loc, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);
$res_loc = curl_exec($ch_loc);
$code_loc = curl_getinfo($ch_loc, CURLINFO_HTTP_CODE);
curl_close($ch_loc);

if ($code_loc === 200) {
    $locaciones = json_decode($res_loc, true);
}

// =========================================================================
// 3. PROCESAR EL FORMULARIO DE ALTA DE CLIENTE (POST hacia FastAPI)
// =========================================================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'crear') {
    $url_create = 'http://127.0.0.1:8000/clients/'; // Modifica esta URL según tu endpoint exacto de Python
    
    // Armamos el payload según las llaves que espere tu modelo Pydantic de Clientes
    $data = [
        "name"        => $_POST['name'] ?? '',
        "email"       => $_POST['email'] ?? '',
        "phone"       => $_POST['phone'] ?? '',
        "location_id" => $_POST['location_id'] ? (int)$_POST['location_id'] : null,
        "is_active"   => true
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
        $success_msg = "¡Cliente registrado con éxito en MySQL!";
    } else {
        $res_decoded = json_decode($response, true);
        $error_msg = $res_decoded['detail'] ?? "Error al guardar cliente (Código HTTP: $http_code)";
        if (is_array($error_msg)) {
            $error_msg = json_encode($error_msg);
        }
    }
}

// =========================================================================
// 4. LEER EL CATÁLOGO DE CLIENTES (GET desde FastAPI)
// =========================================================================
$url_clients = 'http://127.0.0.1:8000/clients/'; // Modifica esta URL según tu endpoint exacto de Python
$ch_cli = curl_init($url_clients);
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
} else {
    // Si todavía no creaste el endpoint de listado de clientes, inicializamos vacío para que no falle la UI
    $clientes = []; 
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABM Clientes - Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen font-sans flex flex-col md:flex-row">

    <div class="bg-slate-900 text-slate-100 w-full md:w-64 flex-shrink-0 flex flex-col shadow-xl">
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
            <span class="text-2xl">🏠</span>
            <div>
                <h1 class="font-bold text-sm uppercase tracking-wider">Domótica IoT</h1>
                <p class="text-xs text-slate-400">Módulo Clientes</p>
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
            <a href="abm_clientes.php" class="flex items-center gap-3 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition shadow-sm">
                <span>👥</span> Gestionar Clientes
            </a>
            <a href="abm_locaciones.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
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
            <h2 class="text-2xl font-black text-gray-800">👥 Administración de Clientes</h2>
            <p class="text-sm text-gray-500">Gestión de cuentas de clientes corporativos y residenciales asociados en MySQL.</p>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Clientes Registrados</h3>
                
                <?php if (empty($clientes)): ?>
                    <p class="text-center text-gray-400 py-8 text-sm italic">No hay clientes cargados en MySQL o el endpoint está en desarrollo.</p>
                <?php else: ?>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-gray-600">
                            <thead class="bg-gray-50 text-gray-700 text-xs uppercase font-bold border-b border-gray-100">
                                <tr>
                                    <th class="p-3">ID</th>
                                    <th class="p-3">Nombre / Razón Social</th>
                                    <th class="p-3">Contacto</th>
                                    <th class="p-3">Locación Asignada</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <?php foreach ($clientes as $cli): ?>
                                    <tr class="hover:bg-gray-50/80 transition">
                                        <td class="p-3 font-mono font-bold text-blue-600">#<?php echo htmlspecialchars($cli['id'] ?? '-'); ?></td>
                                        <td class="p-3 font-medium text-gray-900"><?php echo htmlspecialchars($cli['name'] ?? 'Sin Nombre'); ?></td>
                                        <td class="p-3 text-xs">
                                            <div class="font-bold text-gray-700"><?php echo htmlspecialchars($cli['email'] ?? '-'); ?></div>
                                            <div class="text-gray-400 mt-0.5">📞 <?php echo htmlspecialchars($cli['phone'] ?? '-'); ?></div>
                                        </td>
                                        <td class="p-3">
                                            <span class="bg-blue-50 text-blue-700 border border-blue-100 px-2.5 py-1 rounded-full text-xs font-semibold">
                                                ID Locación: #<?php echo htmlspecialchars($cli['location_id'] ?? 'Ninguna'); ?>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Registrar Nuevo Cliente</h3>
                
                <form action="abm_clientes.php" method="POST" class="space-y-4">
                    <input type="hidden" name="action" value="crear">
                    
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre Completo / Razón Social</label>
                        <input type="text" name="name" required placeholder="Ej: Juan Pérez o Empresa S.A." 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Correo Electrónico</label>
                        <input type="email" name="email" required placeholder="juan@ejemplo.com" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Teléfono de Contacto</label>
                        <input type="text" name="phone" placeholder="Ej: 1123456789" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Vincular Domicilio (MySQL)</label>
                        <select name="location_id" class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white">
                            <option value="">-- Sin locación asignada temporalmente --</option>
                            <?php foreach ($locaciones as $loc): ?>
                                <option value="<?php echo htmlspecialchars($loc['location_id'] ?? $loc['id']); ?>">
                                    <?php echo htmlspecialchars(($loc['street'] ?? '') . " " . ($loc['street_number'] ?? '') . " (" . ($loc['district'] ?? '') . ")"); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold text-sm transition shadow-sm mt-2">
                        💾 Registrar Cliente
                    </button>
                </form>
            </div>

        </div>
    </div>

</body>
</html>