//frontend\src\features\proveedores\api\proveedor_api.ts
import api from '@/lib/axios';

export interface Proveedor {
  id: number;
  nombre: string;
  direccion: string | null;
  contacto: string | null;
  email: string | null;
  telefono1: string | null;
  telefono2: string | null;
  observaciones: string | null;
  activo: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface ProveedorFormData {
  nombre: string;
  direccion: string;
  contacto?: string;
  email?: string;
  telefono1: string;
  telefono2?: string;
  observaciones?: string;
}

export const proveedorApi = {
  listar: async (activo?: boolean, nombre?: string) => {
    const params = new URLSearchParams();
    if (activo !== undefined) params.append('activo', String(activo));
    if (nombre) params.append('nombre', nombre);
    
    const response = await api.get<{ total: number; proveedores: Proveedor[] }>(`/proveedores/listar?${params.toString()}`);
    return response.data.proveedores;
  },

  crear: async (data: ProveedorFormData) => {
    const response = await api.post<Proveedor>('/proveedores/crear', data);
    return response.data;
  },

  actualizar: async (id: number, data: ProveedorFormData) => {
    const response = await api.put<Proveedor>(`/proveedores/actualizar/${id}`, data);
    return response.data;
  },

  eliminar: async (id: number) => {
    const response = await api.delete<{ message: string }>(`/proveedores/eliminar/${id}`);
    return response.data;
  },
};