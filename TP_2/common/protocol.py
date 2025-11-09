# common/protocol.py

import datetime

# Claves para identificar los datos en la comunicación
KEY_URL = "url"
KEY_SCRAPING_DATA = "scraping_data"
KEY_PROCESSING_DATA = "processing_data"

def create_scraping_request(url: str) -> dict:
    """Crea el mensaje de solicitud de procesamiento para el Servidor B."""
    return {
        KEY_URL: url,
    }

def create_scraping_response(url: str, scraping_data: dict, processing_data: dict, status: str = "success") -> dict:
    """Crea la respuesta JSON consolidada final para el cliente."""
    return {
        "url": url,
        "timestamp": datetime.datetime.now().isoformat() + "Z", # ISO 8601 con Z (UTC)
        KEY_SCRAPING_DATA: scraping_data,
        KEY_PROCESSING_DATA: processing_data,
        "status": status
    }