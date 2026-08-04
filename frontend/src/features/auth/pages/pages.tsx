// frontend/src/features/auth/pages/pages.tsx

import { RouteObject } from 'react-router-dom';
import { LoginPage } from '../components/LoginPage';

// 📌 CONFIGURACIÓN DE RUTAS PÚBLICAS DE AUTENTICACIÓN
// Este array se importa en el enrutador principal (router.tsx) 
// para registrar las rutas que NO requieren que el usuario esté autenticado.
export const authRoutes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />, // 🔗 Renderiza el componente de inicio de sesión.
  },
  // ⚠️ Nota de escalabilidad: Si en el futuro se agregan rutas públicas como '/registro' 
  // o '/recuperar-password', se añadirán como nuevos objetos en este mismo array.
];