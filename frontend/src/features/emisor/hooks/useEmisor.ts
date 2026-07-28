import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { emisorApi, EmisorFormData } from '../api/emisor_api';

export function useEmisor() {
  const queryClient = useQueryClient();

  const { data: emisor, isLoading, isError, error } = useQuery({
    queryKey: ['emisor'],
    queryFn: emisorApi.obtener,
    retry: false, // No reintentar si es 404 (significa que no está configurado)
  });

  const mutationCrear = useMutation({
    mutationFn: (data: EmisorFormData) => emisorApi.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emisor'] });
    },
  });

  const mutationActualizar = useMutation({
    mutationFn: (data: EmisorFormData) => emisorApi.actualizar(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emisor'] });
    },
  });

  return {
    emisor,
    isLoading,
    isError, // Será true si el backend responde 404 (No configurado)
    error,
    crearEmisor: mutationCrear.mutateAsync,
    actualizarEmisor: mutationActualizar.mutateAsync,
    isCreating: mutationCrear.isPending,
    isUpdating: mutationActualizar.isPending,
  };
}