//frontend\src\features\usuarios\hooks\useUsuarios.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usuarioApi, UsuarioFormData } from '../api/usuario_api';

export function useUsuarios(busqueda?: string) {
  const queryClient = useQueryClient();

  const { data: usuarios = [], isLoading } = useQuery({
    queryKey: ['usuarios', busqueda],
    queryFn: () => usuarioApi.listarUsuarios(busqueda),
  });

  const mutationCrear = useMutation({
    mutationFn: (data: UsuarioFormData) => usuarioApi.crearUsuario(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UsuarioFormData }) => 
      usuarioApi.actualizarUsuario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });

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