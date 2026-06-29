<?php
session_start();

// Control de seguridad: Si no hay token, al login
if (!isset($_SESSION['token'])) {
    header("Location: login.php");
    exit;
}

// Variables de conteo simuladas (En el futuro se pueden conectar a endpoints tipo /stats)
$total_clientes = 1; 
$total_dispositivos = 2;
$total_locaciones = 1;
$usuario_actual = $_SESSION['usuario'] ?? 'Administrador';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard General - Sistema Domótica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen font-sans flex flex-col md:flex-row">

    <div class="bg-slate-900 text-slate-100 w-full md:w-64 flex-shrink-0 flex flex-col shadow-xl">
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
            <span class="text-2xl">🏠</span>
            <div>
                <h1 class="font-bold text-sm uppercase tracking-wider">Domótica IoT</h1>
                <p class="text-xs text-slate-400">Panel de Control</p>
            </div>
        </div>
        
        <div class="p-4 bg-slate-950/40 text-xs flex items-center justify-between">
            <span class="truncate">👤 <?php echo htmlspecialchars($usuario_actual); ?></span>
            <span class="bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide">Online</span>
        </div>

        <nav class="flex-1 p-4 space-y-1">
            <a href="dashboard.php" class="flex items-center gap-3 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition shadow-sm">
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
            <a href="abm_usuarios.php" class="flex items-center gap-3 text-slate-300 hover:bg-slate-800 hover:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition">
                <span>🔐</span> Administrar Usuarios
            </a>
        </nav>

        <div class="p-4 border-t border-slate-800">
            <a href="logout.php" class="flex items-center justify-center gap-2 w-full bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white py-2 px-4 rounded-lg text-xs font-semibold transition border border-red-500/30">
                <span>🚪</span> Cerrar Sesión
            </a>
        </div>
    </div>

    <div class="flex-1 p-6 md:p-8 overflow-y-auto">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b pb-4 mb-6 gap-4">
            <div>
                <h2 class="text-2xl font-black text-gray-800">Panel Principal de Administración</h2>
                <p class="text-sm text-gray-500">Administración general de motores de bases de datos híbridos (MySQL y MongoDB Atlas).</p>
            </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div class="bg-white border border-gray-200 p-5 rounded-2xl shadow-sm flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Clientes Activos</p>
                    <p class="text-3xl font-black text-gray-800 mt-1"><?php echo $total_clientes; ?></p>
                </div>
                <div class="bg-blue-50 text-blue-600 p-3 rounded-xl text-2xl font-semibold">👥</div>
            </div>

            <div class="bg-white border border-gray-200 p-5 rounded-2xl shadow-sm flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Locaciones Cargadas</p>
                    <p class="text-3xl font-black text-gray-800 mt-1"><?php echo $total_locaciones; ?></p>
                </div>
                <div class="bg-amber-50 text-amber-600 p-3 rounded-xl text-2xl font-semibold">📍</div>
            </div>

            <div class="bg-white border border-gray-200 p-5 rounded-2xl shadow-sm flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Dispositivos en Mongo</p>
                    <p class="text-3xl font-black text-gray-800 mt-1"><?php echo $total_dispositivos; ?></p>
                </div>
                <div class="bg-purple-50 text-purple-600 p-3 rounded-xl text-2xl font-semibold">📟</div>
            </div>
        </div>

        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Acciones e Inserciones de Datos</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div class="flex items-center gap-3 border-b pb-3 mb-4">
                    <span class="text-xl">🐬</span>
                    <h4 class="font-bold text-gray-800 text-base">Entidades Relacionales (MySQL)</h4>
                </div>
                <p class="text-xs text-gray-500 mb-4">Administración estructural básica. Los datos ingresados aquí impactan de forma relacional en tablas vinculadas por ID.</p>
                <div class="flex flex-col sm:flex-row gap-3">
                    <a href="abm_clientes.php" class="flex-1 bg-gray-50 hover:bg-blue-50 hover:border-blue-200 border border-gray-200 p-3 rounded-xl text-center transition">
                        <span class="block text-xl mb-1">➕</span>
                        <span class="text-xs font-bold text-gray-700 block">Nuevo Cliente</span>
                    </a>
                    <a href="abm_locaciones.php" class="flex-1 bg-gray-50 hover:bg-amber-50 hover:border-amber-200 border border-gray-200 p-3 rounded-xl text-center transition">
                        <span class="block text-xl mb-1">➕</span>
                        <span class="text-xs font-bold text-gray-700 block">Nueva Locación</span>
                    </a>
                </div>
            </div>

            <div class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div class="flex items-center gap-3 border-b pb-3 mb-4">
                    <span class="text-xl">🍃</span>
                    <h4 class="font-bold text-gray-800 text-base">Entidades de Telemetría (MongoDB)</h4>
                </div>
                <p class="text-xs text-gray-500 mb-4">Gestión de dispositivos IoT maestros. Los documentos guardados aquí manejan sub-arrays complejos de sensores MQTT.</p>
                <div class="flex flex-col sm:flex-row gap-3">
                    <a href="dispositivos.php" class="flex-1 bg-gray-50 hover:bg-purple-50 hover:border-purple-200 border border-gray-200 p-3 rounded-xl text-center transition">
                        <span class="block text-xl mb-1">👁️‍🗨️</span>
                        <span class="text-xs font-bold text-gray-700 block">Ver Monitoreo</span>
                    </a>
                    <a href="nuevo_dispositivo.php" class="flex-1 bg-blue-600 hover:bg-blue-700 p-3 rounded-xl text-center transition text-white shadow-sm">
                        <span class="block text-xl mb-1">📟</span>
                        <span class="text-xs font-bold block">Alta de Dispositivo</span>
                    </a>
                </div>
            </div>

        </div>

    </div>

</body>
</html>