// frontend/src/features/emisor/pages/pages.tsx

import { RouteObject } from 'react-router-dom';
import { EmisorConfigPage } from '../components/EmisorForm';

// 📌 CONFIGURACIÓN DE RUTAS DEL MÓDULO DE EMISOR
// Este array se importa en el enrutador principal (router.tsx) y se inyecta 
// dentro del Layout del Dashboard, protegido por los permisos de SUPER_ADMIN o ADMIN.
export const emisorRoutes: RouteObject[] = [
  {
    path: '/configuracion/emisor',
    element: <EmisorConfigPage />, // 🔗 Renderiza el formulario principal de configuración.
  },
];