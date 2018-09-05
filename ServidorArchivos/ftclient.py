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
        s.connect("tcp://"+ ad.decode("ascii"))
        sockets.append(s)

    with open(filename, "rb") as f:
        completeSha1= bytes(computeHashFile(filename), "ascii")
        finished = False
        part = 0
        while not finished:
            print("Uploading part {}".format(part))
            f.seek(part*partSize)
            bt = f.read(partSize)
            sha1bt = bytes(computeHash(bt), "ascii")
            s = sockets[part % len(sockets)]
            s.send_multipart([b"upload", filename, bt, sha1bt, completeSha1])
            response = s.recv()
            proxy.send_multipart([b"ubicacionParte", sha1bt,servers[part%len(sockets)]])
            proxy.recv()
            with open(completeSha1.decode("ascii")+".txt", "a") as output:
            	output.write(sha1bt.decode("ascii")+"\n")
            print("Received reply for part {} ".format(part))
            part = part + 1
            if len(bt) < partSize:
                finished = True
    with open(completeSha1.decode("ascii")+".txt", "rb") as f:
        indice=f.read()
        sha1Indice=bytes(computeHashFile(completeSha1.decode("ascii")+".txt"),"ascii")
        s.send_multipart([b"sendIndex",indice,sha1Indice,filename])
        response=s.recv()
        proxy.send_multipart([b"ubicacionParte", sha1Indice,servers[part%len(sockets)]])
        proxy.recv()
        proxy.send_multipart([b"propietarioIndex", sha1Indice,propietario])
        proxy.recv()
        proxy.send_multipart([b"nombreArchivo", sha1Indice,filename])
        proxy.recv()
    os.remove(completeSha1.decode("ascii")+".txt")

def main():
    if len(sys.argv) != 4:
        print("Must be called with a filename")
        print("Sample call: python ftclient <username> <operation> <filename>")
        exit()


    username = sys.argv[1].encode('ascii')
    operation = sys.argv[2]
    filename = sys.argv[3].encode('ascii')

    context = zmq.Context()
    proxy = context.socket(zmq.REQ)
    proxy.connect("tcp://localhost:6666")

    print("Operation: {}".format(operation))
    if operation == "upload":
        proxy.send_multipart([b"availableServers"])
        servers = proxy.recv_multipart()
        print("There are {} available servers".format(len(servers)))
        uploadFile(context, filename, servers,proxy,username)
        print("File {} was uploaded.".format(filename))
    elif operation == "download":
        print("Not implemented yet")
    elif operation == "share":
        print("Not implemented yet")
    else:
        print("Operation not found!!!")

if __name__ == '__main__':
    main()
