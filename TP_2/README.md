# TP2 - Sistema de Scraping Web Distribuido

## Descripción General

Sistema distribuido cliente-servidor para scraping y análisis de páginas web, implementado en Python con arquitectura asíncrona y multiprocesamiento.
Alumno: Candela González

### Arquitectura

El sistema consta de tres componentes principales:

1. **Cliente HTTP (`client.py`)**: Interfaz de usuario que envía solicitudes de scraping
2. **Servidor A - Scraping (`server_scraping.py`)**: Servidor asíncrono (asyncio/aiohttp) que:
   - Recibe peticiones HTTP del cliente
   - Descarga y parsea HTML
   - Coordina tareas de procesamiento con Servidor B
   - Devuelve resultados consolidados en JSON

3. **Servidor B - Procesamiento (`server_processing.py`)**: Servidor multi-proceso que ejecuta tareas CPU-intensivas:
   - Screenshots con Selenium
   - Análisis de performance
   - Generación de thumbnails de imágenes

### Características Principales

- **Arquitectura Distribuida**: Separación clara entre scraping (I/O-bound) y procesamiento (CPU-bound)
- **Protocolo Binario Eficiente**: Comunicación entre servidores mediante protocolo custom con framing
- **Soporte IPv4 e IPv6**: Ambos servidores soportan dual-stack
- **Concurrencia Asíncrona**: Servidor A utiliza asyncio para manejar múltiples conexiones simultáneas
- **Multiprocesamiento**: Servidor B utiliza pool de procesos para tareas CPU-intensivas
- **Manejo Robusto de Errores**: Excepciones personalizadas y timeouts configurables
- **Serialización JSON**: Comunicación eficiente con encoding UTF-8

## Requisitos del Sistema

### Software Necesario

- Python 3.8 o superior
- Google Chrome o Chromium (para Selenium)
- pip (gestor de paquetes de Python)

### Dependencias Python

Todas las dependencias están en `requirements.txt`:

```
aiohttp              # Servidor async y cliente HTTP
beautifulsoup4       # Parsing HTML
lxml                 # Parser HTML rápido
Pillow               # Procesamiento de imágenes
selenium             # Screenshots automatizados
webdriver-manager    # Gestión automática de ChromeDriver
requests             # Cliente HTTP síncro no
pytest               # Testing
pytest-asyncio       # Testing async
```

## Instalación

### 1. Clonar/Descargar el Proyecto

```bash
cd TP_2/
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nota**: La primera vez que ejecutes el servidor de procesamiento, `webdriver-manager` descargará automáticamente ChromeDriver (puede tardar unos minutos).

## Uso Básico

### Inicio Rápido (Localhost IPv4)

#### Terminal 1: Iniciar Servidor B (Procesamiento)
```bash
python server_processing.py -i 127.0.0.1 -p 9000
```

#### Terminal 2: Iniciar Servidor A (Scraping)
```bash
python server_scraping.py -i 127.0.0.1 -p 8000 --processing-host 127.0.0.1 --processing-port 9000
```

#### Terminal 3: Realizar una Solicitud
```bash
python client.py -u https://www.python.org --save
```

### Opciones del Servidor de Procesamiento (`server_processing.py`)

```bash
python server_processing.py -i <IP> -p <PUERTO> [-n <NUM_PROCESOS>]
```

**Argumentos**:
- `-i, --ip`: Dirección IP de escucha (ej: `0.0.0.0`, `::`, `127.0.0.1`)
- `-p, --port`: Puerto de escucha
- `-n, --processes`: Número de procesos en el pool (default: núcleos CPU)

**Ejemplos**:
```bash
# IPv4 en todas las interfaces
python server_processing.py -i 0.0.0.0 -p 9000

# IPv6 dual-stack
python server_processing.py -i :: -p 9000

# Con pool de 4 procesos
python server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

### Opciones del Servidor de Scraping (`server_scraping.py`)

```bash
python server_scraping.py -i <IP> -p <PUERTO> [--processing-host <HOST>] [--processing-port <PORT>]
```

**Argumentos**:
- `-i, --ip`: Dirección IP de escucha
- `-p, --port`: Puerto de escucha
- `-w, --workers`: Número de workers (default: 1)
- `--processing-host`: Host del servidor de procesamiento (default: 127.0.0.1)
- `--processing-port`: Puerto del servidor de procesamiento (default: 9000)

**Ejemplos**:
```bash
# Servidor en todas las interfaces IPv4, conecta a procesador local
python server_scraping.py -i 0.0.0.0 -p 8000 --processing-host 127.0.0.1 --processing-port 9000

# Dual-stack IPv6, conecta a procesador remoto
python server_scraping.py -i :: -p 8000 --processing-host 192.168.1.100 --processing-port 9000
```

### Opciones del Cliente (`client.py`)

```bash
python client.py -u <URL> [--server_host <HOST>] [--server_port <PORT>] [--save]
```

**Argumentos**:
- `-u, --url`: URL a scrapear (obligatorio)
- `--server_host`: Host del servidor de scraping (default: localhost)
- `--server_port`: Puerto del servidor de scraping (default: 8000)
- `--save`: Guardar JSON y screenshot en disco

**Ejemplos**:
```bash
# Solicitud básica
python client.py -u https://www.example.com

# Guardar resultados
python client.py -u https://www.github.com --save

# Servidor remoto
python client.py -u https://www.python.org --server_host 192.168.1.100 --server_port 8080 --save
```

## Formato de Respuesta

El servidor devuelve un JSON con la siguiente estructura:

```json
{
  "url": "https://www.python.org",
  "timestamp": "2025-11-13T10:30:45.123456",
  "status": "success",
  "scraping_data": {
    "title": "Welcome to Python.org",
    "links": ["https://...", "https://..."],
    "meta_tags": {
      "description": "...",
      "keywords": "...",
      "og:title": "..."
    },
    "structure": {
      "h1": 2,
      "h2": 5,
      "h3": 10,
      "h4": 0,
      "h5": 0,
      "h6": 0
    },
    "images_count": 15
  },
  "processing_data": {
    "screenshot": "iVBORw0KGgoAAAANSUhEUgAA...",
    "performance": {
      "load_time_ms": 1234.56,
      "total_size_kb": 567.89,
      "num_requests": 42
    },
    "thumbnails": [
      "iVBORw0KGgoAAAANSUhEUgAA...",
      "iVBORw0KGgoAAAANSUhEUgAA..."
    ]
  }
}
```

### Archivos Generados (con `--save`)

- **`outputs/<dominio>_<timestamp>.json`**: Respuesta JSON completa
- **`screenshots/<dominio>_<timestamp>.png`**: Screenshot de la página

## Estructura del Proyecto

```
TP_2/
├── client.py                    # Cliente HTTP
├── server_scraping.py           # Servidor A (Async)
├── server_processing.py         # Servidor B (Multiprocessing)
├── requirements.txt             # Dependencias
├── common/
│   ├── __init__.py             # Excepciones personalizadas
│   ├── protocol.py             # Protocolo de comunicación binario
│   └── serialization.py        # Serialización JSON
├── scraper/
│   ├── __init__.py
│   ├── async_http.py           # Cliente HTTP asíncrono
│   ├── html_parser.py          # Parser HTML (BeautifulSoup)
│   └── metadata_extractor.py   # Extractor de metadatos
├── processor/
│   ├── __init__.py
│   ├── screenshot.py           # Módulo de screenshots (Selenium)
│   ├── performance.py          # Análisis de performance
│   └── image_processor.py      # Procesador de imágenes (Pillow)
└── tests/
    ├── __init__.py
    ├── test_protocol.py        # Tests del protocolo
    ├── test_scraper.py         # Tests de scraping
    ├── test_processor.py       # Tests de procesamiento
    └── test_integration.py     # Tests E2E (IPv4/IPv6)
```

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/

# Tests específicos
pytest tests/test_protocol.py
pytest tests/test_scraper.py

# Tests de integración (lentos, requieren servidores activos)
pytest tests/test_integration.py -v

# Excluir tests lentos
pytest tests/ -m "not slow"
```

### Tests Parametrizados IPv4/IPv6

Los tests de integración se ejecutan automáticamente en IPv4 e IPv6 para validar el soporte dual-stack:

```bash
pytest tests/test_integration.py -v
```

## Protocolo de Comunicación

### Formato del Mensaje

Cada mensaje entre Servidor A y B sigue este formato binario:

```
[Header: 5 bytes][Payload: N bytes]

Header:
- 4 bytes: Longitud total (Big Endian, unsigned int)
- 1 byte:  Tipo de mensaje (Big Endian, unsigned byte)

Payload:
- N bytes: Datos serializados en JSON UTF-8
```

### Tipos de Mensaje

**Requests (A → B)**:
- `0x01`: TASK_SCREENSHOT
- `0x02`: TASK_PERFORMANCE
- `0x03`: TASK_IMAGES

**Responses (B → A)**:
- `0x80`: RESP_SUCCESS
- `0x81`: RESP_ERROR

## Manejo de Errores

### Excepciones Personalizadas

- `TP2Exception`: Excepción base
- `ProtocolError`: Error en comunicación entre servidores
- `ScrapingError`: Error al descargar/parsear HTML
- `ProcessingError`: Error en tareas de procesamiento
- `TaskTimeoutError`: Timeout en operaciones

### Códigos de Estado HTTP

- `200`: Éxito
- `400`: URL inválida o parámetros faltantes
- `502`: Error de scraping (URL inaccesible)
- `503`: Error de comunicación con servidor de procesamiento
- `500`: Error interno del servidor

## Troubleshooting

### ChromeDriver no se descarga

```bash
# Instalar manualmente
pip install --upgrade webdriver-manager

# O especificar ruta manualmente en screenshot.py
```

### Puerto en uso

```bash
# Verificar puertos ocupados
# Linux/Mac:
lsof -i :8000
lsof -i :9000

# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :9000
```

### Error de conexión entre servidores

1. Verificar que el Servidor B esté corriendo
2. Verificar firewall (permitir puertos)
3. Verificar que las IPs/puertos coincidan en ambos servidores

### Error "Address already in use"

Cambiar el puerto o esperar a que el SO libere el puerto anterior:

```bash
# En el servidor que da error, usar otro puerto
python server_scraping.py -i 127.0.0.1 -p 8001
```

## Configuración Avanzada

### Despliegue en Red Local

**Servidor B (Máquina potente para procesamiento)**:
```bash
python server_processing.py -i 0.0.0.0 -p 9000 -n 8
```

**Servidor A (Máquina para I/O)**:
```bash
python server_scraping.py -i 0.0.0.0 -p 8000 --processing-host <IP_SERVIDOR_B> --processing-port 9000
```

**Cliente (Cualquier máquina)**:
```bash
python client.py -u https://example.com --server_host <IP_SERVIDOR_A> --server_port 8000 --save
```

### Timeouts Configurables

Modificar en el código:

- **HTTP requests**: `scraper/async_http.py` → `AsyncHTTPClient(timeout=30)`
- **Screenshot**: `processor/screenshot.py` → `driver.set_page_load_timeout(30)`
- **Performance**: `processor/performance.py` → `requests.get(url, timeout=30)`

## Limitaciones Conocidas

1. **Tamaño de Página**: Screenshots limitados a 15000px de altura
2. **Imágenes**: Máximo 5 thumbnails generados por solicitud
3. **Concurrencia**: Servidor B procesa una tarea por proceso a la vez
4. **ChromeDriver**: Requiere Chrome/Chromium instalado en el sistema

## Licencia

Este proyecto es material educativo para el curso de Computación II - UTN FRM.

## Autores

Proyecto desarrollado como Trabajo Práctico #2 - Sistemas Distribuidos.

## Changelog

### v1.0.0
- Implementación inicial
- Soporte IPv4/IPv6
- Protocolo binario custom
- Tests parametrizados
- Cliente con guardado de artefactos