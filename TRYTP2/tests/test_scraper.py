# tests/test_scraper.py
"""Tests para el módulo scraper"""

import pytest
import asyncio
from bs4 import BeautifulSoup
from scraper.html_parser import HTMLParser
from scraper.metadata_extractor import MetadataExtractor
from scraper.async_http import AsyncHTTPClient


# Fixtures
@pytest.fixture
def html_parser():
    return HTMLParser()


@pytest.fixture
def metadata_extractor():
    return MetadataExtractor()


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta name="keywords" content="test, sample">
        <meta property="og:title" content="OG Title">
        <link rel="canonical" href="https://example.com/canonical">
    </head>
    <body>
        <h1>Main Header</h1>
        <h2>Subheader 1</h2>
        <h2>Subheader 2</h2>
        <h3>Detail 1</h3>
        <a href="https://example.com/page1">Link 1</a>
        <a href="/relative">Relative Link</a>
        <a href="#anchor">Anchor</a>
        <img src="image1.jpg" alt="Image 1">
        <img src="image2.png" alt="Image 2">
        <img src="image3.gif" alt="Image 3">
    </body>
    </html>
    """


# Tests para HTMLParser
class TestHTMLParser:
    
    def test_parse_html(self, html_parser, sample_html):
        """Test parsing HTML"""
        soup = html_parser.parse(sample_html)
        assert isinstance(soup, BeautifulSoup)
        assert soup.find('title') is not None
    
    def test_extract_title(self, html_parser, sample_html):
        """Test extracción de título"""
        soup = html_parser.parse(sample_html)
        title = html_parser.extract_title(soup)
        assert title == "Test Page"
    
    def test_extract_title_fallback_to_h1(self, html_parser):
        """Test fallback a H1 cuando no hay title"""
        html_no_title = "<html><body><h1>Header Title</h1></body></html>"
        soup = html_parser.parse(html_no_title)
        title = html_parser.extract_title(soup)
        assert title == "Header Title"
    
    def test_extract_links(self, html_parser, sample_html):
        """Test extracción de enlaces"""
        soup = html_parser.parse(sample_html)
        links = html_parser.extract_links(soup, "https://example.com")
        
        assert len(links) >= 2
        assert "https://example.com/page1" in links
        assert any("/relative" in link for link in links)
        # Los anchors (#) deben ser filtrados
        assert not any(link.startswith('#') for link in links)
    
    def test_count_images(self, html_parser, sample_html):
        """Test conteo de imágenes"""
        soup = html_parser.parse(sample_html)
        count = html_parser.count_images(soup)
        assert count == 3
    
    def test_extract_structure(self, html_parser, sample_html):
        """Test extracción de estructura"""
        soup = html_parser.parse(sample_html)
        structure = html_parser.extract_structure(soup)
        
        assert structure['h1'] == 1
        assert structure['h2'] == 2
        assert structure['h3'] == 1
        assert structure['h4'] == 0


# Tests para MetadataExtractor
class TestMetadataExtractor:
    
    def test_extract_meta_tags(self, metadata_extractor, sample_html):
        """Test extracción de meta tags"""
        soup = BeautifulSoup(sample_html, 'lxml')
        meta_tags = metadata_extractor.extract_meta_tags(soup)
        
        assert 'description' in meta_tags
        assert meta_tags['description'] == "Test description"
        assert 'keywords' in meta_tags
        assert meta_tags['keywords'] == "test, sample"
    
    def test_extract_og_tags(self, metadata_extractor, sample_html):
        """Test extracción de Open Graph tags"""
        soup = BeautifulSoup(sample_html, 'lxml')
        meta_tags = metadata_extractor.extract_meta_tags(soup)
        
        assert 'og_title' in meta_tags
        assert meta_tags['og_title'] == "OG Title"
    
    def test_extract_canonical(self, metadata_extractor, sample_html):
        """Test extracción de URL canonical"""
        soup = BeautifulSoup(sample_html, 'lxml')
        meta_tags = metadata_extractor.extract_meta_tags(soup)
        
        assert 'canonical' in meta_tags
        assert meta_tags['canonical'] == "https://example.com/canonical"
    
    def test_extract_language(self, metadata_extractor, sample_html):
        """Test extracción de idioma"""
        soup = BeautifulSoup(sample_html, 'lxml')
        meta_tags = metadata_extractor.extract_meta_tags(soup)
        
        assert 'language' in meta_tags
        assert meta_tags['language'] == "en"


# Tests para AsyncHTTPClient
class TestAsyncHTTPClient:
    
    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Test fetch exitoso (usando example.com)"""
        client = AsyncHTTPClient()
        try:
            html = await client.fetch("https://example.com", timeout=10)
            assert html is not None
            assert len(html) > 0
            assert "example" in html.lower()
        finally:
            await client.close()
    
    @pytest.mark.asyncio
    async def test_fetch_timeout(self):
        """Test timeout"""
        client = AsyncHTTPClient()
        try:
            with pytest.raises(asyncio.TimeoutError):
                # URL que debería hacer timeout
                await client.fetch("https://httpbin.org/delay/10", timeout=2)
        finally:
            await client.close()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test uso como context manager"""
        async with AsyncHTTPClient() as client:
            html = await client.fetch("https://example.com", timeout=10)
            assert html is not None


# Tests de integración
class TestScraperIntegration:
    
    @pytest.mark.asyncio
    async def test_full_scraping_workflow(self):
        """Test workflow completo de scraping"""
        # Setup
        parser = HTMLParser()
        extractor = MetadataExtractor()
        
        # Fetch página real
        async with AsyncHTTPClient() as client:
            html = await client.fetch("https://example.com", timeout=10)
        
        # Parse
        soup = parser.parse(html)
        
        # Extraer datos
        title = parser.extract_title(soup)
        links = parser.extract_links(soup, "https://example.com")
        meta_tags = extractor.extract_meta_tags(soup)
        images = parser.count_images(soup)
        structure = parser.extract_structure(soup)
        
        # Verificaciones
        assert title is not None
        assert len(title) > 0
        assert isinstance(links, list)
        assert isinstance(meta_tags, dict)
        assert isinstance(images, int)
        assert isinstance(structure, dict)
        assert all(f'h{i}' in structure for i in range(1, 7))