//frontend\src\features\proveedores\components\ProveedorList.tsx.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useProveedores } from '../hooks/useProveedores';
import { Proveedor, ProveedorFormData } from '../api/proveedor_api';
import { FiltroBusquedaProveedores } from './filtro_busqueda_proveedores';

// Validación: nombre, direccion y telefono1 son obligatorios
const proveedorSchema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres').max(150, 'Máximo 150 caracteres'),
  direccion: z.string().min(1, 'La dirección es obligatoria').max(255, 'Máximo 255 caracteres'),
  contacto: z.string().max(100, 'Máximo 100 caracteres').optional().or(z.literal('')),
  email: z.string().email('Correo inválido').max(150, 'Máximo 150 caracteres').optional().or(z.literal('')),
  telefono1: z.string().min(1, 'El teléfono principal es obligatorio').max(20, 'Máximo 20 caracteres'),
  telefono2: z.string().max(20, 'Máximo 20 caracteres').optional().or(z.literal('')),
  observaciones: z.string().optional().or(z.literal('')),
});

export function ProveedorList() {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pasamos el searchTerm al hook para que refetch cuando cambie
  const { proveedores, isLoading, crearProveedor, actualizarProveedor, eliminarProveedor, isCreating, isUpdating, isDeleting } = useProveedores(searchTerm);
  
  const [showForm, setShowForm] = useState(false);
  const [editingProveedor, setEditingProveedor] = useState<Proveedor | null>(null);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ProveedorFormData>({
    resolver: zodResolver(proveedorSchema),
    defaultValues: {
      nombre: '', direccion: '', contacto: '', email: '', telefono1: '', telefono2: '', observaciones: ''
    },
  });

  const handleOpenCreate = () => {
    setEditingProveedor(null);
    reset({ nombre: '', direccion: '', contacto: '', email: '', telefono1: '', telefono2: '', observaciones: '' });
    setShowForm(true);
  };

  const handleOpenEdit = (proveedor: Proveedor) => {
    setEditingProveedor(proveedor);
    reset({
      nombre: proveedor.nombre,
      direccion: proveedor.direccion || '',
      contacto: proveedor.contacto || '',
      email: proveedor.email || '',
      telefono1: proveedor.telefono1 || '',
      telefono2: proveedor.telefono2 || '',
      observaciones: proveedor.observaciones || '',
    });
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingProveedor(null);
    reset();
  };

  const onSubmit = async (data: ProveedorFormData) => {
    try {
      const payload = {
        ...data,
        contacto: data.contacto || undefined,
        email: data.email || undefined,
        telefono2: data.telefono2 || undefined,
        observaciones: data.observaciones || undefined,
      };

      if (editingProveedor) {
        await actualizarProveedor({ id: editingProveedor.id, data: payload });
      } else {
        await crearProveedor(payload);
      }
      handleCloseForm();
    } catch (error: any) {
      console.error('Error al guardar proveedor:', error);
      alert(error.response?.data?.detail || '❌ Error al guardar el proveedor.');
    }
  };

  const handleDelete = async (id: number, nombre: string) => {
    if (window.confirm(`¿Estás seguro de que deseas desactivar al proveedor "${nombre}"?`)) {
      try {
        await eliminarProveedor(id);
      } catch (error: any) {
        alert(error.response?.data?.detail || '❌ Error al eliminar el proveedor.');
      }
    }
  };

  return (
    <div className="p-6 h-[calc(100vh-80px)] flex gap-6 relative">
      
      {/* SECCIÓN IZQUIERDA: Datagrid (Tabla) */}
      <div className={`flex-1 transition-all duration-300 ${showForm ? 'mr-0 lg:mr-[400px]' : ''}`}>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <h1 className="text-2xl font-bold text-gray-800">Gestión de Proveedores</h1>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            {/* Pasamos isLoading para que el input muestre el spinner */}
            <FiltroBusquedaProveedores onSearch={setSearchTerm} isLoading={isLoading} />
            <button 
              onClick={handleOpenCreate}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2 transition-colors shadow-sm whitespace-nowrap"
            >
              <span>+</span> Nuevo Proveedor
            </button>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Teléfono</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      <div className="flex flex-col items-center">
                        <svg className="animate-spin h-8 w-8 text-blue-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p>Buscando proveedores...</p>
                      </div>
                    </td>
                  </tr>
                ) : proveedores.length > 0 ? (
                  proveedores.map((prov) => (
                    <tr key={prov.id} className="hover:bg-gray-50 transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{prov.nombre}</div>
                        <div className="text-xs text-gray-500 truncate max-w-xs">{prov.direccion || 'Sin dirección'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{prov.telefono1 || <span className="text-gray-400">-</span>}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600">{prov.email || <span className="text-gray-400">-</span>}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          prov.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {prov.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button 
                          onClick={() => handleOpenEdit(prov)}
                          className="text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors duration-150"
                        >
                          ✏️ Editar
                        </button>
                        {prov.activo && (
                          <button 
                            onClick={() => handleDelete(prov.id, prov.nombre)}
                            disabled={isDeleting}
                            className="text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-md transition-colors duration-150 disabled:opacity-50"
                          >
                            🗑️ Desactivar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      <p className="text-lg font-medium">
                        {searchTerm ? `No se encontraron proveedores que coincidan con "${searchTerm}"` : 'No hay proveedores registrados.'}
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        {searchTerm ? 'Intenta con otro nombre o borra la búsqueda.' : 'Haz clic en "Nuevo Proveedor" para comenzar.'}
                      </p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* SECCIÓN DERECHA: Panel Lateral de Formulario */}
      {showForm && (
        <div className="fixed inset-y-0 right-0 w-full lg:w-[400px] bg-white shadow-2xl border-l border-gray-200 transform transition-transform duration-300 ease-in-out z-40 overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">
                {editingProveedor ? 'Editar Proveedor' : 'Nuevo Proveedor'}
              </h2>
              <button onClick={handleCloseForm} className="text-gray-500 hover:text-gray-700 text-2xl leading-none">&times;</button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input {...register('nombre')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dirección *</label>
                <input {...register('direccion')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                {errors.direccion && <p className="text-red-500 text-xs mt-1">{errors.direccion.message}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono 1 *</label>
                  <input {...register('telefono1')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  {errors.telefono1 && <p className="text-red-500 text-xs mt-1">{errors.telefono1.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono 2</label>
                  <input {...register('telefono2')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Persona de Contacto</label>
                <input {...register('contacto')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
                <input type="email" {...register('email')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
                <textarea {...register('observaciones')} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none" />
              </div>

              <div className="flex gap-3 pt-4 border-t mt-6">
                <button 
                  type="button" 
                  onClick={handleCloseForm}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={isCreating || isUpdating}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {isCreating || isUpdating ? 'Guardando...' : (editingProveedor ? 'Actualizar' : 'Crear')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {showForm && (
        <div className="fixed inset-0 bg-black/20 z-30 lg:hidden" onClick={handleCloseForm}></div>
      )}
    </div>
  );
}