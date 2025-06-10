# Rlock

import multiprocessing
import time

class CuentaBancaria:
    def __init__(self, saldo_inicial=0):
        self.saldo = saldo_inicial
        self.lock = multiprocessing.RLock()  # Usar RLock para sincronización

    def depositar(self, cantidad):
        with self.lock:  # Adquirir el RLock
            print(f"Depositando {cantidad}...")
            self.saldo += cantidad
            time.sleep(0.1)  # Simular trabajo
            print(f"Nuevo saldo después de depositar: {self.saldo}")

    def retirar(self, cantidad):
        with self.lock:  # Adquirir el RLock
            if self.saldo >= cantidad:
                print(f"Retirando {cantidad}...")
                self.saldo -= cantidad
                time.sleep(0.1)  # Simular trabajo
                print(f"Nuevo saldo después de retirar: {self.saldo}")
            else:
                print(f"No se puede retirar {cantidad}. Saldo insuficiente: {self.saldo}")

    def transferencia(self, otra_cuenta, cantidad):
        with self.lock:  # Adquirir el RLock
            print(f"Transfiriendo {cantidad} a otra cuenta...")
            self.retirar(cantidad)  # Llamada recursiva a método sincronizado
            otra_cuenta.depositar(cantidad)  # Llamada recursiva a método sincronizado

def simular_acceso(cuenta, otra_cuenta, proceso_id):
    """Simula depósitos, retiros y transferencias desde varios procesos."""
    print(f"Proceso {proceso_id} iniciando operaciones...")
    cuenta.depositar(100)
    cuenta.retirar(50)
    cuenta.transferencia(otra_cuenta, 30)
    print(f"Proceso {proceso_id} terminó operaciones.")

def main():
    cuenta1 = CuentaBancaria(200)
    cuenta2 = CuentaBancaria(100)

    procesos = []

    # Crear 5 procesos que acceden a la cuenta bancaria
    for i in range(5):
        proceso = multiprocessing.Process(target=simular_acceso, args=(cuenta1, cuenta2, i + 1))
        procesos.append(proceso)
        proceso.start()

    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()

    print(f"Saldo final cuenta 1: {cuenta1.saldo}")
    print(f"Saldo final cuenta 2: {cuenta2.saldo}")

if __name__ == "__main__":
    main()