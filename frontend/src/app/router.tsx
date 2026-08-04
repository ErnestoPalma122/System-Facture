// frontend\src\app\router.tsx

// 📌 IMPORTACIONES DE ENRUTAMIENTO Y ESTADO
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore'; // 🔗 Hook de Zustand (o similar) para el estado global de autenticación

// 📌 IMPORTACIONES DE COMPONENTES DE UI Y PROTECCIÓN
import { ProtectedRoute } from '@/components/ui/ProtectedRoute'; // 🔗 Componente HOC/Wrapper que valida roles y departamentos
import { routesPermissions } from '@/features/dashboard/components/filtro_departamento'; // 🔗 Configuración centralizada de permisos

// 📌 IMPORTACIONES DE RUTAS POR MÓDULO (FEATURES)
import { authRoutes } from '@/features/auth/pages/pages'; // Rutas públicas (Login, Registro, etc.)
import { Dashboard } from '@/features/dashboard/pages/Dashboard'; // ✅ Layout principal (contiene el Sidebar)
import { DashboardHome } from '@/features/dashboard/pages/Dashboard'; // Página de inicio del dashboard
import { AccesoDenegado } from '@/features/dashboard/pages/AccesoDenegado'; // Página de error 403

// Rutas específicas de cada módulo de negocio
import { bodegasRoutes } from '@/features/bodegas/pages/pages';
import { emisorRoutes } from '@/features/emisor/pages/pages';
import { proveedoresRoutes } from '@/features/proveedores/pages/pages';
import { productosRutas } from '@/features/productos/pages/productos.rutas';
import { usuariosRutas } from '@/features/usuarios/pages/usuarios.rutas';
import { ingresoMercaderiaRutas } from '@/features/Ingreso_de_mercaderia/pages/ingreso_mercaderia.rutas.tsx'; // <-- NUEVO MÓDULO

// 📌 CONFIGURACIÓN DE MÓDULOS CON RUTAS Y PERMISOS
// Este array centraliza la relación entre:
// 1. basePath: La ruta padre del módulo.
// 2. children / element: Los componentes o sub-rutas que renderiza.
// 3. permissions: Los permisos requeridos (extraídos de routesPermissions).
// ⚠️ Nota: Se usa el operador '!' (non-null assertion) al final de .find() porque TypeScript 
// no puede garantizar que el elemento exista, pero el desarrollador asume que la configuración es correcta.
const modulesWithRoutes = [
  { basePath: '/', element: <DashboardHome />, permissions: routesPermissions.find(r => r.path === '/')! },
  { basePath: '/bodegas', children: bodegasRoutes, permissions: routesPermissions.find(r => r.path === '/bodegas')! },
  { basePath: '/configuracion/emisor', children: emisorRoutes, permissions: routesPermissions.find(r => r.path === '/configuracion/emisor')! },
  { basePath: '/proveedores', children: proveedoresRoutes, permissions: routesPermissions.find(r => r.path === '/proveedores')! },
  { basePath: '/productos', children: productosRutas, permissions: routesPermissions.find(r => r.path === '/productos')! },
  { basePath: '/ingreso-mercaderia', children: ingresoMercaderiaRutas, permissions: routesPermissions.find(r => r.path === '/ingreso-mercaderia')! }, // <-- NUEVO  
  { basePath: '/usuarios', children: usuariosRutas, permissions: routesPermissions.find(r => r.path === '/usuarios')! },
];

// 📌 COMPONENTE PRINCIPAL DE ENRUTAMIENTO
export function Router() {
  // 🔗 Suscripción al estado de autenticación. 
  // Se re-renderizará si el estado de 'isAuthenticated' cambia.
  const { isAuthenticated } = useAuthStore();

  // 📌 FUNCIÓN GENERADORA DE RUTAS PROTEGIDAS
  // Recorre el array 'modulesWithRoutes' y genera elementos <Route> de React Router.
  const generateRoutes = () => {
    // 🔗 flatMap se usa para aplanar el array resultante, ya que module.children.map 
    // devolvería un array de arrays, y necesitamos un array plano de elementos <Route>.
    return modulesWithRoutes.flatMap((module) => {
      
      // 📌 CASO 1: El módulo tiene sub-rutas (children)
      if (module.children) {
        return module.children.map((child: any, idx: number) => (
          // ⚠️ Nota: 'child: any' podría tiparse mejor en el futuro con una interfaz de Ruta, 
          // pero funciona para acceder a 'path' y 'element' dinámicamente.
          <Route
            key={`${module.basePath}-${child.path || idx}`} // 🔗 Key única combinando ruta padre e hija
            path={child.path}
            element={
              // 📌 WRAPPER DE PROTECCIÓN
              // Envuelve el componente hijo validando roles y departamentos antes de renderizar.
              <ProtectedRoute
                allowedRoles={module.permissions.allowedRoles}
                allowedDepartments={module.permissions.allowedDepartments}
              >
                {child.element}
              </ProtectedRoute>
            }
          />
        ));
      }
      
      // 📌 CASO 2: El módulo es una ruta única (sin children), tiene un 'element' directo
      return (
        <Route
          key={module.basePath}
          path={module.basePath}
          element={
            <ProtectedRoute
              allowedRoles={module.permissions.allowedRoles}
              allowedDepartments={module.permissions.allowedDepartments}
            >
              {module.element}
            </ProtectedRoute>
          }
        />
      );
    });
  };

  // 📌 RENDERIZADO DEL ÁRBOL DE RUTAS
  return (
    <Routes>
      {/* 📌 1. RUTAS PÚBLICAS (AUTENTICACIÓN) */}
      {/* Se renderizan siempre, sin protección. Ej: /login, /registro */}
      {authRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}

      {/* 📌 2. PÁGINA DE ACCESO DENEGADO */}
      {/* Ruta explícita para mostrar cuando un usuario no tiene permisos (403) */}
      <Route path="/acceso-denegado" element={<AccesoDenegado />} />

      {/* 📌 3. RUTAS PROTEGIDAS CON LAYOUT (DASHBOARD + SIDEBAR) */}
      {/* 🔗 Lógica condicional: Si está autenticado, renderiza el Layout <Dashboard /> 
          que contendrá las rutas hijas generadas. Si no, redirige forzozamente a "/login". 
          'replace' evita que el usuario pueda usar el botón "Atrás" del navegador para volver a la ruta protegida. */}
      <Route element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />}>
        {generateRoutes()}
      </Route>

      {/* 📌 4. RUTA COMODÍN (404 - NOT FOUND) */}
      {/* 🔗 El path="*" captura cualquier URL no definida anteriormente y la redirige al inicio ("/"). */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}