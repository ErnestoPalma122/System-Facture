// C:\Users\PC\Desktop\Factu\frontend\src\features\productos\components\ProductoFormulario.tsx
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useProductos } from '../hooks/useProductos';
import { Producto, ProductoFormData } from '../api/producto_api';

const productoSchema = z.object({
  codigo: z.string().min(2, 'Mínimo 2 caracteres').max(50, 'Máximo 50 caracteres'),
  nombre: z.string().min(2, 'Mínimo 2 caracteres').max(150, 'Máximo 150 caracteres'),
  descripcion: z.string().optional().or(z.literal('')),
  marca: z.string().optional().or(z.literal('')),
  tipo: z.enum(['BIEN', 'SERVICIO']),
  categoria_id: z.string().optional().or(z.literal('')),
  precio: z.object({
    precio_base: z.string().min(1, 'El precio base es obligatorio'),
    precio_publico: z.string().min(1, 'El precio público es obligatorio'),
    precio_costo: z.string().optional().or(z.literal('')),
    precio_iva: z.string().optional().or(z.literal('')),
    precio_promo: z.string().optional().or(z.literal('')),
    precio_descuento: z.string().optional().or(z.literal('')),
  }),
});

type FormValues = z.infer<typeof productoSchema>;

interface ProductoFormularioProps {
  onGuardado: () => void;
  onCancelado: () => void;
  productoAEditar?: Producto | null;
}

export function ProductoFormulario({ onGuardado, onCancelado, productoAEditar }: ProductoFormularioProps) {
  const { categorias, crearProducto, actualizarProducto, isCreating, isUpdating } = useProductos();
  const isSubmitting = isCreating || isUpdating;

  const { register, handleSubmit, reset, formState: { errors }, setValue } = useForm<FormValues>({
    resolver: zodResolver(productoSchema),
    defaultValues: {
      codigo: '', nombre: '', descripcion: '', marca: '', tipo: 'BIEN', categoria_id: '',
      precio: { precio_base: '', precio_publico: '', precio_costo: '', precio_iva: '', precio_promo: '', precio_descuento: '' }
    },
  });

  // Cargar datos en el formulario cuando hay un producto a editar
  useEffect(() => {
    if (productoAEditar) {
      setValue('codigo', productoAEditar.codigo);
      setValue('nombre', productoAEditar.nombre);
      setValue('descripcion', productoAEditar.descripcion || '');
      setValue('marca', productoAEditar.marca || '');
      setValue('tipo', productoAEditar.tipo as 'BIEN' | 'SERVICIO');
      setValue('categoria_id', productoAEditar.categoria_id ? String(productoAEditar.categoria_id) : '');
      if (productoAEditar.precio) {
        setValue('precio.precio_base', String(productoAEditar.precio.precio_base));
        setValue('precio.precio_publico', String(productoAEditar.precio.precio_publico));
        setValue('precio.precio_costo', '');
        setValue('precio.precio_iva', '');
        setValue('precio.precio_promo', '');
        setValue('precio.precio_descuento', '');
      }
    } else {
      reset();
    }
  }, [productoAEditar, reset, setValue]);

  const onSubmit = async (data: FormValues) => {
    try {
      const payload: ProductoFormData = {
        codigo: data.codigo,
        nombre: data.nombre,
        tipo: data.tipo,
        descripcion: data.descripcion || undefined,
        marca: data.marca || undefined,
        categoria_id: data.categoria_id || undefined,
        precio: {
          precio_base: data.precio.precio_base,
          precio_publico: data.precio.precio_publico,
          precio_costo: data.precio.precio_costo || undefined,
          precio_iva: data.precio.precio_iva || undefined,
          precio_promo: data.precio.precio_promo || undefined,
          precio_descuento: data.precio.precio_descuento || undefined,
        }
      };

      if (productoAEditar) {
        await actualizarProducto({ id: productoAEditar.id, data: payload });
      } else {
        await crearProducto(payload);
      }
      
      reset();
      onGuardado();
    } catch (error: any) {
      console.error('Error al guardar producto:', error);
      alert(error.response?.data?.detail || '❌ Error al guardar el producto.');
    }
  };

  const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const errorClass = "text-red-500 text-xs mt-1";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-6">
      <h2 className="text-lg font-bold text-gray-800 border-b pb-2">
        {productoAEditar ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className={labelClass}>Código *</label>
          <input {...register('codigo')} className={inputClass} placeholder="Ej: PROD-001" />
          {errors.codigo && <p className={errorClass}>{errors.codigo.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Nombre *</label>
          <input {...register('nombre')} className={inputClass} placeholder="Nombre del producto" />
          {errors.nombre && <p className={errorClass}>{errors.nombre.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Marca</label>
          <input {...register('marca')} className={inputClass} placeholder="Marca (opcional)" />
        </div>
        <div className="md:col-span-2">
          <label className={labelClass}>Descripción</label>
          <input {...register('descripcion')} className={inputClass} placeholder="Descripción detallada (opcional)" />
        </div>
        <div>
          <label className={labelClass}>Tipo *</label>
          <select {...register('tipo')} className={inputClass}>
            <option value="BIEN">Bien</option>
            <option value="SERVICIO">Servicio</option>
          </select>
        </div>
        <div>
          <label className={labelClass}>Categoría</label>
          <select {...register('categoria_id')} className={inputClass}>
            <option value="">Sin categoría</option>
            {categorias.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="text-md font-semibold text-gray-700 mb-3">Precios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>Precio Base *</label>
            <input type="number" step="0.01" {...register('precio.precio_base')} className={inputClass} placeholder="0.00" />
            {errors.precio?.precio_base && <p className={errorClass}>{errors.precio.precio_base.message}</p>}
          </div>
          <div>
            <label className={labelClass}>Precio Público *</label>
            <input type="number" step="0.01" {...register('precio.precio_publico')} className={inputClass} placeholder="0.00" />
            {errors.precio?.precio_publico && <p className={errorClass}>{errors.precio.precio_publico.message}</p>}
          </div>
          <div>
            <label className={labelClass}>Precio Costo</label>
            <input type="number" step="0.01" {...register('precio.precio_costo')} className={inputClass} placeholder="0.00" />
          </div>
          <div>
            <label className={labelClass}>Precio con IVA</label>
            <input type="number" step="0.01" {...register('precio.precio_iva')} className={inputClass} placeholder="0.00" />
          </div>
          <div>
            <label className={labelClass}>Precio Promoción</label>
            <input type="number" step="0.01" {...register('precio.precio_promo')} className={inputClass} placeholder="0.00" />
          </div>
          <div>
            <label className={labelClass}>Precio Descuento</label>
            <input type="number" step="0.01" {...register('precio.precio_descuento')} className={inputClass} placeholder="0.00" />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        {productoAEditar && (
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
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
        >
          {isSubmitting ? 'Guardando...' : (productoAEditar ? '💾 Actualizar Producto' : '💾 Guardar Producto')}
        </button>
      </div>
    </form>
  );
}