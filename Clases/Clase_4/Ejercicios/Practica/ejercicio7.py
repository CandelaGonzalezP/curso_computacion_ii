# EJERCICIO 7 - SISTEMA DE PROCESAMIENTO DE TRANSACCIONES

import os
import sys
import json
import time
import random
from collections import defaultdict

class Operacion:
    def __init__(self, codigo=None, categoria=None, valor=None):
        self.codigo = codigo or random.randint(1000, 9999)
        self.categoria = categoria or random.choice(["deposito", "extraccion", "pago", "envio"])
        self.valor = valor or round(random.uniform(20, 1200), 2)

    def serializar(self):
        return json.dumps({
            "codigo": self.codigo,
            "categoria": self.categoria,
            "valor": self.valor
        })

    @staticmethod
    def deserializar(cadena):
        try:
            datos = json.loads(cadena)
            return Operacion(datos["codigo"], datos["categoria"], datos["valor"])
        except Exception as e:
            print(f"Error deserializando operación: {e}")
            return None

    def __str__(self):
        return f"[{self.codigo}] {self.categoria.upper()} - ${self.valor:.2f}"

def productor(nombre, salida_fd, cantidad):
    with os.fdopen(salida_fd, "w") as salida:
        for _ in range(cantidad):
            op = Operacion()
            salida.write(op.serializar() + "\n")
            salida.flush()
            print(f"{nombre} creó {op}")
            time.sleep(random.uniform(0.2, 0.6))
        salida.write("FIN\n")
        salida.flush()
        print(f"{nombre} terminó")

def validador(entradas_fd, salida_fd):
    entradas = [os.fdopen(fd, "r") for fd in entradas_fd]
    salida = os.fdopen(salida_fd, "w")

    activos = len(entradas)
    total_ok, total_fallos, total_procesadas = 0, 0, 0

    while activos > 0:
        for i, entrada in enumerate(entradas):
            if entrada is None:
                continue
            linea = entrada.readline().strip()
            if not linea:
                continue
            if linea == "FIN":
                entradas[i] = None
                activos -= 1
                print(f"Validador: Productor {i+1} finalizó")
                continue

            operacion = Operacion.deserializar(linea)
            if operacion is None:
                continue

            es_valida = True
            motivo = ""

            if operacion.valor <= 0:
                es_valida = False
                motivo = "Valor no puede ser negativo"
            elif operacion.categoria == "extraccion" and operacion.valor > 700:
                es_valida = False
                motivo = "Extracciones limitadas a $700"

            resultado = {
                "operacion": operacion.__dict__,
                "valida": es_valida,
                "motivo": motivo,
                "marca_tiempo": time.time()
            }

            salida.write(json.dumps(resultado) + "\n")
            salida.flush()

            total_procesadas += 1
            if es_valida:
                total_ok += 1
            else:
                total_fallos += 1

        time.sleep(0.1)

    resumen = {
        "resumen_final": True,
        "total": total_procesadas,
        "validas": total_ok,
        "invalidas": total_fallos
    }
    salida.write(json.dumps(resumen) + "\n")
    salida.write("FIN\n")
    salida.flush()

def registrador(entrada_fd):
    stats = defaultdict(int)
    totales = defaultdict(float)
    registros = []

    with os.fdopen(entrada_fd, "r") as entrada:
        while True:
            linea = entrada.readline().strip()
            if not linea:
                continue
            if linea == "FIN":
                break

            data = json.loads(linea)
            if data.get("resumen_final"):
                print("\nResumen del Validador:")
                print(f"- Procesadas: {data['total']}")
                print(f"- Válidas: {data['validas']}")
                print(f"- Inválidas: {data['invalidas']}")
                continue

            op = data["operacion"]
            if data["valida"]:
                stats[op["categoria"]] += 1
                totales[op["categoria"]] += op["valor"]
                registros.append(op)

        print("\n=== REGISTRO FINAL ===")
        for tipo, cantidad in stats.items():
            print(f"{tipo}: {cantidad} operaciones - ${totales[tipo]:.2f}")

        top = sorted(registros, key=lambda x: x["valor"], reverse=True)[:5]
        print("\nTop 5 operaciones más altas:")
        for op in top:
            print(f"- [{op['codigo']}] {op['categoria']} ${op['valor']:.2f}")

def main():
    productores = 3
    tubos_pv = []
    for _ in range(productores):
        r, w = os.pipe()
        tubos_pv.append((r, w))

    r_val_log, w_val_log = os.pipe()

    for i in range(productores):
        pid = os.fork()
        if pid == 0:
            for j, (r_fd, w_fd) in enumerate(tubos_pv):
                if i != j:
                    os.close(r_fd)
                    os.close(w_fd)
                else:
                    os.close(r_fd)
            os.close(r_val_log)
            os.close(w_val_log)
            productor(f"Prod-{i+1}", tubos_pv[i][1], random.randint(5, 10))
            sys.exit(0)

    # Proceso validador
    pid = os.fork()
    if pid == 0:
        for r_fd, w_fd in tubos_pv:
            os.close(w_fd)
        os.close(r_val_log)
        validador([r for r, _ in tubos_pv], w_val_log)
        sys.exit(0)

    # Proceso registrador
    pid = os.fork()
    if pid == 0:
        for r_fd, w_fd in tubos_pv:
            os.close(r_fd)
            os.close(w_fd)
        os.close(w_val_log)
        registrador(r_val_log)
        sys.exit(0)

    for r_fd, w_fd in tubos_pv:
        os.close(r_fd)
        os.close(w_fd)
    os.close(r_val_log)
    os.close(w_val_log)

    for _ in range(productores + 2):
        os.wait()

if __name__ == "__main__":
    main()

