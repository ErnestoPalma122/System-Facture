// frontend/src/features/usuarios/components/UsuarioFormulario.tsx

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUsuarios } from '../hooks/useUsuarios';
import { useRoles } from '../hooks/useRoles';
import { useDepartamentos } from '../hooks/useDepartamentos';
import { Usuario, UsuarioFormData } from '../api/usuario_api';

// 📌 ESQUEMA DE VALIDACIÓN (ZOD)
const usuarioSchema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres').max(100, 'Máximo 100 caracteres'),
  email: z.string().email('Correo electrónico inválido'),
  telefono: z.string().max(20, 'Máximo 20 caracteres').optional().or(z.literal('')),
  departamento_id: z.string().optional().or(z.literal('')),
  rol_id: z.string().min(1, 'El rol es obligatorio'),
  // ⚠️ La contraseña es opcional en edición, pero obligatoria (min 8) si se proporciona.
  password: z.string().min(8, 'Mínimo 8 caracteres').optional().or(z.literal('')),
});

type FormValues = z.infer<typeof usuarioSchema>;

interface UsuarioFormularioProps {
  onGuardado: () => void;
  onCancelado: () => void;
  usuarioAEditar?: Usuario | null; // 🔗 Si existe, el form entra en "Modo Edición"
}

export function UsuarioFormulario({ onGuardado, onCancelado, usuarioAEditar }: UsuarioFormularioProps) {
  const { crearUsuario, actualizarUsuario, isCreating, isUpdating } = useUsuarios();
  const { data: roles = [] } = useRoles();
  const { data: departamentos = [] } = useDepartamentos();
  const isSubmitting = isCreating || isUpdating;

  // 📌 CONFIGURACIÓN DE REACT HOOK FORM
  const { register, handleSubmit, reset, formState: { errors }, setValue } = useForm<FormValues>({
    resolver: zodResolver(usuarioSchema),
    defaultValues: {
      nombre: '', email: '', telefono: '', departamento_id: '', rol_id: '', password: ''
    },
  });

  // 📌 SINCRONIZACIÓN DE DATOS PARA EDICIÓN
  useEffect(() => {
    if (usuarioAEditar) {
      // Rellena el formulario con los datos del usuario seleccionado
      setValue('nombre', usuarioAEditar.nombre);
      setValue('email', usuarioAEditar.email);
      setValue('telefono', usuarioAEditar.telefono || '');
      setValue('departamento_id', usuarioAEditar.departamento_id ? String(usuarioAEditar.departamento_id) : '');
      setValue('rol_id', usuarioAEditar.rol_id ? String(usuarioAEditar.rol_id) : '');
      // ⚠️ CRÍTICO: Nunca mostramos la contraseña actual. Se deja vacía.
      setValue('password', ''); 
    } else {
      reset(); // Limpia el formulario al cambiar a "Modo Creación"
    }
  }, [usuarioAEditar, reset, setValue]);

  // 📌 MANEJADOR DE ENVÍO
  const onSubmit = async (data: FormValues) => {
    try {
      // Construye el payload final, convirtiendo cadenas vacías a 'undefined' para no enviar datos basura
      const payload: UsuarioFormData = {
        nombre: data.nombre,
        email: data.email,
        telefono: data.telefono || undefined,
        departamento_id: data.departamento_id || undefined,
        rol_id: data.rol_id,
        password: data.password || undefined,
      };

      if (usuarioAEditar) {
        await actualizarUsuario({ id: usuarioAEditar.id, data: payload });
      } else {
        await crearUsuario(payload);
      }
      
      reset(); // Limpia el formulario tras el éxito
      onGuardado(); // Notifica al padre para mostrar mensaje y recargar tabla
    } catch (error: any) {
      console.error('Error al guardar usuario:', error);
      alert(error.response?.data?.detail || '❌ Error al guardar el usuario.');
    }
  };

  const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const errorClass = "text-red-500 text-xs mt-1";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-6">
      <h2 className="text-lg font-bold text-gray-800 border-b pb-2">
        {usuarioAEditar ? '✏️ Editar Usuario' : '➕ Nuevo Usuario'}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Nombre Completo *</label>
          <input {...register('nombre')} className={inputClass} placeholder="Nombre del usuario" />
          {errors.nombre && <p className={errorClass}>{errors.nombre.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Correo Electrónico *</label>
          <input type="email" {...register('email')} className={inputClass} placeholder="correo@ejemplo.com" />
          {errors.email && <p className={errorClass}>{errors.email.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Teléfono</label>
          <input {...register('telefono')} className={inputClass} placeholder="Opcional" />
        </div>
        <div>
          <label className={labelClass}>Rol *</label>
          <select {...register('rol_id')} className={inputClass}>
            <option value="">Seleccionar rol...</option>
            {roles.map((rol) => (
              <option key={rol.id} value={rol.id}>{rol.nombre} ({rol.tipo})</option>
            ))}
          </select>
          {errors.rol_id && <p className={errorClass}>{errors.rol_id.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Departamento</label>
          <select {...register('departamento_id')} className={inputClass}>
            <option value="">Sin departamento</option>
            {departamentos.map((dept) => (
              <option key={dept.id} value={dept.id}>{dept.nombre}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>
            {usuarioAEditar ? 'Nueva Contraseña (dejar en blanco para no cambiar)' : 'Contraseña *'}
          </label>
          <input 
            type="password" 
            // ⚠️ Validación condicional: solo es required si NO estamos editando.
            {...register('password', { required: !usuarioAEditar ? 'La contraseña es obligatoria' : false })} 
            className={inputClass} 
            placeholder={usuarioAEditar ? "Opcional" : "Mínimo 8 caracteres"} 
          />
          {errors.password && <p className={errorClass}>{errors.password.message}</p>}
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        {usuarioAEditar && (
          <button 
            type="button" 
            onClick={onCancelado}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancelar
          </button>
        )}
        <button 
          type="submit" 
          disabled={isSubmitting}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
        >
          {isSubmitting ? 'Guardando...' : (usuarioAEditar ? '💾 Actualizar Usuario' : '💾 Crear Usuario')}
        </button>
      </div>
    </form>
  );
}