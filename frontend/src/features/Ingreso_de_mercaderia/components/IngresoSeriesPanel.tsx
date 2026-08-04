// frontend/src/features/ingreso_mercaderia/components/IngresoSeriesPanel.tsx

import { useRef } from 'react';
import * as XLSX from 'xlsx'; // 🔗 Librería para parsear archivos Excel/CSV en el navegador

interface IngresoSeriesPanelProps {
  productoId: number;
  bodegaId: number;
  productoNombre?: string;
  bodegaNombre?: string;
  seriesTexto: string;
  onSeriesTextoChange: (texto: string) => void;
}

export function IngresoSeriesPanel({
  productoId,
  bodegaId,
  productoNombre,
  bodegaNombre,
  seriesTexto,
  onSeriesTextoChange,
}: IngresoSeriesPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scanInputRef = useRef<HTMLInputElement>(null);

  // 📌 1. PROCESADOR DE TEXTO
  // Convierte una cadena de texto (con saltos de línea o comas) en un array limpio de series.
  function procesarSeriesTexto(texto: string): string[] {
    return texto.split(/[\n,]+/).map(s => s.trim()).filter(s => s.length > 0);
  }

  // 📌 2. VALIDADOR DE SERIES
  // Aplica reglas de negocio: solo alfanuméricos/guiones y detección de duplicados.
  function validarSeries(series: string[]): { validas: string[]; errores: string[] } {
    const validas: string[] = [];
    const errores: string[] = [];
    const serieRegex = /^[a-zA-Z0-9\-]+$/;
    // 🔗 Uso de Set para búsqueda de duplicados en O(1), mucho más eficiente que .includes() en arrays grandes.
    const vistas = new Set<string>();

    series.forEach(serie => {
      if (!serieRegex.test(serie)) {
        errores.push(`"${serie}" (caracteres especiales)`);
        return;
      }
      if (vistas.has(serie.toUpperCase())) {
        errores.push(`"${serie}" (duplicada)`);
        return;
      }
      vistas.add(serie.toUpperCase());
      validas.push(serie);
    });

    return { validas, errores };
  }

  const seriesActuales = procesarSeriesTexto(seriesTexto);
  const seriesCount = seriesActuales.length;

  // 📌 3. MANEJO DE ESCÁNER (INPUT DE TEXTO)
  // Simula el comportamiento de un lector de código de barras USB/Bluetooth (que envía un "Enter" al final).
  const handleScanInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const scannedValue = e.target.value.trim();
    
    if (scannedValue && productoId && bodegaId) {
      const { validas, errores } = validarSeries([scannedValue]);
      
      if (errores.length > 0) {
        alert(`⚠️ Serie inválida: ${errores[0]}`);
      } else {
        const serieValida = validas[0];
        const seriesExistentes = procesarSeriesTexto(seriesTexto);
        // Verificación extra de mayúsculas/minúsculas
        if (!seriesExistentes.some(s => s.toUpperCase() === serieValida.toUpperCase())) {
          const nuevaSerie = seriesTexto ? `${seriesTexto}\n${serieValida}` : serieValida;
          onSeriesTextoChange(nuevaSerie);
        }
      }
    }
    // ⚠️ CRÍTICO: Limpia el input inmediatamente para que el siguiente escaneo funcione, 
    // incluso si el valor escaneado es el mismo que el anterior.
    e.target.value = '';
  };

  // 📌 4. MANEJO DE CARGA DE ARCHIVO (EXCEL/CSV)
  const handleFileUpload = (file: File) => {
    if (!productoId || !bodegaId) {
      alert("⚠️ Selecciona Producto y Bodega primero.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target?.result as ArrayBuffer);
      const workbook = XLSX.read(data, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      // 🔗 Convierte la hoja de cálculo en un array plano de strings
      const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 }) as string[][];
      
      const seriesExtraidas = jsonData.flat().map(s => String(s).trim()).filter(s => s.length > 0);
      const { validas, errores } = validarSeries(seriesExtraidas);
      
      if (errores.length > 0) {
        // Muestra solo los primeros 5 errores para no saturar el alert
        alert(`⚠️ El archivo contiene errores:\n${errores.slice(0, 5).join('\n')}${errores.length > 5 ? '\n...' : ''}`);
        return;
      }

      const seriesExistentes = procesarSeriesTexto(seriesTexto);
      // Filtra las series del archivo que ya están en el textarea
      const duplicados = validas.filter(s => 
        seriesExistentes.some(ex => ex.toUpperCase() === s.toUpperCase())
      );

      if (duplicados.length > 0) {
        alert(`⚠️ ${duplicados.length} series del archivo ya existen en la lista.`);
      }

      // Solo agrega las series que son nuevas
      const nuevas = validas.filter(s => 
        !seriesExistentes.some(ex => ex.toUpperCase() === s.toUpperCase())
      );

      if (nuevas.length > 0) {
        const textoActual = seriesTexto || '';
        const textoNuevo = textoActual ? `${textoActual}\n${nuevas.join('\n')}` : nuevas.join('\n');
        onSeriesTextoChange(textoNuevo);
      }
      
      // Limpia el input file para permitir subir el mismo archivo de nuevo si es necesario
      if (fileInputRef.current) fileInputRef.current.value = '';
    };
    reader.readAsArrayBuffer(file);
  };

  const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <div className="border-t pt-4">
      <h3 className="text-md font-semibold text-gray-700 mb-3">📦 Ingreso de Series (Objetos Vivos)</h3>
      
      {/* 📌 INDICADOR DE CONTEXTO */}
      {productoId && bodegaId && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-sm text-green-800">
            ✅ Producto: <strong>{productoNombre}</strong> | Bodega: <strong>{bodegaNombre}</strong>
          </p>
          <p className="text-xs text-green-600 mt-1">
            Usa cualquiera de los tres métodos para agregar series. Solo se permiten letras, números y guiones.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        {/* 📌 MÉTODO 1: ESCÁNER */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <label className={labelClass}>📷 Escáner de Series (Lector USB/Bluetooth)</label>
          <input 
            ref={scanInputRef}
            type="text"
            onChange={handleScanInput}
            disabled={!productoId || !bodegaId}
            className={`${inputClass} ${(!productoId || !bodegaId) ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
            placeholder="Escanea una serie (Enter agrega automáticamente)"
            autoComplete="off"
          />
          <p className="text-xs text-blue-600 mt-1">El lector debe enviar Enter al final. Se agrega automáticamente.</p>
        </div>

        {/* 📌 MÉTODO 2: ARCHIVO EXCEL/CSV */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <label className={labelClass}>📁 Cargar desde Excel/CSV</label>
          <input 
            type="file" 
            accept=".xlsx, .xls, .csv" 
            ref={fileInputRef}
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
            disabled={!productoId || !bodegaId}
            className={`block w-full text-sm ${(!productoId || !bodegaId) ? 'text-gray-400 cursor-not-allowed' : 'text-gray-500'}`}
          />
          <p className="text-xs text-purple-600 mt-1">Columna A: una serie por fila</p>
        </div>
      </div>

      {/* 📌 MÉTODO 3: INGRESO MANUAL / PEGAR */}
      <div className="mb-4">
        <label className={labelClass}>✍️ Ingreso Manual (Pegar o Escribir)</label>
        <textarea 
          value={seriesTexto}
          onChange={(e) => onSeriesTextoChange(e.target.value)}
          disabled={!productoId || !bodegaId}
          className={`${inputClass} font-mono text-sm ${(!productoId || !bodegaId) ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
          rows={6}
          placeholder="SER001&#10;SER002&#10;SER003&#10;O separadas por coma: SER004, SER005, SER006"
        />
        <p className="text-xs text-gray-500 mt-1">Una serie por línea o separadas por coma</p>
      </div>

      {/* 📌 RESUMEN DE CANTIDAD */}
      <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div>
          <p className="text-sm text-gray-600">Series cargadas para este producto:</p>
          <p className={`text-2xl font-bold ${seriesCount > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
            {seriesCount} {seriesCount === 1 ? 'serie' : 'series'}
          </p>
        </div>
      </div>
    </div>
  );
}