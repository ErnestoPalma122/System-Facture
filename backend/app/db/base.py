#app\db\base.py
"""
Base de datos y configuración de modelos.
Este archivo importa todos los modelos para que Alembic los detecte.
"""

from app.core.database import Base

# Importar todos los modelos desde el módulo central
from app.modules.usuarios.models import (
    Usuario,
    Departamento,
    Rol,
    Sesion
)
# Importar modelos de productos
from app.modules.productos.modelsproducto import (
    Producto, 
    Categoria, 
    Precio, 
    Stock, 
    Bodega, 
    TipoProducto
)
#importa modelo de probeedores
from app.modules.proveedores.models_proveedor import(
    Proveedor
)
#importa modelos de inventario
from app.modules.inventario.models_inventario import(
    Ingreso,
    EstadoItems,
    Items,
    Estado_Ingreso
)
#Importa modelo Clientes
from app.modules.clientes.modelsclientes import(
    Cliente
)

#Lista de Exportaciones
__all__ = [
    "Base",
    "Usuario",
    "Departamento",
    "Rol",
    "Sesion",
    "Producto",
    "Categoria",
    "Precio",
    "Stock",
    "Bodega",
    "TipoProducto",
    "Proveedor",
    "Ingreso",
    "EstadoItems",
    "Items",
    "Estado_Ingreso",
    "Cliente"
]