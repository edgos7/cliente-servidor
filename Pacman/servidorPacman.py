import zmq

def movimientoValido(posPersonaje, direccion,posicionPersonaje,obtenerPersonaje):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	posCeresa = posicionPersonaje[b"ceresa"]
	if(obtenerPersonaje==b"pacman" ):
		if direccion == b"derecha":
			if ((posx+50) < 1000) and (posCeresa==(posx+50,posy)):
				return "GanaPacman"
		if direccion == b"izquierda":
			if ((posx-50) > -50) and (posCeresa==(posx-50,posy)):
				return "GanaPacman"
		if direccion == b"arriba":
			if ((posy-50) > -50) and (posCeresa==(posx,posy-50)):
				return "GanaPacman"
		if direccion == b"abajo":
			if ((posy+50) < 700) and (posCeresa==(posx,posy+50)):
				return "GanaPacman"
	else:
		if direccion == b"derecha":
			if ((posx+50) < 1000) and (posicionPersonaje[b"pacman"]==(posx+50,posy)):
				return "PierdePacman"
		if direccion == b"izquierda":
			if ((posx-50) > -50) and (posicionPersonaje[b"pacman"]==(posx-50,posy)):
				return "PierdePacman"
		if direccion == b"arriba":
			if ((posy-50) > -50) and (posicionPersonaje[b"pacman"]==(posx,posy-50)):
				return "PierdePacman"
		if direccion == b"abajo":
			if ((posy+50) < 700) and (posicionPersonaje[b"pacman"]==(posx,posy+50)):
				return "PierdePacman"
	
	if direccion == b"derecha":
		if ((posx+50) < 1000) and hayOtraPersonaje(posicionPersonaje,(posx+50,posy)):
			return "valido"
	if direccion == b"izquierda":
		if ((posx-50) > -50) and hayOtraPersonaje(posicionPersonaje,(posx-50,posy)):
			return "valido"
	if direccion == b"arriba":
		if ((posy-50) > -50) and hayOtraPersonaje(posicionPersonaje,(posx,posy-50)):
			return "valido"
	if direccion == b"abajo":
		if ((posy+50) < 700) and hayOtraPersonaje(posicionPersonaje,(posx,posy+50)):
			return "valido"


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

def hayOtraPersonaje(posicionPersonaje,posPersonaje):
	for member in posicionPersonaje:
		if(posicionPersonaje[member] == posPersonaje):
			return False
	return True

def main():
	conectados = 0
	listaPersonajes = (b"pacman",b"fantasmaAmarillo",b"fantasmaAzul",b"fantasmaRojo",b"fantasmaRosa")
	usuariosConectados = {}
	personaje = {}
	posicionPersonaje = {b"pacman":(500,350),b"fantasmaAmarillo":(0,0),b"fantasmaAzul":(0,650),b"fantasmaRojo":(950,0),b"fantasmaRosa":(950,650),b"ceresa":(300,300)}
	context = zmq.Context()
	socket = context.socket(zmq.ROUTER)
	socket.bind("tcp://*:5555")

	while True:
		identidad, operacion, *mensaje = socket.recv_multipart()
		if operacion == b"nuevoJugador": 
			usuariosConectados[mensaje[0]]=identidad
			personaje[mensaje[0]]=listaPersonajes[conectados]
			conectados+=1
			socket.send_multipart([identidad , b"personaje", personaje[identidad]])
		if operacion == b"movimiento":
			direccion = mensaje[0]
			obtenerPersonaje = personaje[identidad]
			posPersonaje = posicionPersonaje[obtenerPersonaje]
			valido = movimientoValido(posPersonaje, direccion,posicionPersonaje,obtenerPersonaje)
			if valido == "valido":
				nuevaPos = actualizarPosicion(posPersonaje,direccion)
				posicionPersonaje[obtenerPersonaje] = nuevaPos
				for member in usuariosConectados:
					socket.send_multipart([member , b"actualizarPosicion",obtenerPersonaje, bytes(str(nuevaPos[0]),"ascii"), bytes(str(nuevaPos[1]),"ascii")])
			if valido =="GanaPacman":
				for member in usuariosConectados:
					socket.send_multipart([member , b"ganaPacman"])
			if valido =="PierdePacman":
				for member in usuariosConectados:
					socket.send_multipart([member , b"pierdePacman"])
		if conectados == 2:
			for member in usuariosConectados:
				socket.send_multipart([member , b"iniciarJuego" ])

if __name__ == '__main__':
	main()