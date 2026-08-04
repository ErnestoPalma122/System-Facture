// frontend\src\features\dashboard\components\filtro_departamento.tsx

// 📌 DEFINICIÓN DE TIPOS DE ROLES
// Union type que restringe los valores posibles a los roles válidos del sistema.
// ⚠️ Cualquier nuevo rol debe añadirse aquí para mantener la consistencia en toda la app.
export type RoleType = 'SUPER_ADMIN' | 'ADMIN' | 'GERENTE' | 'SUPERVISOR' | 'VENDEDOR' | 'CONTADOR' | 'USUARIO';

// 📌 INTERFAZ DE PERMISOS DE RUTA
// Define la estructura de datos que utiliza el sistema para controlar el acceso y la renderización del menú.
export interface RoutePermission {
  path: string;          // 🔗 Ruta exacta o patrón (Ej: '/bodegas' o '/')
  label: string;         // 🔗 Texto visible que se mostrará en el Sidebar
  icon: string;          // 🔗 Emoji o string de icono para el Sidebar
  allowedRoles: RoleType[]; // 🔗 Array de roles que tienen acceso a esta ruta
  allowedDepartments?: string[]; // ⚠️ Opcional: Array de departamentos autorizados. Si no existe, solo se valida el rol.
}

// ========================================================================
// 🌟 ÚNICA FUENTE DE VERDAD: Configuración de Permisos y Menú
// ========================================================================
// 📌 Este array es el núcleo de la seguridad a nivel de UI. 
// Define qué roles y departamentos pueden ver y acceder a cada módulo.

export const routesPermissions: RoutePermission[] = [
  { path: '/', label: 'Dashboard', icon: '📊', allowedRoles: ['SUPER_ADMIN', 'ADMIN', 'GERENTE', 'SUPERVISOR', 'VENDEDOR', 'CONTADOR', 'USUARIO'] },
  { path: '/bodegas', label: 'Bodegas', icon: '🏢', allowedRoles: ['SUPER_ADMIN', 'ADMIN', 'USUARIO'], allowedDepartments: ['Administración', 'Bodegas'] },
  { path: '/configuracion/emisor', label: 'Configuración del Emisor', icon: '⚙️', allowedRoles: ['SUPER_ADMIN', 'ADMIN'], allowedDepartments: ['Administración'] },
  { path: '/ingreso-mercaderia', label: 'Ingreso Mercadería', icon: '📥', allowedRoles: ['SUPER_ADMIN', 'ADMIN', 'USUARIO'], allowedDepartments: ['Administración', 'Bodegas'] }, // <-- AGREGAR ESTA  
  { path: '/proveedores', label: 'Proveedores', icon: '🚚', allowedRoles: ['SUPER_ADMIN', 'ADMIN', 'USUARIO'], allowedDepartments: ['Administración', 'Bodegas'] },
  { path: '/productos', label: 'Productos', icon: '📦', allowedRoles: ['SUPER_ADMIN', 'ADMIN', 'GERENTE', 'SUPERVISOR', 'VENDEDOR', 'USUARIO'] },
  { path: '/usuarios', label: 'Usuarios', icon: '👤', allowedRoles: ['SUPER_ADMIN'], allowedDepartments: ['Administración'] },
];

// ========================================================================
// 📌 EXPORTACIÓN PARA EL SIDEBAR
// ========================================================================
// 🔗 Transforma 'routesPermissions' para limpiar el '/*' de las rutas.
// Esto es necesario porque React Router usa '/*' para rutas anidadas, 
// pero el componente <Link> del Sidebar necesita la ruta limpia para navegar correctamente.
export const sidebarMenuItems = routesPermissions.map(route => ({
  ...route,
  path: route.path.replace('/*', '')
}));

/**
 * 📌 FUNCIÓN DE VALIDACIÓN DE PERMISOS
 * Valida si un usuario tiene permiso para un módulo específico.
 * Se reutiliza tanto en el Sidebar (para ocultar opciones) como en ProtectedRoute (para bloquear acceso).
 * 
 * @param userRole - Rol actual del usuario
 * @param userDepartment - Departamento actual del usuario
 * @param route - Objeto de configuración de la ruta a validar
 * @returns boolean - true si tiene acceso, false si se deniega
 */
export function tienePermiso(userRole: string, userDepartment: string | undefined, route: RoutePermission): boolean {
  // 1. 📌 BYPASS DE SEGURIDAD: SUPER_ADMIN tiene acceso total a todo, siempre.
  if (userRole === 'SUPER_ADMIN') return true;

  // 2. 📌 VALIDACIÓN DE ROL
  // Si el rol del usuario no está en la lista de roles permitidos, se deniega el acceso.
  if (!route.allowedRoles.includes(userRole as RoleType)) {
    return false;
  }

  // 3. 📌 VALIDACIÓN DE DEPARTAMENTO (Condicional)
  // Solo se evalúa si la ruta tiene departamentos restringidos configurados.
  if (route.allowedDepartments && route.allowedDepartments.length > 0) {
    // Si el usuario no tiene departamento asignado, o su departamento no está en la lista permitida, se deniega.
    if (!userDepartment || !route.allowedDepartments.includes(userDepartment)) {
      return false;
    }
  }

  // Si supera todas las validaciones, el acceso es válido.
  return true;
}