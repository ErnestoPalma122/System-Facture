// frontend/src/features/usuarios/pages/usuarios.rutas.tsx

import { RouteObject } from 'react-router-dom';
import { UsuarioVistaGeneral } from '../components/UsuarioVistaGeneral';

// 📌 CONFIGURACIÓN DE RUTAS DEL MÓDULO DE USUARIOS
// Este array se importa en el enrutador principal (router.tsx) y se inyecta 
// dentro del Layout del Dashboard, protegido por los permisos correspondientes (ej: SUPER_ADMIN).
export const usuariosRutas: RouteObject[] = [
  {
    path: '/usuarios',
    element: <UsuarioVistaGeneral />, // 🔗 Renderiza la vista orquestadora del módulo.
  },
];