// frontend\src\features\proveedores\hooks\useProveedores.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { proveedorApi, ProveedorFormData } from '../api/proveedor_api';

// 📌 HOOK PERSONALIZADO DE GESTIÓN DE PROVEEDORES
// Encapsula toda la lógica de estado del servidor (React Query) para el módulo de proveedores.
// Recibe un 'searchTerm' opcional para permitir búsquedas dinámicas en tiempo real.
export function useProveedores(searchTerm: string = '') {
  // 🔗 Instancia del cliente de React Query para manipular la caché manualmente (invalidación).
  const queryClient = useQueryClient();

  // 📌 1. CONSULTA: LISTAR PROVEEDORES
  const { data: proveedores = [], isLoading, isError } = useQuery({
    // ⚠️ CLAVE DE CACHÉ CRÍTICA: Incluir 'searchTerm' en el array del queryKey asegura que 
    // React Query cachee por separado los resultados de "sin búsqueda" y "con búsqueda".
    // Si el usuario busca "ABC" y luego "XYZ", React Query no mezclará los resultados.
    queryKey: ['proveedores', searchTerm],
    
    // 🔗 Ejecuta la función de la API. Si searchTerm está vacío, pasa 'undefined' para traer la lista completa.
    queryFn: () => proveedorApi.listar(undefined, searchTerm || undefined),
  });

  // 📌 2. MUTACIÓN: CREAR PROVEEDOR
  const mutationCrear = useMutation({
    mutationFn: (data: ProveedorFormData) => proveedorApi.crear(data),
    onSuccess: () => {
      // 🔗 INVALIDACIÓN DE CACHÉ: Al invalidar la clave base ['proveedores'], React Query 
      // marca como obsoletas TODAS las variantes de esa consulta (incluyendo las que tienen searchTerm).
      // Esto fuerza una recarga automática de la tabla para mostrar el nuevo registro inmediatamente.
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  // 📌 3. MUTACIÓN: ACTUALIZAR PROVEEDOR
  const mutationActualizar = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProveedorFormData }) => 
      proveedorApi.actualizar(id, data),
    onSuccess: () => {
      // Misma lógica de invalidación: actualiza la lista tras una edición exitosa.
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  // 📌 4. MUTACIÓN: ELIMINAR (DESACTIVAR) PROVEEDOR
  const mutationEliminar = useMutation({
    mutationFn: (id: number) => proveedorApi.eliminar(id),
    onSuccess: () => {
      // Misma lógica de invalidación: actualiza la lista tras una desactivación exitosa.
      queryClient.invalidateQueries({ queryKey: ['proveedores'] });
    },
  });

  // 📌 RETORNO DEL HOOK
  // Expone los datos, estados de carga y las funciones de mutación al componente.
  // ⚠️ NOTA DE DISEÑO: Se exponen 'mutateAsync' en lugar de 'mutate'. 
  // Esto permite que el componente padre use 'await' y bloques 'try/catch' para manejar 
  // los errores de red o validación del backend de forma limpia y controlada.
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