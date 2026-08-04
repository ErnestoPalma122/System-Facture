// frontend/src/features/bodegas/components/BodegaForm.tsx

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useBodegas } from '../hooks/useBodegas';
import { useUsuarios } from '@/features/usuarios/hooks/useUsuarios'; // <-- NUEVO: Hook para obtener la lista de usuarios
import { Bodega } from '../api/bodega_api';

// 📌 ESQUEMA DE VALIDACIÓN CON ZOD
// Define las reglas del formulario. 
// ⚠️ Nota: Los campos opcionales usan .optional().or(z.literal('')) para aceptar tanto 'undefined' como cadenas vacías ''.
// ⚠️ 'encargado_id' se maneja como string en el formulario (para el input de texto) y se convierte a número al enviar.
const bodegaSchema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres').max(100, 'Máximo 100 caracteres'),
  direccion: z.string().max(255, 'Máximo 255 caracteres').optional().or(z.literal('')),
  ubicacion: z.string().max(150, 'Máximo 150 caracteres').optional().or(z.literal('')),
  telefono: z.string().max(20, 'Máximo 20 caracteres').optional().or(z.literal('')),
  encargado_id: z.string().optional(), 
});

type BodegaFormData = z.infer<typeof bodegaSchema>;

// 📌 COMPONENTE PRINCIPAL DE LA PÁGINA DE BODEGAS
// Combina la visualización de la tabla (Datagrid) y el modal de creación/edición en un solo componente.
export function BodegaPage() {
  // 🔗 Hooks personalizados para obtener datos y acciones del servidor
  const { bodegas, isLoading: isLoadingBodegas, crearBodega, actualizarBodega, isCreating, isUpdating } = useBodegas();
  const { usuarios, isLoading: isLoadingUsuarios } = useUsuarios(); 
  
  // 📌 ESTADOS LOCALES DE LA UI
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBodega, setEditingBodega] = useState<Bodega | null>(null);
  
  // Estados para el filtro dinámico (autocomplete) de usuarios
  const [busquedaEncargado, setBusquedaEncargado] = useState('');
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false);

  // 📌 CONFIGURACIÓN DE REACT HOOK FORM
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<BodegaFormData>({
    resolver: zodResolver(bodegaSchema),
    defaultValues: {
      nombre: '',
      direccion: '',
      ubicacion: '',
      telefono: '',
      encargado_id: '',
    },
  });

  // 📌 EFECTO: SINCRONIZAR BUSCADOR AL EDITAR
  // Cuando se abre el modal en modo edición, busca el nombre del usuario correspondiente al 'encargado_id' 
  // y lo muestra en el input de búsqueda para que el usuario vea quién está asignado.
  useEffect(() => {
    if (editingBodega && editingBodega.encargado_id) {
      const usuarioEncontrado = usuarios.find(u => u.id === editingBodega.encargado_id);
      setBusquedaEncargado(usuarioEncontrado ? usuarioEncontrado.nombre : '');
    } else {
      setBusquedaEncargado('');
    }
  }, [editingBodega, usuarios]);

  // 📌 HANDLERS: ABRIR MODAL EN MODO CREACIÓN
  const handleOpenCreate = () => {
    setEditingBodega(null);
    setBusquedaEncargado('');
    reset({ nombre: '', direccion: '', ubicacion: '', telefono: '', encargado_id: '' });
    setIsModalOpen(true);
  };

  // 📌 HANDLERS: ABRIR MODAL EN MODO EDICIÓN
  const handleOpenEdit = (bodega: Bodega) => {
    setEditingBodega(bodega);
    reset({
      nombre: bodega.nombre,
      direccion: bodega.direccion || '',
      ubicacion: bodega.ubicacion || '',
      telefono: bodega.telefono || '',
      encargado_id: bodega.encargado_id ? String(bodega.encargado_id) : '', // 🔗 Convierte number a string para el formulario
    });
    setIsModalOpen(true);
  };

  // 📌 HANDLER: ENVÍO DEL FORMULARIO
  const onSubmit = async (data: BodegaFormData) => {
    try {
      // ⚠️ TRANSFORMACIÓN DE PAYLOAD: Convierte los datos del formulario al formato que espera la API.
      // Convierte 'encargado_id' de string a number (o undefined si está vacío).
      // Convierte cadenas vacías a 'undefined' para no enviar campos nulos innecesarios.
      const payload = {
        nombre: data.nombre,
        direccion: data.direccion || undefined,
        ubicacion: data.ubicacion || undefined,
        telefono: data.telefono || undefined,
        encargado_id: data.encargado_id ? parseInt(data.encargado_id, 10) : undefined, 
      };

      if (editingBodega) {
        await actualizarBodega({ id: editingBodega.id, data: payload });
      } else {
        await crearBodega(payload);
      }
      
      // Limpieza post-éxito
      setIsModalOpen(false);
      reset();
    } catch (error) {
      console.error('Error al guardar bodega:', error);
      alert('Error al guardar la bodega. Revisa la consola para más detalles.');
    }
  };

  // 📌 LÓGICA DE AUTOCOMPLETE: FILTRAR USUARIOS
  // Filtra la lista de usuarios en tiempo real por nombre o email, ignorando mayúsculas/minúsculas.
  const sugerencias = usuarios.filter(u => 
    u.nombre.toLowerCase().includes(busquedaEncargado.toLowerCase()) ||
    u.email.toLowerCase().includes(busquedaEncargado.toLowerCase())
  );

  // 📌 ESTADO DE CARGA INICIAL
  if (isLoadingBodegas || isLoadingUsuarios) {
    return <div className="p-8 text-center text-gray-600">Cargando datos...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* 📌 ENCABEZADO DE LA PÁGINA */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Bodegas</h1>
        <button 
          onClick={handleOpenCreate}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors shadow-sm"
        >
          <span>+</span> Nueva Bodega
        </button>
      </div>

      {/* 📌 DATAGRID (TABLA) DE BODEGAS */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Dirección</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Ubicación</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Teléfono</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Encargado</th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {bodegas.length > 0 ? (
                bodegas.map((bodega) => {
                  // 🔗 CRUCE VISUAL (JOIN): Busca el objeto usuario completo usando el 'encargado_id' de la bodega.
                  const encargado = usuarios.find(u => u.id === bodega.encargado_id);
                  
                  return (
                    <tr key={bodega.id} className="hover:bg-gray-50 transition-colors duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{bodega.nombre}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{bodega.direccion || <span className="text-gray-400">-</span>}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{bodega.ubicacion || <span className="text-gray-400">-</span>}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{bodega.telefono || <span className="text-gray-400">-</span>}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {/* 📌 MUESTRA EL NOMBRE DEL USUARIO EN LUGAR DEL ID NUMÉRICO */}
                        <div className="text-sm text-gray-900 font-medium">
                          {encargado ? encargado.nombre : <span className="text-gray-400">Sin asignar</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          bodega.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {bodega.activo ? 'Activa' : 'Inactiva'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          onClick={() => handleOpenEdit(bodega)}
                          className="text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors duration-150 flex items-center gap-1 ml-auto"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                          Editar
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                // 📌 ESTADO VACÍO (EMPTY STATE) DE LA TABLA
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center justify-center">
                      <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                      <p className="text-lg font-medium">No hay bodegas registradas.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 📌 MODAL DE FORMULARIO (CREAR / EDITAR) */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800">
                {editingBodega ? 'Editar Bodega' : 'Nueva Bodega'}
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4 relative">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input {...register('nombre')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                <input {...register('direccion')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
                  <input {...register('ubicacion')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                  <input {...register('telefono')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>

              {/* 📌 CAMPO DE AUTOCOMPLETE PERSONALIZADO PARA "ENCARGADO" */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">Encargado (Buscar por nombre)</label>
                <input 
                  type="text"
                  value={busquedaEncargado}
                  onChange={(e) => {
                    setBusquedaEncargado(e.target.value);
                    setMostrarSugerencias(true);
                    setValue('encargado_id', ''); // 🔗 Limpia el ID oculto si el usuario modifica el texto manualmente
                  }}
                  onFocus={() => setMostrarSugerencias(true)}
                  placeholder="Escribe el nombre del usuario..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                />
                
                {/* 📌 LISTA DESPLEGABLE DE SUGERENCIAS */}
                {mostrarSugerencias && busquedaEncargado.length > 0 && (
                  <ul className="absolute z-20 w-full bg-white border border-gray-200 rounded-lg shadow-xl max-h-48 overflow-y-auto mt-1">
                    {sugerencias.length > 0 ? (
                      sugerencias.map((u) => (
                        <li 
                          key={u.id}
                          onClick={() => {
                            setBusquedaEncargado(u.nombre); // Muestra el nombre legible en el input
                            setValue('encargado_id', String(u.id)); // 🔗 Guarda el ID numérico (como string) en el campo oculto de RHF
                            setMostrarSugerencias(false);
                          }}
                          className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-sm border-b border-gray-100 last:border-0 transition-colors"
                        >
                          <span className="font-medium text-gray-900">{u.nombre}</span>
                          <span className="text-gray-500 text-xs ml-2">({u.email})</span>
                        </li>
                      ))
                    ) : (
                      <li className="px-4 py-2 text-sm text-gray-500">No se encontraron usuarios</li>
                    )}
                  </ul>
                )}
                {/* ⚠️ CAMPO OCULTO: React Hook Form usa este input para gestionar el valor de 'encargado_id' */}
                <input type="hidden" {...register('encargado_id')} />
              </div>

              {/* 📌 BOTONES DE ACCIÓN DEL MODAL */}
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Cancelar
                </button>
                <button type="submit" disabled={isCreating || isUpdating} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed font-medium">
                  {isCreating || isUpdating ? 'Guardando...' : (editingBodega ? 'Actualizar' : 'Crear')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* 📌 OVERLAY INVISIBLE PARA CERRAR SUGERENCIAS AL HACER CLIC FUERA */}
      {/* z-10 asegura que esté por debajo del modal (z-50) pero por encima del contenido de la página */}
      {mostrarSugerencias && (
        <div className="fixed inset-0 z-10" onClick={() => setMostrarSugerencias(false)}></div>
      )}
    </div>
  );
}