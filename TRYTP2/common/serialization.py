# common/serialization.py
"""Serialización y deserialización de datos"""

import pickle
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Serializer:
    """
    Serializador de datos con soporte para múltiples formatos
    Por defecto usa pickle para máxima compatibilidad
    """
    
    @staticmethod
    def serialize(data: Any, format: str = 'pickle') -> bytes:
        """
        Serializar datos a bytes
        
        Args:
            data: Datos a serializar
            format: Formato ('pickle' o 'json')
            
        Returns:
            Datos serializados (bytes)
        """
        try:
            if format == 'pickle':
                return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            elif format == 'json':
                json_str = json.dumps(data, ensure_ascii=False)
                return json_str.encode('utf-8')
            else:
                raise ValueError(f"Unknown format: {format}")
                
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            raise
    
    @staticmethod
    def deserialize(data: bytes, format: str = 'pickle') -> Any:
        """
        Deserializar datos desde bytes
        
        Args:
            data: Datos serializados (bytes)
            format: Formato ('pickle' o 'json')
            
        Returns:
            Datos deserializados
        """
        try:
            if format == 'pickle':
                return pickle.loads(data)
            elif format == 'json':
                json_str = data.decode('utf-8')
                return json.loads(json_str)
            else:
                raise ValueError(f"Unknown format: {format}")
                
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            raise
    
    @staticmethod
    def serialize_safe(data: Dict[str, Any]) -> bytes:
        """
        Serializar de forma segura, intentando pickle y fallback a JSON
        
        Args:
            data: Diccionario de datos
            
        Returns:
            Datos serializados (bytes)
        """
        try:
            return Serializer.serialize(data, format='pickle')
        except:
            logger.warning("Pickle serialization failed, falling back to JSON")
            try:
                return Serializer.serialize(data, format='json')
            except:
                logger.error("Both serialization methods failed")
                raise
    
    @staticmethod
    def deserialize_safe(data: bytes) -> Any:
        """
        Deserializar de forma segura, intentando pickle y fallback a JSON
        
        Args:
            data: Datos serializados (bytes)
            
        Returns:
            Datos deserializados
        """
        try:
            return Serializer.deserialize(data, format='pickle')
        except:
            logger.warning("Pickle deserialization failed, trying JSON")
            try:
                return Serializer.deserialize(data, format='json')
            except:
                logger.error("Both deserialization methods failed")
                raise
