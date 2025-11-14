"""
Módulo de Protocolo de Comunicación (SRP)

Define un protocolo simple de sockets basado en longitud + tipo + payload,
tal como se sugiere en los consejos del enunciado.

Formato del Header:
- 4 bytes: Longitud total del mensaje (Payload + Header) (Big Endian, 'I')
- 1 byte:  Tipo de mensaje (Big Endian, 'B')
Formato Total:
[Header (5 bytes)] [Payload (N bytes)]
"""

import struct
import asyncio
import socket
from typing import Dict, Any, Tuple

from common.serialization import serialize_data, deserialize_data

# Tipos de Tareas (Request de A -> B)
TASK_SCREENSHOT = 0x01
TASK_PERFORMANCE = 0x02
TASK_IMAGES = 0x03

# Tipos de Respuesta (Response de B -> A)
RESP_SUCCESS = 0x80
RESP_ERROR = 0x81

HEADER_FORMAT = "!IB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


class ProtocolException(Exception):
    """Excepción custom para errores de protocolo (ej. desconexión)."""
    pass


class ProtocolHandler:
    """
    Abstracción para manejar el empaquetado y desempaquetado de mensajes.
    Contiene la lógica para la comunicación binaria eficiente.
    """

    def pack_message(self, msg_type: int, payload: Dict[str, Any]) -> bytes:
        """Empaqueta un mensaje completo."""
        payload_bytes = serialize_data(payload)
        total_len = HEADER_SIZE + len(payload_bytes)
        
        header = struct.pack(HEADER_FORMAT, total_len, msg_type)
        return header + payload_bytes

    async def async_read_message(self, reader: asyncio.StreamReader) -> Tuple[int, Dict[str, Any]]:
        """Lee un mensaje completo de forma asíncrona."""
        try:
            header_data = await reader.readexactly(HEADER_SIZE)
        except (asyncio.IncompleteReadError, ConnectionResetError) as e:
            raise ProtocolException(f"Desconexión al leer header: {e}")
            
        total_len, msg_type = struct.unpack(HEADER_FORMAT, header_data)
        
        payload_len = total_len - HEADER_SIZE
        if payload_len < 0:
            raise ProtocolException(f"Longitud de payload inválida: {payload_len}")
        
        try:
            payload_bytes = await reader.readexactly(payload_len)
        except (asyncio.IncompleteReadError, ConnectionResetError) as e:
            raise ProtocolException(f"Desconexión al leer payload: {e}")
            
        payload = deserialize_data(payload_bytes)
        
        return msg_type, payload

    async def async_send_message(self, writer: asyncio.StreamWriter, msg_type: int, payload: Dict[str, Any]):
        """Envía un mensaje completo de forma asíncrona."""
        try:
            message = self.pack_message(msg_type, payload)
            writer.write(message)
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError) as e:
            raise ProtocolException(f"Error al enviar mensaje (async): {e}")

    def sync_read_message(self, sock: socket.socket) -> Tuple[int, Dict[str, Any]]:
        """Lee un mensaje completo de forma síncrona (bloqueante)."""
        header_data = self._recv_exactly(sock, HEADER_SIZE)
        if not header_data:
            raise ProtocolException("Cliente desconectado (header vacío)")
            
        total_len, msg_type = struct.unpack(HEADER_FORMAT, header_data)
        
        payload_len = total_len - HEADER_SIZE
        if payload_len < 0:
            raise ProtocolException(f"Longitud de payload inválida: {payload_len}")
        
        payload_bytes = self._recv_exactly(sock, payload_len)
        if not payload_bytes:
             raise ProtocolException("Cliente desconectado (payload vacío)")
             
        payload = deserialize_data(payload_bytes)
        
        return msg_type, payload

    def sync_send_message(self, sock: socket.socket, msg_type: int, payload: Dict[str, Any]):
        """Envía un mensaje completo de forma síncrona (bloqueante)."""
        try:
            message = self.pack_message(msg_type, payload)
            sock.sendall(message)
        except (ConnectionResetError, BrokenPipeError) as e:
            raise ProtocolException(f"Error al enviar mensaje (sync): {e}")

    def _recv_exactly(self, sock: socket.socket, n_bytes: int) -> bytes:
        """Helper síncrono para recibir exactamente N bytes."""
        chunks = []
        bytes_recd = 0
        while bytes_recd < n_bytes:
            try:
                chunk = sock.recv(min(n_bytes - bytes_recd, 4096))
                if chunk == b'':
                    raise ProtocolException("Socket cerrado inesperadamente")
                chunks.append(chunk)
                bytes_recd += len(chunk)
            except socket.timeout:
                raise ProtocolException(f"Timeout esperando datos (recibidos {bytes_recd}/{n_bytes})")
            except ConnectionResetError:
                 raise ProtocolException("Conexión reseteada por el peer")
        return b''.join(chunks)