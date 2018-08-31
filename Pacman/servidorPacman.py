import zmq

def movimientoValido(posPersonaje, direccion):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	if direccion == b"derecha":
		if (posx+50) < 500:
			return True
	if direccion == b"izquierda":
		if (posx-50) > -50:
			return True
	if direccion == b"arriba":
		if (posy-50) > -50:
			return True
	if direccion == b"abajo":
		if (posy+50) < 500:
			return True


def actualizarPosicion(posPersonaje, direccion):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	if direccion == b"derecha":
		posx = posx+50
	if direccion == b"izquierda":
		posx = posx-50
	if direccion == b"arriba":
		posy = posy-50
	if direccion == b"abajo":
		posy = posy+50
	nuevaDireccion = (posx,posy)
	return nuevaDireccion


def main():
	conectados = 0
	listaPersonajes = (b"pacman",b"fantasmaAmarillo",b"fantasmaAzul",b"fantasmaRojo",b"fantasmaRosa")
	usuariosConectados = {}
	personaje = {}
	posicionPersonaje = {b"pacman":(250,250),b"fantasmaAmarillo":(0,0),b"fantasmaAzul":(0,450),b"fantasmaRojo":(450,0),b"fantasmaRosa":(450,450)}
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
					socket.send_multipart([member , b"actualizarPosicion",obtenerPersonaje, bytes(str(nuevaPos[0]),"ascii"), bytes(str(nuevaPos[1]),"ascii")])

		if conectados == 2:
			for member in usuariosConectados:
				socket.send_multipart([member , b"iniciarJuego" ])

if __name__ == '__main__':
	main()