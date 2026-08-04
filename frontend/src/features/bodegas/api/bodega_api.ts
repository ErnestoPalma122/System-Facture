// frontend/src/features/bodegas/api/bodega_api.ts

// 📌 CAPA DE SERVICIO DE API PARA MÓDULO DE BODEGAS
// Este archivo centraliza todas las peticiones HTTP relacionadas con las "Bodegas".
// Actúa como una capa de abstracción: los componentes/hooks no llaman a Axios directamente, 
// sino que usan estos métodos, lo que facilita el mantenimiento y el tipado.

// 🔗 Importamos la instancia configurada de Axios (que ya incluye interceptores de token y refresh)
import api from '@/lib/axios';

// 📌 INTERFAZ: MODELO DE DATOS COMPLETO (RESPUESTA DEL BACKEND)
// Representa la estructura exacta de una Bodega tal como la devuelve el servidor.
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

// 📌 INTERFAZ: PAYLOAD DE CREACIÓN (DTO)
// Define los datos necesarios para crear una nueva bodega.
// ⚠️ Solo 'nombre' es obligatorio. El resto son opcionales ('?'), lo que coincide con la validación del backend.
export interface BodegaCreate {
  nombre: string;
  direccion?: string;
  ubicacion?: string;
  telefono?: string;
  encargado_id?: number;
}

// 📌 INTERFAZ: PAYLOAD DE ACTUALIZACIÓN (DTO)
// Define los datos para modificar una bodega existente.
// ⚠️ Todos los campos son opcionales ('?'), permitiendo actualizaciones parciales (PATCH/PUT flexible).
// Incluye 'activo' para permitir habilitar/deshabilitar la bodega sin cambiar otros datos.
export interface BodegaUpdate {
  nombre?: string;
  direccion?: string;
  ubicacion?: string;
  telefono?: string;
  encargado_id?: number | null;
  activo?: boolean;
}

// 📌 OBJETO DE SERVICIO (API SERVICE)
// Agrupa todas las funciones relacionadas con bodegas en un solo namespace exportable.
export const bodegaApi = {
  
  // 📌 1. LISTAR BODEGAS
  // Obtiene la lista de bodegas registradas en el sistema.
  listar: async () => {
    // 🔗 Tipado de la respuesta: El backend devuelve un objeto { total: number, bodegas: Bodega[] }.
    const response = await api.get<{ total: number; bodegas: Bodega[] }>('/productos/bodegas/listar');
    
    // ⚠️ Nota: La función extrae y devuelve solo el array 'bodegas', ignorando el campo 'total' en este nivel.
    // Si en el futuro se necesita paginación, se debería devolver 'response.data' completo.
    return response.data.bodegas;
  },

  // 📌 2. CREAR BODEGA
  // Envía los datos al backend para registrar una nueva bodega.
  crear: async (data: BodegaCreate) => {
    // 🔗 Se usa POST y se pasa el objeto 'data' tipado como cuerpo de la petición.
    const response = await api.post<Bodega>('/productos/bodegas/crear', data);
    return response.data; // Devuelve la bodega recién creada (con su ID y fechas asignadas por el backend).
  },

  // 📌 3. ACTUALIZAR BODEGA
  // Modifica los datos de una bodega existente identificada por su ID.
  actualizar: async (id: number, data: BodegaUpdate) => {
    // 🔗 Se usa PUT (o PATCH, dependiendo del backend) e inyecta el 'id' dinámicamente en la URL.
    const response = await api.put<Bodega>(`/productos/bodegas/actualizar/${id}`, data);
    return response.data; // Devuelve la bodega actualizada.
  },
};