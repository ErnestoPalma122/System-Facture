//frontend\src\features\productos\components\ProductoVistaGeneral.tsx
import { useState, useEffect } from 'react';
import { useProductos } from '../hooks/useProductos';
import { Producto } from '../api/producto_api';
import { ProductoFormulario } from './ProductoFormulario';
import { ProductoTabla } from './ProductoTabla';

export function ProductoVistaGeneral() {
  const { productos, categorias, isLoading } = useProductos();
  const [mensajeExito, setMensajeExito] = useState('');
  const [productoAEditar, setProductoAEditar] = useState<Producto | null>(null);

  // Cuando se selecciona un producto para editar, hacemos scroll suave hacia arriba
  useEffect(() => {
    if (productoAEditar) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [productoAEditar]);

  const handleGuardado = () => {
    setMensajeExito(productoAEditar ? '✅ Producto actualizado exitosamente.' : '✅ Producto creado exitosamente.');
    setProductoAEditar(null); // Salir del modo edición
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const handleCancelado = () => {
    setProductoAEditar(null);
  };

  const handleEditar = (producto: Producto) => {
    setProductoAEditar(producto);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Productos</h1>
      </div>

      {mensajeExito && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2 animate-pulse">
          {mensajeExito}
        </div>
      )}

      {/* Formulario estático en la parte superior (modo creación o edición) */}
      <ProductoFormulario 
        onGuardado={handleGuardado} 
        onCancelado={handleCancelado}
        productoAEditar={productoAEditar} 
      />

      {/* Tabla de datos en la parte inferior */}
      <ProductoTabla 
        productos={productos} 
        categorias={categorias}
        isLoading={isLoading} 
        onEditar={handleEditar}
      />
    </div>
  );
}