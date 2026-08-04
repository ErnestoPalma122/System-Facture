// frontend\src\features\auth\hooks\useLogout.ts

import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { logoutApi } from '../api/auth_api';

// 📌 HOOK PERSONALIZADO DE CIERRE DE SESIÓN
export function useLogout() {
  const navigate = useNavigate();
  // 🔗 Renombramos 'logout' a 'clearAuthStore' para mayor claridad semántica en este contexto.
  const { logout: clearAuthStore } = useAuthStore();

  const handleLogout = async () => {
    try {
      // 1. Intentar notificar al backend para invalidar el token en la base de datos (buena práctica de seguridad).
      await logoutApi();
      console.log("✅ Sesión cerrada exitosamente en el backend");
    } catch (error) {
      // ⚠️ Si falla el backend (ej: el token ya había expirado), NO debemos detener el proceso.
      // Es más importante limpiar el frontend que recibir una respuesta del servidor.
      console.warn("⚠️ El backend no respondió, cerrando localmente...", error);
    } finally {
      // 2. Limpieza local GARANTIZADA: Se ejecuta tanto en éxito como en error del bloque 'try'.
      // Esto asegura que el usuario siempre sea desconectado de la interfaz.
      clearAuthStore();
      
      // 3. Redirigir al login. Nuevamente, 'replace: true' limpia el historial para evitar bucles de navegación.
      navigate('/login', { replace: true });
    }
  };

  return { handleLogout };
}