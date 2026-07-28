// frontend/src/features/bodegas/api/bodega_api.ts
import api from '@/lib/axios';

export interface Bodega {
  id: number;
  nombre: string;
  direccion: string | null;
  ubicacion: string | null;
  telefono: string | null;
  encargado_id: number | null;
  activo: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface BodegaCreate {
  nombre: string;
  direccion?: string;
  ubicacion?: string;
  telefono?: string;
  encargado_id?: number;
}

export interface BodegaUpdate {
  nombre?: string;
  direccion?: string;
  ubicacion?: string;
  telefono?: string;
  encargado_id?: number | null;
  activo?: boolean;
}

export const bodegaApi = {
  listar: async () => {
    const response = await api.get<{ total: number; bodegas: Bodega[] }>('/productos/bodegas/listar');
    return response.data.bodegas;
  },

  crear: async (data: BodegaCreate) => {
    const response = await api.post<Bodega>('/productos/bodegas/crear', data);
    return response.data;
  },

  actualizar: async (id: number, data: BodegaUpdate) => {
    const response = await api.put<Bodega>(`/productos/bodegas/actualizar/${id}`, data);
    return response.data;
  },
};