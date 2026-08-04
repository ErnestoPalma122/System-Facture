// frontend\src\features\proveedores\pages\pages.tsx

import { RouteObject } from 'react-router-dom';
import { ProveedorList } from '../components/ProveedorList.tsx';

// 📌 CONFIGURACIÓN DE RUTAS DEL MÓDULO DE PROVEEDORES
// Este array se importa en el enrutador principal (router.tsx) y se inyecta 
// dentro del Layout del Dashboard, protegido por los permisos correspondientes.
export const proveedoresRoutes: RouteObject[] = [
  {
    path: '/proveedores',
    element: <ProveedorList />, // 🔗 Renderiza el componente que orquesta la tabla y el panel lateral.
  },
];