"""
Función de extracción de Metadatos (SRP: Solo extrae <meta> tags).
Extrae: Description, Keywords, y OpenGraph.
"""

from bs4 import BeautifulSoup
from typing import Dict, Any
import re

def extract_metadata(html: str) -> Dict[str, Any]:
    """
    Extrae meta tags relevantes (description, keywords, Open Graph).
    """
    soup = BeautifulSoup(html, 'lxml')
    metadata: Dict[str, Any] = {}

    desc_tag = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
    if desc_tag and desc_tag.get('content'):
        metadata['description'] = desc_tag['content'].strip()

    keys_tag = soup.find('meta', attrs={'name': re.compile(r'^keywords$', re.I)})
    if keys_tag and keys_tag.get('content'):
        metadata['keywords'] = keys_tag['content'].strip()

    og_tags = soup.find_all('meta', property=re.compile(r'^og:', re.I))
    for tag in og_tags:
        prop = tag.get('property')
        content = tag.get('content')
        if prop and content:
            metadata[prop] = content.strip()

    return metadata