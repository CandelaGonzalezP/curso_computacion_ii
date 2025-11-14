"""
Pruebas Unitarias para los módulos de scraping (parser y metadata).
"""

import pytest
from scraper.html_parser import parse_basic_data
from scraper.metadata_extractor import extract_metadata

MOCK_HTML = """
<html>
<head>
    <title>Título de Prueba</title>
    <meta name="description" content="Descripción de prueba.">
    <meta name="keywords" content="key1, key2">
    <meta property="og:title" content="Título OG">
</head>
<body>
    <h1>Header H1</h1>
    <h2>Header H2</h2>
    <h2>Otro H2</h2>
    
    <a href="/pagina_interna">Link Interno</a>
    <a href="https://www.externo.com/page">Link Externo</a>
    <a href="mailto:test@test.com">Mail</a>
    <a href="#">Ancla</a>
    
    <img src="img/logo.png">
    <img src="httpsG://cdn.com/img.jpg">
    <img src="data:image/png;base64,iVBORw0...">
</body>
</html>
"""
BASE_URL = "https://www.dominio.com"

def test_parse_basic_data():
    """Prueba el parser de datos básicos (html_parser.py)"""
    data = parse_basic_data(MOCK_HTML, BASE_URL)
    
    assert data['title'] == "Título de Prueba"
    
    assert data['structure']['h1'] == 1
    assert data['structure']['h2'] == 2
    assert data['structure']['h3'] == 0
    
    assert data['images_count'] == 2 
    
    assert len(data['links']) == 2
    assert "https://www.dominio.com/pagina_interna" in data['links']
    assert "https://www.externo.com/page" in data['links']

    img_urls = data['image_urls_for_processing']
    assert len(img_urls) == 2
    assert "https://www.dominio.com/img/logo.png" in img_urls
    assert "https://cdn.com/img.jpg" in img_urls

def test_extract_metadata():
    """Prueba el extractor de metadatos (metadata_extractor.py)"""
    metadata = extract_metadata(MOCK_HTML)
    
    assert metadata['description'] == "Descripción de prueba."
    assert metadata['keywords'] == "key1, key2"
    assert metadata['og:title'] == "Título OG"
    
def test_parse_title_fallback():
    """Prueba que el título haga fallback a H1 si <title> no existe."""
    html = "<html><body><h1>Título H1</h1></body></html>"
    data = parse_basic_data(html, BASE_URL)
    assert data['title'] == "Título H1"