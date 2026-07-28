# backend\seed_permisos.py
from app.core.database import SessionLocal
from app.modules.usuarios.models import Permiso, Rol, RolPermiso
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista completa de permisos asertivos definidos por módulo
PERMISOS_DATA = [
    # Módulo Dashboard
    {"codigo": "dashboard:leer", "nombre": "Ver Dashboard", "modulo": "dashboard"},
    
    # Módulo Bodegas
    {"codigo": "bodega:leer", "nombre": "Listar Bodegas", "modulo": "bodega"},
    {"codigo": "bodega:crear", "nombre": "Crear Bodega", "modulo": "bodega"},
    {"codigo": "bodega:actualizar", "nombre": "Actualizar Bodega", "modulo": "bodega"},
    
    # Módulo Usuarios
    {"codigo": "usuario:leer", "nombre": "Listar Usuarios", "modulo": "usuarios"},
    {"codigo": "usuario:crear", "nombre": "Crear Usuario", "modulo": "usuarios"},
    {"codigo": "usuario:actualizar", "nombre": "Actualizar Usuario", "modulo": "usuarios"},
    {"codigo": "usuario:desactivar", "nombre": "Desactivar Usuario", "modulo": "usuarios"},
    
    # Módulo Emisor (Configuración)
    {"codigo": "emisor:leer", "nombre": "Ver Configuración Emisor", "modulo": "emisor"},
    {"codigo": "emisor:actualizar", "nombre": "Actualizar Configuración Emisor", "modulo": "emisor"},
    
    # Módulo Catálogos
    {"codigo": "catalogo:leer", "nombre": "Ver Catálogos de Hacienda", "modulo": "catalogos"},

    # Módulo Categorías
    {"codigo": "categoria:leer", "nombre": "Listar Categorías", "modulo": "categorias"},
    {"codigo": "categoria:crear", "nombre": "Crear Categoría", "modulo": "categorias"},
    {"codigo": "categoria:actualizar", "nombre": "Actualizar Categoría", "modulo": "categorias"},
    
    # Módulo Stocks
    {"codigo": "stock:leer", "nombre": "Listar Stocks", "modulo": "stocks"},
    {"codigo": "stock:crear", "nombre": "Crear Stock", "modulo": "stocks"},
    {"codigo": "stock:actualizar", "nombre": "Actualizar Stock", "modulo": "stocks"},
    
    # Módulo Productos
    {"codigo": "producto:leer", "nombre": "Listar Productos", "modulo": "productos"},
    {"codigo": "producto:crear", "nombre": "Crear Producto", "modulo": "productos"},
    {"codigo": "producto:actualizar", "nombre": "Actualizar Producto", "modulo": "productos"},
    {"codigo": "producto:eliminar", "nombre": "Eliminar Producto", "modulo": "productos"},
    {"codigo": "producto:actualizar_precio", "nombre": "Actualizar Precio de Producto", "modulo": "productos"},

    # Módulo Clientes
    {"codigo": "cliente:leer", "nombre": "Listar Clientes", "modulo": "clientes"},
    {"codigo": "cliente:crear", "nombre": "Crear Cliente", "modulo": "clientes"},
    {"codigo": "cliente:actualizar", "nombre": "Actualizar Cliente", "modulo": "clientes"},
    {"codigo": "cliente:eliminar", "nombre": "Eliminar/Desactivar Cliente", "modulo": "clientes"},

    # ✅ NUEVO: Módulo Inventario (Estados de Items)
    {"codigo": "estado_item:leer", "nombre": "Listar Estados de Items", "modulo": "inventario"},
    {"codigo": "estado_item:crear", "nombre": "Crear Estado de Item", "modulo": "inventario"},
    {"codigo": "estado_item:actualizar", "nombre": "Actualizar Estado de Item", "modulo": "inventario"},
    
    # ✅ NUEVO: Módulo Inventario (Items)
    {"codigo": "item:leer", "nombre": "Listar Items", "modulo": "inventario"},
    {"codigo": "item:crear", "nombre": "Crear Item", "modulo": "inventario"},
    {"codigo": "item:actualizar", "nombre": "Actualizar Item", "modulo": "inventario"},
    
    # ✅ NUEVO: Módulo Inventario (Ingresos)
    {"codigo": "ingreso:leer", "nombre": "Listar Ingresos", "modulo": "inventario"},
    {"codigo": "ingreso:crear", "nombre": "Crear Ingreso", "modulo": "inventario"},
    {"codigo": "ingreso:actualizar", "nombre": "Actualizar Ingreso", "modulo": "inventario"},
    {"codigo": "ingreso:eliminar", "nombre": "Eliminar Ingreso", "modulo": "inventario"},
]

def seed_permisos():
    logger.info("🚀 Iniciando seed de permisos...")
    db = SessionLocal()
    
    try:
        # 1. Crear permisos si no existen
        permisos_creados = {}
        for p_data in PERMISOS_DATA:
            permiso = db.query(Permiso).filter(Permiso.codigo == p_data["codigo"]).first()
            if not permiso:
                permiso = Permiso(**p_data)
                db.add(permiso)
                logger.info(f"✅ Permiso creado: {p_data['codigo']}")
            permisos_creados[p_data["codigo"]] = permiso
        
        db.commit()
        logger.info("✅ Todos los permisos están registrados en la base de datos.")

        # 2. Asignar TODOS los permisos a los administradores (ID 1 y 2)
        roles_administradores = db.query(Rol).filter(Rol.id.in_([1, 2])).all()
        
        for rol in roles_administradores:
            logger.info(f"🔄 Asignando permisos al rol: {rol.nombre} (ID: {rol.id})")
            for permiso in permisos_creados.values():
                existe = db.query(RolPermiso).filter(
                    RolPermiso.rol_id == rol.id,
                    RolPermiso.permiso_id == permiso.id
                ).first()
                
                if not existe:
                    db.add(RolPermiso(rol_id=rol.id, permiso_id=permiso.id))
            
            logger.info(f"✅ Todos los permisos asignados exitosamente a {rol.nombre}")

        db.commit()
        logger.info("🎉 Seed de permisos completado exitosamente.")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error durante el seed de permisos: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_permisos()