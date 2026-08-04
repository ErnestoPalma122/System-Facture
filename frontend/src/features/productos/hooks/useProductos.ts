//frontend\src\features\productos\hooks\useProductos.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productoApi, ProductoFormData } from '../api/producto_api';

// DOCUMENTACIÓN: Hook personalizado que centraliza toda la lógica de estado asíncrono (React Query)
// para el módulo de productos. Abstrae las llamadas a la API del componente visual.
export function useProductos() {
  const queryClient = useQueryClient();

  // DOCUMENTACIÓN: Query para obtener la lista de productos activos. Se cachea automáticamente.
  const { data: productos = [], isLoading: isLoadingProductos } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productoApi.listarProductos(true),
  });

  // DOCUMENTACIÓN: Query para obtener la lista de categorías. Se cachea automáticamente.
  const { data: categorias = [], isLoading: isLoadingCategorias } = useQuery({
    queryKey: ['categorias'],
    queryFn: productoApi.listarCategorias,
  });

  // DOCUMENTACIÓN: Mutación para crear un nuevo producto.
  // onSuccess invalida la caché de 'productos' para que la tabla se actualice automáticamente con el nuevo registro.
  const mutationCrear = useMutation({
    mutationFn: (data: ProductoFormData) => productoApi.crearProducto(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  // DOCUMENTACIÓN: Mutación para actualizar un producto existente.
  // También invalida la caché para reflejar los cambios inmediatamente en la UI.
  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoFormData }) => 
      productoApi.actualizarProducto(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
  });

  // DOCUMENTACIÓN: Exposición de datos, estados de carga y funciones de mutación al componente que use este hook.
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