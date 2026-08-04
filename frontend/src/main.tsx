// frontend\src\main.tsx

// 📌 PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
// Este archivo es el primero que se ejecuta cuando el navegador carga la app.
// Su responsabilidad es montar (renderizar) todo el árbol de componentes de React en el DOM.

// 🔗 Importaciones de React y ReactDOM (el puente entre React y el navegador)
import React from 'react';
import ReactDOM from 'react-dom/client';

// 🔗 BrowserRouter: Habilita el enrutamiento basado en la API History del navegador 
// (permite usar URLs limpias como /bodegas en lugar de /#/bodegas)
import { BrowserRouter } from 'react-router-dom';

// 🔗 Providers: Componente wrapper que inyecta el contexto de React Query 
// (y cualquier otro proveedor global futuro) a toda la aplicación
import { Providers } from './app/providers';

// 🔗 App: Componente raíz que contiene la lógica de enrutamiento
import App from './app/App';

// 🔗 Estilos globales: Importa Tailwind CSS y cualquier estilo base definido globalmente
import './index.css';

// 📌 MONTAJE DE LA APLICACIÓN EN EL DOM
// ReactDOM.createRoot crea una raíz de React en el elemento HTML con id="root" (definido en index.html).
// El operador '!' (non-null assertion) le dice a TypeScript que estamos seguros de que el elemento existe.
ReactDOM.createRoot(document.getElementById('root')!).render(
  // 📌 MODO ESTRICTO DE REACT (React.StrictMode)
  // 🔗 Herramienta de desarrollo que ayuda a identificar prácticas inseguras o antipatrones.
  // En desarrollo, renderiza los componentes dos veces para detectar efectos secundarios impuros.
  // En producción, se elimina automáticamente y no afecta el rendimiento.
  <React.StrictMode>
    
    {/* 📌 1. ENVOLTURA DE ENRUTAMIENTO (BrowserRouter) */}
    {/* Debe estar en el nivel más alto del árbol para que TODA la aplicación pueda acceder a las funciones de enrutamiento 
        (useNavigate, useParams, Link, etc.) */}
    <BrowserRouter>
      
      {/* 📌 2. ENVOLTURA DE PROVEEDORES GLOBALES (Providers) */}
      {/* Inyecta el QueryClientProvider (React Query) y cualquier otro contexto global necesario.
          El orden es importante: BrowserRouter debe envolver a Providers para que las peticiones HTTP 
          puedan acceder a la URL actual si es necesario. */}
      <Providers>
        
        {/* 📌 3. COMPONENTE RAÍZ (App) */}
        {/* Este componente renderiza el <Router /> que contiene toda la lógica de navegación 
            y protección de rutas de la aplicación. */}
        <App />
        
      </Providers>
    </BrowserRouter>
  </React.StrictMode>
);