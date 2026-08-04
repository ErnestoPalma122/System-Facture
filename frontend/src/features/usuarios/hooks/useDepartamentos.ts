// frontend/src/features/usuarios/hooks/useDepartamentos.ts
import { useQuery } from '@tanstack/react-query';
import { usuarioApi } from '../api/usuario_api';

// 📌 HOOK SIMPLE DE CONSULTA
// Obtiene la lista estática de departamentos para llenar el dropdown del formulario.
export function useDepartamentos() {
  return useQuery({
    queryKey: ['departamentos'],
    queryFn: usuarioApi.listarDepartamentos,
  });
}
