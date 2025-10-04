import socket
import socketserver
import threading
import sys
import math

# --- Configuración y Constantes ---
PORT = 9997
CHUNK_SIZE = 1024
# Caracteres matemáticos seguros permitidos: dígitos, punto, y operadores básicos
CARACTERES_SEGUROS = '0123456789.+-*/() '

def calcular_expresion_segura(expresion):
    """
    Evalúa una expresión matemática básica de forma segura.
    La seguridad se basa en la validación estricta de caracteres permitidos.
    """
    expresion = expresion.strip()
    
    if not expresion:
        return "ERROR: Expresión vacía."

    # 1. Validación de seguridad (El paso más crítico)
    expresion_limpia = expresion.replace(' ', '')
    
    # Comprobar que CADA carácter es seguro.
    if not all(c in CARACTERES_SEGUROS for c in expresion_limpia):
        return "ERROR: Expresión contiene caracteres no permitidos (solo números y +, -, *, /, ( ))."
    
    # 2. Evaluación con manejo de errores
    try:
        # Se usa eval() sólo después de la validación rigurosa de caracteres.
        resultado = eval(expresion)
        
        # Verificar que el resultado sea un número simple (entero o flotante)
        if isinstance(resultado, (int, float)):
            return f"RESULTADO: {resultado}"
        else:
            return "ERROR: El resultado no es un número simple."

    except ZeroDivisionError:
        return "ERROR: División por cero"
    except (SyntaxError, TypeError, NameError):
        # Captura errores como expresiones incompletas (ej: "5 +")
        return "ERROR: Expresión inválida o mal formada."
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"[ERROR interno]: {e}")
        return "ERROR: Ocurrió un error inesperado al calcular."


class ManejadorCalculadora(socketserver.BaseRequestHandler):
    """Maneja las solicitudes de cálculo de cada cliente."""
    
    def setup(self):
        # Desempaqueta IP y Puerto (los dos primeros valores de la tupla IPv6)
        self.ip, self.puerto, _, _ = self.client_address 
        self.client_info = f"[{self.ip}]:{self.puerto}"
        print(f"[*] Nueva conexión: {self.client_info}")

    def handle(self):
        """Bucle principal de recepción de expresiones."""
        
        self.request.sendall(b"Conectado. Ingresa una expresion (ej: 5 * (2 + 1) / 3) o QUIT.\n")

        while True:
            try:
                # Recibir la expresión del cliente
                data = self.request.recv(CHUNK_SIZE).decode().strip()
                if not data:
                    break # Cliente se desconectó
                
                print(f"[{self.client_info}] EXPR: {data}")
                
                if data.upper() == "QUIT":
                    break
                
                # 1. Calcular de forma segura
                respuesta = calcular_expresion_segura(data)
                
                # 2. Devolver el resultado/error al cliente
                self.request.sendall(respuesta.encode() + b'\n')
                    
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[ERROR en {self.client_info}]: {e}")
                break

    def finish(self):
        """Se llama cuando la conexión termina."""
        print(f"[*] Conexión cerrada con: {self.client_info}")


class ServidorCalculadoraIPv6(socketserver.ThreadingTCPServer):
    """Clase de servidor que utiliza IPv6 y Threads."""
    address_family = socket.AF_INET6
    allow_reuse_address = True 

# --- Ejecución Principal del Servidor ---
if __name__ == "__main__":
    HOST = "::" # Escucha en todas las interfaces IPv6
    
    print("--- Servidor de Calculadora Remota IPv6 ---")
    
    try:
        servidor = ServidorCalculadoraIPv6((HOST, PORT), ManejadorCalculadora)
        
        server_thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        server_thread.start()
        
        print(f"Servidor iniciado: Escuchando en [{HOST}]:{PORT}")
        print("Presiona Ctrl+C para detener el servidor.")

        while True:
            import time
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidor...")
        servidor.shutdown()
        servidor.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] Error al iniciar el servidor: {e}")