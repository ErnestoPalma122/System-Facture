// frontend/src/features/usuarios/api/usuario_api.ts

import api from '@/lib/axios';

// 📌 INTERFACES DE DATOS
export interface Rol {
  id: number;
  nombre: string;
  tipo: string;
}

export interface Departamento {
  id: number;
  nombre: string;
}

// 📌 MODELO COMPLETO DEL USUARIO (RESPUESTA DEL BACKEND)
// Incluye las relaciones anidadas (departamento y rol) para facilitar su muestra en la UI.
export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  telefono: string | null;
  estado: string;
  departamento_id: number | null;
  rol_id: number | null;
  departamento?: Departamento | null;
  rol?: Rol | null;
}

// 📌 PAYLOAD DEL FORMULARIO (DATA TRANSFER OBJECT)
// ✅ CORREGIDO: telefono y departamento_id ahora son opcionales (?) para coincidir con la lógica de la UI.
// password es opcional porque solo se envía si el usuario decide cambiarla (o es obligatoria solo en creación).
export interface UsuarioFormData {
  nombre: string;
  email: string;
  telefono?: string;
  departamento_id?: string; // 🔗 Se maneja como string en el form, se convierte a number en la API
  rol_id: string;
  password?: string;
}

// 📌 OBJETO DE SERVICIO API
export const usuarioApi = {
  listarRoles: async () => {
    const response = await api.get<{ total: number; roles: Rol[] }>('/usuarios/roles/listar?limit=100');
    return response.data.roles;
  },

  listarDepartamentos: async () => {
    const response = await api.get<{ total: number; departamentos: Departamento[] }>('/usuarios/departamentos/listar?limit=100');
    return response.data.departamentos;
  },

  // 📌 LISTAR USUARIOS CON BÚSQUEDA DINÁMICA
  listarUsuarios: async (busqueda?: string) => {
    // 🔗 Uso de URLSearchParams para construir la query string de forma segura y limpia.
    const params = new URLSearchParams();
    if (busqueda) params.append('busqueda', busqueda);
    // ⚠️ Lógica de paginación inteligente: si hay búsqueda, trae 100; si no, solo 10 para rendimiento inicial.
    params.append('limit', busqueda ? '100' : '10'); 
    
    const response = await api.get<{ total: number; usuarios: Usuario[] }>(`/usuarios/listar?${params.toString()}`);
    return response.data.usuarios;
  },

  // 📌 CREAR USUARIO
  crearUsuario: async (data: UsuarioFormData) => {
    // 🔗 Transformación de payload: convierte los IDs de string (del form) a number (que espera el backend).
    const payload = {
      ...data,
      departamento_id: data.departamento_id ? Number(data.departamento_id) : undefined,
      rol_id: data.rol_id ? Number(data.rol_id) : undefined,
    };
    const response = await api.post<Usuario>('/usuarios/crear', payload);
    return response.data;
  },

  // 📌 ACTUALIZAR USUARIO
  actualizarUsuario: async (id: number, data: UsuarioFormData) => {
    // ⚠️ NOTA: Solo incluimos 'password' en el payload si el usuario la escribió. 
    // Esto evita sobrescribir o invalidar la contraseña actual por error.
    const payload: any = {
      nombre: data.nombre,
      email: data.email,
      telefono: data.telefono || undefined,
      departamento_id: data.departamento_id ? Number(data.departamento_id) : undefined,
      rol_id: data.rol_id ? Number(data.rol_id) : undefined,
    };
    
    if (data.password) {
      payload.password = data.password;
    }
    
    const response = await api.put<Usuario>(`/usuarios/actualizar/${id}`, payload);
    return response.data;
  },

  // 📌 ELIMINAR USUARIO
  eliminarUsuario: async (id: number) => {
    const response = await api.delete<{ message: string }>(`/usuarios/eliminar/${id}`);
    return response.data;
  },
};