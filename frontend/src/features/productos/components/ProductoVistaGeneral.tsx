//frontend\src\features\productos\components\ProductoVistaGeneral.tsx

import { useState, useEffect } from 'react';
import { useProductos } from '../hooks/useProductos';
import { Producto } from '../api/producto_api';
import { ProductoFormulario } from './ProductoFormulario';
import { ProductoTabla } from './ProductoTabla';

export function ProductoVistaGeneral() {
  // DOCUMENTACIÓN: Consumo de datos y estados de carga desde el hook personalizado.
  const { productos, categorias, isLoading } = useProductos();
  
  // DOCUMENTACIÓN: Estados locales para manejar la retroalimentación visual y el modo edición.
  const [mensajeExito, setMensajeExito] = useState('');
  const [productoAEditar, setProductoAEditar] = useState<Producto | null>(null);

  // DOCUMENTACIÓN: Efecto para hacer scroll suave hacia arriba cuando se entra en modo edición,
  // mejorando la experiencia de usuario al traer el formulario a la vista.
  useEffect(() => {
    if (productoAEditar) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [productoAEditar]);

  // DOCUMENTACIÓN: Manejador de éxito post-guardado. Muestra mensaje, limpia modo edición y oculta mensaje a los 3s.
  const handleGuardado = () => {
    setMensajeExito(productoAEditar ? '✅ Producto actualizado exitosamente.' : '✅ Producto creado exitosamente.');
    setProductoAEditar(null); 
    setTimeout(() => setMensajeExito(''), 3000);
  };

  // DOCUMENTACIÓN: Manejador para cancelar la edición y limpiar el estado.
  const handleCancelado = () => {
    setProductoAEditar(null);
  };

  // DOCUMENTACIÓN: Manejador que activa el modo edición y carga los datos del producto seleccionado.
  const handleEditar = (producto: Producto) => {
    setProductoAEditar(producto);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Productos</h1>
      </div>

      {/* DOCUMENTACIÓN: Banner de notificación de éxito con animación de pulso */}
      {mensajeExito && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2 animate-pulse">
          {mensajeExito}
        </div>
      )}

      {/* DOCUMENTACIÓN: Renderizado condicional del formulario. Sirve tanto para crear como para editar */}
      <ProductoFormulario 
        onGuardado={handleGuardado} 
        onCancelado={handleCancelado}
        productoAEditar={productoAEditar} 
      />

      {/* DOCUMENTACIÓN: Renderizado de la tabla de datos que consume la lista filtrada o completa */}
      <ProductoTabla 
        productos={productos} 
        categorias={categorias}
        isLoading={isLoading} 
        onEditar={handleEditar}
      />
    </div>
  );
}