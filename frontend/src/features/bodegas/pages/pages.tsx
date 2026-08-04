// frontend/src/features/bodegas/pages/pages.tsx

import { RouteObject } from 'react-router-dom';
import { BodegaPage } from '../components/BodegaForm';

// 📌 CONFIGURACIÓN DE RUTAS DEL MÓDULO DE BODEGAS
// Este array se importa en el enrutador principal (router.tsx) y se inyecta 
// dentro del Layout del Dashboard, protegido por los permisos correspondientes.
export const bodegasRoutes: RouteObject[] = [
  {
    path: '/bodegas',
    element: <BodegaPage />, // 🔗 Renderiza el componente que contiene la tabla y el modal.
  },
];