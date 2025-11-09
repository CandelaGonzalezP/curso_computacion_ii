# processor/image_processor.py

import base64
import time
from PIL import Image
import io
import random

def generate_thumbnails(url: str) -> list:
    """Simula la descarga de imágenes y generación de thumbnails en base64."""
    print(f"[Processor] Generando thumbnails para: {url}")
    # Simula trabajo CPU
    time.sleep(random.uniform(0.8, 1.5)) 
    
    thumbnails = []
    for i in range(2):
        # Simula la creación de thumbnails optimizados (2 por requisito)
        img = Image.new('RGB', (100, 100), 
                        color = (random.randint(0, 255), 0, random.randint(0, 255))) 
        img_buffer = io.BytesIO()
        # Uso de JPEG y calidad para simular optimización
        img.save(img_buffer, format="JPEG", quality=60) 
        base64_thumb = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        thumbnails.append(base64_thumb)
        
    return thumbnails