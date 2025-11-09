"""
Módulo para extraer metadatos de páginas web
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extractor de metadatos y meta tags"""
    
    def __init__(self):
        self.parser = 'lxml'
        
    def _get_soup(self, html_content: str) -> BeautifulSoup:
        """Crea objeto BeautifulSoup"""
        return BeautifulSoup(html_content, self.parser)
        
    def extract_meta_tags(self, html_content: str) -> Dict[str, any]:
        """
        Extrae todos los meta tags relevantes
        
        Returns:
            Diccionario con metadatos organizados
        """
        try:
            soup = self._get_soup(html_content)
            meta_data = {}
            
            # Meta tags estándar
            meta_data.update(self._extract_standard_meta(soup))
            
            # Open Graph tags
            og_tags = self._extract_og_tags(soup)
            if og_tags:
                meta_data['open_graph'] = og_tags
                
            # Twitter Cards
            twitter_tags = self._extract_twitter_tags(soup)
            if twitter_tags:
                meta_data['twitter'] = twitter_tags
                
            # Schema.org / JSON-LD
            schema_data = self._extract_schema_org(soup)
            if schema_data:
                meta_data['schema_org'] = schema_data
                
            return meta_data
            
        except Exception as e:
            logger.error(f"Error extrayendo meta tags: {str(e)}")
            return {}
            
    def _extract_standard_meta(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrae meta tags estándar"""
        meta_data = {}
        
        # Description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            meta_data['description'] = desc_tag['content']
            
        # Keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            meta_data['keywords'] = keywords_tag['content']
            
        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag and author_tag.get('content'):
            meta_data['author'] = author_tag['content']
            
        # Robots
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        if robots_tag and robots_tag.get('content'):
            meta_data['robots'] = robots_tag['content']
            
        # Viewport
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag and viewport_tag.get('content'):
            meta_data['viewport'] = viewport_tag['content']
            
        # Charset
        charset_tag = soup.find('meta', attrs={'charset': True})
        if charset_tag:
            meta_data['charset'] = charset_tag['charset']
        else:
            # Alternativa
            charset_tag = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
            if charset_tag and charset_tag.get('content'):
                meta_data['charset'] = charset_tag['content']
                
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            meta_data['language'] = html_tag['lang']
            
        return meta_data
        
    def _extract_og_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrae Open Graph meta tags"""
        og_data = {}
        
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                og_data[prop] = content
                
        return og_data
        
    def _extract_twitter_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrae Twitter Card meta tags"""
        twitter_data = {}
        
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                twitter_data[name] = content
                
        return twitter_data
        
    def _extract_schema_org(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae datos estructurados JSON-LD (Schema.org)"""
        import json
        
        schema_data = []
        
        # Buscar scripts con tipo application/ld+json
        ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in ld_scripts:
            try:
                data = json.loads(script.string)
                schema_data.append(data)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.debug(f"Error parseando JSON-LD: {str(e)}")
                continue
                
        return schema_data if schema_data else None
        
    def extract_canonical_url(self, html_content: str) -> Optional[str]:
        """Extrae la URL canónica de la página"""
        try:
            soup = self._get_soup(html_content)
            
            # Buscar link canonical
            canonical = soup.find('link', rel='canonical')
            if canonical and canonical.get('href'):
                return canonical['href']
                
            # Fallback a og:url
            og_url = soup.find('meta', property='og:url')
            if og_url and og_url.get('content'):
                return og_url['content']
                
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo URL canónica: {str(e)}")
            return None
            
    def extract_favicon(self, html_content: str) -> Optional[str]:
        """Extrae la URL del favicon"""
        try:
            soup = self._get_soup(html_content)
            
            # Buscar link rel="icon"
            icon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if icon and icon.get('href'):
                return icon['href']
                
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo favicon: {str(e)}")
            return None
            
    def extract_rss_feeds(self, html_content: str) -> List[str]:
        """Extrae URLs de feeds RSS/Atom"""
        try:
            soup = self._get_soup(html_content)
            feeds = []
            
            # Buscar links de tipo RSS/Atom
            feed_links = soup.find_all('link', type=lambda x: x and ('rss' in x.lower() or 'atom' in x.lower()))
            
            for link in feed_links:
                href = link.get('href')
                if href:
                    feeds.append(href)
                    
            return feeds
            
        except Exception as e:
            logger.error(f"Error extrayendo feeds: {str(e)}")
            return []