from multiprocessing import Process, Pipe

def enviar(conexion):
    conexion.send("Mensaje desde el proceso hijo")
    conexion.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=enviar, args=(child_conn,))
    p.start()
    
    print(parent_conn.recv())  # Recibe el mensaje
    p.join()
