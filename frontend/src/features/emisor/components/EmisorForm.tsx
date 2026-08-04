// frontend/src/features/emisor/components/EmisorForm.tsx

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEmisor } from '../hooks/useEmisor';
import { useCatalogos } from '@/features/catalogos/hooks/useCatalogos';
import { EmisorFormData, EmisorResponse } from '../api/emisor_api';
import { UbicacionSelector } from './UbicacionSelector';
import { ActividadEconomicaSelector } from './ActividadEconomicaSelector';

// 📌 1. ESQUEMA DE VALIDACIÓN COMPLETO CON ZOD
// Define reglas estrictas para todos los campos, incluyendo el objeto anidado 'direccion'.
const emisorSchema = z.object({
  nit: z.string().min(1, 'Requerido'),
  nrc: z.string().min(2, 'Mínimo 2 caracteres').max(8, 'Máximo 8 caracteres'),
  nombre: z.string().min(1, 'Requerido').max(250, 'Máximo 250 caracteres'),
  nombre_comercial: z.string().min(1, 'Requerido').max(150, 'Máximo 150 caracteres'),
  cod_actividad: z.string().min(5, 'Mínimo 5 caracteres').max(6, 'Máximo 6 caracteres'),
  desc_actividad: z.string().min(5, 'Mínimo 5 caracteres').max(150, 'Máximo 150 caracteres'),
  direccion: z.object({
    cod_departamento: z.string().min(1, 'Requerido'),
    desc_departamento: z.string().min(1, 'Requerido'),
    cod_municipio: z.string().min(1, 'Requerido'),
    desc_municipio: z.string().min(1, 'Requerido'),
    cod_distrito: z.string().min(1, 'Requerido'),
    desc_distrito: z.string().min(1, 'Requerido'),
    complemento: z.string().min(1, 'Requerido').max(200, 'Máximo 200 caracteres'),
  }),
  telefono: z.string().min(8, 'Mínimo 8 caracteres').max(30, 'Máximo 30 caracteres'),
  correo: z.string().email('Correo inválido').min(6).max(100),
  correo_interno: z.string().email('Correo inválido').min(6).max(100),
  cod_estable: z.string().min(2, 'Mínimo 2 caracteres').max(4, 'Máximo 4 caracteres'),
  cod_punto_venta: z.string().min(1, 'Requerido').max(15, 'Máximo 15 caracteres'),
});

// 📌 2. FUNCIÓN DE MAPEO (RESPUESTA BACKEND -> FORMULARIO)
// Transforma la estructura "plana" que devuelve el backend en la estructura "anidada" que espera el formulario (y Zod).
const mapResponseToForm = (res: EmisorResponse): EmisorFormData => ({
  nit: res.nit,
  nrc: res.nrc,
  nombre: res.nombre,
  nombre_comercial: res.nombre_comercial,
  cod_actividad: res.cod_actividad,
  desc_actividad: res.desc_actividad,
  direccion: {
    cod_departamento: res.cod_departamento,
    desc_departamento: res.desc_departamento,
    cod_municipio: res.cod_municipio,
    desc_municipio: res.desc_municipio,
    cod_distrito: res.cod_distrito,
    desc_distrito: res.desc_distrito,
    complemento: res.dirr_complemento, // ⚠️ Nota: mapeo del nombre de campo diferente del backend
  },
  telefono: res.telefono,
  correo: res.correo,
  correo_interno: res.correo_interno,
  cod_estable: res.cod_estable,
  cod_punto_venta: res.cod_punto_venta,
});

export function EmisorConfigPage() {
  const { emisor, isLoading, isError, crearEmisor, actualizarEmisor, isCreating, isUpdating } = useEmisor();
  const { catalogos, isLoading: isLoadingCatalogos } = useCatalogos();
  
  // 📌 3. CONFIGURACIÓN DE REACT HOOK FORM
  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<EmisorFormData>({
    resolver: zodResolver(emisorSchema),
    defaultValues: {
      nit: '', nrc: '', nombre: '', nombre_comercial: '',
      cod_actividad: '', desc_actividad: '',
      direccion: { cod_departamento: '', desc_departamento: '', cod_municipio: '', desc_municipio: '', cod_distrito: '', desc_distrito: '', complemento: '' },
      telefono: '', correo: '', correo_interno: '', cod_estable: '', cod_punto_venta: ''
    }
  });

  // 📌 4. CARGA DE DATOS EXISTENTES
  // Cuando el hook 'useEmisor' termina de cargar, si existe un emisor, rellena el formulario.
  useEffect(() => {
    if (emisor) {
      reset(mapResponseToForm(emisor));
    }
  }, [emisor, reset]);

  // 📌 5. MANEJADOR DE ENVÍO
  const onSubmit = async (data: EmisorFormData) => {
    try {
      if (emisor) {
        // Si ya existe, actualizamos
        await actualizarEmisor(data);
        alert('✅ Configuración del emisor actualizada exitosamente.');
      } else {
        // Si no existe, creamos
        await crearEmisor(data);
        alert('✅ Configuración del emisor creada exitosamente.');
      }
    } catch (error: any) {
      console.error('Error al guardar emisor:', error);
      alert(error.response?.data?.detail || '❌ Error al guardar la configuración. Revisa la consola.');
    }
  };

  if (isLoading || isLoadingCatalogos) {
    return <div className="p-8 text-center text-gray-600">Cargando datos del sistema...</div>;
  }

  // 🔗 Determina si estamos en modo "Creación" (si hubo error 404 o no hay datos cargados).
  const modoCreacion = isError || (!emisor && !isLoading);

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Configuración del Emisor</h1>
          <p className="text-sm text-gray-500 mt-1">
            {modoCreacion 
              ? 'No se ha encontrado una configuración activa. Complete todos los campos para crearla.' 
              : 'Datos fiscales configurados de la empresa emisora. Todos los campos son obligatorios.'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-8">
        
        {/* 📌 SECCIÓN 1: DATOS FISCALES PRINCIPALES */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Datos Fiscales Principales</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">NIT *</label>
              <input {...register('nit')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="0000-000000-000-0" />
              {errors.nit && <p className="text-red-500 text-xs mt-1">{errors.nit.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">NRC *</label>
              <input {...register('nrc')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="123456" />
              {errors.nrc && <p className="text-red-500 text-xs mt-1">{errors.nrc.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre o Razón Social *</label>
              <input {...register('nombre')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Comercial *</label>
              <input {...register('nombre_comercial')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              {errors.nombre_comercial && <p className="text-red-500 text-xs mt-1">{errors.nombre_comercial.message}</p>}
            </div>
          </div>
        </div>

        {/* 📌 SECCIÓN 2: ACTIVIDAD ECONÓMICA */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Actividad Económica</h3>
          {catalogos?.['cat-019-actividad-economica'] ? (
            <ActividadEconomicaSelector 
              catalogData={catalogos['cat-019-actividad-economica']} 
              setValue={setValue} 
              watch={watch} 
              errors={errors} 
            />
          ) : (
            <p className="text-red-500 text-sm">No se pudo cargar el catálogo de actividades económicas.</p>
          )}
        </div>

        {/* 📌 SECCIÓN 3: DIRECCIÓN (CATÁLOGOS DE HACIENDA) */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Dirección (Catálogos de Hacienda)</h3>
          {catalogos?.['cat-008-distrito'] ? (
            <UbicacionSelector 
              catalogData={catalogos['cat-008-distrito']} 
              register={register} /* 🔗 Se pasa register para el campo de texto 'complemento' */
              setValue={setValue} 
              watch={watch} 
              errors={errors} 
            />
          ) : (
            <p className="text-red-500 text-sm">No se pudo cargar el catálogo de ubicaciones.</p>
          )}
        </div>

        {/* 📌 SECCIÓN 4: DATOS DE CONTACTO */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Datos de Contacto</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
              <input {...register('telefono')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="2222-3333" />
              {errors.telefono && <p className="text-red-500 text-xs mt-1">{errors.telefono.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Correo Fiscal (para DTE) *</label>
              <input type="email" {...register('correo')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              {errors.correo && <p className="text-red-500 text-xs mt-1">{errors.correo.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Correo Interno (notificaciones) *</label>
              <input type="email" {...register('correo_interno')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
              {errors.correo_interno && <p className="text-red-500 text-xs mt-1">{errors.correo_interno.message}</p>}
            </div>
          </div>
        </div>

        {/* 📌 SECCIÓN 5: CÓDIGOS INTERNOS */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Códigos Internos del Contribuyente</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Código de Establecimiento *</label>
              <input {...register('cod_estable')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: 0001" />
              {errors.cod_estable && <p className="text-red-500 text-xs mt-1">{errors.cod_estable.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Código de Punto de Venta *</label>
              <input {...register('cod_punto_venta')} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: PV-001" />
              {errors.cod_punto_venta && <p className="text-red-500 text-xs mt-1">{errors.cod_punto_venta.message}</p>}
            </div>
          </div>
        </div>

        {/* 📌 BOTONES DE ACCIÓN */}
        <div className="flex justify-end gap-4 pt-6 border-t">
          <button 
            type="button" 
            onClick={() => window.history.back()}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            disabled={isCreating || isUpdating}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
          >
            {isCreating || isUpdating ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
              </>
            ) : (
              modoCreacion ? 'Crear Configuración' : 'Actualizar Configuración'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}