//frontend\src\lib\queryClient.ts

//Manejara los datos por defecto en toda la app que se configuro en providers.tsx
import { QueryClient } from '@tanstack/react-query';


//
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // Datos frescos por 5 minutos
      retry: 1, // Reintentar 1 vez si falla
      refetchOnWindowFocus: false, // No recargar al cambiar de pestaña
    },
  },
});