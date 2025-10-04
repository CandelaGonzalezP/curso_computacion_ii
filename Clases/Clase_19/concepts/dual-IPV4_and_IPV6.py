import socket

def obtener_direcciones(host, puerto):
    """Obtiene todas las direcciones disponibles para un host"""
    direcciones = socket.getaddrinfo(
        host, 
        puerto, 
        socket.AF_UNSPEC,  # IPv4 o IPv6
        socket.SOCK_STREAM
    )
    
    for addr in direcciones:
        familia, tipo, proto, canonname, sockaddr = addr
        protocolo = "IPv4" if familia == socket.AF_INET else "IPv6"
        print(f"{protocolo}: {sockaddr}")
    
    return direcciones

# Ejemplo de uso
direcciones = obtener_direcciones("localhost", 8080)