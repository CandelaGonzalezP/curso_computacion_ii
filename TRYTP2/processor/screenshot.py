# processor/screenshot.py
"""Generador de screenshots de páginas web"""

import base64
import time
import logging
from io import BytesIO
from typing import Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available, screenshots will be disabled")

logger = logging.getLogger(__name__)


class ScreenshotGenerator:
    """Generador de screenshots usando Selenium"""
    
    def __init__(self):
        self.selenium_available = SELENIUM_AVAILABLE
        
    def capture(self, url: str, width: int = 1920, height: int = 1080) -> Optional[str]:
        """
        Capturar screenshot de la página
        
        Args:
            url: URL de la página
            width: Ancho del viewport
            height: Alto del viewport
            
        Returns:
            Screenshot en base64 o None si falla
        """
        if not self.selenium_available:
            logger.warning("Selenium not available, skipping screenshot")
            return None
        
        driver = None
        try:
            # Configurar Chrome en modo headless
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Crear driver
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(20)
            
            # Navegar a la URL
            logger.info(f"Capturing screenshot for {url}")
            driver.get(url)
            
            # Esperar que la página cargue
            time.sleep(2)
            
            # Capturar screenshot
            screenshot_png = driver.get_screenshot_as_png()
            
            # Convertir a base64
            screenshot_base64 = base64.b64encode(screenshot_png).decode('utf-8')
            
            logger.info(f"Screenshot captured successfully: {len(screenshot_base64)} bytes")
            return screenshot_base64
            
        except Exception as e:
            logger.error(f"Error capturing screenshot for {url}: {str(e)}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
