# common/__init__.py
"""
Módulos comunes para comunicación entre servidores
Contiene protocolo de comunicación y serialización
"""

from .protocol import Protocol
from .serialization import Serializer

__all__ = [
    'Protocol',
    'Serializer'
]

__version__ = '1.0.0'

