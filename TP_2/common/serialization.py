"""
Módulo de Serialización (SRP)
Maneja la serialización y deserialización de datos para comunicación.
"""

import json
from typing import Dict, Any

def serialize_data(data: Dict[str, Any]) -> bytes:
    """Serializa un diccionario a bytes (JSON UTF-8)."""
    try:
        return json.dumps(data, ensure_ascii=False).encode('utf-8')
    except TypeError as e:
        print(f"Error de serialización: {e}. Objeto no serializable: {str(data)[:200]}")
        error_data = {"serialization_error": str(e), "original_data_snippet": str(data)[:200]}
        return json.dumps(error_data, ensure_ascii=False).encode('utf-8')

def deserialize_data(byte_data: bytes) -> Dict[str, Any]:
    """Deserializa bytes (JSON UTF-8) a un diccionario."""
    try:
        return json.loads(byte_data.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error de deserialización: {e}. Data: {byte_data[:200]}")
        return {"deserialization_error": str(e), "raw_data_snippet": repr(byte_data[:200])}