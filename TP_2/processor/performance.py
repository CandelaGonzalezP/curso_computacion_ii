# processor/performance.py

import random
import time

# Requisito 4: Análisis de rendimiento (simulado)
def analyze_performance(url: str) -> dict:
    """Simula el análisis de rendimiento (tiempo de carga, tamaño, requests)."""
    print(f"[Processor] Analizando rendimiento de: {url}")
    # Simula trabajo CPU
    time.sleep(random.uniform(0.5, 1.0)) 
    
    return {
        "load_time_ms": random.randint(500, 3000),
        "total_size_kb": random.randint(1024, 5120),
        "num_requests": random.randint(20, 100)
    }