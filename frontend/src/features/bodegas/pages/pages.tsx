// frontend/src/features/bodegas/pages/pages.tsx
import { RouteObject } from 'react-router-dom';
import { BodegaPage } from '../components/BodegaForm';

export const bodegasRoutes: RouteObject[] = [
  {
    path: '/bodegas',
    element: <BodegaPage />,
  },
];