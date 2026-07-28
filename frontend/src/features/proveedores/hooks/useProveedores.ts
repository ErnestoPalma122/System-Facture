import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { proveedorApi, ProveedorFormData } from '../api/proveedor_api';

export function useProveedores(searchTerm: string = '') {
  const queryClient = useQueryClient();

  const { data: proveedores = [], isLoading, isError } = useQuery({
    queryKey: ['proveedores', searchTerm],
    queryFn: () => proveedorApi.listar(undefined, searchTerm || undefined),
  });

  const mutationCrear = useMutation({
    mutationFn: (data: ProveedorFormData) => proveedorApi.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProveedorFormData }) => 
      proveedorApi.actualizar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  const mutationEliminar = useMutation({
    mutationFn: (id: number) => proveedorApi.eliminar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  return {
    proveedores,
    isLoading,
    isError,
    crearProveedor: mutationCrear.mutateAsync,
    actualizarProveedor: mutationActualizar.mutateAsync,
    eliminarProveedor: mutationEliminar.mutateAsync,
    isCreating: mutationCrear.isPending,
    isUpdating: mutationActualizar.isPending,
    isDeleting: mutationEliminar.isPending,
  };
}