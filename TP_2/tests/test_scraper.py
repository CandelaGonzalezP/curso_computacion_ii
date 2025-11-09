# tests/test_scraper.py

import asyncio
import sys
import os
import unittest


# --- INICIO: AJUSTE DE RUTA UNIVERSAL ---
# Ruta absoluta al directorio donde está el script (tests/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ruta absoluta al directorio raíz del proyecto (TP_2/)
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# Añadir el directorio raíz del proyecto (TP_2) a sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN: AJUSTE DE RUTA UNIVERSAL ---

# NOTA: Las importaciones ahora son ABSOLUTAS desde TP_2/
# Ya no se usan los puntos (..)
from scraper.html_parser import extract_links_and_structure
from scraper.metadata_extractor import extract_meta_tags
from scraper.async_http import fetch_url, SCRAPING_TIMEOUT
import aiohttp
import time


# Simulación de HTML simple para test
HTML_MOCK = """
<!DOCTYPE html>
<html>
<head>
    <title>Título de Prueba</title>
    <meta name="description" content="Una descripción genial.">
    <meta name="keywords" content="test, python, tp2">
    <meta property="og:title" content="OG Title">
</head>
<body>
    <h1>Header 1</h1>
    <h2>Subtítulo</h2>
    <a href="https://link1.com">Link 1</a>
    <a href="/local/link">Link 2</a>
    <img src="img1.png" alt="Imagen 1">
    <img src="img2.png" alt="Imagen 2">
    <img src="img3.png" alt="Imagen 3">
</body>
</html>
"""

class TestScraper(unittest.IsolatedAsyncioTestCase):

    def test_01_parser_structure(self):
        """Verifica la extracción de título, enlaces, estructura Hx y conteo de imágenes."""
        data = extract_links_and_structure(HTML_MOCK)
        self.assertEqual(data['title'], "Título de Prueba")
        self.assertEqual(data['images_count'], 3) # Ahora esperamos 3 imágenes
        self.assertEqual(data['structure']['h1'], 1)
        self.assertIn('https://link1.com', data['links'])
        self.assertIn('/local/link', data['links'])

    def test_02_metadata_extraction(self):
        """Verifica la extracción de meta tags estándar y Open Graph."""
        meta_data = extract_meta_tags(HTML_MOCK)
        self.assertEqual(meta_data['description'], "Una descripción genial.")
        self.assertEqual(meta_data['keywords'], "test, python, tp2")
        self.assertEqual(meta_data['og:title'], "OG Title")
        
    async def test_03_fetch_url_network_error(self):
        """Simula y verifica el manejo de errores de conexión/red."""
        # Usamos una URL/puerto que no responde para simular un fallo de conexión
        async with aiohttp.ClientSession() as session:
            with self.assertRaises(ConnectionError) as cm:
                await fetch_url(session, 'http://127.0.0.1:9999/unreachable') 
            
            # Verificamos que el mensaje de error sea el esperado
            self.assertIn("Error de conexión", str(cm.exception))

    async def test_04_fetch_url_timeout_error(self):
        """Simula y verifica el manejo del timeout (máx 30s)."""
        # Nota: Esto es difícil de simular sin un servidor mock, 
        # pero verificamos que al menos se levante un error de timeout de asyncio
        # si una operación excede el límite. Usamos una URL que debería fallar rápido.
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
             with self.assertRaises((ConnectionError, asyncio.TimeoutError)):
                 # Usamos un servicio que sabemos que tardará si es posible, o un IP conocido que no responde
                 await fetch_url(session, 'http://10.255.255.1:8080') # IP privado que suele fallar en timeout
            
if __name__ == '__main__':
    unittest.main()