# scraper/html_parser.py

from bs4 import BeautifulSoup
from typing import List, Dict

# Requisito 1: Scraping de contenido HTML (parcial)
def extract_links_and_structure(html_content: str) -> dict:
    """Extrae título, enlaces, conteo de imágenes y estructura de headers."""
    # Uso de lxml (si está instalado) para mayor velocidad
    soup = BeautifulSoup(html_content, 'lxml') 
    
    # Título de la página
    title = soup.title.string.strip() if soup.title and soup.title.string else "Sin Título"
    
    # Enlaces
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    
    # Estructura (H1-H6)
    structure = {}
    for i in range(1, 7):
        header_tag = f'h{i}'
        count = len(soup.find_all(header_tag))
        if count > 0:
            structure[header_tag] = count
            
    # Cantidad de imágenes
    images_count = len(soup.find_all('img'))
    
    return {
        "title": title,
        "links": sorted(list(set(links))), # Eliminar duplicados y ordenar
        "structure": structure,
        "images_count": images_count
    }