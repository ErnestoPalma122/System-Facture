import { RouteObject } from 'react-router-dom';
import { UsuarioVistaGeneral } from '../components/UsuarioVistaGeneral';

export const usuariosRutas: RouteObject[] = [
  {
    path: '/usuarios',
    element: <UsuarioVistaGeneral />,
  },
];