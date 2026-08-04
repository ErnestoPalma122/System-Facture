// frontend/src/features/emisor/components/ActividadEconomicaSelector.tsx

import { useState, useEffect, useRef } from 'react';
import { UseFormSetValue, UseFormWatch, FieldErrors } from 'react-hook-form';
import { EmisorFormData } from '../api/emisor_api';

// 📌 INTERFAZ DE PROPS
// Recibe los datos del catálogo y las funciones de React Hook Form para manipular el estado del formulario padre.
interface ActividadSelectorProps {
  catalogData: any[];
  setValue: UseFormSetValue<EmisorFormData>;
  watch: UseFormWatch<EmisorFormData>;
  errors: FieldErrors<EmisorFormData>;
}

export function ActividadEconomicaSelector({ catalogData, setValue, watch, errors }: ActividadSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  // 🔗 useRef se usa para detectar clics fuera del componente y cerrar el dropdown.
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Observa el valor actual del código de actividad en el formulario
  const codActual = watch('cod_actividad');

  // 📌 1. SINCRONIZACIÓN INICIAL (MODO EDICIÓN)
  // Si el formulario se carga con datos existentes, busca el elemento en el catálogo 
  // y pre-llena el input de búsqueda con "Código - Descripción" para que el usuario lo vea.
  useEffect(() => {
    if (codActual && catalogData) {
      const item = catalogData.find((a: any) => a.codigo === codActual);
      if (item) {
        setSearchTerm(`${item.codigo} - ${item.valor}`);
      }
    }
  }, [codActual, catalogData]);

  // 📌 2. FILTRADO EN TIEMPO REAL
  // Filtra por código o por nombre. 
  // ⚠️ .slice(0, 50) es una optimización de rendimiento crítica: evita renderizar miles de nodos DOM si el catálogo es gigante.
  const filtered = catalogData.filter((item: any) => 
    item.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.valor.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, 50);

  // 📌 3. SELECCIÓN DE ELEMENTO
  const handleSelect = (item: any) => {
    // Actualiza AMBOS campos en el formulario padre (código y descripción)
    setValue('cod_actividad', item.codigo, { shouldValidate: true });
    setValue('desc_actividad', item.valor, { shouldValidate: true });
    setSearchTerm(`${item.codigo} - ${item.valor}`);
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
    // Si el usuario borra el texto manualmente, limpiamos los campos ocultos del formulario para evitar datos inconsistentes.
    if (e.target.value.trim() === '') {
      setValue('cod_actividad', '');
      setValue('desc_actividad', '');
    }
  };

  // 📌 4. DETECCIÓN DE CLIC FUERA (CLICK OUTSIDE)
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  return (
    <div className="relative" ref={wrapperRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">Actividad Económica *</label>
      
      {/* Input de búsqueda principal */}
      <input
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        onFocus={() => setIsOpen(true)}
        placeholder="Escribe código o nombre (ej: 6201 o programacion)..."
        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all ${
          errors.cod_actividad || errors.desc_actividad ? 'border-red-500 bg-red-50' : 'border-gray-300'
        }`}
      />

      {/* 📌 LISTA DESPLEGABLE FILTRADA */}
      {isOpen && searchTerm.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
          {filtered.length > 0 ? (
            filtered.map((item: any) => (
              <button
                key={item.codigo}
                type="button"
                onClick={() => handleSelect(item)}
                className="w-full text-left px-4 py-2.5 hover:bg-blue-50 text-sm border-b border-gray-100 last:border-0 transition-colors flex gap-2"
              >
                <span className="font-bold text-blue-700 min-w-[60px]">{item.codigo}</span>
                <span className="text-gray-700">{item.valor}</span>
              </button>
            ))
          ) : (
            <div className="px-4 py-3 text-sm text-gray-500 text-center">
              No se encontraron coincidencias
            </div>
          )}
        </div>
      )}

      {/* Mensajes de error de Zod */}
      {(errors.cod_actividad || errors.desc_actividad) && (
        <p className="text-red-500 text-xs mt-1">
          {errors.cod_actividad?.message || errors.desc_actividad?.message}
        </p>
      )}
      
      {/* 📌 FEEDBACK VISUAL DE CONFIRMACIÓN */}
      {/* Muestra al usuario qué valores exactos se guardarán en la BD, generando confianza en la selección. */}
      {codActual && (
        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs text-green-800 flex gap-4">
          <span>💾 Código: <strong>{watch('cod_actividad')}</strong></span>
          <span>💾 Descripción: <strong>{watch('desc_actividad')}</strong></span>
        </div>
      )}
    </div>
  );
}