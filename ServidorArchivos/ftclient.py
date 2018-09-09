import zmq
import sys
import hashlib
import os

partSize = 1024 * 1024 * 10

def uploadFile2(filename, socket):
    with open(filename, "rb") as f:
        finished = False
        part = 0
        while not finished:
            print("Uploading part {}".format(part))
            f.seek(part*partSize)
            bt = f.read(partSize)
            socket.send_multipart([filename, bt])
            response = socket.recv()
            print("Received reply  [%s ]" % (response))
            part = part + 1
            if len(bt) < partSize:
                finished = True

def computeHashFile(filename):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def computeHash(bytes):
    sha1 = hashlib.sha1()
    sha1.update(bytes)
    return sha1.hexdigest()

def uploadFile(context, filename, servers, proxy,propietario):
    sockets = []
    for ad in servers:
        s = context.socket(zmq.REQ)
        s.connect("tcp://"+ ad)
        sockets.append(s)

    with open(filename, "rb") as f:
        completeSha1= computeHashFile(filename)
        finished = False
        part = 0
        while not finished:
            print("Uploading part {}".format(part))
            f.seek(part*partSize)
            bt = f.read(partSize)
            sha1bt = computeHash(bt)
            s = sockets[part % len(sockets)]
            s.send_json({"operation" : "upload", "filename": filename, "sha1Datos": sha1bt,"sha1Completo" : completeSha1 })
            response = s.recv_string()
            s.send(bt)
            s.recv_string()
            proxy.send_json({"operation":"ubicacionParte", "sha1": sha1bt,"ipServidor": servers[part%len(sockets)]})
            proxy.recv_string()
            with open(completeSha1+".txt", "a") as output:
            	output.write(sha1bt+"\n")
            print("Received reply for part {} ".format(part))
            part = part + 1
            if len(bt) < partSize:
                finished = True
    with open(completeSha1+".txt", "rb") as f:
        indice=f.read()
        sha1Indice=computeHash(indice)
        s.send_json({"operation" : "sendIndex", "datos": indice.decode("ascii","ignore"),"completeSha1": sha1Indice, "nombreArchivo":filename})
        s.recv_string()
        proxy.send_json({"operation": "ubicacionParte","sha1": sha1Indice,"ipServidor":servers[part%len(sockets)]})
        proxy.recv_string()
        proxy.send_json({"operation":"propietarioIndex", "sha1Indice": sha1Indice, "propietario": propietario})
        proxy.recv_string()
        proxy.send_json({"operation": "nombreArchivo" , "sha1Indice":sha1Indice, "nombreArchivo":filename})
        proxy.recv_string()
    os.remove(completeSha1+".txt")


def download(filename,context,proxy,username):
	proxy.send_json({"operation":"descargarIndex","nombreArchivo":filename, "usuario":username})
	msg = proxy.recv_json()
	ipProxy = msg["ipIndex"]
	sha1Indice= msg["sha1Indice"]
	s = context.socket(zmq.REQ)
	s.connect("tcp://"+ ipProxy)
	s.send_json({"operation": "descargarIndex", "indexDescargar": sha1Indice})
	msg=s.recv_json()
	datos = msg["datos"].encode("ascii","ignore")
	with open("descargas/"+sha1Indice+".txt", "wb") as output:
		output.write(datos)
	with open ("descargas/"+sha1Indice+".txt", "r") as output:
		linea = output.readline()
		linea = linea.rstrip("\n")
		while linea !='':
			proxy.send_json({"operation":"descargarParte","nombreArchivo":linea, })
			msg = proxy.recv_json()
			ipParte= msg["ipParte"]
			s=context.socket(zmq.REQ)
			s.connect("tcp://"+ ipParte)
			s.send_json({"operation": "descargarParte", "parteDescargar": linea})
			datos =s.recv()
			with open("descargas/"+filename, "ab") as f:
				f.write(datos)
			linea = output.readline()
			linea = linea.rstrip("\n")
	os.remove("descargas/"+sha1Indice+".txt")
	print("descarga finalisada")




def main():
    if len(sys.argv) != 2:
        print("Sample call: python ftclient <username> ")
        exit()
    username = sys.argv[1]
    context = zmq.Context()
    proxy = context.socket(zmq.REQ)
    proxy.connect("tcp://localhost:6666")
    proxy.send_json({"operation": "registrarUsuario", "user":username})
    proxy.recv()
    while True:
        operation = input("Ingrese la opcion que desea realisar: ")
        print("Operation: {}".format(operation))
        if operation == "upload":
            proxy.send_json({"operation": "availableServers"})
            msg = proxy.recv_json()
            servers = msg["direccionServidores"]
            print("There are {} available servers".format(len(servers)))
            filename = input("Ingrese nombre del archivo a subir: ")
            uploadFile(context, filename, servers,proxy,username)
            print("File {} was uploaded.".format(filename))
        elif operation == "listar":
            proxy.send_json({"operation":"listar","user": username})
            listado = proxy.recv_json()
            listaArchivos=listado["listadoArchivos"]
            print("Lista de archivos del usuario: "+username)
            for member in listaArchivos:
                print(member)
        elif operation == "download":
            filename=input("Ingrese nombre del archivo a descargar: ")
            download(filename,context,proxy,username)
        elif operation == "share":
            print("Not implemented yet")
            
        else:
            print("Operation not found!!!")

if __name__ == '__main__':
    main()
