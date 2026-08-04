// frontend/src/features/ingreso_mercaderia/components/IngresoMercaderiaTabla.tsx

import { useQuery } from '@tanstack/react-query';
import { ingresoApi } from '../api/ingreso_api';

export function IngresoMercaderiaTabla() {
  // 📌 CONSULTA REACT QUERY PARA HISTORIAL RECIENTE
  // Se configura para reintentar solo 1 vez en caso de error (ej. 404 temporal o fallo de red).
  const { data: ingresos = [], isLoading, isError } = useQuery({
    queryKey: ['ingresos-recientes'],
    queryFn: ingresoApi.listarIngresos,
    retry: 1, 
  });

  // 📌 ESTADO DE CARGA VISUAL
  if (isLoading) return <div className="p-8 text-center text-gray-600">Cargando ingresos recientes...</div>;

  // 📌 MANEJO ELEGANTE DE ERRORES
  // Evita que la app se rompa si el endpoint del backend aún no está desplegado o falla.
  if (isError) {
    return (
      <div className="p-8 text-center text-red-600 bg-red-50 rounded-xl border border-red-200 mt-6">
        <p className="font-semibold">⚠️ No se pudieron cargar los ingresos recientes.</p>
        <p className="text-sm text-red-500 mt-1">Verifica que el endpoint del backend esté activo o vuelve a intentarlo más tarde.</p>
      </div>
    );
  }

  return (
    // 📌 CONTENEDOR PRINCIPAL DE LA TABLA
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-bold text-gray-800">Últimos Ingresos Registrados</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">DTE</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Proveedor ID</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Fecha</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Estado</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {ingresos.length > 0 ? (
              // 📌 MAPEO DE LA LISTA CON FORMATO DE FECHA LEGIBLE
              ingresos.map((ing) => (
                <tr key={ing.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{ing.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ing.dte}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{ing.proveedor_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {new Date(ing.fecha).toLocaleDateString('es-ES', { 
                      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                    })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 font-medium">
                      Procesado
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              // 📌 ESTADO VACÍO (EMPTY STATE)
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  <p className="text-lg font-medium">No hay ingresos registrados recientemente.</p>
                  <p className="text-sm text-gray-400 mt-1">Los nuevos ingresos aparecerán aquí automáticamente.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}