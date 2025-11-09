# processor/performance.py
"""Analizador de rendimiento de páginas web"""

import time
import logging
from typing import Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analizador de métricas de rendimiento"""
    
    def analyze(self, url: str, html: str) -> Dict[str, Any]:
        """
        Analizar rendimiento de la página
        
        Args:
            url: URL de la página
            html: Contenido HTML
            
        Returns:
            Diccionario con métricas de rendimiento
        """
        try:
            start_time = time.time()
            
            # Parsear HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # Calcular tamaño del HTML
            html_size_kb = len(html.encode('utf-8')) / 1024
            
            # Contar recursos
            num_scripts = len(soup.find_all('script', src=True))
            num_stylesheets = len(soup.find_all('link', rel='stylesheet'))
            num_images = len(soup.find_all('img', src=True))
            
            # Estimar número total de requests
            total_requests = 1 + num_scripts + num_stylesheets + num_images
            
            # Estimar tamaño total (aproximado)
            # Asumimos promedios: script=50KB, css=30KB, image=100KB
            estimated_total_size = (
                html_size_kb +
                (num_scripts * 50) +
                (num_stylesheets * 30) +
                (num_images * 100)
            )
            
            # Tiempo de procesamiento
            processing_time = (time.time() - start_time) * 1000  # en ms
            
            # Simular tiempo de carga (estimado)
            # Basado en tamaño y número de requests
            estimated_load_time = (
                processing_time +
                (total_requests * 50) +  # 50ms por request
                (estimated_total_size * 0.1)  # Factor de descarga
            )
            
            performance_data = {
                'load_time_ms': int(estimated_load_time),
                'total_size_kb': int(estimated_total_size),
                'num_requests': total_requests,
                'breakdown': {
                    'html_size_kb': round(html_size_kb, 2),
                    'scripts': num_scripts,
                    'stylesheets': num_stylesheets,
                    'images': num_images
                },
                'metrics': {
                    'processing_time_ms': round(processing_time, 2),
                    'estimated_download_time_ms': int(estimated_load_time - processing_time)
                }
            }
            
            logger.info(f"Performance analysis completed for {url}")
            return performance_data
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            return {
                'error': str(e),
                'load_time_ms': 0,
                'total_size_kb': 0,
                'num_requests': 0
            }
