# Tarea 3: Verificación de integridad y generación de reporte

import json
import hashlib


def calcular_hash(prev_hash, datos, timestamp):
    bloque_str = f"{prev_hash}{json.dumps(datos, sort_keys=True)}{timestamp}"
    return hashlib.sha256(bloque_str.encode()).hexdigest()


def verificar_cadena_y_generar_reporte(ruta="output/blockchain.json"):
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

    with open("reporte.txt", "w") as f:
        f.write(f"Total de bloques: {total_bloques}\n")
        f.write(f"Bloques con alertas: {alertas}\n")
        f.write(f"Bloques corruptos: {len(bloques_corruptos)} -> {bloques_corruptos}\n")
        f.write(f"Promedio frecuencia: {prom_frec:.2f}\n")
        f.write(f"Promedio presión sistólica: {prom_pres:.2f}\n")
        f.write(f"Promedio oxígeno: {prom_oxi:.2f}\n")

    print("[✔] Verificación completa. Reporte generado como reporte.txt")


if __name__ == "__main__":
    verificar_cadena_y_generar_reporte()
