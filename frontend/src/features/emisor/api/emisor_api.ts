// frontend/src/features/emisor/api/emisor_api.ts

import api from '@/lib/axios';

// 📌 INTERFAZ: ESTRUCTURA DE DIRECCIÓN ANIDADA
// Representa la estructura jerárquica de la dirección según los catálogos de Hacienda.
export interface DireccionEmisor {
  cod_departamento: string;
  desc_departamento: string;
  cod_municipio: string;
  desc_municipio: string;
  cod_distrito: string;
  desc_distrito: string;
  complemento: string;
}

// 📌 INTERFAZ: PAYLOAD DE PETICIÓN (REQUEST)
// Define la estructura de datos que el frontend envía al backend. 
// Nota cómo 'direccion' es un objeto anidado, lo cual es más limpio para el formulario.
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

// 📌 INTERFAZ: RESPUESTA DEL BACKEND
// Define la estructura plana que devuelve el servidor. 
// ⚠️ Nota: El backend devuelve los campos de dirección "aplanados" (ej: cod_departamento, desc_departamento) 
// y usa 'dirr_complemento' en lugar de 'complemento'. La función de mapeo en el formulario se encarga de adaptar esto.
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

// 🔗 Alias para mayor claridad semántica en el formulario
export type EmisorFormData = EmisorRequest;

// 📌 OBJETO DE SERVICIO API
export const emisorApi = {
  // 📌 1. OBTENER CONFIGURACIÓN
  obtener: async (): Promise<EmisorResponse> => {
    const response = await api.get<EmisorResponse>('/emisor/obtener');
    return response.data;
  },

  // 📌 2. CREAR CONFIGURACIÓN
  crear: async (data: EmisorRequest) => {
    const response = await api.post<EmisorResponse>('/emisor/crear', data);
    return response.data;
  },

  // 📌 3. ACTUALIZAR CONFIGURACIÓN
  actualizar: async (data: EmisorRequest) => {
    // ⚠️ NOTA ARQUITECTÓNICA: El backend trata al Emisor como un "Singleton" (solo puede existir uno).
    // Por eso, la ruta es PUT /emisor/actualizar y NO requiere un ID en la URL. 
    // El backend identifica el registro por el usuario/empresa autenticada.
    const response = await api.put<EmisorResponse>('/emisor/actualizar', data);
    return response.data;
  },
};