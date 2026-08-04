// frontend/src/features/ingreso_mercaderia/pages/ingreso_mercaderia.rutas.tsx

import { RouteObject } from 'react-router-dom';
import { IngresoMercaderiaVistaGeneral } from '../components/IngresoMercaderiaVistaGeneral';

// 📌 CONFIGURACIÓN DE RUTAS DEL MÓDULO DE INGRESO DE MERCADERÍA
// Este array se importa en el enrutador principal (router.tsx) y se inyecta 
// dentro del Layout del Dashboard, protegido por los permisos correspondientes.
export const ingresoMercaderiaRutas: RouteObject[] = [
  {
    path: '/ingreso-mercaderia',
    element: <IngresoMercaderiaVistaGeneral />, // 🔗 Renderiza la vista que orquesta el formulario y la tabla.
  },
];