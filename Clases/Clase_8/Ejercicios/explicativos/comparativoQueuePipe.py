from multiprocessing import Process, Pipe, Queue

def enviar_pipe(conn):
    conn.send("Hola desde Pipe")
    conn.close()

def enviar_queue(q):
    q.put("Hola desde Queue")

if __name__ == '__main__':
    # Pipe
    p_conn, c_conn = Pipe()
    p1 = Process(target=enviar_pipe, args=(c_conn,))
    
    # Queue
    q = Queue()
    p2 = Process(target=enviar_queue, args=(q,))
    
    p1.start()
    p2.start()
    
    print(p_conn.recv())
    print(q.get())
    
    p1.join()
    p2.join()
