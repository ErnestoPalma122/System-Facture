// frontend\src\app\providers.tsx

import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { ReactNode } from 'react';

// 📌 COMPONENTE PROVEEDOR (WRAPPER)
// Este componente actúa como un contenedor de contexto para toda la aplicación.
// Su propósito es inyectar las dependencias necesarias (en este caso, React Query) 
// a todos los componentes hijos que estén envueltos por él.

// 🔗 Tipado de props: 'children' representa cualquier nodo JSX (componentes, elementos) 
// que se renderice dentro de este proveedor.
export function Providers({ children }: { children: ReactNode }) {
  return (
    // 📌 QueryClientProvider: Habilita el uso de hooks como useQuery y useMutation 
    // en cualquier componente hijo, gestionando el estado del servidor, caché y reintentos.
    // 🔗 'client={queryClient}': Se pasa la instancia configurada (probablemente con 
    // tiempos de caché, reintentos y configuraciones globales definidas en '@/lib/queryClient').
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}