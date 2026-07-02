<?php
session_start();

if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

$error_msg = "";
$success_msg = "";
$usuarios = [];
$clientes = [];

// =========================================================================
// A. LEER EL CATÁLOGO DE CLIENTES (Para el desplegable obligatorio)
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
// B. PROCESAR EL FORMULARIO DE ALTA (POST hacia FastAPI)
// =========================================================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'crear') {
    $url_create = 'http://127.0.0.1:8000/users/'; 
    
    $data = [
        "name"      => $_POST['name'] ?? '',
        "email"     => $_POST['email'] ?? '',
        "password"  => $_POST['password'] ?? '', 
        "client_id" => (int)($_POST['client_id'] ?? 0), // Mandamos el ID obligatorio
        "role"      => $_POST['role'] ?? 'viewer'
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
        $success_msg = "¡Usuario creado con éxito en MySQL!";
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
// C. LEER EL LISTADO DE USUARIOS (GET desde FastAPI)
// =========================================================================
$url_list = 'http://127.0.0.1:8000/users/'; 
$ch_list = curl_init($url_list);
curl_setopt($ch_list, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch_list, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $_SESSION['token'],
    'Content-Type: application/json'
]);
$res_list = curl_exec($ch_list);
$code_list = curl_getinfo($ch_list, CURLINFO_HTTP_CODE);
curl_close($ch_list);

if ($code_list === 200) {
    $usuarios = json_decode($res_list, true);
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABM Usuarios - Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen font-sans flex flex-col md:flex-row">

    <div class="bg-slate-900 text-slate-100 w-full md:w-64 flex-shrink-0 flex flex-col shadow-xl">
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
            <span class="text-2xl">🏠</span>
            <div>
                <h1 class="font-bold text-sm uppercase tracking-wider">Domótica IoT</h1>
                <p class="text-xs text-slate-400">Módulo Usuarios</p>
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
            <a href="abm_locaciones.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>📍</span> Gestionar Locaciones
            </a>
            <a href="abm_usuarios.php" class="flex items-center gap-3 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition shadow-sm">
                <span>🔐</span> Administrar Usuarios
            </a>
        </nav>
    </div>

    <div class="flex-1 p-6 md:p-8 overflow-y-auto">
        <div class="border-b pb-4 mb-6">
            <h2 class="text-2xl font-black text-gray-800">🔐 Control de Usuarios y Permisos</h2>
            <p class="text-sm text-gray-500">Mapeo alineado al modelo de SQLAlchemy.</p>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Cuentas Existentes</h3>
                
                <?php if (empty($usuarios)): ?>
                    <p class="text-center text-gray-400 py-8 text-sm italic">No hay más usuarios listados o tabla vacía.</p>
                <?php else: ?>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-gray-600">
                            <thead class="bg-gray-50 text-gray-700 text-xs uppercase font-bold border-b border-gray-100">
                                <tr>
                                    <th class="p-3">ID</th>
                                    <th class="p-3">Nombre</th>
                                    <th class="p-3">Email</th>
                                    <th class="p-3">Client ID</th>
                                    <th class="p-3">Rol</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <?php foreach ($usuarios as $usr): ?>
                                    <tr class="hover:bg-gray-50/80 transition">
                                        <td class="p-3 font-mono text-gray-400">#<?php echo htmlspecialchars($usr['user_id'] ?? $usr['id'] ?? '-'); ?></td>
                                        <td class="p-3 font-bold text-gray-900">👤 <?php echo htmlspecialchars($usr['name'] ?? 'S/N'); ?></td>
                                        <td class="p-3"><?php echo htmlspecialchars($usr['email'] ?? '-'); ?></td>
                                        <td class="p-3 font-mono text-xs text-blue-600 font-bold">#<?php echo htmlspecialchars($usr['client_id'] ?? '-'); ?></td>
                                        <td class="p-3">
                                            <span class="px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wide bg-purple-100 text-purple-700">
                                                <?php echo htmlspecialchars($usr['role'] ?? 'viewer'); ?>
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
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Crear Nueva Cuenta</h3>
                
                <form action="abm_usuarios.php" method="POST" class="space-y-4">
                    <input type="hidden" name="action" value="crear">
                    
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre y Apellido</label>
                        <input type="text" name="name" required placeholder="Ej: Nelson Admin" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Email</label>
                        <input type="email" name="email" required placeholder="ejemplo@correo.com" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Contraseña</label>
                        <input type="password" name="password" required placeholder="••••••••" 
                               class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Asignar a Cliente</label>
                        <select name="client_id" required class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white">
                            <option value="">-- Seleccionar Cliente --</option>
                            <?php foreach ($clientes as $cli): ?>
                                <option value="<?php echo htmlspecialchars($cli['id'] ?? $cli['client_id']); ?>">
                                    <?php echo htmlspecialchars($cli['name']); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Rol del Sistema</label>
                        <select name="role" class="w-full border border-gray-200 p-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white">
                            <option value="viewer">Viewer (Solo Lectura)</option>
                            <option value="technician">Technician (Técnico / Operador)</option>
                            <option value="admin">Admin (Administrador total)</option>
                        </select>
                    </div>

                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold text-sm transition shadow-sm mt-2">
                        💾 Crear Usuario
                    </button>
                </form>
            </div>

        </div>
    </div>

</body>
</html>