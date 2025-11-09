# processor/screenshot.py

import base64
import time
from PIL import Image
import io
import random

# Requisito 3: Generación de screenshot (simulado para evitar dependencias de driver)
def generate_screenshot(url: str) -> str:
    """Genera un screenshot (simulado) y devuelve la imagen en base64."""
    print(f"[Processor] Generando screenshot para: {url}")
    # Simula una operación CPU-bound y I/O de renderizado
    time.sleep(random.uniform(1.0, 2.0)) 

    try:
        # Crear una imagen simulada (pequeño placeholder)
        img = Image.new('RGB', (200, 150), 
                        color = (random.randint(50, 200), random.randint(50, 200), 200))
        
        # Añadir texto simulado
        from PIL import ImageDraw, ImageFont
        d = ImageDraw.Draw(img)
        d.text((10,10), "Screenshot Simulada", fill=(0,0,0))

        # Guardar en buffer y codificar a base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        base64_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return base64_img

    except Exception as e:
        print(f"[Processor] Error al generar screenshot para {url}: {e}")
        return "error_screenshot"
    
    # NOTA: Para el código REAL con Selenium, reemplazar este bloque por la implementación real