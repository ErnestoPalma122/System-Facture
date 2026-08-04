// frontend/src/features/usuarios/components/UsuarioTabla.tsx

import { Usuario } from '../api/usuario_api';

interface UsuarioTablaProps {
  usuarios: Usuario[];
  isLoading: boolean;
  busqueda: string;
  onBusquedaChange: (valor: string) => void;
  onEditar: (usuario: Usuario) => void;
  onEliminarClick: (usuario: Usuario) => void;
}

export function UsuarioTabla({ 
  usuarios, 
  isLoading, 
  busqueda, 
  onBusquedaChange, 
  onEditar, 
  onEliminarClick 
}: UsuarioTablaProps) {

  const inputClass = "block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out";

  if (isLoading) {
    return <div className="p-8 text-center text-gray-600">Cargando usuarios...</div>;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mt-6">
      {/* 📌 ENCABEZADO DE LA TABLA Y BARRA DE BÚSQUEDA */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-lg font-bold text-gray-800">Listado de Usuarios</h2>
        
        <div className="relative w-full sm:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={busqueda}
            onChange={(e) => onBusquedaChange(e.target.value)}
            placeholder="Buscar por nombre o correo..."
            className={inputClass}
          />
          {/* ⚠️ Feedback visual para guiar al usuario sobre la longitud mínima de búsqueda */}
          {busqueda.length > 0 && busqueda.length < 2 && (
            <p className="text-xs text-gray-500 mt-1 pl-1">Mínimo 2 caracteres para buscar</p>
          )}
        </div>
      </div>
      
      {/* 📌 BARRA DE ESTADO DE RESULTADOS */}
      <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center text-sm text-gray-600">
        <span>
          {busqueda.length >= 2 
            ? `Mostrando ${usuarios.length} resultados`
            : `Mostrando ${usuarios.length} usuarios`
          }
        </span>
        {busqueda.length >= 2 && (
          <button onClick={() => onBusquedaChange('')} className="text-blue-600 hover:text-blue-800 text-xs font-medium">
            Limpiar búsqueda
          </button>
        )}
      </div>

      {/* 📌 CUERPO DE LA TABLA */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Correo</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Rol</th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios.length > 0 ? (
              usuarios.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.nombre}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {user.rol?.nombre || <span className="text-gray-400">Sin rol</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.estado === 'ACTIVO' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center space-x-2">
                    <button 
                      onClick={() => onEditar(user)}
                      className="text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors duration-150 text-sm font-medium"
                    >
                      ✏️ Editar
                    </button>
                    {/* ⚠️ SEGURIDAD: Solo se permite eliminar usuarios que estén actualmente ACTIVOS */}
                    {user.estado === 'ACTIVO' && (
                      <button 
                        onClick={() => onEliminarClick(user)}
                        className="text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-md transition-colors duration-150 text-sm font-medium"
                      >
                        🗑️ Eliminar
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              // 📌 ESTADOS VACÍOS (EMPTY STATES) DIFERENCIADOS
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  {busqueda.length >= 2 ? (
                    <>
                      <p className="text-lg font-medium">No se encontraron usuarios</p>
                      <p className="text-sm text-gray-400 mt-1">Intenta con otro término de búsqueda</p>
                    </>
                  ) : (
                    <>
                      <p className="text-lg font-medium">No hay usuarios registrados.</p>
                      <p className="text-sm text-gray-400 mt-1">Usa el formulario de arriba para crear el primero.</p>
                    </>
                  )}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}