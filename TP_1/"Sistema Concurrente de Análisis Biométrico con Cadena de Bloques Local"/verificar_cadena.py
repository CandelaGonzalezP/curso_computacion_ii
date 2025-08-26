# Tarea 3: Verificación de integridad y generación de reporte

import json
import hashlib
import os
from datetime import datetime


def calcular_hash(prev_hash, datos, timestamp):

    """
    Calcula el hash SHA-256 de un bloque a partir de:
    - El hash previo
    - Los datos biométricos
    - El timestamp

    Retorna el hash como string en hexadecimal.
    """

    bloque_str = f"{prev_hash}{json.dumps(datos, sort_keys=True)}{timestamp}"
    return hashlib.sha256(bloque_str.encode()).hexdigest()


def verificar_cadena_y_generar_reporte():

    """
    Verifica la integridad de la blockchain y genera un reporte:
    - Comprueba que cada bloque tenga un hash válido.
    - Cuenta la cantidad de bloques corruptos y con alertas.
    - Calcula promedios generales de frecuencia, presión y oxígeno.
    - Genera un archivo 'reporte.txt' con el resumen de resultados.
    """

    ruta = os.path.join(os.path.dirname(__file__), "output", "blockchain.json")

    with open(ruta, "r") as f:
        cadena = json.load(f)

    bloques_corruptos = []
    alertas = 0
    suma_frec = 0
    suma_pres = 0
    suma_oxi = 0

    for i, bloque in enumerate(cadena):
        timestamp = bloque["timestamp"]
        datos = bloque["datos"]
        prev_hash = bloque["prev_hash"]
        hash_actual = bloque["hash"]

        hash_recalculado = calcular_hash(prev_hash, datos, timestamp)

        if hash_actual != hash_recalculado:
            bloques_corruptos.append(i + 1)

        if bloque["alerta"]:
            alertas += 1

        suma_frec += datos["frecuencia"]["media"]
        suma_pres += datos["presion"]["media"]
        suma_oxi += datos["oxigeno"]["media"]

    total_bloques = len(cadena)
    prom_frec = suma_frec / total_bloques
    prom_pres = suma_pres / total_bloques
    prom_oxi = suma_oxi / total_bloques

    # Construcción del reporte
    contenido = []
    contenido.append("=== REPORTE DE ANÁLISIS BIOMÉTRICO ===\n")
    contenido.append("Este reporte resume la integridad de la cadena de bloques y los valores biométricos procesados.\n")

    contenido.append("Información General:")
    contenido.append(f"- Total de bloques: {total_bloques}")
    contenido.append(f"- Bloques con alertas: {alertas}")
    contenido.append(f"- Bloques corruptos: {len(bloques_corruptos)} -> {bloques_corruptos}\n")

    contenido.append("Promedios Generales:")
    contenido.append(f"- Frecuencia cardíaca promedio: {prom_frec:.2f} bpm")
    contenido.append(f"- Presión sistólica promedio: {prom_pres:.2f} mmHg")
    contenido.append(f"- Oxígeno en sangre promedio: {prom_oxi:.2f} %\n")

    contenido.append("Verificación de Integridad:")
    if len(bloques_corruptos) == 0:
        contenido.append("✔ La cadena de bloques mantiene su integridad.\n")
    else:
        contenido.append("✘ Se detectaron bloques corruptos en la cadena.\n")

    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    hora_actual = datetime.now().strftime('%H:%M:%S')

    contenido.append("Fecha de generación del reporte:")
    contenido.append(f"{fecha_actual}\n")
    contenido.append("Hora de generación del reporte:")
    contenido.append(f"{hora_actual}\n")

    ruta_reporte = os.path.join(os.path.dirname(__file__), "reporte.txt")
    with open(ruta_reporte, "w") as f:
        f.write("\n".join(contenido))

    print("[✔] Verificación completa. Reporte generado como reporte.txt")


if __name__ == "__main__":
    verificar_cadena_y_generar_reporte()
