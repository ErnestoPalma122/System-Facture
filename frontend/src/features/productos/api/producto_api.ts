import api from '@/lib/axios';

// DOCUMENTACIÓN: Interfaz que representa una Categoría de producto.
export interface Categoria {
  id: number;
  nombre: string;
}

// DOCUMENTACIÓN: Interfaz que representa la respuesta de un Producto desde el backend.
// ✅ ACTUALIZACIÓN: Ahora incluye TODOS los campos de precio para una edición y visualización completa.
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
    id?: number;
    producto_id?: number;
    precio_base: number | string;
    precio_costo: number | string;
    precio_publico: number | string;
    precio_iva: number | string;
    precio_promo: number | string;
    precio_descuento: number | string;
  } | null;
}

// DOCUMENTACIÓN: Interfaz que define la estructura de datos que el formulario envía.
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
        precio_base: Number(data.precio.precio_base) || 0,
        precio_publico: Number(data.precio.precio_publico) || 0,
        precio_costo: Number(data.precio.precio_costo) || 0,
        precio_iva: Number(data.precio.precio_iva) || 0,
        precio_promo: Number(data.precio.precio_promo) || 0,
        precio_descuento: Number(data.precio.precio_descuento) || 0,
      }
    };
    const response = await api.post<Producto>('/productos/crear', payload);
    return response.data;
  },

  // DOCUMENTACIÓN: Actualiza un producto existente.
  // ✅ CORRECCIÓN CRÍTICA: Ahora envía el objeto 'precio' completo con todos sus campos.
  // Esto permite que el backend actualice tanto la cabecera como los precios en una sola transacción atómica.
  actualizarProducto: async (id: number, data: ProductoFormData) => {
    const payload = {
      codigo: data.codigo,
      nombre: data.nombre,
      descripcion: data.descripcion || undefined,
      marca: data.marca || undefined,
      tipo: data.tipo,
      categoria_id: data.categoria_id ? Number(data.categoria_id) : undefined,
      precio: {
        precio_base: Number(data.precio.precio_base) || 0,
        precio_publico: Number(data.precio.precio_publico) || 0,
        precio_costo: Number(data.precio.precio_costo) || 0,
        precio_iva: Number(data.precio.precio_iva) || 0,
        precio_promo: Number(data.precio.precio_promo) || 0,
        precio_descuento: Number(data.precio.precio_descuento) || 0,
      }
    };
    const response = await api.put<Producto>(`/productos/actualizar/${id}`, payload);
    return response.data;
  },
};