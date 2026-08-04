//frontend\src\components\ui\ProtectedRoute.tsx
import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom'; // ✅ Usamos Navigate en lugar de useNavigate
import { useAuthStore } from '@/stores/useAuthStore';

interface ProtectedRouteProps {
  allowedDepartments?: string[];
  allowedRoles?: string[];
  children: ReactNode;
}

export function ProtectedRoute({ allowedDepartments, allowedRoles, children }: ProtectedRouteProps) {
  const { user } = useAuthStore();
  const location = useLocation();

  // 1. Si no hay usuario, redirigir al login de forma declarativa
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // 2. SUPER_ADMIN tiene acceso total a todo, siempre.
  if (user.rol.tipo === 'SUPER_ADMIN') {
    return <>{children}</>;
  }

  // 3. Validar Rol (si se especificó)
  if (allowedRoles && allowedRoles.length > 0) {
    if (!allowedRoles.includes(user.rol.tipo)) {
      sessionStorage.setItem('deniedPath', location.pathname);
      return <Navigate to="/acceso-denegado" replace />; // ✅ Redirección declarativa
    }
  }

  // 4. Validar Departamento (si se especificó)
  if (allowedDepartments && allowedDepartments.length > 0) {
    const userDeptName = user.departamento?.nombre;
    if (!userDeptName || !allowedDepartments.includes(userDeptName)) {
      sessionStorage.setItem('deniedPath', location.pathname);
      return <Navigate to="/acceso-denegado" replace />; // ✅ Redirección declarativa
    }
  }

  // Si pasa todas las validaciones, muestra el contenido protegido
  return <>{children}</>;
}