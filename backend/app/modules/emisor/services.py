# app/modules/emisor/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.emisor.models import Emisor
from app.modules.emisor.schemas import EmisorCreate, EmisorUpdate
import logging

logger = logging.getLogger(__name__)

def get_emisor_activo(db: Session) -> Emisor | None:
    """Obtiene la configuración del emisor activo"""
    logger.info("🔍 Buscando configuración del emisor activo...")
    emisor = db.query(Emisor).filter(Emisor.activo == True).first()
    
    if emisor:
        logger.info(f"✅ Emisor encontrado: ID={emisor.id}, Nombre={emisor.nombre}")
    else:
        logger.warning("⚠️ No se encontró configuración de emisor activo")
    return emisor

def guardar_emisor(db: Session, emisor_data: EmisorCreate | EmisorUpdate) -> Emisor:
    """
    Crea o actualiza la configuración del emisor (Patrón Upsert).
    Todos los campos son obligatorios, por lo que se reemplaza o crea por completo.
    """
    logger.info("=" * 60)
    logger.info("💾 INICIANDO PROCESO DE GUARDADO DE EMISOR")
    logger.info("=" * 60)
    
    emisor_existente = get_emisor_activo(db)
    
    # Convertimos los datos a diccionario (todos los campos están presentes, incluido correo_interno)
    datos = emisor_data.model_dump()
    
    # Extraemos la dirección anidada para guardarla en columnas planas del modelo
    direccion = datos.pop("direccion")
    datos["cod_departamento"] = direccion["cod_departamento"]
    datos["desc_departamento"] = direccion["desc_departamento"]
    datos["cod_municipio"] = direccion["cod_municipio"]
    datos["desc_municipio"] = direccion["desc_municipio"]
    datos["cod_distrito"] = direccion["cod_distrito"]
    datos["desc_distrito"] = direccion["desc_distrito"]
    datos["dirr_complemento"] = direccion["complemento"]  # Coincide con tu modelo (doble 'r')

    try:
        if emisor_existente:
            logger.info(f"🔄 Actualizando emisor existente (ID: {emisor_existente.id})")
            for campo, valor in datos.items():
                setattr(emisor_existente, campo, valor)
            db.commit()
            db.refresh(emisor_existente)
            logger.info("✅ EMISOR ACTUALIZADO EXITOSAMENTE")
            return emisor_existente
        else:
            logger.info("🆕 Creando nueva configuración de emisor")
            nuevo_emisor = Emisor(**datos, activo=True)
            db.add(nuevo_emisor)
            db.commit()
            db.refresh(nuevo_emisor)
            logger.info(f"✅ EMISOR CREADO EXITOSAMENTE (ID: {nuevo_emisor.id})")
            return nuevo_emisor

    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD (ej. NIT duplicado): {str(e)}")
        raise ValueError("Error de integridad: Verifica que el NIT no esté registrado o que los datos sean válidos.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError("Error interno de la base de datos al guardar el emisor.")