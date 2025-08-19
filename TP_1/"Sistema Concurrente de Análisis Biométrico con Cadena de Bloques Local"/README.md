README = """
# Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

## 📌 Descripción
Este proyecto implementa un sistema distribuido en **procesos** que:
1. Genera datos biométricos simulados en tiempo real.
2. Procesa cada señal en paralelo mediante **multiprocessing** y comunicación por **Pipe/Queue**.
3. Verifica y almacena los resultados en una **cadena de bloques local** (`blockchain.json`) para garantizar integridad.
4. Permite validar la integridad de la cadena y generar un **reporte final** (`reporte.txt`).

El trabajo práctico está dividido en tres tareas principales:
- **Tarea 1:** Generación y análisis concurrente.
- **Tarea 2:** Verificación y construcción de la blockchain.
- **Tarea 3:** Verificación de integridad y generación de reporte.

---

## 📂 Estructura del Proyecto
TP_1/
│
├── sistema_biometrico.py   
├── verificar_cadena.py     
├── output/
│   └── blockchain.json     
└── reporte.txt             

---

## ⚙️ Requisitos
- Python **3.9 o superior**
- Librerías estándar: multiprocessing, queue, os, json, hashlib, datetime, random
- Librería adicional: numpy


---
## 🛠️ Configuración del entorno virtual

1. Crear el entorno virtual (solo la primera vez):
   ```bash
   python3 -m venv venv

2. Activar el entorno virtual:
   ```bash
    source venv/bin/activate

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```



## ▶️ Instrucciones de Ejecución

### 1. Ejecutar el sistema principal (Tareas 1 y 2)

    python sistema_biometrico.py

Esto:
- Genera **60 bloques** (1 por segundo).
- Muestra en pantalla el índice del bloque, su hash y si contiene alerta.
- Guarda los bloques en output/blockchain.json.

Ejemplo de salida:
    [Bloque #1] Hash: a44121... | ALERTA: False
    [Bloque #10] Hash: 607604... | ALERTA: True
    ...
    [Main] Ejecución completada.

---

### 2. Verificar la cadena y generar reporte (Tarea 3)

    python verificar_cadena.py

Esto:
- Lee output/blockchain.json.
- Verifica que los hashes y el encadenamiento sean correctos.
- Informa si existen bloques corruptos.
- Genera el archivo reporte.txt con:
    - Cantidad total de bloques.
    - Número de bloques con alertas.
    - Bloques corruptos (si los hubiera).
    - Promedios de frecuencia, presión y oxígeno.

Ejemplo de reporte.txt:
    Total de bloques: 60
    Bloques con alertas: 1
    Bloques corruptos: 0 -> []
    Promedio frecuencia: 130.31
    Promedio presión sistólica: 144.67
    Promedio oxígeno: 94.13

---

## 👩‍💻 Autor
Candela González — Ingeniería Informática, Universidad de Mendoza.
"""

if __name__ == "__main__":
    print(README)
