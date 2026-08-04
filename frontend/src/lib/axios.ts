// frontend\src\lib\axios.ts

// 📌 CONFIGURACIÓN DE INSTANCIA PERSONALIZADA DE AXIOS
// Este archivo centraliza toda la comunicación HTTP con el backend, 
// manejando automáticamente la inyección de tokens y la renovación de sesiones (Refresh Token).

// 🔗 Importación de la librería para hacer peticiones HTTP
import axios from 'axios';
// 🔗 Importación del store para acceder a los tokens de forma programática (fuera de componentes React)
import { useAuthStore } from '@/stores/useAuthStore';

// 📌 1. CREACIÓN DE LA INSTANCIA BASE
// Configura la URL base y los encabezados por defecto para todas las peticiones que usen esta instancia 'api'.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // 🔗 Lee la URL del backend desde las variables de entorno (.env)
  headers: { 'Content-Type': 'application/json' }, // 🔗 Indica al backend que enviamos datos en formato JSON
});

// ⚠️ NOTA DE DEPURACIÓN: Esta línea es útil en desarrollo para verificar que la variable de entorno se está leyendo correctamente.
console.log("🔗 Axios URL configurada como:", api.defaults.baseURL);

// 📌 2. INTERCEPTOR DE PETICIÓN (REQUEST INTERCEPTOR)
// Se ejecuta ANTES de que cada petición salga del frontend hacia el backend.
api.interceptors.request.use((config) => {
  // 🔗 Usamos .getState() en lugar del hook useAuthStore() porque los interceptores 
  // se ejecutan fuera del ciclo de vida de los componentes de React.
  const token = useAuthStore.getState().accessToken;
  
  if (token) {
    // Si existe un token, lo inyectamos en el encabezado Authorization con el prefijo 'Bearer'.
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config; // Devuelve la configuración modificada para que la petición continúe.
});

// 📌 3. INTERCEPTOR DE RESPUESTA (RESPONSE INTERCEPTOR)
// Se ejecuta DESPUÉS de que el backend responde. Maneja éxitos y, crucialmente, los errores (como el 401).
api.interceptors.response.use(
  // ✅ CASO DE ÉXITO: Simplemente devuelve la respuesta tal cual.
  (response) => response,
  
  // ⚠️ CASO DE ERROR: Manejo avanzado de sesiones expiradas (Refresh Token Flow)
  async (error) => {
    const originalRequest = error.config; // Guarda la configuración de la petición que falló.
    
    // 🔗 Condición clave: Si el error es 401 (No Autorizado) Y la petición no ha sido reintentada ya (_retry).
    // ⚠️ El flag '_retry' es vital: evita un bucle infinito si el refresh token también falla o está expirado.
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Marcamos la petición como reintentada.
      
      try {
        // 1. Obtenemos el refresh token del estado global.
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) throw new Error('No refresh token');
        
        // 2. Pedimos un nuevo access token al backend.
        // Nota: Usamos 'axios' directo aquí, no 'api', para evitar que este interceptor se dispare a sí mismo recursivamente.
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL}/auth/refrescar-token`,
          {}, // Cuerpo vacío, la autenticación va en los headers
          { headers: { Authorization: `Bearer ${refreshToken}` } } // Actualiza la autorización con el token de refresco
        );
        
        // 3. Actualizamos el store con el nuevo access token (el refresh token suele mantenerse igual o también actualizarse).
        useAuthStore.getState().setTokens(data.access_token, refreshToken);
        
        // 4. Reintentamos la petición original que falló, ahora con el nuevo token en los headers.
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // ⚠️ CASO DE FALLO CRÍTICO: Si el refresh token también es inválido o expiró.
        // Limpiamos todo el estado de autenticación y forzamos la redirección al login.
        useAuthStore.getState().logout();
        window.location.href = '/login'; // Usamos window.location para una recarga limpia del estado de la app.
      }
    }
    
    // Si no es un 401 o ya se reintentó, rechazamos la promesa para que el componente que hizo la petición maneje el error.
    return Promise.reject(error);
  }
);

export default api;