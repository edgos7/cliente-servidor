
import zmq
import sys

def main():
    if len(sys.argv) != 6:
        print("Sample call: python ftserver <address servidor> <port servidor> <folder> <address proxy> <port proxy>")
        exit()

    clientsPort = sys.argv[2]
    clientsAddress = sys.argv[1]
    serversFolder = sys.argv[3]
    ipProxy = sys.argv[4]
    portProxy = sys.argv[5]
    clientsAddress = clientsAddress + ":" + clientsPort

    context = zmq.Context()
    proxy = context.socket(zmq.REQ)
    proxy.connect("tcp://{}:{}".format(ipProxy,portProxy))

    clients = context.socket(zmq.REP)
    clients.bind("tcp://*:{}".format(clientsPort))

    
    proxy.send_json({"operation" : "newServer","direccionIp":clientsAddress})
    m = proxy.recv_string()
    print(m)

    while True:
        print("Waitting for useres to upload!!!")
        msg = clients.recv_json()
        if msg["operation"] == "upload":
            filename = msg["filename"]
            sha1byts = msg["sha1Datos"]
            sha1complete = msg["sha1Completo"]
            storeAs = serversFolder + sha1byts
            clients.send_string("Done")
            byts = clients.recv()
            clients.send_string("ok")
            print("Storing {}".format(storeAs))
            with open(storeAs, "wb") as f:
                f.write(byts)
            print("Uploaded as {}".format(storeAs))
            
        if msg["operation"] == "sendIndex":
                datos = msg["datos"].encode("ascii","ignore")
                completeSha1 = msg["completeSha1"]
                filename = msg["nombreArchivo"]
                with open(serversFolder+""+completeSha1+".txt", "wb") as f:
                    f.write(datos)
                print("index Subido")
                clients.send_string("Done")
        if msg["operation"]== "descargarIndex":
            nombreArchivo= msg["indexDescargar"]
            with open(serversFolder+""+nombreArchivo+".txt", "rb") as output:
                datos=output.read()
                clients.send_json({"datos": datos.decode("ascii","ignore")})
        if msg["operation"]=="descargarParte":
            nombreParte=msg["parteDescargar"]
            with open(serversFolder+""+nombreParte,"rb") as output:
                datos=output.read()
                clients.send(datos)
        

if __name__ == '__main__':
    main()
