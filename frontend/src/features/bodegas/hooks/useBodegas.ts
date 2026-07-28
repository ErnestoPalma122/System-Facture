// frontend/src/features/bodegas/hooks/useBodegas.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bodegaApi, BodegaCreate, BodegaUpdate } from '../api/bodega_api';

export function useBodegas() {
  const queryClient = useQueryClient();

  // 1. Listar bodegas
  const { data: bodegas = [], isLoading, isError, error } = useQuery({
    queryKey: ['bodegas'],
    queryFn: bodegaApi.listar,
  });

  // 2. Crear bodega
  const mutationCrear = useMutation({
    mutationFn: (data: BodegaCreate) => bodegaApi.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bodegas'] });
    },
  });

  // 3. Actualizar bodega
  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: BodegaUpdate }) => 
      bodegaApi.actualizar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bodegas'] });
    },
  });

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