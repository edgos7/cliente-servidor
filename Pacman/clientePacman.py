import zmq
import sys
import pygame
import threading
from pygame.locals import *

def juego(socket):
	alto=640
	ancho=480
	pygame.init()
	ventana=pygame.display.set_mode((alto, ancho))
	pygame.display.set_caption("Remedo de Pacman")
	while True:
		teclado=pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit()
			if teclado[K_RIGHT]:
				print("der")
				socket.send_multipart([b"movimiento", b"derecha"])
			if teclado[K_LEFT]:
				print("isq")
				socket.send_multipart([b"movimiento", b"izquierda"])
			if teclado[K_UP]:
				print("arr")
				socket.send_multipart([b"movimiento", b"arriba"])
			if teclado[K_DOWN]:
				print("aba")
				socket.send_multipart([b"movimiento", b"abajo"])
		
			


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
				print("tu personaje es: " + miPersonaje.decode("ascii"))
			if operacion == b"iniciarJuego":
				iniciarJuego = True
				#threading.Thread(target = juego, args = (socket, "hola")).start()
				juego(socket)
				print(posicionPersonaje)
			if operacion == b"actualizarPosicion":
				print("su madre")
			
			

		elif sys.stdin.fileno() in socks and iniciarJuego:
			print("?")
            #command = input()
            #dest, msg = command.split(' ', 1)
            #socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])


if __name__ == '__main__':
	main()
