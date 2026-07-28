//frontend\src\features\proveedores\pages\pages.tsx
import { RouteObject } from 'react-router-dom';
import { ProveedorList } from '../components/ProveedorList.tsx';


export const proveedoresRoutes: RouteObject[] = [
  {
    path: '/proveedores',
    element: <ProveedorList />,
  },
];