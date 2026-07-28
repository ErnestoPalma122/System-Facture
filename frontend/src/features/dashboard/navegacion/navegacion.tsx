export interface MenuItem {
  path: string;
  label: string;
  icon: string;
  roles: string[];
}

export const menuItems: MenuItem[] = [
  { path: '/', label: 'Dashboard', icon: '📊', roles: ['SUPER_ADMIN', 'ADMIN', 'VENDEDOR'] },
  { path: '/bodegas', label: 'Bodegas', icon: '🏢', roles: ['SUPER_ADMIN', 'ADMIN'] },
  { path: '/clientes', label: 'Clientes', icon: '👥', roles: ['SUPER_ADMIN', 'ADMIN', 'VENDEDOR'] },
  { path: '/productos', label: 'Productos', icon: '📦', roles: ['SUPER_ADMIN', 'ADMIN', 'VENDEDOR'] },
  { path: '/inventario', label: 'Inventario', icon: '📥', roles: ['SUPER_ADMIN', 'ADMIN'] },
  { path: '/ventas', label: 'Ventas', icon: '💰', roles: ['SUPER_ADMIN', 'ADMIN', 'VENDEDOR'] },
  { path: '/proveedores', label: 'Proveedores', icon: '🚚', roles: ['SUPER_ADMIN', 'ADMIN'] },
  { path: '/configuracion/emisor', label: 'Configuración del Emisor', icon: '⚙️', roles: ['SUPER_ADMIN'] },
  
  // ✅ NUEVO: Gestión de Usuarios (SOLO SUPER_ADMIN)
  { path: '/usuarios', label: 'Usuarios', icon: '👤', roles: ['SUPER_ADMIN'] },
];