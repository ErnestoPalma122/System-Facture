// frontend\src\features\proveedores\api\proveedor_api.ts

import api from '@/lib/axios';

// 📌 MODELO COMPLETO DEL PROVEEDOR (RESPUESTA DEL BACKEND)
// Representa la estructura de datos tal como la devuelve el servidor, incluyendo metadatos como fechas y estado.
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

// 📌 PAYLOAD DEL FORMULARIO (DATA TRANSFER OBJECT)
// Define los datos que el frontend envía. 
// ⚠️ Nota: 'contacto', 'email', 'telefono2' y 'observaciones' son opcionales, 
// lo que permite enviar el formulario sin llenar campos secundarios.
export interface ProveedorFormData {
  nombre: string;
  direccion: string;
  contacto?: string;
  email?: string;
  telefono1: string;
  telefono2?: string;
  observaciones?: string;
}

// 📌 OBJETO DE SERVICIO API
export const proveedorApi = {
  // 📌 1. LISTAR PROVEEDORES CON FILTROS DINÁMICOS
  listar: async (activo?: boolean, nombre?: string) => {
    // 🔗 Uso de URLSearchParams para construir la query string de forma segura, 
    // evitando errores de concatenación manual de URLs.
    const params = new URLSearchParams();
    if (activo !== undefined) params.append('activo', String(activo));
    if (nombre) params.append('nombre', nombre);
    
    const response = await api.get<{ total: number; proveedores: Proveedor[] }>(`/proveedores/listar?${params.toString()}`);
    return response.data.proveedores;
  },

  // 📌 2. CREAR PROVEEDOR
  crear: async (data: ProveedorFormData) => {
    const response = await api.post<Proveedor>('/proveedores/crear', data);
    return response.data;
  },

  // 📌 3. ACTUALIZAR PROVEEDOR
  actualizar: async (id: number, data: ProveedorFormData) => {
    const response = await api.put<Proveedor>(`/proveedores/actualizar/${id}`, data);
    return response.data;
  },

  // 📌 4. ELIMINAR (DESACTIVAR) PROVEEDOR
  eliminar: async (id: number) => {
    // ⚠️ Nota: Aunque la función se llama 'eliminar', en la UI se presenta como "Desactivar". 
    // El backend probablemente realiza un "Soft Delete" (cambia 'activo' a false) en lugar de un borrado físico.
    const response = await api.delete<{ message: string }>(`/proveedores/eliminar/${id}`);
    return response.data;
  },
};