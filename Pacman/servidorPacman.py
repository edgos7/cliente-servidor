import zmq

def movimientoValido(posPersonaje, direccion,posicionPersonaje,obtenerPersonaje,muros):
	posx = posPersonaje[0]
	posy = posPersonaje[1]
	posCeresa = posicionPersonaje[b"ceresa"]
	if(obtenerPersonaje==b"pacman" ):
		if direccion == b"derecha":
			if ((posx+50) < 650) and (posCeresa==(posx+50,posy)):
				return "GanaPacman"
		if direccion == b"izquierda":
			if ((posx-50) > 0) and (posCeresa==(posx-50,posy)):
				return "GanaPacman"
		if direccion == b"arriba":
			if ((posy-50) > 0) and (posCeresa==(posx,posy-50)):
				return "GanaPacman"
		if direccion == b"abajo":
			if ((posy+50) < 650) and (posCeresa==(posx,posy+50)):
				return "GanaPacman"
	else:
		if direccion == b"derecha":
			if ((posx+50) < 650) and (posicionPersonaje[b"pacman"]==(posx+50,posy)):
				return "PierdePacman"
		if direccion == b"izquierda":
			if ((posx-50) > 0) and (posicionPersonaje[b"pacman"]==(posx-50,posy)):
				return "PierdePacman"
		if direccion == b"arriba":
			if ((posy-50) > 0) and (posicionPersonaje[b"pacman"]==(posx,posy-50)):
				return "PierdePacman"
		if direccion == b"abajo":
			if ((posy+50) < 650) and (posicionPersonaje[b"pacman"]==(posx,posy+50)):
				return "PierdePacman"
	
	if direccion == b"derecha":
		if ((posx+50) < 650) and hayOtraPersonaje(posicionPersonaje,(posx+50,posy),muros):
			return "valido"
	if direccion == b"izquierda":
		if ((posx-50) > 0) and hayOtraPersonaje(posicionPersonaje,(posx-50,posy),muros):
			return "valido"
	if direccion == b"arriba":
		if ((posy-50) > 0) and hayOtraPersonaje(posicionPersonaje,(posx,posy-50),muros):
			return "valido"
	if direccion == b"abajo":
		if ((posy+50) < 650) and hayOtraPersonaje(posicionPersonaje,(posx,posy+50),muros):
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

def hayOtraPersonaje(posicionPersonaje,posPersonaje,muros):
	for member in posicionPersonaje:
		if(posicionPersonaje[member] == posPersonaje):
			return False
	for pos in muros:
		if(pos == posPersonaje):
			return False
	return True

def main():
	conectados = 0
	listaPersonajes = (b"pacman",b"fantasmaAmarillo",b"fantasmaAzul",b"fantasmaRojo",b"fantasmaRosa")
	usuariosConectados = {}
	personaje = {}
	posicionPersonaje = {b"pacman":(350,400),b"fantasmaAmarillo":(50,50),b"fantasmaAzul":(50,600),b"fantasmaRojo":(600,50),b"fantasmaRosa":(600,600),b"ceresa":(350,150)}
	muros = [(100,100),(150,100),(100,150),(150,150),(500,100),(550,100),(500,150),(550,150),(100,500),(150,500),(100,550),(150,550),(500,500),(550,500),(500,550),(550,550),(300,300),(350,300),(300,350),(350,350)]
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
			valido = movimientoValido(posPersonaje, direccion,posicionPersonaje,obtenerPersonaje,muros)
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
		if conectados == 5:
			for member in usuariosConectados:
				socket.send_multipart([member , b"iniciarJuego" ])

if __name__ == '__main__':
	main()