// frontend/src/features/usuarios/hooks/useUsuarios.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usuarioApi, UsuarioFormData } from '../api/usuario_api';

// 📌 HOOK PRINCIPAL DE GESTIÓN DE USUARIOS
export function useUsuarios(busqueda?: string) {
  const queryClient = useQueryClient();

  // 📌 CONSULTA: LISTAR USUARIOS
  // ⚠️ CRÍTICO: 'busqueda' se incluye en el queryKey. Esto asegura que React Query 
  // cachee por separado los resultados de "sin búsqueda" y "con búsqueda".
  const { data: usuarios = [], isLoading } = useQuery({
    queryKey: ['usuarios', busqueda],
    queryFn: () => usuarioApi.listarUsuarios(busqueda),
  });

  // 📌 MUTACIÓN: CREAR
  const mutationCrear = useMutation({
    mutationFn: (data: UsuarioFormData) => usuarioApi.crearUsuario(data),
    onSuccess: () => {
      // Invalida la caché para refrescar la tabla automáticamente
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  // 📌 MUTACIÓN: ACTUALIZAR
  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UsuarioFormData }) => 
      usuarioApi.actualizarUsuario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  // 📌 MUTACIÓN: ELIMINAR
  const mutationEliminar = useMutation({
    mutationFn: (id: number) => usuarioApi.eliminarUsuario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  return {
    usuarios,
    isLoading,
    crearUsuario: mutationCrear.mutateAsync,
    actualizarUsuario: mutationActualizar.mutateAsync,
    eliminarUsuario: mutationEliminar.mutateAsync,
    isCreating: mutationCrear.isPending,
    isUpdating: mutationActualizar.isPending,
    isDeleting: mutationEliminar.isPending,
  };
}