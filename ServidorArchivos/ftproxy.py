import zmq

def main():
    # Address for each server to receive files
    servAddresses = []
    #diccionario para saber en que servidor se encuentran almacenado un archivo
    ubicacion = {}
    #diccionario para saber el nombre de archivo que debe tener un indice
    nombreArchivo = {}
    #diccionario para saber quien es el dueño de un archivo
    propietario = {}
    #diccionario para saber que usuarios hay conectados
    usuarios = {}


    context = zmq.Context()
    servers = context.socket(zmq.REP)
    servers.bind("tcp://*:5555")

    clients = context.socket(zmq.REP)
    clients.bind("tcp://*:6666")

    poller = zmq.Poller()
    poller.register(servers, zmq.POLLIN)
    poller.register(clients, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if clients in socks:
            #print("Message from client")
            operation, *msg = clients.recv_multipart()
            if operation == b"availableServers":
                clients.send_multipart(servAddresses)
            if operation == b"ubicacionParte":
                sha1Parte = msg[0]
                ipServidor = msg[1]
                clients.send(b"ok")
                ubicacion[sha1Parte]=ipServidor
                print("ubicacion")
                print(ubicacion)
            if operation == b"propietarioIndex":
                sha1Indice = msg[0]
                dueno = msg[1]
                clients.send(b"ok")
                propietario[sha1Indice]=dueno
                print("dueños")
                print(propietario)
            if operation == b"nombreArchivo":
                sha1Indice = msg[0]
                nombreIndice = msg[1]
                clients.send(b"ok")
                nombreArchivo[sha1Indice]=nombreIndice
                print("nombres")
                print(nombreArchivo)
            #print(msg)

        if servers in socks:
            print("Message from server")
            operation, *rest = servers.recv_multipart()
            if operation == b"newServer":
                servAddresses.append(rest[0])
                print(servAddresses)
                servers.send(b"Ok")



if __name__ == '__main__':
    main()
