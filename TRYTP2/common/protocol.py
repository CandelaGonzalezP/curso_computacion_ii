# common/protocol.py
"""Protocolo de comunicación entre servidores"""

import struct
import asyncio
import socket
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Protocol:
    """
    Protocolo de comunicación binario eficiente
    Formato: [LENGTH (4 bytes)] [DATA (LENGTH bytes)]
    """
    
    HEADER_SIZE = 4  # 4 bytes para el tamaño
    MAX_MESSAGE_SIZE = 50 * 1024 * 1024  # 50MB máximo
    
    @staticmethod
    async def send_async(writer: asyncio.StreamWriter, data: bytes):
        """
        Enviar datos de forma asíncrona
        
        Args:
            writer: StreamWriter de asyncio
            data: Datos a enviar (bytes)
        """
        try:
            # Verificar tamaño
            if len(data) > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(f"Message too large: {len(data)} bytes")
            
            # Enviar tamaño (4 bytes, big-endian)
            size_header = struct.pack('>I', len(data))
            writer.write(size_header)
            
            # Enviar datos
            writer.write(data)
            await writer.drain()
            
            logger.debug(f"Sent {len(data)} bytes")
            
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            raise
    
    @staticmethod
    async def receive_async(reader: asyncio.StreamReader) -> Optional[bytes]:
        """
        Recibir datos de forma asíncrona
        
        Args:
            reader: StreamReader de asyncio
            
        Returns:
            Datos recibidos (bytes) o None si error
        """
        try:
            # Leer header (4 bytes)
            header = await reader.readexactly(Protocol.HEADER_SIZE)
            
            # Extraer tamaño
            message_size = struct.unpack('>I', header)[0]
            
            # Verificar tamaño
            if message_size > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(f"Message too large: {message_size} bytes")
            
            if message_size == 0:
                return b''
            
            # Leer datos
            data = await reader.readexactly(message_size)
            
            logger.debug(f"Received {len(data)} bytes")
            return data
            
        except asyncio.IncompleteReadError:
            logger.warning("Connection closed by peer")
            return None
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            return None
    
    @staticmethod
    def send_sync(sock: socket.socket, data: bytes):
        """
        Enviar datos de forma síncrona (para servidor multiprocessing)
        
        Args:
            sock: Socket
            data: Datos a enviar (bytes)
        """
        try:
            # Verificar tamaño
            if len(data) > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(f"Message too large: {len(data)} bytes")
            
            # Enviar tamaño
            size_header = struct.pack('>I', len(data))
            sock.sendall(size_header)
            
            # Enviar datos
            sock.sendall(data)
            
            logger.debug(f"Sent {len(data)} bytes (sync)")
            
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            raise
    
    @staticmethod
    def receive_sync(sock: socket.socket) -> Optional[bytes]:
        """
        Recibir datos de forma síncrona (para servidor multiprocessing)
        
        Args:
            sock: Socket
            
        Returns:
            Datos recibidos (bytes) o None si error
        """
        try:
            # Leer header
            header = Protocol._recv_all(sock, Protocol.HEADER_SIZE)
            if not header:
                return None
            
            # Extraer tamaño
            message_size = struct.unpack('>I', header)[0]
            
            # Verificar tamaño
            if message_size > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(f"Message too large: {message_size} bytes")
            
            if message_size == 0:
                return b''
            
            # Leer datos
            data = Protocol._recv_all(sock, message_size)
            
            logger.debug(f"Received {len(data) if data else 0} bytes (sync)")
            return data
            
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            return None
    
    @staticmethod
    def _recv_all(sock: socket.socket, size: int) -> Optional[bytes]:
        """
        Recibir exactamente 'size' bytes del socket
        
        Args:
            sock: Socket
            size: Número de bytes a recibir
            
        Returns:
            Datos recibidos o None si error
        """
        data = bytearray()
        while len(data) < size:
            try:
                packet = sock.recv(size - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.timeout:
                logger.warning("Socket timeout")
                return None
            except Exception as e:
                logger.error(f"Error receiving: {str(e)}")
                return None
        return bytes(data)
