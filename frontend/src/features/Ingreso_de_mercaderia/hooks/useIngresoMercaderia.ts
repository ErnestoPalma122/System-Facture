// frontend/src/features/ingreso_mercaderia/hooks/useIngresoMercaderia.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ingresoApi, IngresoMercaderiaFormData, ItemIngresoCreate } from '../api/ingreso_api';

// 📌 HOOK PERSONALIZADO DE GESTIÓN DE INGRESOS
export function useIngresoMercaderia() {
  const queryClient = useQueryClient();

  // 📌 CONSULTAS (QUERIES) PARA LLENAR DROPDOWNS
  // Se ejecutan en paralelo al montar el componente.
  const { data: estados = [] } = useQuery({
    queryKey: ['estados-ingreso'],
    queryFn: ingresoApi.listarEstadosIngreso,
  });

  const { data: proveedores = [] } = useQuery({
    queryKey: ['proveedores-activos'],
    queryFn: ingresoApi.listarProveedores,
  });

  const { data: productos = [] } = useQuery({
    queryKey: ['productos-activos'],
    queryFn: ingresoApi.listarProductos,
  });

  const { data: bodegas = [] } = useQuery({
    queryKey: ['bodegas-activas'],
    queryFn: ingresoApi.listarBodegas,
  });

  // 📌 MUTACIÓN PARA CREAR EL INGRESO
  const mutationCrear = useMutation({
    mutationFn: (data: IngresoMercaderiaFormData & { items: ItemIngresoCreate[] }) => 
      ingresoApi.crearIngreso(data),
    onSuccess: () => {
      // 🔗 INVALIDACIÓN DE CACHÉ MÚLTIPLE:
      // 1. Actualiza la tabla de ingresos recientes.
      queryClient.invalidateQueries({ queryKey: ['ingresos-recientes'] });
      // 2. ⚠️ CRÍTICO: Actualiza la lista de productos para reflejar los nuevos niveles de stock 
      // en caso de que otras partes de la app los estén mostrando.
      queryClient.invalidateQueries({ queryKey: ['productos-activos'] }); 
    },
  });

  return {
    estados,
    proveedores,
    productos,
    bodegas,
    crearIngreso: mutationCrear.mutateAsync,
    isCreating: mutationCrear.isPending,
  };
}