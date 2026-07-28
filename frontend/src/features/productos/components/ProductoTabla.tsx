import { useState, useEffect } from 'react';
import { Producto, Categoria } from '../api/producto_api';

interface ProductoTablaProps {
  productos: Producto[];
  categorias: Categoria[];
  isLoading: boolean;
  onEditar: (producto: Producto) => void;
}

export function ProductoTabla({ productos, categorias, isLoading, onEditar }: ProductoTablaProps) {
  const [terminoBusqueda, setTerminoBusqueda] = useState('');
  const [productosFiltrados, setProductosFiltrados] = useState<Producto[]>(productos);

  // Función para obtener el nombre de la categoría buscando por su ID
  const obtenerNombreCategoria = (categoriaId: number | null) => {
    if (!categoriaId) return 'Sin categoría';
    const categoria = categorias.find(c => c.id === categoriaId);
    return categoria ? categoria.nombre : 'Sin categoría';
  };

  // Filtrado con debounce: espera 500ms después de que el usuario deje de escribir
  useEffect(() => {
    const timer = setTimeout(() => {
      if (terminoBusqueda.length >= 2) {
        const termino = terminoBusqueda.toLowerCase();
        const filtrados = productos.filter((prod) => 
          prod.codigo.toLowerCase().includes(termino) ||
          prod.nombre.toLowerCase().includes(termino) ||
          (prod.marca && prod.marca.toLowerCase().includes(termino))
        );
        setProductosFiltrados(filtrados);
      } else if (terminoBusqueda === '') {
        // Si borra todo, mostrar todos los productos
        setProductosFiltrados(productos);
      }
      // Si tiene 1 letra o menos, no hacer nada (mantener lista actual)
    }, 500); // Espera 500ms (medio segundo)

    return () => clearTimeout(timer);
  }, [terminoBusqueda, productos]);

  if (isLoading) {
    return <div className="p-8 text-center text-gray-600">Cargando productos...</div>;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-lg font-bold text-gray-800">Listado de Productos</h2>
        
        {/* Barra de búsqueda dinámica */}
        <div className="relative w-full sm:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={terminoBusqueda}
            onChange={(e) => setTerminoBusqueda(e.target.value)}
            placeholder="Buscar por código o nombre..."
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out"
          />
          {terminoBusqueda.length > 0 && terminoBusqueda.length < 2 && (
            <p className="text-xs text-gray-500 mt-1 pl-1">Mínimo 2 caracteres para buscar</p>
          )}
        </div>
      </div>
      
      <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center text-sm text-gray-600">
        <span>
          {terminoBusqueda.length >= 2 
            ? `Mostrando ${productosFiltrados.length} de ${productos.length} productos`
            : `Total: ${productos.length} productos`
          }
        </span>
        {terminoBusqueda.length >= 2 && (
          <button 
            onClick={() => setTerminoBusqueda('')}
            className="text-blue-600 hover:text-blue-800 text-xs font-medium"
          >
            Limpiar búsqueda
          </button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Código</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Categoría</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tipo</th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Precio Público</th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th className="px-6 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {productosFiltrados.length > 0 ? (
              productosFiltrados.map((prod) => (
                <tr key={prod.id} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{prod.codigo}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    <div className="font-medium">{prod.nombre}</div>
                    {prod.marca && <div className="text-xs text-gray-500">{prod.marca}</div>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {obtenerNombreCategoria(prod.categoria_id)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    <span className={`px-2 py-1 text-xs rounded-full ${prod.tipo === 'BIEN' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                      {prod.tipo}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
                    ${Number(prod.precio?.precio_publico || 0).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      prod.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {prod.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <button 
                      onClick={() => onEditar(prod)}
                      className="text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors duration-150 text-sm font-medium"
                    >
                      ✏️ Editar
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                  {terminoBusqueda.length >= 2 ? (
                    <>
                      <p className="text-lg font-medium">No se encontraron productos</p>
                      <p className="text-sm text-gray-400 mt-1">
                        Intenta con otro término de búsqueda o limpia el filtro
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="text-lg font-medium">No hay productos registrados.</p>
                      <p className="text-sm text-gray-400 mt-1">Usa el formulario de arriba para crear el primero.</p>
                    </>
                  )}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}