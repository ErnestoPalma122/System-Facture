import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { logoutApi } from '../api/auth_api';

export function useLogout() {
  const navigate = useNavigate();
  const { logout: clearAuthStore } = useAuthStore();

  const handleLogout = async () => {
    try {
      // 1. Intentar cerrar sesión en el backend (invalidar token en BD)
      await logoutApi();
      console.log("✅ Sesión cerrada exitosamente en el backend");
    } catch (error) {
      // 2. Si falla el backend (ej: token ya expiró), igual debemos cerrar en el frontend
      console.warn("⚠️ El backend no respondió, cerrando localmente...", error);
    } finally {
      // 3. Limpiar estado local (Zustand) SIN IMPORTAR si el backend falló o no
      clearAuthStore();
      
      // 4. Redirigir al login
      navigate('/login', { replace: true });
    }
  };

  return { handleLogout };
}