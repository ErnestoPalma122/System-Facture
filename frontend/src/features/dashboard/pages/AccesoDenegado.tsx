// frontend\src\features\dashboard\pages\AccesoDenegado.tsx

import { Link } from 'react-router-dom';

// 📌 PÁGINA DE ERROR 403 (ACCESO DENEGADO)
// Se muestra cuando el <ProtectedRoute> bloquea el acceso de un usuario autenticado.
export function AccesoDenegado() {
  // 🔗 Recupera la ruta que el usuario intentó visitar (guardada previamente por el ProtectedRoute) 
  // o usa un texto genérico si no está disponible.
  const deniedPath = sessionStorage.getItem('deniedPath') || 'esta ruta';

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
      <div className="text-center p-8 bg-white rounded-2xl shadow-xl max-w-md">
        <div className="text-8xl mb-6">🚫</div>
        <h1 className="text-3xl font-bold text-red-700 mb-4">Acceso Denegado</h1>
        <p className="text-gray-600 mb-2">
          No tienes permisos para acceder a:
        </p>
        
        {/* 📌 Muestra visualmente la ruta bloqueada con estilo de código para claridad. */}
        <p className="text-sm font-mono bg-gray-100 px-4 py-2 rounded mb-6 text-gray-800">
          {deniedPath}
        </p>
        
        <p className="text-gray-500 mb-8">
          Tu departamento o rol no tiene autorización para visualizar esta sección.
        </p>
        
        {/* 📌 OPCIONES DE NAVEGACIÓN POST-ERROR */}
        <div className="flex gap-4 justify-center">
          <Link 
            to="/"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir al Dashboard
          </Link>
          {/* 🔗 window.history.back() permite al usuario regresar a la última página válida que visitó. */}
          <button 
            onClick={() => window.history.back()}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Volver Atrás
          </button>
        </div>
      </div>
    </div>
  );
}