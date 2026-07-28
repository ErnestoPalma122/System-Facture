// frontend\src\lib\axios.ts

//Se crea una instancia personalizada de axios  


//Hace peticiones HTTP
import axios from 'axios';
import { useAuthStore } from '@/stores/useAuthStore';

//Configuracion de instancia que se comunica con el backend
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// AGREGA ESTA LÍNEA TEMPORAL PARA DEPURAR:
console.log("🔗 Axios URL configurada como:", api.defaults.baseURL);

// Interceptor: Adjuntar Token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor: Manejar 401 de no autorizado y hacer Refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    //Evita un bucle infinito por el refresh token faclla, no lo intenta de manera infinita
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) throw new Error('No refresh token');
        //Pide un nuevo token a el backend
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL}/auth/refrescar-token`,
          {},
          //actualiza la utorizacion con el nuevo token refrescado
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );
        // Reintenta la peticion original del tokend
        useAuthStore.getState().setTokens(data.access_token, refreshToken);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        //Si el refresh falla limplia todo y muestra la pagina de login
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;