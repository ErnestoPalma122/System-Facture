// frontend/src/features/ingreso_mercaderia/api/ingreso_api.ts

import api from '@/lib/axios';
// 🔗 Importación de tipos de otros módulos para mantener la consistencia tipada en las respuestas
import { Proveedor } from '@/features/proveedores/api/proveedor_api';
import { Producto } from '@/features/productos/api/producto_api';
import { Bodega } from '@/features/bodegas/api/bodega_api';

// 📌 INTERFAZ: ESTADO DEL INGRESO
export interface EstadoIngreso {
  id: number;
  nombre_estado: string;
}

// 📌 INTERFAZ: ÍTEM DE INGRESO (DETALLE)
// Representa un producto específico, la bodega de destino y las series asociadas a este ingreso.
export interface ItemIngresoCreate {
  producto_id: number;
  bodega_id: number;
  series: string[];
  dias_stock: number;
}

// 📌 INTERFAZ: DATOS DE LA CABECERA DEL FORMULARIO
// Define los campos principales que el usuario llena en la parte superior del formulario.
export interface IngresoMercaderiaFormData {
  proveedor_id: number;
  dte: string;
  sello: string;
  cotizacion: string;
  codigo_generacion: string;
  observaciones: string;
  estado_ingreso_id: number;
}

// 📌 INTERFAZ: RESPUESTA DEL BACKEND TRAS CREAR
export interface IngresoResponse {
  id: number;
  dte: string;
  proveedor_id: number;
  fecha: string;
  estado_ingreso_id: number;
}

// 📌 OBJETO DE SERVICIO API
export const ingresoApi = {
  listarEstadosIngreso: async () => {
    const response = await api.get<{ total: number; estados: EstadoIngreso[] }>('/inventario/estados-ingreso/listar');
    return response.data.estados;
  },

  listarProveedores: async () => {
    // 🔗 Filtra solo proveedores activos para el dropdown
    const response = await api.get<{ total: number; proveedores: Proveedor[] }>('/proveedores/listar?activo=true');
    return response.data.proveedores;
  },

  listarProductos: async () => {
    // 🔗 Filtra solo productos activos para el dropdown
    const response = await api.get<{ total: number; productos: Producto[] }>('/productos/listar?activo=true');
    return response.data.productos;
  },

  listarBodegas: async () => {
    const response = await api.get<{ total: number; bodegas: Bodega[] }>('/productos/bodegas/listar');
    return response.data.bodegas;
  },

  crearIngreso: async (data: IngresoMercaderiaFormData & { items: ItemIngresoCreate[] }) => {
    // 🔗 Combina la cabecera y el array de ítems en una sola petición POST
    const response = await api.post<IngresoResponse>('/ingreso-mercaderia/crear', data);
    return response.data;
  },

  listarIngresos: async () => {
    // Endpoint genérico para obtener el historial reciente
    const response = await api.get<{ total: number; ingresos: IngresoResponse[] }>('/ingreso-mercaderia/listar');
    return response.data.ingresos;
  }
};