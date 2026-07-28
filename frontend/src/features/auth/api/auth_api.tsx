// frontend/src/features/auth/api/auth_api.tsx
import api from '@/lib/axios';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  usuario: {
    id: number;
    email: string;
    nombre: string;
    rol: {
      id: number;
      nombre: string;
      tipo: string;
    };
  };
}

/**
 * Envía las credenciales al backend para iniciar sesión.
 */
export const loginApi = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/iniciar-sesion', credentials);
  return response.data;
};


// ✅ AGREGA ESTA FUNCIÓN:
export const logoutApi = async (): Promise<void> => {
  // El interceptor de axios se encarga de enviar el Bearer Token automáticamente
  await api.post('/auth/cerrar-sesion');
};