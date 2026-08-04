// frontend/src/features/emisor/hooks/useEmisor.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { emisorApi, EmisorFormData } from '../api/emisor_api';

// 📌 HOOK PERSONALIZADO DE GESTIÓN DEL EMISOR
export function useEmisor() {
  const queryClient = useQueryClient();

  // 📌 1. CONSULTA: OBTENER DATOS DEL EMISOR
  const { data: emisor, isLoading, isError, error } = useQuery({
    queryKey: ['emisor'],
    queryFn: emisorApi.obtener,
    // ⚠️ CONFIGURACIÓN CRÍTICA: retry: false
    // Si el backend devuelve 404 (No encontrado), NO debemos reintentar la petición. 
    // Un 404 es un estado válido que indica que el emisor aún no ha sido configurado.
    retry: false, 
  });

  // 📌 2. MUTACIÓN: CREAR EMISOR
  const mutationCrear = useMutation({
    mutationFn: (data: EmisorFormData) => emisorApi.crear(data),
    onSuccess: () => {
      // Invalida la caché para que la consulta 'emisor' se vuelva a ejecutar y obtenga los datos recién creados.
      queryClient.invalidateQueries({ queryKey: ['emisor'] });
    },
  });

  // 📌 3. MUTACIÓN: ACTUALIZAR EMISOR
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