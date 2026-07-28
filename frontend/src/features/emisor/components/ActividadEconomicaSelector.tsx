import { useState, useEffect, useRef } from 'react';
import { UseFormSetValue, UseFormWatch, FieldErrors } from 'react-hook-form';
import { EmisorFormData } from '../api/emisor_api';

interface ActividadSelectorProps {
  catalogData: any[];
  setValue: UseFormSetValue<EmisorFormData>;
  watch: UseFormWatch<EmisorFormData>;
  errors: FieldErrors<EmisorFormData>;
}

export function ActividadEconomicaSelector({ catalogData, setValue, watch, errors }: ActividadSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef<HTMLDivElement>(null);

  const codActual = watch('cod_actividad');

  // 1. Sincronizar si viene con datos (modo edición)
  useEffect(() => {
    if (codActual && catalogData) {
      const item = catalogData.find((a: any) => a.codigo === codActual);
      if (item) {
        setSearchTerm(`${item.codigo} - ${item.valor}`);
      }
    }
  }, [codActual, catalogData]);

  // 2. Filtrar resultados en tiempo real (limitado a 50 para rendimiento)
  const filtered = catalogData.filter((item: any) => 
    item.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.valor.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, 50);

  // 3. Al hacer clic en una opción, llenar los DOS campos por separado
  const handleSelect = (item: any) => {
    setValue('cod_actividad', item.codigo, { shouldValidate: true });
    setValue('desc_actividad', item.valor, { shouldValidate: true });
    setSearchTerm(`${item.codigo} - ${item.valor}`);
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
    // Si el usuario borra todo, limpiamos los campos ocultos
    if (e.target.value.trim() === '') {
      setValue('cod_actividad', '');
      setValue('desc_actividad', '');
    }
  };

  // 4. Cerrar el desplegable si se hace clic fuera de él
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
      
      {/* Input de búsqueda */}
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

      {/* Lista desplegable filtrada */}
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
      
      {/* Feedback visual de lo que se guardará en la BD */}
      {codActual && (
        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs text-green-800 flex gap-4">
          <span>💾 Código: <strong>{watch('cod_actividad')}</strong></span>
          <span>💾 Descripción: <strong>{watch('desc_actividad')}</strong></span>
        </div>
      )}
    </div>
  );
}