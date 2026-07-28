import { useQuery } from '@tanstack/react-query';
import { usuarioApi } from '../api/usuario_api';

export function useDepartamentos() {
  return useQuery({
    queryKey: ['departamentos'],
    queryFn: usuarioApi.listarDepartamentos,
  });
}