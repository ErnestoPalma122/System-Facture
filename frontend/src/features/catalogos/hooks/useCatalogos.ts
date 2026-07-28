import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';

export function useCatalogos() {
  const { data: catalogos, isLoading, isError } = useQuery({
    queryKey: ['catalogos-unificados'],
    queryFn: async () => {
      const response = await api.get('/catalogos/unificados');
      return response.data;
    },
    staleTime: 1000 * 60 * 60, // Caché por 1 hora (los catálogos de Hacienda no cambian)
  });

  return { catalogos, isLoading, isError };
}