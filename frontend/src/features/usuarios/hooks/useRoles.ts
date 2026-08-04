// frontend/src/features/usuarios/hooks/useRoles.ts
import { useQuery } from '@tanstack/react-query';
import { usuarioApi } from '../api/usuario_api';

// 📌 HOOK SIMPLE DE CONSULTA
// Obtiene la lista estática de roles para llenar el dropdown del formulario.
export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: usuarioApi.listarRoles,
  });
}