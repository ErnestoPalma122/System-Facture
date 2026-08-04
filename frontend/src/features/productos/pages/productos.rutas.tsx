//frontend\src\features\productos\pages\productos.rutas.tsx

import { RouteObject } from 'react-router-dom';
import { ProductoVistaGeneral } from '../components/ProductoVistaGeneral';

// DOCUMENTACIÓN: Definición de las rutas específicas para el módulo de productos.
// Este array se importa en el router principal para ser inyectado dentro del layout protegido.
export const productosRutas: RouteObject[] = [
  {
    path: '/productos',
    element: <ProductoVistaGeneral />,
  },
];