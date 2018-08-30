import zmq

def movimientoValido(posPersonaje, direccion):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	if direccion == b"derecha":
		if (posx+1) < 10:
			return True
	if direccion == b"izquierda":
		if (posx-1) > -1:
			return True
	if direccion == b"arriba":
		if (posy-1) > -1:
			return True
	if direccion == b"abajo":
		if (posx+1) < 10:
			return True


def actualizarPosicion(posPersonaje, direccion):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	if direccion == b"derecha":
		posx = posx+1
	if direccion == b"izquierda":
		posx = posx-1
	if direccion == b"arriba":
		posy = posy-1
	if direccion == b"abajo":
		posy = posy+1
	nuevaDireccion = (posx,posy)
	return nuevaDireccion


def main():
	conectados = 0
	listaPersonajes = (b"pacman",b"fa",b"fb",b"fc",b"fd")
	usuariosConectados = {}
	personaje = {}
	posicionPersonaje = {b"pacman":(5,5),b"fa":(0,0),b"fb":(0,9),b"fc":(9,0),b"fd":(9,9)}
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
			obtenerPersonaje = personaje[identidad]
			posPersonaje = posicionPersonaje[obtenerPersonaje]
			valido = movimientoValido(posPersonaje, direccion)
			print(valido)
			if valido == True:
				nuevaPos = actualizarPosicion(posPersonaje,direccion)
				posicionPersonaje[obtenerPersonaje] = nuevaPos
				for member in usuariosConectados:
					print("enviando nuevas posiciones")
					socket.send_multipart([member , b"actualizarPosicion",obtenerPersonaje, bytes(nuevaPos[0]), bytes(nuevaPos[1])])

		if conectados == 2:
			for member in usuariosConectados:
				socket.send_multipart([member , b"iniciarJuego" ])

if __name__ == '__main__':
	main()