// frontend\src\stores\useAuthStore.ts

// 📌 IMPORTACIONES DE ZUSTAND
// 🔗 'create': Función principal para crear un store de estado global en Zustand.
// 🔗 'persist': Middleware que permite guardar el estado del store en el almacenamiento local (localStorage) 
// para que la sesión del usuario persista incluso si recarga la página o cierra la pestaña.
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 📌 INTERFAZ DEL USUARIO
// Define la estructura tipada de los datos del usuario que se almacenan en el estado global.
export interface User {
  id: number;
  email: string;
  nombre: string;
  rol: { tipo: string }; // 🔗 Contiene el tipo de rol (ej: 'SUPER_ADMIN', 'ADMIN'), usado para validaciones de permiso en el Sidebar y Rutas.
  departamento?: { id: number; nombre: string }; // ✅ AGREGADO: Información del departamento (opcional), usada para filtros de acceso granular.
}

// 📌 INTERFAZ DEL ESTADO DE AUTENTICACIÓN (AUTH STATE)
// Define tanto las variables de estado (datos) como las funciones (acciones) que pueden modificar ese estado.
interface AuthState {
  // Variables de estado
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  
  // Acciones para mutar el estado
  setAuth: (user: User, access: string, refresh: string) => void;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

// 📌 CREACIÓN DEL STORE GLOBAL DE AUTENTICACIÓN
// Se exporta para ser consumido por cualquier componente o hook de la aplicación mediante useAuthStore().
export const useAuthStore = create<AuthState>()(
  // 🔗 Middleware 'persist': Envuelve el estado base para guardarlo/sincronizarlo automáticamente con el navegador.
  persist(
    (set) => ({
      // 📌 1. ESTADO INICIAL
      // Valores por defecto cuando no hay ningún usuario logueado.
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      // 📌 2. ACCIÓN: ESTABLECER AUTENTICACIÓN COMPLETA
      // Se llama tras un login exitoso. Guarda el objeto usuario y ambos tokens, y marca la sesión como activa.
      setAuth: (user, access, refresh) => 
        set({ user, accessToken: access, refreshToken: refresh, isAuthenticated: true }),

      // 📌 3. ACCIÓN: ACTUALIZAR SOLO LOS TOKENS
      // Útil para procesos de "refresco de token" (refresh token flow) sin necesidad de volver a pedir o sobrescribir los datos del usuario.
      setTokens: (access, refresh) => 
        set({ accessToken: access, refreshToken: refresh }),

      // 📌 4. ACCIÓN: CERRAR SESIÓN (LOGOUT)
      // Limpia todos los datos sensibles del estado, revirtiendo el store a su estado inicial.
      // ⚠️ Nota: Gracias al middleware 'persist', ejecutar esta acción también elimina automáticamente 
      // los datos guardados en el localStorage, garantizando una limpieza total.
      logout: () => 
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),
    }),
    
    // ⚠️ CONFIGURACIÓN DEL MIDDLEWARE PERSIST
    // 'name': Es la clave exacta bajo la cual se guardará el objeto JSON en el localStorage del navegador.
    // Puedes verificarlo en las DevTools del navegador -> Application -> Local Storage -> 'factu-auth-storage'.
    { name: 'factu-auth-storage' }
  )
);