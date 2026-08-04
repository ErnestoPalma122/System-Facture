// frontend\src\features\auth\hooks\useLogin.ts

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { loginApi, LoginRequest } from '../api/auth_api';

// 📌 HOOK PERSONALIZADO DE INICIO DE SESIÓN
// Encapsula toda la lógica, estado y efectos secundarios del proceso de login.
export function useLogin() {
  // 🔗 Estados locales para manejar la UI durante la petición asíncrona.
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const { setAuth } = useAuthStore(); // Función del store para persistir la sesión.

  const login = async (credentials: LoginRequest) => {
    // 1. Preparar el estado antes de la petición
    setIsLoading(true);
    setError(null);

    try {
      // 2. Llamar a la API con las credenciales
      const data = await loginApi(credentials);

      // 3. Guardar tokens y datos del usuario en el store global (generalmente persiste en localStorage)
      setAuth(data.usuario, data.access_token, data.refresh_token);

      // 4. Redirigir al dashboard. 
      // ⚠️ 'replace: true' es crucial: reemplaza la entrada en el historial del navegador, 
      // evitando que el usuario pueda pulsar "Atrás" y volver a la pantalla de login estando ya autenticado.
      navigate('/', { replace: true });
      
    } catch (err: any) {
      // 5. Manejo de errores: extrae el mensaje del backend o usa uno genérico.
      const errorMessage = err.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      setError(errorMessage);
      console.error('Error en login:', err);
    } finally {
      // 6. Restablecer el estado de carga, ocurra lo que ocurra (éxito o error).
      setIsLoading(false);
    }
  };

  // 📌 Se exponen solo las variables y funciones necesarias para el componente UI.
  return { login, isLoading, error };
}