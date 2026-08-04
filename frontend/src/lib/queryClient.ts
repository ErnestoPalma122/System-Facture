// frontend\src\lib\queryClient.ts

// 📌 CONFIGURACIÓN GLOBAL DE REACT QUERY (TANSTACK QUERY)
// Este archivo define el cliente que manejará el estado del servidor (caché, reintentos, sincronización) 
// en toda la aplicación. Se inyecta en el árbol de componentes a través de <Providers.tsx>.

import { QueryClient } from '@tanstack/react-query';

// 📌 INSTANCIACIÓN DEL CLIENTE CON OPCIONES POR DEFECTO
// Estas opciones se aplican a TODAS las consultas (useQuery) de la app, a menos que se sobrescriban explícitamente.
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 🔗 staleTime: 5 minutos (1000ms * 60s * 5min).
      // Significa que los datos se consideran "frescos" durante 5 minutos. 
      // React Query NO hará peticiones de fondo automáticas si los datos tienen menos de 5 minutos de antigüedad.
      staleTime: 1000 * 60 * 5, 
      
      // 🔗 retry: 1.
      // Si una petición falla (ej: error de red temporal), React Query la reintentará automáticamente 1 vez adicional 
      // antes de considerar la consulta como fallida y lanzar el error al componente.
      retry: 1, 
      
      // 🔗 refetchOnWindowFocus: false.
      // ⚠️ Desactiva la recarga automática de datos cuando el usuario cambia de pestaña del navegador y vuelve.
      // Esto es una decisión de UX importante: evita que la interfaz muestre estados de "carga" inesperados 
      // o parpadeos cuando el usuario solo estaba revisando otra pestaña momentáneamente.
      refetchOnWindowFocus: false, 
    },
  },
});