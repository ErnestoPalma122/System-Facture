import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';

export function Router() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Routes>
      <Route 
        path="/" 
        element={
          isAuthenticated ? (
            <div className="p-8">
              <h1 className="text-3xl font-bold text-blue-600">
                🚀 Dashboard - Sistema Factu
              </h1>
              <p className="mt-4 text-gray-600">
                Bienvenido al sistema. Sesión activa.
              </p>
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      <Route 
        path="/login" 
        element={
          <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md">
              <h1 className="text-2xl font-bold text-gray-800">
                🔐 Login (Próximamente)
              </h1>
              <p className="mt-2 text-gray-600">
                Módulo de autenticación en desarrollo
              </p>
            </div>
          </div>
        } 
      />
    </Routes>
  );
}