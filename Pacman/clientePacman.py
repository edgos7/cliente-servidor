import zmq
import sys
import pygame
from pygame.locals import *

def mostrarImagenes (ventana,posicionPersonaje):
	fondo=pygame.image.load("imagenes/fondo.jpg")
	pacman=pygame.image.load("imagenes/pacman.png")
	amarillo=pygame.image.load("imagenes/amarillo.png")
	azul=pygame.image.load("imagenes/asul.png")
	rojo=pygame.image.load("imagenes/rojo.png")
	rosa=pygame.image.load("imagenes/rosa.png")
	ventana.blit(fondo, (0,0))
	ventana.blit(pacman, posicionPersonaje[b"pacman"])
	ventana.blit(amarillo, posicionPersonaje[b"fantasmaAmarillo"])
	ventana.blit(azul, posicionPersonaje[b"fantasmaAzul"])
	ventana.blit(rojo, posicionPersonaje[b"fantasmaRojo"])
	ventana.blit(rosa, posicionPersonaje[b"fantasmaRosa"])
	pygame.display.flip()

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
	posicionPersonaje = {b"pacman":(250,250),b"fantasmaAmarillo":(0,0),b"fantasmaAzul":(0,450),b"fantasmaRojo":(450,0),b"fantasmaRosa":(450,450)}
	ventana=""
	while True:
		socks = dict(poller.poll())
		if socket in socks:
			operacion, *mensaje = socket.recv_multipart()
			if operacion == b"personaje":
				miPersonaje=mensaje[0]
				print("tu personaje es: " + miPersonaje.decode("ascii"))
			if operacion == b"iniciarJuego":
				iniciarJuego = True
				alto=500
				ancho=500
				pygame.init()
				ventana=pygame.display.set_mode((alto, ancho))
				pygame.display.set_caption("figuras de pacman moviendose")
				mostrarImagenes(ventana,posicionPersonaje)
			if operacion == b"actualizarPosicion":
				personaje = mensaje[0]
				posx = int(mensaje[1].decode("ascii"))
				posy = int(mensaje[2].decode("ascii"))
				posicionPersonaje[personaje]=(posx,posy)		
				mostrarImagenes(ventana,posicionPersonaje)
		elif sys.stdin.fileno() in socks and iniciarJuego:
			command = input()
			if command == "d":
				socket.send_multipart([b"movimiento", b"derecha"])
			if command == "a":
				socket.send_multipart([b"movimiento", b"izquierda"])
			if command == "w":
				socket.send_multipart([b"movimiento", b"arriba"])
			if command == "s":
				socket.send_multipart([b"movimiento", b"abajo"])


if __name__ == '__main__':
	main()