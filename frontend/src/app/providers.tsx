// frontend\src\app\providers.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { ReactNode } from 'react';

//Es un componente emboltorio, lo que hace es dar contexto de peticiones
// HTTP lo que hace que se pueda utilizar useQuery o useMutation.
export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
