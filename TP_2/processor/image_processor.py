"""
Módulo de Procesamiento de Imágenes (SRP: Solo maneja imágenes).
Descarga y crea thumbnails.
"""

import requests
import base64
import io
from PIL import Image, ImageFile
from typing import List

ImageFile.LOAD_TRUNCATED_IMAGES = True

def process_images(image_urls: List[str]) -> List[str]:
    """
    Descarga imágenes (máximo 5) y genera thumbnails.
    """
    thumbnails = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Accept': 'image/*'
    }
    
    for url in image_urls[:5]: 
        try:
            response = requests.get(url, headers=headers, timeout=10) 
            response.raise_for_status()
            
            img_data = response.content
            if not img_data:
                continue

            img = Image.open(io.BytesIO(img_data))
            
            if img.mode not in ('RGB', 'L'): 
                img = img.convert('RGB')
                
            img.thumbnail((150, 150)) 
            
            out_buf = io.BytesIO()
            img.save(out_buf, format='JPEG', quality=85) 
            
            b64_str = base64.b64encode(out_buf.getvalue()).decode('utf-8')
            thumbnails.append(b64_str)
            
        except requests.RequestException:
            pass 
        except (IOError, Image.DecompressionBombError) as e:
            pass 
        except Exception as e:
            pass
            
    return thumbnails