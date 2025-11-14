"""
Pruebas Unitarias para el Protocolo de Comunicación (common/protocol.py)

Estas pruebas validan que el empaquetado y desempaquetado de mensajes
funciona correctamente tanto en modo síncrono (Servidor B) como 
asíncrono (Servidor A).
"""

import pytest
import pytest_asyncio
import asyncio
import socket
import struct
import json
from unittest.mock import AsyncMock, MagicMock

from common.protocol import (
    ProtocolHandler, 
    TASK_SCREENSHOT, 
    RESP_SUCCESS, 
    HEADER_SIZE, 
    HEADER_FORMAT
)


def test_pack_message_format():
    """Prueba que el formato del mensaje empaquetado sea correcto."""
    handler = ProtocolHandler()
    payload = {"url": "https://test.com"}
    
    message = handler.pack_message(TASK_SCREENSHOT, payload)
    
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    expected_total_len = HEADER_SIZE + len(payload_bytes)
    
    header_data = message[:HEADER_SIZE]
    total_len, msg_type = struct.unpack(HEADER_FORMAT, header_data)
    
    assert total_len == expected_total_len
    assert msg_type == TASK_SCREENSHOT
    
    payload_data = message[HEADER_SIZE:]
    assert payload_data == payload_bytes

@pytest.mark.asyncio
async def test_async_read_message():
    """Prueba la lectura asíncrona mockeando un StreamReader."""
    handler = ProtocolHandler()
    payload = {"status": "ok"}
    
    msg_bytes = handler.pack_message(RESP_SUCCESS, payload)
    header_bytes = msg_bytes[:HEADER_SIZE]
    payload_bytes = msg_bytes[HEADER_SIZE:]

    mock_reader = AsyncMock(spec=asyncio.StreamReader)
    
    mock_reader.readexactly.side_effect = [
        header_bytes, 
        payload_bytes   
    ]
    
    msg_type, rec_payload = await handler.async_read_message(mock_reader)
    
    assert msg_type == RESP_SUCCESS
    assert rec_payload == payload
    assert mock_reader.readexactly.call_count == 2

@pytest.mark.asyncio
async def test_async_send_message():
    """Prueba el envío asíncrono mockeando un StreamWriter."""
    handler = ProtocolHandler()
    payload = {"url": "https://test.com"}
    
    mock_writer = AsyncMock(spec=asyncio.StreamWriter)
    mock_writer.write = MagicMock() # Mock síncrono
    mock_writer.drain = AsyncMock() # Mock asíncrono

    await handler.async_send_message(mock_writer, TASK_SCREENSHOT, payload)

    expected_message = handler.pack_message(TASK_SCREENSHOT, payload)
    mock_writer.write.assert_called_once_with(expected_message)
    
    mock_writer.drain.assert_called_once()


def test_sync_send_and_read_with_socketpair():
    """
    Prueba la comunicación síncrona (usada por Servidor B)
    utilizando un par de sockets reales en memoria (socketpair).
    """
    
    s1, s2 = socket.socketpair()
    
    handler_cliente = ProtocolHandler()
    handler_servidor = ProtocolHandler()
    
    payload_enviado = {"url": "https://example.com"}
    
    try:
        handler_cliente.sync_send_message(s1, TASK_SCREENSHOT, payload_enviado)
        
        msg_type, payload_recibido = handler_servidor.sync_read_message(s2)
        
        assert msg_type == TASK_SCREENSHOT
        assert payload_recibido == payload_enviado
        
        respuesta_payload = {"data": "screenshot_base64"}
        handler_servidor.sync_send_message(s2, RESP_SUCCESS, respuesta_payload)
        
        resp_type, resp_payload = handler_cliente.sync_read_message(s1)
        
        assert resp_type == RESP_SUCCESS
        assert resp_payload == respuesta_payload
        
    finally:
        s1.close()
        s2.close()