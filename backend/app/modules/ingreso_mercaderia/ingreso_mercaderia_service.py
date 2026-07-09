# app/modules/ingreso_mercaderia/ingreso_mercaderia_service.py
"""
Servicio para el módulo de ingreso de mercadería.
Implementa lógica transaccional robusta con manejo de errores avanzado.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.inventario.models_inventario import Ingreso, Items, EstadoItems, Estado_Ingreso
from app.modules.productos.modelsproducto import Producto
from app.modules.proveedores.models_proveedor import Proveedor
from app.modules.productos.modelsproducto import Bodega
from app.modules.productos.modelsproducto import Stock
from app.modules.ingreso_mercaderia.ingreso_mercaderia_shemas import IngresoMercaderiaCreate
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IngresoMercaderiaService:
    """
    Servicio para gestionar ingresos de mercadería.
    Implementa transacciones atómicas con rollback automático en caso de error.
    """
    
    # Constantes de configuración
    DEFAULT_ESTADO_INGRESO_ID = 8  # COMPLETO PROCESADO
    DEFAULT_ESTADO_ITEM_ID = 1     # DISPONIBLE
    
    @staticmethod
    def validar_referencias(db: Session, data: IngresoMercaderiaCreate) -> dict:
        """
        Valida que todas las referencias existan en la base de datos.
        
        Args:
            db: Sesión de base de datos
            data: Datos del ingreso a validar
            
        Returns:
            dict: Diccionario con las entidades validadas
            
        Raises:
            ValueError: Si alguna referencia no existe
        """
        logger.info("=" * 60)
        logger.info("🔍 VALIDANDO REFERENCIAS")
        logger.info("=" * 60)
        
        referencias = {}
        
        # Validar proveedor
        logger.info(f"📦 Validando proveedor ID: {data.proveedor_id}")
        proveedor = db.query(Proveedor).filter(Proveedor.id == data.proveedor_id).first()
        if not proveedor:
            logger.error(f"❌ Proveedor ID {data.proveedor_id} NO existe")
            raise ValueError(f"El proveedor con ID {data.proveedor_id} ese proveedor que  esta ingresando no existe")
        referencias['proveedor'] = proveedor
        logger.info(f"✅ Proveedor válido: {proveedor.nombre}")
        
        # Validar estado_ingreso
        logger.info(f"📊 Validando estado_ingreso ID: {data.estado_ingreso_id}")
        estado_ingreso = db.query(Estado_Ingreso).filter(Estado_Ingreso.id == data.estado_ingreso_id).first()
        if not estado_ingreso:
            logger.error(f"❌ Estado ingreso ID {data.estado_ingreso_id} NO existe")
            raise ValueError(f"El estado de ingreso con ID {data.estado_ingreso_id} no existe")
        referencias['estado_ingreso'] = estado_ingreso
        logger.info(f"✅ Estado ingreso válido: {estado_ingreso.nombre_estado}")
        
        # Validar estado_items (default = 1)
        logger.info(f"📊 Validando estado_items ID: {IngresoMercaderiaService.DEFAULT_ESTADO_ITEM_ID}")
        estado_item = db.query(EstadoItems).filter(EstadoItems.id == IngresoMercaderiaService.DEFAULT_ESTADO_ITEM_ID).first()
        if not estado_item:
            logger.error(f"❌ Estado items ID {IngresoMercaderiaService.DEFAULT_ESTADO_ITEM_ID} NO existe")
            raise ValueError(f"El estado de items con ID {IngresoMercaderiaService.DEFAULT_ESTADO_ITEM_ID} no existe")
        referencias['estado_item'] = estado_item
        logger.info(f"✅ Estado items válido: {estado_item.estado}")
        
        # Validar productos y bodegas de cada item
        productos_ids = set()
        bodegas_ids = set()
        
        for idx, item in enumerate(data.items, 1):
            logger.info(f"📦 Validando item {idx}/{len(data.items)}")
            
            # Validar producto
            if item.producto_id not in productos_ids:
                logger.info(f"   🔍 Validando producto ID: {item.producto_id}")
                producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
                if not producto:
                    logger.error(f"   ❌ Producto ID {item.producto_id} NO existe")
                    raise ValueError(f"El producto con ID {item.producto_id} no existe (item {idx})")
                productos_ids.add(item.producto_id)
                logger.info(f"   ✅ Producto válido: {producto.nombre}")
            
            # Validar bodega
            if item.bodega_id not in bodegas_ids:
                logger.info(f"   🏭 Validando bodega ID: {item.bodega_id}")
                bodega = db.query(Bodega).filter(Bodega.id == item.bodega_id).first()
                if not bodega:
                    logger.error(f"   ❌ Bodega ID {item.bodega_id} NO existe")
                    raise ValueError(f"La bodega con ID {item.bodega_id} no existe (item {idx})")
                bodegas_ids.add(item.bodega_id)
                logger.info(f"   ✅ Bodega válida: {bodega.nombre}")
        
        logger.info("=" * 60)
        logger.info("✅ TODAS LAS REFERENCIAS SON VÁLIDAS")
        logger.info("=" * 60)
        
        return referencias
    
    @staticmethod
    def crear_ingreso(db: Session, data: IngresoMercaderiaCreate, usuario_id: int) -> Ingreso:
        """
        Crea un nuevo ingreso de mercadería con transacción atómica.
    
        Args:
            db: Sesión de base de datos
            data: Datos del ingreso a crear
            usuario_id: ID del usuario que realiza el ingreso (de la sesión actual)
        
        Returns:
            Ingreso: Objeto de ingreso creado con sus items
        """
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO CREACIÓN DE INGRESO DE MERCADERÍA")
        logger.info("=" * 60)
        logger.info(f"👤 Usuario ID: {usuario_id}")  # ← NUEVO
        logger.info(f"📦 Proveedor ID: {data.proveedor_id}")
        logger.info(f"📄 DTE: {data.dte}")
        logger.info(f"🔖 Sello: {data.sello}")
        logger.info(f"📊 Estado Ingreso ID: {data.estado_ingreso_id}")
        logger.info(f"📦 Total items: {len(data.items)}")
        logger.info("=" * 60)
    
        try:
            # PASO 1: Validar referencias
            referencias = IngresoMercaderiaService.validar_referencias(db, data)
        
            # PASO 2: Crear cabecera (ingresos)
            logger.info("=" * 60)
            logger.info("💾 PASO 2: CREANDO CABECERA DE INGRESO")
            logger.info("=" * 60)
        
            nuevo_ingreso = Ingreso(
                proveedor_id=data.proveedor_id,
                usuario_id=usuario_id,  # ← NUEVO: Asignar usuario de la sesión
                dte=data.dte,
                sello=data.sello,
                codigo_generacion=data.codigo_generacion,
                cotizacion=data.cotizacion,
                observaciones=data.observaciones,
                estado_ingreso_id=data.estado_ingreso_id,
                activo=True
            )
        
            db.add(nuevo_ingreso)
            db.flush()
        
            logger.info(f"✅ Cabecera creada: ID={nuevo_ingreso.id}")
            logger.info(f"👤 Usuario ID: {nuevo_ingreso.usuario_id}")  # ← NUEVO
            logger.info(f"📅 Fecha: {nuevo_ingreso.fecha}")
        
        # ... resto del código permanece igual ...
            
            # PASO 3: Crear detalle (items) con series
            logger.info("=" * 60)
            logger.info("💾 PASO 3: CREANDO ITEMS CON SERIES")
            logger.info("=" * 60)
            
            total_series_creadas = 0
            items_creados = []
            
            for idx, item_data in enumerate(data.items, 1):
                logger.info(f"📦 Procesando item {idx}/{len(data.items)}")
                logger.info(f"   - Producto ID: {item_data.producto_id}")
                logger.info(f"   - Bodega ID: {item_data.bodega_id}")
                logger.info(f"   - Series: {len(item_data.series)} unidades")
                
                # Crear un item por cada serie
                for serie_idx, serie in enumerate(item_data.series, 1):
                    logger.info(f"   🔢 Creando serie {serie_idx}/{len(item_data.series)}: {serie}")
                    
                    nuevo_item = Items(
                        ingreso_id=nuevo_ingreso.id,
                        producto_id=item_data.producto_id,
                        bodega_id=item_data.bodega_id,
                        estado_item_id=IngresoMercaderiaService.DEFAULT_ESTADO_ITEM_ID,
                        serie=serie,
                        dias_stock=item_data.dias_stock,
                        activo=True
                    )
                    
                    db.add(nuevo_item)
                    items_creados.append(nuevo_item)
                    total_series_creadas += 1
                    
                    logger.info(f"   ✅ Serie creada: {serie}")
                
                logger.info(f"✅ Item {idx} completado: {len(item_data.series)} series creadas")
            
            logger.info(f"✅ Total items creados: {total_series_creadas}")
            
            # PASO 4: Actualizar stock
            logger.info("=" * 60)
            logger.info("💾 PASO 4: ACTUALIZANDO STOCK")
            logger.info("=" * 60)
            
            # Agrupar por producto_id y bodega_id para optimizar actualizaciones
            stock_updates = {}
            for item_data in data.items:
                key = (item_data.producto_id, item_data.bodega_id)
                if key not in stock_updates:
                    stock_updates[key] = 0
                stock_updates[key] += len(item_data.series)
            
            # Actualizar o crear stock para cada combinación producto-bodega
            for (producto_id, bodega_id), cantidad in stock_updates.items():
                logger.info(f"📊 Actualizando stock: Producto {producto_id}, Bodega {bodega_id}, Cantidad +{cantidad}")
                
                # Buscar stock existente
                stock_existente = db.query(Stock).filter(
                    Stock.producto_id == producto_id,
                    Stock.bodega_id == bodega_id
                ).first()
                
                if stock_existente:
                    # Actualizar stock existente
                    stock_existente.cantidad += cantidad
                    logger.info(f"   ✅ Stock actualizado: {stock_existente.cantidad - cantidad} → {stock_existente.cantidad}")
                else:
                    # Crear nuevo stock
                    logger.info(f"   🆕 Creando nuevo stock")
                    nuevo_stock = Stock(
                        producto_id=producto_id,
                        bodega_id=bodega_id,
                        cantidad=cantidad,
                        cantidad_minima=0,
                        activo=True
                    )
                    db.add(nuevo_stock)
                    logger.info(f"   ✅ Stock creado: {cantidad} unidades")
            
            # PASO 5: Commit transacción
            logger.info("=" * 60)
            logger.info("💾 PASO 5: COMMIT TRANSACCIÓN")
            logger.info("=" * 60)
            
            db.commit()
            db.refresh(nuevo_ingreso)
            
            logger.info("=" * 60)
            logger.info("✅ INGRESO DE MERCADERÍA CREADO EXITOSAMENTE")
            logger.info("=" * 60)
            logger.info(f"📦 Ingreso ID: {nuevo_ingreso.id}")
            logger.info(f"📅 Fecha: {nuevo_ingreso.fecha}")
            logger.info(f"📦 Total items: {total_series_creadas}")
            logger.info(f"🏭 Productos únicos: {len(stock_updates)}")
            logger.info("=" * 60)
            
            return nuevo_ingreso
            
        except ValueError as e:
            # Error de validación - rollback
            logger.error("=" * 60)
            logger.error(f"❌ ERROR DE VALIDACIÓN: {str(e)}")
            logger.error("=" * 60)
            db.rollback()
            raise
            
        except IntegrityError as e:
            # Error de integridad - rollback
            logger.error("=" * 60)
            logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
            logger.error("=" * 60)
            db.rollback()
            raise ValueError(f"Error de integridad en la base de datos: {str(e)}")
            
        except SQLAlchemyError as e:
            # Error de base de datos - rollback
            logger.error("=" * 60)
            logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
            logger.error("=" * 60)
            db.rollback()
            raise ValueError(f"Error en la base de datos: {str(e)}")
            
        except Exception as e:
            # Error inesperado - rollback
            logger.error("=" * 60)
            logger.error(f"❌ ERROR INESPERADO: {str(e)}")
            logger.error("=" * 60)
            db.rollback()
            raise ValueError(f"Error inesperado: {str(e)}")
    
    @staticmethod
    def obtener_ingreso_por_id(db: Session, ingreso_id: int) -> Ingreso:
        """
        Obtiene un ingreso por ID con sus items.
        
        Args:
            db: Sesión de base de datos
            ingreso_id: ID del ingreso a buscar
            
        Returns:
            Ingreso: Objeto de ingreso con sus items
            
        Raises:
            ValueError: Si el ingreso no existe
        """
        logger.info(f"🔍 Buscando ingreso ID: {ingreso_id}")
        
        ingreso = db.query(Ingreso).filter(Ingreso.id == ingreso_id).first()
        
        if not ingreso:
            logger.error(f"❌ Ingreso ID {ingreso_id} NO encontrado")
            raise ValueError(f"El ingreso con ID {ingreso_id} no existe")
        
        logger.info(f"✅ Ingreso encontrado: ID={ingreso.id}, Items={len(ingreso.items)}")
        
        return ingreso