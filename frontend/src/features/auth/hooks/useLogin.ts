// frontend/src/features/auth/hooks/useLogin.ts
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { loginApi, LoginRequest } from '../api/auth_api';

export function useLogin() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      // 1. Llamar a la API
      const data = await loginApi(credentials);

      // 2. Guardar tokens y usuario en el store (persiste en localStorage)
      setAuth(data.usuario, data.access_token, data.refresh_token);

      // 3. Redirigir al dashboard
      navigate('/', { replace: true });
      
    } catch (err: any) {
      // 4. Manejar errores (ej: 401 Credenciales inválidas)
      const errorMessage = err.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      setError(errorMessage);
      console.error('Error en login:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return { login, isLoading, error };
}