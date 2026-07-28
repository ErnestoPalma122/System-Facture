import { RouteObject } from 'react-router-dom';
import { EmisorConfigPage } from '../components/EmisorForm';

export const emisorRoutes: RouteObject[] = [
  {
    path: '/configuracion/emisor',
    element: <EmisorConfigPage />,
  },
];