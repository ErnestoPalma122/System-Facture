import { useQuery } from '@tanstack/react-query';
import { usuarioApi } from '../api/usuario_api';

export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: usuarioApi.listarRoles,
  });
}