//frontend\src\features\productos\api\producto_api.ts
import api from '@/lib/axios';

export interface Categoria {
  id: number;
  nombre: string;
}

export interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  marca: string | null;
  tipo: string;
  categoria_id: number | null;
  activo: boolean;
  precio: {
    precio_base: number | string;
    precio_publico: number | string;
  } | null;
}

export interface ProductoFormData {
  codigo: string;
  nombre: string;
  descripcion?: string;
  marca?: string;
  tipo: 'BIEN' | 'SERVICIO';
  categoria_id?: string;
  precio: {
    precio_base: string;
    precio_publico: string;
    precio_costo?: string;
    precio_iva?: string;
    precio_promo?: string;
    precio_descuento?: string;
  };
}

export const productoApi = {
  listarCategorias: async () => {
    const response = await api.get<{ total: number; categorias: Categoria[] }>('/productos/categorias/listar');
    return response.data.categorias;
  },

  listarProductos: async (activo: boolean = true) => {
    const response = await api.get<{ total: number; productos: Producto[] }>(`/productos/listar?activo=${activo}`);
    return response.data.productos;
  },

  obtenerProductoPorId: async (id: number) => {
    const response = await api.get<Producto>(`/productos/obtener/${id}`);
    return response.data;
  },

  crearProducto: async (data: ProductoFormData) => {
    const payload = {
      ...data,
      categoria_id: data.categoria_id ? Number(data.categoria_id) : undefined,
      descripcion: data.descripcion || undefined,
      marca: data.marca || undefined,
      precio: {
        precio_base: Number(data.precio.precio_base),
        precio_publico: Number(data.precio.precio_publico),
        precio_costo: data.precio.precio_costo ? Number(data.precio.precio_costo) : undefined,
        precio_iva: data.precio.precio_iva ? Number(data.precio.precio_iva) : undefined,
        precio_promo: data.precio.precio_promo ? Number(data.precio.precio_promo) : undefined,
        precio_descuento: data.precio.precio_descuento ? Number(data.precio.precio_descuento) : undefined,
      }
    };
    const response = await api.post<Producto>('/productos/crear', payload);
    return response.data;
  },

  actualizarProducto: async (id: number, data: ProductoFormData) => {
    // El backend solo espera estos campos para actualizar (según tu schema ProductoUpdate)
    const payload = {
      codigo: data.codigo,
      nombre: data.nombre,
      descripcion: data.descripcion || undefined,
      marca: data.marca || undefined,
      tipo: data.tipo,
      categoria_id: data.categoria_id ? Number(data.categoria_id) : undefined,
    };
    const response = await api.put<Producto>(`/productos/actualizar/${id}`, payload);
    return response.data;
  },
};