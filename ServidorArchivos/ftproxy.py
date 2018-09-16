import zmq

def main():
    # Address for each server to receive files
    servAddresses = []
    #diccionario para saber en que servidor se encuentran almacenado un archivo sha1Parte=ipserver
    ubicacion = {}
    #diccionario para saber el nombre de archivo que debe tener un indice sha1Parte=nombreArchivo
    nombreArchivo = {}
    #diccionario para saber quien es el dueño de un archivo sha1Parte=dueño
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
            msg=clients.recv_json()
            if msg["operation"] == "availableServers":
                clients.send_json({"direccionServidores":servAddresses})
            if msg["operation"] == "ubicacionParte":
                sha1Parte = msg["sha1"]
                ipServidor = msg["ipServidor"]
                clients.send_string("ok")
                ubicacion[sha1Parte]=ipServidor
                print("ubicacion")
                print(ubicacion)
            if msg["operation"]== "propietarioIndex":
                sha1Indice = msg["sha1Indice"]
                dueno = msg["propietario"]
                clients.send_string("ok")
                propietario[sha1Indice]=dueno
                print("dueños")
                print(propietario)
            if msg["operation"] == "nombreArchivo":
                sha1Indice = msg["sha1Indice"]
                nombreIndice = msg["nombreArchivo"]
                clients.send_string("ok")
                nombreArchivo[sha1Indice]=nombreIndice
                print("nombres")
                print(nombreArchivo)
            if msg["operation"] =="listar":
                user = msg["user"]
                listadoSha1=[]
                listadoArchivos=[]
                for member in propietario:
                    if propietario[member] == user:
                        listadoSha1.append(member)
                for member in listadoSha1:
                    listadoArchivos.append(nombreArchivo[member])
                clients.send_json({"listadoArchivos": listadoArchivos})
            if msg["operation"] == "descargarIndex":
                nameArchivo = msg["nombreArchivo"]
                dueno =msg["usuario"]
                for member in nombreArchivo:
                    if (nombreArchivo[member] == nameArchivo) and (propietario[member] == dueno):
                        ipIndice = ubicacion[member]
                        sha1Indice = member
                        break
                clients.send_json({"ipIndex": ipIndice, "sha1Indice": sha1Indice})
            if msg["operation"] =="descargarParte":
                nombreParte=msg["nombreArchivo"]
                ipParte = ubicacion[nombreParte]
                clients.send_json({"ipParte": ipParte})
            if msg["operation"]=="registrarUsuario":
                user =msg["user"]
                ip=msg["ip"]
                port=msg["port"]
                us_socket = context.socket(zmq.REQ)
                us_socket.connect("tcp://{}:{}".format(ip, port))
                usuarios[user]=us_socket
                clients.send_string("ok")
                print(usuarios)
            if msg["operation"]=="compartir":
                quien=msg["quien"]
                conQuien=msg["conQuien"]
                cualArchivo=msg["cualArchivo"]
                socketBuscado=usuarios[conQuien]
                socketBuscado.send_json(msg)
                socketBuscado.recv_string()
                clients.send_string("ok")


        if servers in socks:
            print("Message from server")
            msg=servers.recv_json()
            if msg["operation"] == "newServer":
                ipAdress = msg["direccionIp"]
                servAddresses.append(ipAdress)
                print(servAddresses)
                servers.send_string("Ok")



if __name__ == '__main__':
    main()
