import api from '@/lib/axios';

export interface Rol {
  id: number;
  nombre: string;
  tipo: string;
}

export interface Departamento {
  id: number;
  nombre: string;
}

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

// ✅ CORREGIDO: telefono y departamento_id ahora son opcionales (?)
export interface UsuarioFormData {
  nombre: string;
  email: string;
  telefono?: string;
  departamento_id?: string;
  rol_id: string;
  password?: string;
}

export const usuarioApi = {
  listarRoles: async () => {
    const response = await api.get<{ total: number; roles: Rol[] }>('/usuarios/roles/listar?limit=100');
    return response.data.roles;
  },

  listarDepartamentos: async () => {
    const response = await api.get<{ total: number; departamentos: Departamento[] }>('/usuarios/departamentos/listar?limit=100');
    return response.data.departamentos;
  },

  listarUsuarios: async (busqueda?: string) => {
    const params = new URLSearchParams();
    if (busqueda) params.append('busqueda', busqueda);
    params.append('limit', busqueda ? '100' : '10'); 
    
    const response = await api.get<{ total: number; usuarios: Usuario[] }>(`/usuarios/listar?${params.toString()}`);
    return response.data.usuarios;
  },

  crearUsuario: async (data: UsuarioFormData) => {
    const payload = {
      ...data,
      departamento_id: data.departamento_id ? Number(data.departamento_id) : undefined,
      rol_id: data.rol_id ? Number(data.rol_id) : undefined,
    };
    const response = await api.post<Usuario>('/usuarios/crear', payload);
    return response.data;
  },

  actualizarUsuario: async (id: number, data: UsuarioFormData) => {
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

  eliminarUsuario: async (id: number) => {
    const response = await api.delete<{ message: string }>(`/usuarios/eliminar/${id}`);
    return response.data;
  },
};