// frontend/src/features/usuarios/components/UsuarioVistaGeneral.tsx

import { useState, useEffect } from 'react';
import { useUsuarios } from '../hooks/useUsuarios';
import { Usuario } from '../api/usuario_api';
import { UsuarioFormulario } from './UsuarioFormulario';
import { UsuarioTabla } from './UsuarioTabla';

export function UsuarioVistaGeneral() {
  // 📌 ESTADO CENTRALIZADO PARA LA BÚSQUEDA
  const [busqueda, setBusqueda] = useState('');
  const [busquedaDebounce, setBusquedaDebounce] = useState('');
  
  // 📌 LÓGICA DE DEBOUNCE (OPTIMIZACIÓN DE RENDIMIENTO)
  // ⚠️ Evita hacer una petición al backend por cada tecla pulsada. 
  // Espera 500ms después de que el usuario deje de escribir antes de actualizar 'busquedaDebounce'.
  useEffect(() => {
    const timer = setTimeout(() => {
      if (busqueda.length >= 2 || busqueda === '') {
        setBusquedaDebounce(busqueda);
      }
    }, 500);
    return () => clearTimeout(timer); // Limpia el timer si el usuario sigue escribiendo
  }, [busqueda]);

  // 🔗 Pasa la búsqueda con debounce al hook. Si está vacío, pasa undefined para traer la lista por defecto.
  const { usuarios, isLoading, eliminarUsuario, isDeleting } = useUsuarios(busquedaDebounce || undefined);
  
  const [mensajeExito, setMensajeExito] = useState('');
  const [usuarioAEditar, setUsuarioAEditar] = useState<Usuario | null>(null);
  
  // 📌 ESTADOS PARA LA DOBLE ADVERTENCIA DE ELIMINACIÓN (HARD DELETE)
  const [usuarioAEliminar, setUsuarioAEliminar] = useState<Usuario | null>(null);
  const [showModal1, setShowModal1] = useState(false); // Paso 1: Confirmación inicial
  const [showModal2, setShowModal2] = useState(false); // Paso 2: Confirmación por escritura
  const [confirmacionTexto, setConfirmacionTexto] = useState('');

  // 📌 HANDLERS DE ACCIÓN
  const handleGuardado = () => {
    setMensajeExito(usuarioAEditar ? '✅ Usuario actualizado exitosamente.' : '✅ Usuario creado exitosamente.');
    setUsuarioAEditar(null); // Sale del modo edición
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const handleEliminarClick = (usuario: Usuario) => {
    setUsuarioAEliminar(usuario);
    setShowModal1(true);
  };

  const confirmarPaso1 = () => {
    setShowModal1(false);
    setShowModal2(true);
    setConfirmacionTexto(''); // Limpia el input para el paso 2
  };

  const confirmarEliminacionFinal = async () => {
    // ⚠️ VALIDACIÓN DE SEGURIDAD: Solo permite eliminar si el usuario escribió exactamente "ELIMINAR"
    if (confirmacionTexto.trim() === 'ELIMINAR' && usuarioAEliminar) {
      try {
        await eliminarUsuario(usuarioAEliminar.id);
        setMensajeExito('✅ Usuario eliminado permanentemente.');
        setShowModal2(false);
        setUsuarioAEliminar(null);
        setTimeout(() => setMensajeExito(''), 3000);
      } catch (error: any) {
        alert(error.response?.data?.detail || '❌ Error al eliminar el usuario.');
      }
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto relative">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Usuarios</h1>
      </div>

      {/* 📌 BANNER DE MENSAJES DE ÉXITO */}
      {mensajeExito && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2 animate-pulse">
          {mensajeExito}
        </div>
      )}

      {/* 📌 FORMULARIO (CREAR / EDITAR) */}
      <UsuarioFormulario 
        onGuardado={handleGuardado} 
        onCancelado={() => setUsuarioAEditar(null)}
        usuarioAEditar={usuarioAEditar}
      />

      {/* 📌 TABLA DE DATOS */}
      <UsuarioTabla 
        usuarios={usuarios} 
        isLoading={isLoading} 
        busqueda={busqueda}
        onBusquedaChange={setBusqueda}
        onEditar={setUsuarioAEditar}
        onEliminarClick={handleEliminarClick}
      />

      {/* 📌 MODAL 1: PRIMERA ADVERTENCIA */}
      {showModal1 && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">¿Estás seguro de que deseas eliminar a este usuario?</h3>
            <p className="text-gray-600 mb-6">
              Estás a punto de eliminar a <strong>{usuarioAEliminar?.nombre}</strong>. 
              Esta acción no se puede deshacer fácilmente.
            </p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setShowModal1(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
              >
                Cancelar
              </button>
              <button 
                onClick={confirmarPaso1}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-medium"
              >
                Sí, continuar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 📌 MODAL 2: SEGUNDA ADVERTENCIA (HARD DELETE CON CONFIRMACIÓN POR ESCRITURA) */}
      {showModal2 && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border-l-4 border-red-600">
            <h3 className="text-lg font-bold text-red-700 mb-2 flex items-center gap-2">
              ⚠️ ADVERTENCIA CRÍTICA
            </h3>
            <p className="text-gray-700 mb-4 text-sm">
              Esta acción es una <strong>eliminación permanente (Hard Delete)</strong>. 
              El usuario <strong>{usuarioAEliminar?.nombre}</strong> no podrá ser recuperado de ninguna manera 
              y se perderán todos sus datos asociados.
            </p>
            <p className="text-gray-800 font-semibold mb-2">
              Para confirmar, escribe la palabra <span className="text-red-600">ELIMINAR</span> en el cuadro de abajo:
            </p>
            <input 
              type="text"
              value={confirmacionTexto}
              onChange={(e) => setConfirmacionTexto(e.target.value)}
              className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none mb-4"
              placeholder="Escribe ELIMINAR aquí"
            />
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => { setShowModal2(false); setUsuarioAEliminar(null); }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
              >
                Cancelar
              </button>
              <button 
                // ⚠️ El botón se habilita SOLO si el texto coincide exactamente y no está procesando
                onClick={confirmarEliminacionFinal}
                disabled={confirmacionTexto.trim() !== 'ELIMINAR' || isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-red-300 disabled:cursor-not-allowed font-medium flex items-center gap-2"
              >
                {isDeleting ? 'Eliminando...' : '🗑️ Eliminar Permanentemente'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}