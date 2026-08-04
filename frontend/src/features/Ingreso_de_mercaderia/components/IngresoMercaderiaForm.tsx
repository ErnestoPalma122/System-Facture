// frontend/src/features/ingreso_mercaderia/components/IngresoMercaderiaForm.tsx

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useIngresoMercaderia } from '../hooks/useIngresoMercaderia';
import { IngresoSeriesPanel } from './IngresoSeriesPanel';

// 📌 ESQUEMA DE VALIDACIÓN DE LA CABECERA (ZOD)
// Define las reglas para los campos principales. Los ítems (series) se validan por separado en el panel.
const cabeceraSchema = z.object({
  codigo_generacion: z.string().min(2, 'Obligatorio'),
  dte: z.string().min(2, 'Obligatorio'),
  sello: z.string().min(2, 'Obligatorio'),
  cotizacion: z.string().optional().or(z.literal('')),
  proveedor_id: z.number().min(1, 'Selecciona un proveedor'),
  estado_ingreso_id: z.number().min(1, 'Selecciona un estado'),
  observaciones: z.string().optional().or(z.literal('')),
});

type CabeceraValues = z.infer<typeof cabeceraSchema>;

interface IngresoMercaderiaFormProps {
  onGuardado: () => void; // 🔗 Callback para notificar al padre que el guardado fue exitoso
}

export function IngresoMercaderiaForm({ onGuardado }: IngresoMercaderiaFormProps) {
  // 🔗 Obtiene datos de catálogos y la función de mutación para crear
  const { estados, proveedores, productos, bodegas, crearIngreso, isCreating } = useIngresoMercaderia();

  // 📌 INICIALIZACIÓN DE REACT HOOK FORM
  const { register, handleSubmit, formState: { errors }, setValue, reset } = useForm<CabeceraValues>({
    resolver: zodResolver(cabeceraSchema),
    defaultValues: {
      estado_ingreso_id: 8, // ⚠️ Default: COMPLETO PROCESADO (ajustar según la ID real de tu BD)
      cotizacion: '',
      observaciones: '',
    }
  });

  // 📌 ESTADO LOCAL: "MOLDE" DEL ÍTEM
  // En lugar de un Form Array complejo, usamos un estado local para el producto/bodega/series que se está procesando.
  // Esto simplifica la UI a "un producto a la vez" con sus series, listo para enviar.
  const [molde, setMolde] = useState({ producto_id: 0, bodega_id: 0, seriesTexto: '' });
  
  // 📌 ESTADOS PARA BUSCADORES DINÁMICOS (TYPEAHEAD)
  const [busquedaProducto, setBusquedaProducto] = useState('');
  const [showDropdownProducto, setShowDropdownProducto] = useState(false);
  const [busquedaProveedor, setBusquedaProveedor] = useState('');
  const [showDropdownProveedor, setShowDropdownProveedor] = useState(false);

  // 🔗 Referencias rápidas a los objetos seleccionados para mostrar datos de solo lectura
  const productoSeleccionado = productos.find(p => p.id === molde.producto_id);
  const bodegaSeleccionada = bodegas.find(b => b.id === molde.bodega_id);

  // 📌 LÓGICA DE FILTRADO EN TIEMPO REAL
  const productosFiltrados = productos.filter(p => 
    p.nombre.toLowerCase().includes(busquedaProducto.toLowerCase()) || 
    p.codigo.toLowerCase().includes(busquedaProducto.toLowerCase())
  );

  const proveedoresFiltrados = proveedores.filter(p => 
    p.nombre.toLowerCase().includes(busquedaProveedor.toLowerCase())
  );

  // 📌 HANDLERS DE SELECCIÓN DE DROPDOWN
  const seleccionarProducto = (p: typeof productos[0]) => {
    setMolde(prev => ({ ...prev, producto_id: p.id }));
    setBusquedaProducto(`${p.nombre} (${p.codigo})`);
    setShowDropdownProducto(false);
  };

  const seleccionarProveedor = (p: typeof proveedores[0]) => {
    setValue('proveedor_id', p.id); // Actualiza el campo oculto de React Hook Form
    setBusquedaProveedor(p.nombre);
    setShowDropdownProveedor(false);
  };

  // 📌 VALIDACIÓN PREVIA AL ENVÍO
  // Convierte el texto de series en un array, limpiando espacios y líneas vacías.
  const seriesActualesDelMolde = molde.seriesTexto.split(/[\n,]+/).map(s => s.trim()).filter(s => s.length > 0);
  const haySeriesEnMolde = molde.producto_id > 0 && molde.bodega_id > 0 && seriesActualesDelMolde.length > 0;
  
  const puedeGuardar = haySeriesEnMolde;
  const totalSeries = haySeriesEnMolde ? seriesActualesDelMolde.length : 0;

  // 📌 MANEJADOR DE ENVÍO DEL FORMULARIO
  const onSubmit = async (data: CabeceraValues) => {
    if (!haySeriesEnMolde) {
      alert("⚠️ Debes ingresar al menos un producto con sus series");
      return;
    }

    try {
      // 🔗 Construcción del payload final: une la cabecera validada con el array de ítems del "molde"
      const payload = {
        ...data,
        cotizacion: data.cotizacion || '',
        observaciones: data.observaciones || '',
        items: [{
          producto_id: molde.producto_id,
          bodega_id: molde.bodega_id,
          dias_stock: 0,
          series: seriesActualesDelMolde,
        }],
      };

      await crearIngreso(payload);
      
      // ✅ 📌 LIMPIEZA TOTAL POST-GUARDADO (CRÍTICO PARA UX)
      // 1. Resetea los campos controlados por react-hook-form a sus valores iniciales
      reset({
        codigo_generacion: '',
        dte: '',
        sello: '',
        cotizacion: '',
        proveedor_id: 0,
        estado_ingreso_id: 8,
        observaciones: '',
      });
      // 2. Resetea los estados locales del molde y los buscadores
      setMolde({ producto_id: 0, bodega_id: 0, seriesTexto: '' });
      setBusquedaProducto('');
      setBusquedaProveedor('');
      setShowDropdownProducto(false);
      setShowDropdownProveedor(false);
      
      // 3. Notifica al componente padre para que muestre el banner de éxito
      onGuardado();
      
    } catch (error: any) {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // 📌 CLASES DE TAILWIND REUTILIZABLES
  const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const errorClass = "text-red-500 text-xs mt-1";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-6">
      <h2 className="text-lg font-bold text-gray-800 border-b pb-2">📥 Nuevo Ingreso de Mercadería</h2>
      
      {/* 📌 FILA 1: Datos de identificación y selección de producto */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className={labelClass}>Código de Generación *</label>
          <input {...register('codigo_generacion')} className={inputClass} placeholder="Ej: GEN-2026-001" />
          {errors.codigo_generacion && <p className={errorClass}>{errors.codigo_generacion.message}</p>}
        </div>
        
        <div className="relative">
          <label className={labelClass}>Buscar Producto (Nombre o Código) *</label>
          <input 
            type="text" 
            value={busquedaProducto}
            onChange={(e) => {
              setBusquedaProducto(e.target.value);
              setShowDropdownProducto(true);
              if (!e.target.value) setMolde(prev => ({ ...prev, producto_id: 0 })); // Limpia selección si borra texto
            }}
            onFocus={() => setShowDropdownProducto(true)}
            className={inputClass}
            placeholder="Escribe para buscar..."
            autoComplete="off"
          />
          {showDropdownProducto && busquedaProducto.length >= 2 && (
            <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {productosFiltrados.length > 0 ? (
                productosFiltrados.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => seleccionarProducto(p)}
                    className="w-full text-left px-4 py-2 hover:bg-blue-50 text-sm border-b border-gray-100 last:border-0 transition-colors"
                  >
                    <span className="font-medium text-gray-800">{p.nombre}</span>
                    <span className="text-gray-500 ml-2">({p.codigo})</span>
                  </button>
                ))
              ) : (
                <div className="px-4 py-2 text-sm text-gray-500">No se encontraron productos</div>
              )}
            </div>
          )}
        </div>

        <div>
          <label className={labelClass}>Código Producto</label>
          <input 
            type="text" 
            readOnly 
            value={productoSeleccionado?.codigo || ''} 
            className={`${inputClass} bg-gray-100 text-gray-600 font-mono`} // 🔗 Estilo de solo lectura
          />
        </div>
      </div>

      {/* 📌 FILA 2: Datos fiscales y proveedor */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className={labelClass}>DTE *</label>
          <input {...register('dte')} className={inputClass} placeholder="Ej: DTE-001" />
          {errors.dte && <p className={errorClass}>{errors.dte.message}</p>}
        </div>
        
        <div className="relative">
          <label className={labelClass}>Buscar Proveedor *</label>
          <input 
            type="text" 
            value={busquedaProveedor}
            onChange={(e) => {
              setBusquedaProveedor(e.target.value);
              setShowDropdownProveedor(true);
              setValue('proveedor_id', 0); // Limpia el ID si el usuario modifica el texto
            }}
            onFocus={() => setShowDropdownProveedor(true)}
            className={inputClass}
            placeholder="Escribe el nombre..."
            autoComplete="off"
          />
          {showDropdownProveedor && busquedaProveedor.length >= 2 && (
            <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {proveedoresFiltrados.length > 0 ? (
                proveedoresFiltrados.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => seleccionarProveedor(p)}
                    className="w-full text-left px-4 py-2 hover:bg-blue-50 text-sm border-b border-gray-100 last:border-0 transition-colors"
                  >
                    {p.nombre}
                  </button>
                ))
              ) : (
                <div className="px-4 py-2 text-sm text-gray-500">No se encontraron proveedores</div>
              )}
            </div>
          )}
          {errors.proveedor_id && typeof errors.proveedor_id.message === 'string' && (
            <p className={errorClass}>{errors.proveedor_id.message}</p>
          )}
        </div>

        <div>
          <label className={labelClass}>Estado Ingreso</label>
          <select {...register('estado_ingreso_id', { valueAsNumber: true })} className={`${inputClass} bg-blue-50`}>
            {estados.map(e => <option key={e.id} value={e.id}>{e.nombre_estado}</option>)}
          </select>
        </div>
      </div>

      {/* 📌 FILA 3: Datos complementarios y destino */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className={labelClass}>Sello *</label>
          <input {...register('sello')} className={inputClass} placeholder="Ej: SELLO123" />
          {errors.sello && <p className={errorClass}>{errors.sello.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Cotización</label>
          <input {...register('cotizacion')} className={inputClass} placeholder="Opcional" />
        </div>
        <div>
          <label className={labelClass}>Bodega Destino *</label>
          <select 
            value={molde.bodega_id} 
            onChange={(e) => setMolde(prev => ({ ...prev, bodega_id: Number(e.target.value) }))} 
            className={inputClass}
          >
            <option value={0}>-- Seleccionar Bodega --</option>
            {bodegas.map(b => <option key={b.id} value={b.id}>{b.nombre}</option>)}
          </select>
        </div>
      </div>

      {/* 📌 PANEL DE CARGA DE SERIES (Componente hijo especializado) */}
      <IngresoSeriesPanel
        productoId={molde.producto_id}
        bodegaId={molde.bodega_id}
        productoNombre={productoSeleccionado?.nombre}
        bodegaNombre={bodegaSeleccionada?.nombre}
        seriesTexto={molde.seriesTexto}
        onSeriesTextoChange={(texto) => setMolde(prev => ({ ...prev, seriesTexto: texto }))}
      />

      {/* 📌 BOTÓN DE ENVÍO FINAL */}
      {/* Se deshabilita si está cargando o si no hay series válidas en el molde */}
      <div className="border-t pt-4 flex justify-end">
        <button 
          type="submit" 
          disabled={isCreating || !puedeGuardar}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-bold shadow-lg flex items-center gap-2"
        >
          {isCreating ? (
            '⏳ Procesando...'
          ) : (
            <>
              <span>💾</span>
              <span>Guardar Ingreso ({totalSeries} series totales)</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}