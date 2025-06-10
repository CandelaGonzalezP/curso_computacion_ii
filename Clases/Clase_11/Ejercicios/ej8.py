# condicion de carrera y su correccion

import multiprocessing
import time

def increment_counter_with_lock(counter, lock, iterations):
    """Función que incrementa el contador compartido usando Lock."""
    for _ in range(iterations):
        with lock:  # Adquirir el bloqueo
            current_value = counter.value
            time.sleep(0.01)  # Simular trabajo
            counter.value = current_value + 1

def main():
    iterations = 100
    counter = multiprocessing.Value('i', 0)  # Contador compartido (entero)
    lock = multiprocessing.Lock()  # Crear el bloqueo

    # Crear dos procesos que incrementan el contador
    process1 = multiprocessing.Process(target=increment_counter_with_lock, args=(counter, lock, iterations))
    process2 = multiprocessing.Process(target=increment_counter_with_lock, args=(counter, lock, iterations))

    process1.start()
    process2.start()

    process1.join()
    process2.join()

    print(f"Resultado con Lock: {counter.value}")

if __name__ == "__main__":
    main()