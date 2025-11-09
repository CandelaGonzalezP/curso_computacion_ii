
# processor/__init__.py
"""
Módulo de procesamiento paralelo
Contiene generadores de screenshots, analizadores de rendimiento
y procesadores de imágenes
"""

from .screenshot import ScreenshotGenerator
from .performance import PerformanceAnalyzer
from .image_processor import ImageProcessor

__all__ = [
    'ScreenshotGenerator',
    'PerformanceAnalyzer',
    'ImageProcessor'
]

__version__ = '1.0.0'
