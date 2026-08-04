// frontend/src/features/auth/api/auth_api.tsx

import api from '@/lib/axios';

// 📌 INTERFAZ DE SOLICITUD DE INICIO DE SESIÓN
// Define la estructura exacta y tipada de los datos que se enviarán al backend.
export interface LoginRequest {
  email: string;
  password: string;
}

// 📌 INTERFAZ DE RESPUESTA DE INICIO DE SESIÓN
// Define la estructura de los datos que el backend devuelve tras un login exitoso.
// 🔗 Incluye los tokens de acceso/refresco y el objeto completo del usuario con su rol anidado.
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
 * 📌 FUNCIÓN DE API: INICIAR SESIÓN
 * Envía las credenciales al endpoint de autenticación del backend.
 * @param credentials - Objeto con email y password.
 * @returns Promesa con los tokens y datos del usuario (LoginResponse).
 */
export const loginApi = async (credentials: LoginRequest): Promise<LoginResponse> => {
  // 🔗 'api.post' utiliza la instancia de Axios configurada en '@/lib/axios', 
  // la cual ya contiene la URL base, timeouts y manejadores de errores globales.
  const response = await api.post<LoginResponse>('/auth/iniciar-sesion', credentials);
  return response.data;
};

// ✅ 📌 FUNCIÓN DE API: CERRAR SESIÓN
// Notifica al backend para invalidar el token actual en la base de datos (buena práctica de seguridad).
export const logoutApi = async (): Promise<void> => {
  // ⚠️ Nota: No es necesario pasar el token manualmente como parámetro aquí. 
  // El interceptor de Axios configurado en '@/lib/axios' se encarga de inyectar 
  // el encabezado 'Authorization: Bearer <token>' automáticamente en esta petición.
  await api.post('/auth/cerrar-sesion');
};