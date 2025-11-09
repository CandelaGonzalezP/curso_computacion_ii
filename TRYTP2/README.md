# ============================================
# README.md
# ============================================

# TP2 - Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de scraping web implementado con Python utilizando `asyncio` para operaciones I/O asíncronas y `multiprocessing` para procesamiento paralelo de tareas CPU-bound.

## 📋 Características

- **Servidor Asíncrono (Parte A)**: Maneja múltiples solicitudes concurrentes usando asyncio
- **Servidor de Procesamiento (Parte B)**: Pool de procesos para tareas computacionalmente intensivas
- **Comunicación Transparente**: El cliente solo interactúa con el Servidor A
- **Soporte IPv4/IPv6**: Ambos servidores soportan ambos protocolos
- **Protocolo Binario Eficiente**: Comunicación optimizada entre servidores
- **Manejo Robusto de Errores**: Timeouts, reintentos y fallbacks

## 🏗️ Arquitectura

```
Cliente HTTP
    ↓
Servidor Asyncio (A) ← → Servidor Multiprocessing (B)
    │                         │
    ├─ Scraping              ├─ Screenshots
    ├─ Parsing               ├─ Performance Analysis
    └─ Metadata              └─ Image Processing
```

## 📁 Estructura del Proyecto

```
TP2/
├── server_scraping.py          # Servidor asyncio principal
├── server_processing.py        # Servidor multiprocessing
├── client.py                   # Cliente de prueba
├── scraper/
│   ├── __init__.py
│   ├── html_parser.py          # Parser HTML
│   ├── metadata_extractor.py  # Extractor de metadatos
│   └── async_http.py           # Cliente HTTP asíncrono
├── processor/
│   ├── __init__.py
│   ├── screenshot.py           # Generador de screenshots
│   ├── performance.py          # Análisis de rendimiento
│   └── image_processor.py      # Procesador de imágenes
├── common/
│   ├── __init__.py
│   ├── protocol.py             # Protocolo de comunicación
│   └── serialization.py        # Serialización de datos
├── tests/
│   ├── test_scraper.py
│   └── test_processor.py
├── requirements.txt
└── README.md
```

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd TP2
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar ChromeDriver (para screenshots)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

**Windows:**
Descargar desde: https://chromedriver.chromium.org/

**Alternativa - Playwright (más fácil):**
```bash
pip install playwright
playwright install chromium
```

## 🎮 Uso

### Iniciar el Servidor de Procesamiento (primero)

```bash
# IPv4
python3 server_processing.py -i 127.0.0.1 -p 9000

# IPv6
python3 server_processing.py -i ::1 -p 9000

# Con más procesos
python3 server_processing.py -i 127.0.0.1 -p 9000 -n 8
```

### Iniciar el Servidor de Scraping

```bash
# IPv4
python3 server_scraping.py -i 127.0.0.1 -p 8000

# IPv6
python3 server_scraping.py -i ::1 -p 8000

# Con más workers
python3 server_scraping.py -i 0.0.0.0 -p 8000 -w 8

# Especificar servidor de procesamiento remoto
python3 server_scraping.py -i 0.0.0.0 -p 8000 --processing-host 192.168.1.100 --processing-port 9000
```

### Usar el Cliente de Prueba

```bash
# Scraping básico
python3 client.py --url https://example.com

# Health check
python3 client.py --health

# Usando POST
python3 client.py --url https://python.org --post

# Salida en JSON
python3 client.py --url https://github.com --json

# Servidor remoto
python3 client.py --url https://example.com --host 192.168.1.10 --port 8000
```

### Usando curl

```bash
# GET request
curl "http://localhost:8000/scrape?url=https://example.com" | jq

# POST request
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://python.org"}' | jq

# Health check
curl http://localhost:8000/health | jq
```

## 📊 Formato de Respuesta

```json
{
  "url": "https://example.com",
  "timestamp": "2024-11-10T15:30:00Z",
  "status": "success",
  "scraping_data": {
    "title": "Example Domain",
    "links": ["https://...", "..."],
    "meta_tags": {
      "description": "...",
      "keywords": "...",
      "og_title": "..."
    },
    "images_count": 15,
    "structure": {
      "h1": 2,
      "h2": 5,
      "h3": 10
    }
  },
  "processing_data": {
    "screenshot": "base64_encoded_image...",
    "performance": {
      "load_time_ms": 1250,
      "total_size_kb": 2048,
      "num_requests": 45,
      "breakdown": {
        "html_size_kb": 50.5,
        "scripts": 10,
        "stylesheets": 5,
        "images": 30
      }
    },
    "thumbnails": ["base64_thumb1", "base64_thumb2"]
  }
}
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_scraper.py
pytest tests/test_processor.py

# Con coverage
pytest --cov=. --cov-report=html
```

## ⚙️ Configuración Avanzada

### Límites y Timeouts

En `server_scraping.py`:
- `max_connections`: Límite de conexiones concurrentes (default: workers)
- `timeout`: Timeout por página (default: 30s)

En `server_processing.py`:
- `num_processes`: Procesos en el pool (default: CPU count)
- `task_timeout`: Timeout por tarea (default: 45s)

### Optimización de Rendimiento

**Para alta concurrencia:**
```bash
# Más workers asyncio
python3 server_scraping.py -i 0.0.0.0 -p 8000 -w 20

# Más procesos
python3 server_processing.py -i 0.0.0.0 -p 9000 -n 16
```

**Para procesamiento pesado:**
```bash
# Menos workers, más procesos
python3 server_scraping.py -w 4
python3 server_processing.py -n 12
```

## 🐛 Troubleshooting

### Error: "Connection refused" al servidor de procesamiento

**Solución:** Asegurarse de iniciar primero el servidor de procesamiento

```bash
# Terminal 1
python3 server_processing.py -i 127.0.0.1 -p 9000

# Terminal 2 (después)
python3 server_scraping.py -i 127.0.0.1 -p 8000
```

### Error: "ChromeDriver not found"

**Solución:** Instalar ChromeDriver o usar Playwright

```bash
# Opción 1: ChromeDriver
sudo apt-get install chromium-chromedriver

# Opción 2: Playwright (más fácil)
pip install playwright
playwright install chromium
```

### Error: "Address already in use"

**Solución:** El puerto ya está en uso

```bash
# Encontrar proceso usando el puerto
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Usar otro puerto
python3 server_scraping.py -i 127.0.0.1 -p 8001
```

### Screenshots no funcionan

**Solución:** Verificar instalación de Selenium/ChromeDriver

```bash
# Test manual
python3 -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"
```

## 📚 Documentación Técnica

### Protocolo de Comunicación

El protocolo entre servidores usa un formato binario simple:

```
[4 bytes: tamaño del mensaje (big-endian)]
[N bytes: mensaje serializado (pickle)]
```

### Serialización

- **Por defecto**: Pickle (Python nativo, rápido, soporta objetos complejos)
- **Fallback**: JSON (interoperabilidad, debugging)

### Flujo de Trabajo

1. Cliente envía request HTTP al Servidor A
2. Servidor A inicia scraping asíncrono
3. En paralelo, Servidor A solicita procesamiento al Servidor B
4. Servidor B ejecuta tareas en procesos separados
5. Servidor A consolida resultados y responde al cliente

## 🔒 Seguridad

- **Rate Limiting**: Implementar límites por IP/dominio
- **Input Validation**: URLs sanitizadas antes de procesar
- **Resource Limits**: Límites de memoria y tiempo para prevenir DoS
- **Network Isolation**: Servidor B puede estar en red interna

## 📈 Métricas de Rendimiento

En hardware promedio (4 cores, 8GB RAM):

- **Throughput**: ~50 páginas/minuto
- **Latencia**: 2-10 segundos por página (dependiendo del sitio)
- **Memoria**: ~100-500 MB por worker

## 🤝 Contribuciones

Ver archivo `CONTRIBUTING.md` para guías de contribución.

## 📝 Licencia

Este proyecto es parte del curso de Computación II.

## 👥 Autores

- Estudiante: [Tu Nombre]
- Curso: Computación II
- Fecha: Noviembre 2024

## 📞 Soporte

Para problemas o preguntas:
- Crear issue en GitHub
- Consultar con docentes del curso
- Revisar documentación oficial de asyncio y multiprocessing