// frontend/src/features/bodegas/hooks/useBodegas.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bodegaApi, BodegaCreate, BodegaUpdate } from '../api/bodega_api';

// 📌 HOOK PERSONALIZADO DE GESTIÓN DE BODEGAS
// Encapsula toda la lógica de estado del servidor (React Query) para el módulo de bodegas.
export function useBodegas() {
  // 🔗 Instancia del cliente de React Query para manipular la caché manualmente (invalidación).
  const queryClient = useQueryClient();

  // 📌 1. CONSULTA: LISTAR BODEGAS
  // Obtiene la lista de bodegas. 
  // ⚠️ 'data: bodegas = []' asigna un array vacío por defecto para evitar errores de 'undefined' 
  // en el componente si se intenta hacer '.map' antes de que lleguen los datos.
  const { data: bodegas = [], isLoading, isError, error } = useQuery({
    queryKey: ['bodegas'],
    queryFn: bodegaApi.listar,
  });

  // 📌 2. MUTACIÓN: CREAR BODEGA
  const mutationCrear = useMutation({
    mutationFn: (data: BodegaCreate) => bodegaApi.crear(data),
    onSuccess: () => {
      // 🔗 INVALIDACIÓN DE CACHÉ: Fuerza a React Query a volver a ejecutar la consulta ['bodegas'] 
      // para que la tabla se actualice automáticamente con el nuevo registro sin recargar la página.
      queryClient.invalidateQueries({ queryKey: ['bodegas'] });
    },
  });

  // 📌 3. MUTACIÓN: ACTUALIZAR BODEGA
  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: BodegaUpdate }) => 
      bodegaApi.actualizar(id, data),
    onSuccess: () => {
      // 🔗 Misma lógica de invalidación: actualiza la lista tras una edición exitosa.
      queryClient.invalidateQueries({ queryKey: ['bodegas'] });
    },
  });

  // 📌 RETORNO DEL HOOK
  // Expone los datos, estados de carga y las funciones de mutación al componente.
  // ⚠️ Se exponen 'mutateAsync' en lugar de 'mutate' para permitir el uso de 'await' 
  // dentro del 'onSubmit' del formulario y manejar los bloques try/catch correctamente.
  return {
    bodegas,
    isLoading,
    isError,
    error,
    crearBodega: mutationCrear.mutateAsync,
    actualizarBodega: mutationActualizar.mutateAsync,
    isCreating: mutationCrear.isPending,
    isUpdating: mutationActualizar.isPending,
  };
}