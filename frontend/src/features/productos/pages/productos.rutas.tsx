import { RouteObject } from 'react-router-dom';
import { ProductoVistaGeneral } from '../components/ProductoVistaGeneral';

export const productosRutas: RouteObject[] = [
  {
    path: '/productos',
    element: <ProductoVistaGeneral />,
  },
];