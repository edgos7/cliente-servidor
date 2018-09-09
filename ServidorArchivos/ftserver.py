
import zmq
import sys

def main():
    if len(sys.argv) != 4:
        print("Sample call: python ftserver <address> <port> <folder>")
        exit()

    clientsPort = sys.argv[2]
    clientsAddress = sys.argv[1]
    serversFolder = sys.argv[3]
    clientsAddress = clientsAddress + ":" + clientsPort

    context = zmq.Context()
    proxy = context.socket(zmq.REQ)
    proxy.connect("tcp://localhost:5555")

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
            byts = msg["datos"].encode("UTF-8","ignore")
            sha1byts = msg["sha1Datos"]
            sha1complete = msg["sha1Completo"]
            storeAs = serversFolder + sha1byts
            print("Storing {}".format(storeAs))
            with open(storeAs, "wb") as f:
                f.write(byts)
            print("Uploaded as {}".format(storeAs))
            clients.send_string("Done")
        if msg["operation"] == "sendIndex":
                datos = msg["datos"].encode("ascii","ignore")
                completeSha1 = msg["completeSha1"]
                filename = msg["nombreArchivo"]
                with open("servidor1/"+completeSha1+".txt", "wb") as f:
                    f.write(datos)
                print("index Subido")
                clients.send_string("Done")
        if msg["operation"]== "descargarIndex":
            nombreArchivo= msg["indexDescargar"]
            with open("servidor1/"+nombreArchivo+".txt", "rb") as output:
                datos=output.read()
                clients.send_json({"datos": datos.decode("ascii","ignore")})
        if msg["operation"]=="descargarParte":
            nombreParte=msg["parteDescargar"]
            with open("servidor1/"+nombreParte,"rb") as output:
                datos=output.read()
                clients.send_json({"datos": datos.decode("UTF-8","ignore")})
        

if __name__ == '__main__':
    main()
