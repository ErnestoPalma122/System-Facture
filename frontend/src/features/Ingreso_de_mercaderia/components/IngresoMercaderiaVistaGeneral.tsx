// frontend/src/features/ingreso_mercaderia/components/IngresoMercaderiaVistaGeneral.tsx

import { useState } from 'react';
import { IngresoMercaderiaForm } from './IngresoMercaderiaForm';
import { IngresoMercaderiaTabla } from './IngresoMercaderiaTabla';

export function IngresoMercaderiaVistaGeneral() {
  // 📌 ESTADO LOCAL PARA EL MENSAJE DE ÉXITO GLOBAL
  const [mensajeExito, setMensajeExito] = useState('');

  // 📌 CALLBACK DE ÉXITO
  // Se ejecuta cuando el formulario hijo confirma que el guardado fue exitoso.
  const handleGuardado = () => {
    setMensajeExito('✅ Ingreso de mercadería creado y stock actualizado exitosamente. El formulario ha sido reiniciado.');
    
    // 🔗 Scroll suave hacia la parte superior para que el usuario vea el mensaje inmediatamente
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // ⚠️ Temporizador para ocultar el mensaje automáticamente y no saturar la UI
    setTimeout(() => setMensajeExito(''), 4000);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Ingreso de Mercadería</h1>
      </div>

      {/* 📌 BANNER DE CONFIRMACIÓN CONDICIONAL CON ANIMACIÓN */}
      {mensajeExito && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2 animate-pulse shadow-sm">
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {mensajeExito}
        </div>
      )}

      {/* 📌 RENDERIZADO DEL FORMULARIO */}
      {/* Se le pasa el callback para que pueda notificar el éxito y disparar la limpieza */}
      <IngresoMercaderiaForm onGuardado={handleGuardado} />
      
      {/* 📌 RENDERIZADO DE LA TABLA DE HISTORIAL */}
      {/* Se actualiza automáticamente gracias a la invalidación de caché de React Query en el hook de creación */}
      <IngresoMercaderiaTabla />
    </div>
  );
}