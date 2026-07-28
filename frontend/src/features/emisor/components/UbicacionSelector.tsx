//frontend\src\features\emisor\components\UbicacionSelector.tsx
import { UseFormRegister, UseFormSetValue, UseFormWatch, FieldErrors } from 'react-hook-form';
import { EmisorFormData } from '../api/emisor_api';

interface UbicacionSelectorProps {
  catalogData: any; // Datos de "cat-008-distrito"
  register: UseFormRegister<EmisorFormData>; // <-- AGREGADO
  setValue: UseFormSetValue<EmisorFormData>;
  watch: UseFormWatch<EmisorFormData>;
  errors: FieldErrors<EmisorFormData>;
}

export function UbicacionSelector({ catalogData, register, setValue, watch, errors }: UbicacionSelectorProps) {
  const codDepto = watch('direccion.cod_departamento');
  const codMun = watch('direccion.cod_municipio');

  // 1. Obtener lista de departamentos
  const departamentos = catalogData ? Object.entries(catalogData).map(([key, value]: [string, any]) => ({
    codigo: key,
    nombre: value.nombre
  })) : [];

  // 2. Obtener lista de municipios del departamento seleccionado
  const municipios = codDepto && catalogData?.[codDepto]?.municipios 
    ? Object.entries(catalogData[codDepto].municipios).map(([key, value]: [string, any]) => ({
        codigo: key,
        nombre: value.nombre
      }))
    : [];

  // 3. Obtener lista de distritos del municipio seleccionado
  const distritos = codDepto && codMun && catalogData?.[codDepto]?.municipios?.[codMun]?.distritos
    ? catalogData[codDepto].municipios[codMun].distritos
    : [];

  const handleDeptoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const key = e.target.value;
    const depto = departamentos.find((d: any) => d.codigo === key);
    setValue('direccion.cod_departamento', key);
    setValue('direccion.desc_departamento', depto?.nombre || '');
    // Limpiar dependencias
    setValue('direccion.cod_municipio', '');
    setValue('direccion.desc_municipio', '');
    setValue('direccion.cod_distrito', '');
    setValue('direccion.desc_distrito', '');
  };

  const handleMunChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const key = e.target.value;
    const mun = municipios.find((m: any) => m.codigo === key);
    setValue('direccion.cod_municipio', key);
    setValue('direccion.desc_municipio', mun?.nombre || '');
    // Limpiar dependencias
    setValue('direccion.cod_distrito', '');
    setValue('direccion.desc_distrito', '');
  };

  const handleDistChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const dist = distritos.find((d: any) => d.codigo === e.target.value);
    setValue('direccion.cod_distrito', dist?.codigo || '');
    setValue('direccion.desc_distrito', dist?.nombre || '');
  };

  const selectClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white";
  const errorClass = "text-red-500 text-xs mt-1";

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Departamento */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Departamento *</label>
        <select 
          onChange={handleDeptoChange} 
          value={codDepto} 
          className={`${selectClass} ${errors.direccion?.cod_departamento ? 'border-red-500' : ''}`}
        >
          <option value="">Seleccione...</option>
          {departamentos.map((d: any) => (
            <option key={d.codigo} value={d.codigo}>{d.nombre}</option>
          ))}
        </select>
        {errors.direccion?.cod_departamento && <p className={errorClass}>{errors.direccion.cod_departamento.message}</p>}
      </div>

      {/* Municipio */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Municipio *</label>
        <select 
          onChange={handleMunChange} 
          value={codMun} 
          disabled={!codDepto}
          className={`${selectClass} ${!codDepto ? 'bg-gray-100 cursor-not-allowed' : ''} ${errors.direccion?.cod_municipio ? 'border-red-500' : ''}`}
        >
          <option value="">Seleccione...</option>
          {municipios.map((m: any) => (
            <option key={m.codigo} value={m.codigo}>{m.nombre}</option>
          ))}
        </select>
        {errors.direccion?.cod_municipio && <p className={errorClass}>{errors.direccion.cod_municipio.message}</p>}
      </div>

      {/* Distrito */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Distrito *</label>
        <select 
          onChange={handleDistChange} 
          value={watch('direccion.cod_distrito')} 
          disabled={!codMun}
          className={`${selectClass} ${!codMun ? 'bg-gray-100 cursor-not-allowed' : ''} ${errors.direccion?.cod_distrito ? 'border-red-500' : ''}`}
        >
          <option value="">Seleccione...</option>
          {distritos.map((d: any) => (
            <option key={d.codigo} value={d.codigo}>{d.nombre}</option>
          ))}
        </select>
        {errors.direccion?.cod_distrito && <p className={errorClass}>{errors.direccion.cod_distrito.message}</p>}
      </div>

      {/* Complemento */}
      <div className="md:col-span-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Complemento de Dirección *</label>
        <input 
          {...register('direccion.complemento')} 
          className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none ${errors.direccion?.complemento ? 'border-red-500' : ''}`} 
          placeholder="Calle, avenida, casa, edificio, etc." 
        />
        {errors.direccion?.complemento && <p className={errorClass}>{errors.direccion.complemento.message}</p>}
      </div>
    </div>
  );
}