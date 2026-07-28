//frontend\src\features\productos\hooks\useProductos.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productoApi, ProductoFormData } from '../api/producto_api';

export function useProductos() {
  const queryClient = useQueryClient();

  const { data: productos = [], isLoading: isLoadingProductos } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productoApi.listarProductos(true),
  });

  const { data: categorias = [], isLoading: isLoadingCategorias } = useQuery({
    queryKey: ['categorias'],
    queryFn: productoApi.listarCategorias,
  });

  const mutationCrear = useMutation({
    mutationFn: (data: ProductoFormData) => productoApi.crearProducto(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoFormData }) => 
      productoApi.actualizarProducto(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  return {
    productos,
    categorias,
    isLoading: isLoadingProductos || isLoadingCategorias,
    crearProducto: mutationCrear.mutateAsync,
    actualizarProducto: mutationActualizar.mutateAsync,
    isCreating: mutationCrear.isPending,
    isUpdating: mutationActualizar.isPending,
  };
}