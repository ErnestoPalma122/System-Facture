import api from '@/lib/axios';

export interface DireccionEmisor {
  cod_departamento: string;
  desc_departamento: string;
  cod_municipio: string;
  desc_municipio: string;
  cod_distrito: string;
  desc_distrito: string;
  complemento: string;
}

export interface EmisorRequest {
  nit: string;
  nrc: string;
  nombre: string;
  nombre_comercial: string;
  cod_actividad: string;
  desc_actividad: string;
  direccion: DireccionEmisor;
  telefono: string;
  correo: string;
  correo_interno: string;
  cod_estable: string;
  cod_punto_venta: string;
}

export interface EmisorResponse {
  id: number;
  nit: string;
  nrc: string;
  nombre: string;
  nombre_comercial: string;
  cod_actividad: string;
  desc_actividad: string;
  cod_departamento: string;
  desc_departamento: string;
  cod_municipio: string;
  desc_municipio: string;
  cod_distrito: string;
  desc_distrito: string;
  dirr_complemento: string;
  telefono: string;
  correo: string;
  correo_interno: string;
  cod_estable: string;
  cod_punto_venta: string;
  activo: boolean;
  created_at: string;
  updated_at: string | null;
}

export type EmisorFormData = EmisorRequest;

export const emisorApi = {
  obtener: async (): Promise<EmisorResponse> => {
    const response = await api.get<EmisorResponse>('/emisor/obtener');
    return response.data;
  },

  crear: async (data: EmisorRequest) => {
    const response = await api.post<EmisorResponse>('/emisor/crear', data);
    return response.data;
  },

  actualizar: async (data: EmisorRequest) => {
    // El backend espera PUT /emisor/actualizar sin ID en la URL (es un singleton)
    const response = await api.put<EmisorResponse>('/emisor/actualizar', data);
    return response.data;
  },
};