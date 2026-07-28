// frontend/src/app/router.tsx

//Este archivo es el nucleo de nabegacion 

import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { authRoutes } from '@/features/auth/pages/pages';
import { Dashboard, DashboardHome } from '@/features/dashboard/pages/Dashboard';
import { bodegasRoutes } from '@/features/bodegas/pages/pages';
import { emisorRoutes } from '@/features/emisor/pages/pages';
import { proveedoresRoutes } from '@/features/proveedores/pages/pages';
import { productosRutas } from '@/features/productos/pages/productos.rutas'; // <-- IMPORTADO
import { usuariosRutas } from '@/features/usuarios/pages/usuarios.rutas';

export function Router() {
  const { isAuthenticated } = useAuthStore();
  // se dividen rutas Publicos, Rutas Protegidas y ruta 404(Comodin que lo envia a el Dashboard) 
  return (
    <Routes>
      {/* 1. Rutas Públicas (Auth) */}
      {authRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}

      {/* 2. Rutas Protegidas (Envueltas en el Layout del Dashboard) */}
      <Route
        element={
          isAuthenticated ? (
            <Dashboard />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        {/* Ruta por defecto dentro del Dashboard */}
        <Route path="/" element={<DashboardHome />} />
        
        {/* Inyección de rutas de módulos protegidos */}
        {bodegasRoutes.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
        
        {/* Inyección de rutas del módulo Emisor */}
        {emisorRoutes.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}

        {/* Inyección de rutas del módulo Proveedores */}
        {proveedoresRoutes.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}

        {/* Inyección de rutas del módulo Productos */}
        {productosRutas.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
        
        {/* Inyección de rutas del módulo Usuarios */}
        {usuariosRutas.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>

      {/* 3. Ruta 404 (Redirige al dashboard) */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}