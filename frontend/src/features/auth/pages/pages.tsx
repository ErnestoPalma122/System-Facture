// frontend\src\features\auth\pages\pages.tsx
import { RouteObject } from 'react-router-dom';
import { LoginPage } from '../components/LoginPage';

export const authRoutes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />,
  },
];