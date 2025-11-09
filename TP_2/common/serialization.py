# common/serialization.py

import json
import struct

# Protocolo: 4 bytes (little-endian, unsigned int) para la longitud del mensaje JSON.
HEADER_FORMAT = '<I' 
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def serialize_message(data: dict) -> bytes:
    """Serializa un diccionario a bytes con un encabezado de longitud."""
    try:
        json_data = json.dumps(data).encode('utf-8')
        data_len = len(json_data)
        header = struct.pack(HEADER_FORMAT, data_len)
        return header + json_data
    except Exception as e:
        # En una aplicación real, esto debería registrarse, no imprimir
        print(f"Error en serialización: {e}")
        return b''

def deserialize_message(stream_with_header: bytes) -> dict:
    """Deserializa bytes del socket con encabezado de longitud."""
    try:
        if len(stream_with_header) < HEADER_SIZE:
            raise ValueError("Buffer demasiado corto para el encabezado")
        
        # El Servidor A o B debe asegurar que el buffer está completo
        header = stream_with_header[:HEADER_SIZE]
        (data_len,) = struct.unpack(HEADER_FORMAT, header)
        
        json_data_bytes = stream_with_header[HEADER_SIZE:HEADER_SIZE + data_len]
        
        if len(json_data_bytes) != data_len:
            raise ValueError("Buffer incompleto para el cuerpo del mensaje")
            
        json_data = json_data_bytes.decode('utf-8')
        return json.loads(json_data)
    except Exception as e:
        print(f"Error en deserialización: {e}") 
        return {}