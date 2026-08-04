// frontend\src\app\App.tsx

// 📌 COMPONENTE RAÍZ DE LA APLICACIÓN
// Este es el punto de entrada principal de la UI de React.
// Su única responsabilidad es renderizar el componente <Router />, 
// delegando toda la lógica de navegación y enrutamiento a ese componente.

import { Router } from './router';

function App() {
  // 📌 Renderizado del enrutador principal.
  // Al estar aquí, cualquier cambio en la URL será manejado por <Router />.
  return <Router />;
}

// 📌 Exportación por defecto para ser importado en el index.tsx o main.tsx
export default App;