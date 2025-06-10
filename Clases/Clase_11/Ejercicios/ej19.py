# monitoreo concurrente sin exclusion

import os
import time

def escribir_en_archivo():
    with open("archivo_compartido.txt", "a") as f:
        for i in range(10):
            f.write(f"Proceso {os.getpid()} escribiendo línea {i}\n")
            time.sleep(0.1)  # Simular trabajo

if __name__ == "__main__":
    escribir_en_archivo()