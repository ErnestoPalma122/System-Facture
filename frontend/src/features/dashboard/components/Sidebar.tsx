// frontend\src\features\dashboard\components\Sidebar.tsx

import { Link } from 'react-router-dom';
import { User } from '@/stores/useAuthStore';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { sidebarMenuItems, tienePermiso } from './filtro_departamento';

// 📌 INTERFAZ DE PROPS DEL SIDEBAR
interface SidebarProps {
  user: User | null;
  isOpen: boolean; // 🔗 Controla si el sidebar está expandido (w-64) o colapsado (w-20)
}

// 📌 COMPONENTE SIDEBAR (BARRA LATERAL)
export function Sidebar({ user, isOpen }: SidebarProps) {
  // 🔗 Hook personalizado para manejar la lógica de cierre de sesión (limpiar store, cookies, etc.)
  const { handleLogout } = useLogout();

  // 📌 FILTRADO DE MENÚ POR PERMISOS
  // Recorre todos los ítems del menú y solo conserva aquellos para los que el usuario tiene permiso.
  // ⚠️ Si 'user' es null, devuelve false (no muestra nada), aunque esto normalmente no debería ocurrir 
  // ya que el Sidebar solo se renderiza dentro de rutas protegidas.
  const visibleMenuItems = sidebarMenuItems.filter((item) => 
    user ? tienePermiso(user.rol.tipo, user.departamento?.nombre, item) : false
  );

  return (
    // 🔗 La clase 'transition-all duration-300' anima el cambio de ancho (w-64 a w-20) suavemente.
    <aside className={`bg-gray-800 text-white flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'w-64' : 'w-20'}`}>
      
      {/* 📌 CABECERA DEL SIDEBAR */}
      <div className={`p-6 border-b border-gray-700 flex items-center ${isOpen ? 'justify-between' : 'justify-center'}`}>
        {isOpen ? (
          // Modo expandido: Muestra nombre del sistema y rol del usuario.
          <div>
            <h2 className="text-xl font-bold">Sistema Factu</h2>
            <p className="text-sm text-gray-400 mt-1">{user?.rol.tipo}</p>
          </div>
        ) : (
          // Modo colapsado: Muestra solo las iniciales "SF" como identificador visual.
          <span className="text-2xl font-bold" title="Sistema Factu">SF</span>
        )}
      </div>
      
      {/* 📌 LISTA DE NAVEGACIÓN */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {visibleMenuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            // 🔗 Estilos dinámicos: cambia la alineación (justify-start vs justify-center) según el estado 'isOpen'.
            className={`flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors duration-200 ${isOpen ? 'justify-start' : 'justify-center'}`}
            // 🔗 Tooltip nativo que muestra el nombre del módulo solo cuando el sidebar está colapsado.
            title={!isOpen ? item.label : ''}
          >
            <span className="text-xl flex-shrink-0">{item.icon}</span>
            {/* ⚠️ 'whitespace-nowrap' evita que el texto se parta en dos líneas durante la animación de colapso. */}
            {isOpen && <span className="whitespace-nowrap font-medium">{item.label}</span>}
          </Link>
        ))}
      </nav>
      
      {/* 📌 PIE DEL SIDEBAR: BOTÓN DE CERRAR SESIÓN */}
      <div className={`p-4 border-t border-gray-700 ${isOpen ? '' : 'flex justify-center'}`}>
        <button
          onClick={handleLogout}
          // 🔗 El botón se adapta: ancho completo con texto si está abierto, o cuadrado (w-10 h-10) si está cerrado.
          className={`bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium flex items-center gap-2 ${isOpen ? 'w-full px-4 py-2 justify-center' : 'w-10 h-10 p-0 justify-center'}`}
          title={!isOpen ? 'Cerrar Sesión' : ''}
        >
          {/* Icono SVG de "Logout" */}
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          {isOpen && <span>Salir</span>}
        </button>
      </div>
    </aside>
  );
}