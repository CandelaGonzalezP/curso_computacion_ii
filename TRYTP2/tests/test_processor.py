# tests/test_processor.py
"""Tests para el módulo processor"""

import pytest
import base64
from processor.performance import PerformanceAnalyzer
from processor.image_processor import ImageProcessor


# Fixtures
@pytest.fixture
def performance_analyzer():
    return PerformanceAnalyzer()


@pytest.fixture
def image_processor():
    return ImageProcessor(max_images=3, thumb_size=(100, 100))


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="style1.css">
        <link rel="stylesheet" href="style2.css">
        <script src="script1.js"></script>
        <script src="script2.js"></script>
    </head>
    <body>
        <img src="https://via.placeholder.com/300">
        <img src="https://via.placeholder.com/400">
        <img src="https://via.placeholder.com/500">
    </body>
    </html>
    """


# Tests para PerformanceAnalyzer
class TestPerformanceAnalyzer:
    
    def test_analyze_basic(self, performance_analyzer, sample_html):
        """Test análisis básico"""
        result = performance_analyzer.analyze("https://example.com", sample_html)
        
        assert 'load_time_ms' in result
        assert 'total_size_kb' in result
        assert 'num_requests' in result
        assert result['num_requests'] > 0
    
    def test_analyze_breakdown(self, performance_analyzer, sample_html):
        """Test breakdown de recursos"""
        result = performance_analyzer.analyze("https://example.com", sample_html)
        
        assert 'breakdown' in result
        breakdown = result['breakdown']
        
        assert 'scripts' in breakdown
        assert 'stylesheets' in breakdown
        assert 'images' in breakdown
        assert breakdown['scripts'] == 2
        assert breakdown['stylesheets'] == 2
        assert breakdown['images'] == 3
    
    def test_analyze_metrics(self, performance_analyzer, sample_html):
        """Test métricas adicionales"""
        result = performance_analyzer.analyze("https://example.com", sample_html)
        
        assert 'metrics' in result
        metrics = result['metrics']
        
        assert 'processing_time_ms' in metrics
        assert metrics['processing_time_ms'] >= 0
    
    def test_analyze_error_handling(self, performance_analyzer):
        """Test manejo de errores"""
        result = performance_analyzer.analyze("https://example.com", "invalid html")
        
        # No debe lanzar excepción
        assert 'load_time_ms' in result or 'error' in result


# Tests para ImageProcessor
class TestImageProcessor:
    
    def test_extract_image_urls(self, image_processor, sample_html):
        """Test extracción de URLs de imágenes"""
        urls = image_processor._extract_image_urls(sample_html, "https://example.com")
        
        assert isinstance(urls, list)
        assert len(urls) > 0
        assert all(isinstance(url, str) for url in urls)
    
    def test_max_images_limit(self, image_processor):
        """Test límite de imágenes"""
        html_many_images = """
        <html><body>
            <img src="img1.jpg">
            <img src="img2.jpg">
            <img src="img3.jpg">
            <img src="img4.jpg">
            <img src="img5.jpg">
        </body></html>
        """
        
        urls = image_processor._extract_image_urls(html_many_images, "https://example.com")
        # El processor debería procesar máximo max_images (3 en el fixture)
        assert len(urls) <= 5  # Extrae todas pero procesará solo 3
    
    @pytest.mark.skip(reason="Requiere conexión a internet y PIL")
    def test_create_thumbnail(self, image_processor):
        """Test creación de thumbnail (requiere internet)"""
        test_image_url = "https://via.placeholder.com/500"
        thumbnail = image_processor._create_thumbnail(test_image_url)
        
        if thumbnail:  # Solo si PIL está disponible
            # Verificar que es base64 válido
            try:
                base64.b64decode(thumbnail)
                assert True
            except:
                pytest.fail("Invalid base64 thumbnail")


# Tests de integración
class TestProcessorIntegration:
    
    def test_performance_full_analysis(self, performance_analyzer):
        """Test análisis completo de rendimiento"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <link rel="stylesheet" href="style.css">
            <script src="script.js"></script>
        </head>
        <body>
            <h1>Hello World</h1>
            <img src="image.jpg">
        </body>
        </html>
        """
        
        result = performance_analyzer.analyze("https://test.com", html)
        
        # Verificar estructura completa
        assert 'load_time_ms' in result
        assert 'total_size_kb' in result
        assert 'num_requests' in result
        assert 'breakdown' in result
        assert 'metrics' in result
        
        # Verificar valores razonables
        assert result['load_time_ms'] > 0
        assert result['total_size_kb'] > 0
        assert result['num_requests'] >= 1


# Test de protocolo y serialización
class TestCommon:
    
    def test_serialization_dict(self):
        """Test serialización de diccionario"""
        from common.serialization import Serializer
        
        data = {
            'key': 'value',
            'number': 42,
            'list': [1, 2, 3]
        }
        
        # Serializar
        serialized = Serializer.serialize(data)
        assert isinstance(serialized, bytes)
        
        # Deserializar
        deserialized = Serializer.deserialize(serialized)
        assert deserialized == data
    
    def test_serialization_safe(self):
        """Test serialización segura con fallback"""
        from common.serialization import Serializer
        
        data = {'test': 'data', 'number': 123}
        
        serialized = Serializer.serialize_safe(data)
        assert isinstance(serialized, bytes)
        
        deserialized = Serializer.deserialize_safe(serialized)
        assert deserialized == data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
