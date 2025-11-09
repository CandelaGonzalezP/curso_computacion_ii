# scraper/__init__.py
"""
Módulo de scraping web asíncrono
Contiene parsers HTML, extractores de metadatos y cliente HTTP
"""

from .html_parser import HTMLParser
from .metadata_extractor import MetadataExtractor
from .async_http import AsyncHTTPClient

__all__ = [
    'HTMLParser',
    'MetadataExtractor',
    'AsyncHTTPClient'
]

__version__ = '1.0.0'

