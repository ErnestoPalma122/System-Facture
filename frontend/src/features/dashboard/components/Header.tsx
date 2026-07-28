import { User } from '@/stores/useAuthStore';

interface HeaderProps {
  user: User | null;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export function Header({ user, isSidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 flex-shrink-0">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          {/* Botón para ocultar/mostrar el sidebar */}
          <button 
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors duration-200"
            title={isSidebarOpen ? "Ocultar menú lateral" : "Mostrar menú lateral"}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-xl font-semibold text-gray-800">
            Panel de Control
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-700">{user?.nombre}</p>
            <p className="text-xs text-gray-500">{user?.email}</p>
          </div>
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold shadow-sm">
            {user?.nombre?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>
    </header>
  );
}