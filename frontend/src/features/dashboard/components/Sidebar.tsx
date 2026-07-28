import { Link } from 'react-router-dom';
import { User } from '@/stores/useAuthStore';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { menuItems } from '../navegacion/navegacion';

interface SidebarProps {
  user: User | null;
  isOpen: boolean;
}

export function Sidebar({ user, isOpen }: SidebarProps) {
  const { handleLogout } = useLogout();

  // Filtrar menús según el rol del usuario autenticado
  const visibleMenuItems = menuItems.filter((item) => 
    user?.rol.tipo ? item.roles.includes(user.rol.tipo) : false
  );

  return (
    <aside className={`bg-gray-800 text-white flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'w-64' : 'w-20'}`}>
      
      {/* Encabezado del Sidebar */}
      <div className={`p-6 border-b border-gray-700 flex items-center ${isOpen ? 'justify-between' : 'justify-center'}`}>
        {isOpen ? (
          <div>
            <h2 className="text-xl font-bold">Sistema Factu</h2>
            <p className="text-sm text-gray-400 mt-1">{user?.rol.tipo}</p>
          </div>
        ) : (
          <span className="text-2xl font-bold" title="Sistema Factu">SF</span>
        )}
      </div>
      
      {/* Navegación */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {visibleMenuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors duration-200 ${isOpen ? 'justify-start' : 'justify-center'}`}
            title={!isOpen ? item.label : ''} // Muestra tooltip cuando está colapsado
          >
            <span className="text-xl flex-shrink-0">{item.icon}</span>
            {isOpen && <span className="whitespace-nowrap font-medium">{item.label}</span>}
          </Link>
        ))}
      </nav>
      
      {/* Botón de Cerrar Sesión */}
      <div className={`p-4 border-t border-gray-700 ${isOpen ? '' : 'flex justify-center'}`}>
        <button
          onClick={handleLogout}
          className={`bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium flex items-center gap-2 ${isOpen ? 'w-full px-4 py-2 justify-center' : 'w-10 h-10 p-0 justify-center'}`}
          title={!isOpen ? 'Cerrar Sesión' : ''}
        >
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          {isOpen && <span>Salir</span>}
        </button>
      </div>
    </aside>
  );
}