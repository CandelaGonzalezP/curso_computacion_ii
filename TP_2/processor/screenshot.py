"""
Módulo de Screenshot (SRP: Solo toma screenshots).
"""

import base64
import time 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException

from common import ProcessingError, TaskTimeoutError

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,720")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

DRIVER_PATH = None
try:
    DRIVER_PATH = ChromeDriverManager().install()
except Exception as e:
    print(f"[ScreenshotModule] ADVERTENCIA: No se pudo pre-descargar ChromeDriver: {e}")

def take_screenshot(url: str) -> str:
    """Toma un screenshot headless de PÁGINA COMPLETA y devuelve un string base64."""
    
    driver = None
    try:
        service = Service(DRIVER_PATH) if DRIVER_PATH else Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.set_page_load_timeout(30)
        
        driver.get(url)

        original_width = driver.get_window_size()['width']

        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        
        if total_height > 15000:
            print(f"[ScreenshotModule] ADVERTENCIA: Página {url} es muy alta ({total_height}px), truncando a 15000px.")
            total_height = 15000

        driver.set_window_size(original_width, total_height)
        
        time.sleep(0.5) 
        
        png_data = driver.get_screenshot_as_png()
        
        return base64.b64encode(png_data).decode('utf-8')
        
    except TimeoutException as e:
        print(f"Error en Selenium: Timeout (30s) al cargar {url}")
        raise TaskTimeoutError(f"Timeout al cargar {url} para screenshot") from e
        
    except WebDriverException as e:
        print(f"Error en Selenium al tomar screenshot de {url}: {e}")
        raise ProcessingError(f"Error de WebDriver: {str(e)[:100]}") from e
        
    except Exception as e:
        print(f"Error inesperado en Screenshot: {e}")
        raise ProcessingError(f"Error inesperado en Screenshot: {e}") from e
    
    finally:
        if driver:
            driver.set_window_size(1280, 720) 
            driver.quit()