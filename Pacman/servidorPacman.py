import zmq

def main():
	conectados = 0
	listaPersonajes = (b"pacman",b"fa",b"fb",b"fc",b"fd")
	usuariosConectados = {}
	personaje = {}
	posicionPersonaje = {"pacman":(5,5),"fa":(0,0),"fb":(0,9),"fc":(9,0),"fd":(9,9)}
	context = zmq.Context()
	socket = context.socket(zmq.ROUTER)
	socket.bind("tcp://*:5555")

	while True:
		identidad, operacion, *mensaje = socket.recv_multipart()
		print("Mensaje {}, identidad {} ".format(operacion,mensaje[0]))
		if operacion == b"nuevoJugador": 
			usuariosConectados[mensaje[0]]=identidad
			personaje[mensaje[0]]=listaPersonajes[conectados]
			conectados+=1
			print(usuariosConectados)
			print(personaje)
			print(posicionPersonaje)
			socket.send_multipart([identidad , b"personaje", personaje[identidad]])
		if operacion == b"movimiento":
			direccion = mensaje[0]
		if conectados == 2:
			for member in usuariosConectados:
				socket.send_multipart([member , b"iniciarJuego" ])

if __name__ == '__main__':
	main()