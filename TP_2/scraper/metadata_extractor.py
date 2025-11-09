# scraper/metadata_extractor.py

from bs4 import BeautifulSoup

# Requisito 2: Extracción de metadatos
def extract_meta_tags(html_content: str) -> dict:
    """Extrae meta tags relevantes (description, keywords, Open Graph, Twitter)."""
    soup = BeautifulSoup(html_content, 'lxml')
    meta_tags = {}
    
    for tag in soup.find_all('meta'):
        name = tag.get('name')
        property_attr = tag.get('property')
        content = tag.get('content')
        
        if not content:
            continue
            
        # Tags estándar
        if name in ['description', 'keywords']:
            meta_tags[name] = content.strip()
            
        # Open Graph y Twitter Card tags
        if property_attr and (property_attr.startswith('og:') or property_attr.startswith('twitter:')):
            meta_tags[property_attr] = content.strip()
            
    return meta_tags