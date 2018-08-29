import zmq
import sys


def main():
	if len(sys.argv) != 2:
		print("Debe ingresar su identificador")
		exit()
	miPersonaje = b""
	iniciarJuego = False
	context = zmq.Context()
	socket = context.socket(zmq.DEALER)
	identidad = sys.argv[1].encode('ascii')
	socket.identity = identidad
	socket.connect("tcp://localhost:5555")
	poller = zmq.Poller()
	poller.register(sys.stdin, zmq.POLLIN)
	poller.register(socket, zmq.POLLIN)
	socket.send_multipart([b"nuevoJugador", identidad])

	posicionPersonaje = {"pacman":(5,5),"fa":(0,0),"fb":(0,9),"fc":(9,0),"fd":(9,9)}

	while True:
		socks = dict(poller.poll())
		if socket in socks:
			operacion, *mensaje = socket.recv_multipart()
			if operacion == b"personaje":
				miPersonaje=mensaje[0]
				print(miPersonaje)
			if operacion == b"iniciarJuego":
				iniciarJuego = True
				print(posicionPersonaje)
			

		elif sys.stdin.fileno() in socks and iniciarJuego:
			print("?")
            #command = input()
            #dest, msg = command.split(' ', 1)
            #socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])


if __name__ == '__main__':
	main()
