//frontend\src\features\proveedores\components\filtro_busqueda_proveedores.tsx
import { useState, useEffect } from 'react';

interface FiltroBusquedaProveedoresProps {
  onSearch: (term: string) => void;
  isLoading: boolean;
}

export function FiltroBusquedaProveedores({ onSearch, isLoading }: FiltroBusquedaProveedoresProps) {
  const [term, setTerm] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      // Solo ejecutamos la búsqueda si el usuario escribió 2 o más letras, 
      // o si borró todo el texto (para restaurar la lista completa).
      if (term.length >= 2 || term === '') {
        onSearch(term);
      }
    }, 500); // Espera 500ms después de que el usuario deja de escribir

    return () => clearTimeout(timer);
  }, [term, onSearch]);

  return (
    <div className="relative w-full max-w-md">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        {isLoading ? (
          // Spinner de carga mientras busca
          <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          // Lupa normal cuando no está buscando
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        )}
      </div>
      <input
        type="text"
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        placeholder="Buscar por nombre (mín. 2 letras)..."
        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out"
      />
    </div>
  );
}