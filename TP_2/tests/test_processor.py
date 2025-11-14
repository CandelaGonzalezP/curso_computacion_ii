"""
Pruebas (semi) de integración para los módulos de procesamiento.

Estas pruebas REALIZAN peticiones de red y usan Selenium.
"""

import pytest
import os
from processor import screenshot, performance, image_processor

TARGET_URL = "https://example.com"

@pytest.mark.slow
def test_screenshot():
    """Prueba que Selenium genera un screenshot base64."""
    if os.getenv("CI"):
        pytest.skip("Saltando test de Selenium en entorno CI")
        
    b64_data = screenshot.take_screenshot(TARGET_URL)
    assert isinstance(b64_data, str)
    assert len(b64_data) > 1000 

@pytest.mark.slow
def test_performance():
    """Prueba que el análisis de performance devuelve la estructura correcta."""
    data = performance.analyze_performance(TARGET_URL)
    
    assert "load_time_ms" in data
    assert "total_size_kb" in data
    assert "num_requests" in data
    
    assert data['load_time_ms'] > 0
    assert data['total_size_kb'] > 0
    assert data['num_requests'] >= 1 

@pytest.mark.slow
def test_image_processor():
    """Prueba el procesador de imágenes con una imagen real."""
    IMG_URL = "https://www.python.org/static/img/python-logo.png"
    
    thumbnails = image_processor.process_images([IMG_URL])
    
    assert len(thumbnails) == 1
    assert isinstance(thumbnails[0], str)
    assert len(thumbnails[0]) > 100 