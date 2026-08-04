// frontend\src\features\dashboard\components\Header.tsx

import { User } from '@/stores/useAuthStore';

// 📌 INTERFAZ DE PROPS DEL HEADER
interface HeaderProps {
  user: User | null;           // 🔗 Datos del usuario autenticado
  isSidebarOpen: boolean;      // 🔗 Estado para saber si el sidebar está expandido
  onToggleSidebar: () => void; // 🔗 Función callback para alternar el estado del sidebar
}

// 📌 COMPONENTE HEADER (BARRA SUPERIOR)
// Muestra el botón de colapso del sidebar, el título de la sección y la información del usuario logueado.
export function Header({ user, isSidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    // 📌 Contenedor principal con estilos Tailwind para fondo, sombra y borde inferior.
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 flex-shrink-0">
      <div className="flex justify-between items-center">
        
        {/* 📌 SECCIÓN IZQUIERDA: Botón de menú y Título */}
        <div className="flex items-center gap-4">
          {/* 🔗 Botón que ejecuta onToggleSidebar al hacer clic. 
              Incluye un title dinámico para accesibilidad (tooltip). */}
          <button 
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors duration-200"
            title={isSidebarOpen ? "Ocultar menú lateral" : "Mostrar menú lateral"}
          >
            {/* Icono SVG de "hamburguesa" (menú) */}
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-xl font-semibold text-gray-800">
            Panel de Control
          </h1>
        </div>

        {/* 📌 SECCIÓN DERECHA: Información del Usuario */}
        <div className="flex items-center gap-4">
          {/* 🔗 Texto con nombre y email. 'hidden sm:block' lo oculta en móviles para ahorrar espacio. */}
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-700">{user?.nombre}</p>
            <p className="text-xs text-gray-500">{user?.email}</p>
          </div>
          
          {/* 🔗 Avatar circular: Muestra la primera letra del nombre en mayúscula. 
              El operador '||' proporciona un fallback 'U' si user.nombre es undefined. */}
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold shadow-sm">
            {user?.nombre?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>
    </header>
  );
}