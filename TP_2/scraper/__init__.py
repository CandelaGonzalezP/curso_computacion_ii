# scraper/__init__.py
from .async_http import fetch_url
from .html_parser import extract_links_and_structure
from .metadata_extractor import extract_meta_tags