import socket
import socketserver
import threading
import sys
import time
import os

# --- Configuración y Constantes ---
PORT = 9998 # Usamos un puerto diferente para evitar conflictos con Ejercicio 3
CHUNK_SIZE = 1024

class Estadisticas:
    """Clase para almacenar y gestionar las estadísticas del servidor de forma segura."""
    def __init__(self):
        self.lock = threading.Lock()
        self.conexiones_ipv4 = 0
        self.conexiones_ipv6 = 0
        self.datos_transferidos = 0 # En bytes
        self.tiempos_respuesta = [] # Lista de tiempos de respuesta por sesión

    def registrar_conexion(self, familia_ip):
        """Incrementa el contador de conexiones según la familia IP."""
        with self.lock:
            if familia_ip == socket.AF_INET:
                self.conexiones_ipv4 += 1
            elif familia_ip == socket.AF_INET6:
                self.conexiones_ipv6 += 1

    def registrar_transferencia(self, bytes_transferidos):
        """Acumula los datos transferidos."""
        with self.lock:
            self.datos_transferidos += bytes_transferidos

    def registrar_tiempo_respuesta(self, duracion):
        """Añade el tiempo de duración de la sesión."""
        with self.lock:
            self.tiempos_respuesta.append(duracion)

    def generar_reporte(self):
        """Calcula las métricas finales y genera el reporte."""
        with self.lock:
            total_conexiones = self.conexiones_ipv4 + self.conexiones_ipv6
            
            # Calcular tiempo promedio de respuesta
            if self.tiempos_respuesta:
                tiempo_promedio = sum(self.tiempos_respuesta) / len(self.tiempos_respuesta)
            else:
                tiempo_promedio = 0

            # Formatear datos transferidos
            def format_bytes(bytes_total):
                if bytes_total >= 1024**3:
                    return f"{bytes_total / 1024**3:.2f} GB"
                elif bytes_total >= 1024**2:
                    return f"{bytes_total / 1024**2:.2f} MB"
                elif bytes_total >= 1024:
                    return f"{bytes_total / 1024:.2f} KB"
                else:
                    return f"{bytes_total} bytes"

            reporte = "\n" + "="*50 + "\n"
            reporte += "       REPORTE DE ESTADÍSTICAS DEL SERVIDOR\n"
            reporte += "="*50 + "\n"
            reporte += f"Total de Conexiones: {total_conexiones}\n"
            reporte += f"  - IPv4: {self.conexiones_ipv4}\n"
            reporte += f"  - IPv6: {self.conexiones_ipv6}\n"
            reporte += f"Tiempo Promedio de Sesión: {tiempo_promedio:.4f} segundos\n"
            reporte += f"Total de Datos Transferidos: {format_bytes(self.datos_transferidos)}\n"
            reporte += "="*50
            return reporte

# Objeto global para las estadísticas
STATS = Estadisticas()

class ManejadorDualStack(socketserver.BaseRequestHandler):
    """Maneja las solicitudes de cada cliente (IPv4 o IPv6)."""
    
    def setup(self):
        self.start_time = time.time()
        self.socket_family = self.request.family
        
        # Obtener IP y Puerto sin importar si es IPv4 o IPv6
        if self.socket_family == socket.AF_INET:
            self.ip, self.puerto = self.client_address
            protocolo = "IPv4"
        elif self.socket_family == socket.AF_INET6:
            # Desempaqueta los 4 valores de IPv6
            self.ip, self.puerto, _, _ = self.client_address
            protocolo = "IPv6"
        else:
            self.ip, self.puerto = "Desconocido", "N/A"
            protocolo = "Otro"
            
        self.client_info = f"[{protocolo}] {self.ip}:{self.puerto}"
        
        STATS.registrar_conexion(self.socket_family)
        print(f"[*] Conexión iniciada: {self.client_info}")

    def handle(self):
        """Simulación de un servicio simple (eco y transferencia de datos)."""
        bytes_sesion = 0
        
        # Mensaje de bienvenida
        mensaje_bienvenida = f"Servidor Dual Stack. Tu IP: {self.ip} | Protocolo: {self.client_info.split()[0]}\n"
        self.request.sendall(mensaje_bienvenida.encode())
        bytes_sesion += len(mensaje_bienvenida)

        while True:
            try:
                # Recibir datos del cliente
                data = self.request.recv(CHUNK_SIZE)
                if not data:
                    break # Cliente se desconectó
                
                # Simular transferencia de datos (eco)
                self.request.sendall(b"ECO: " + data)
                bytes_sesion += len(data) * 2 # Recibido + Enviado

                # Actualizar estadísticas en cada transferencia
                STATS.registrar_transferencia(len(data) * 2) 
                
            except ConnectionResetError:
                break
            except Exception:
                break

    def finish(self):
        """Registra el tiempo de la sesión al finalizar."""
        end_time = time.time()
        duracion = end_time - self.start_time
        STATS.registrar_tiempo_respuesta(duracion)
        
        print(f"[*] Conexión finalizada: {self.client_info} (Duración: {duracion:.2f}s)")


class ServidorDualStack(socketserver.ThreadingTCPServer):
    """
    Servidor personalizado que permite escuchar en IPv4 y IPv6 a la vez.
    
    Para lograr el Dual Stack, se debe establecer el atributo address_family
    a AF_INET y luego establecer socket.IPPROTO_IPV6, socket.IPV6_V6ONLY a 0
    en el constructor.
    """
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        # 1. Establecer AF_INET (IPv4) como familia principal
        self.address_family = socket.AF_INET
        self.allow_reuse_address = True
        
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        
        # 2. Configurar el socket para escuchar en IPv6 y en IPv4
        # Si la plataforma lo permite, configura IPV6_V6ONLY=0
        try:
            # Crea un socket IPv6, que también manejará IPv4 si V6ONLY=0
            self.socket = socket.socket(socket.AF_INET6, self.socket_type)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Deshabilitar IPV6_V6ONLY permite recibir conexiones IPv4
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0) 
            self.address_family = socket.AF_INET6 # Se actualiza la familia para el binding
            
            # Rebind (necesario tras la manipulación del socket)
            if bind_and_activate:
                self.server_bind()
                self.server_activate()
            print("[INFO] Socket configurado para Dual Stack (IPv4 e IPv6).")
        except Exception as e:
            # Si falla (ej: SO no soporta Dual Stack o IPV6_V6ONLY), cae a IPv4
            print(f"[ALERTA] Falló configuración Dual Stack ({e}). Cayendo a IPv4 puro.")
            # Se requiere volver a inicializar con IPv4
            self.server_close()
            self.address_family = socket.AF_INET
            socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)


if __name__ == "__main__":
    HOST = "" # Escucha en TODAS las interfaces (IPv4 e IPv6) de forma más segura
    
    print("--- Servidor Dual Stack Inteligente ---")
    
    try:
        # Crea y arranca el servidor
        servidor = ServidorDualStack((HOST, PORT), ManejadorDualStack)
        
        server_thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        server_thread.start()
        
        print(f"Servidor iniciado: Escuchando en [{HOST}]:{PORT} (Protocolo Dual)")
        print("Presiona Ctrl+C para detener el servidor y generar el reporte.")

        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidor...")
        servidor.shutdown()
        servidor.server_close()
        
        # --- Generar Reporte Final ---
        print(STATS.generar_reporte())
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] Error al iniciar el servidor: {e}")