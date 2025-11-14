# --- Excepciones Personalizadas ---

class TP2Exception(Exception):
    """Excepción base para todos los errores de esta aplicación."""
    pass


class ProtocolError(TP2Exception):
    """
    Error en la capa de comunicación (sockets, framing, serialización).
    Indica que la comunicación entre el Servidor A y B falló.
    """
    pass


class ScrapingError(TP2Exception):
    """
    Error durante la fase de scraping (HTTP, parsing).
    Indica que hubo un problema al contactar o entender la URL del usuario.
    """
    pass


class ProcessingError(TP2Exception):
    """
    Error durante la fase de procesamiento (Selenium, Pillow, etc.).
    Indica que una tarea de CPU-bound en el Servidor B falló.
    """
    pass


class TaskTimeoutError(TP2Exception):
    """
    Indica que una tarea específica (scraping o procesamiento) 
    superó el tiempo límite establecido.
    """
    pass