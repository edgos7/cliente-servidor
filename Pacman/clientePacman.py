import zmq
import sys
import pygame
from pygame.locals import *

def mostrarImagenes (ventana,posicionPersonaje):
	fondo=pygame.image.load("imagenes/fondo-negro.jpg")
	ceresa=pygame.image.load("imagenes/ceresa.png")
	pacman=pygame.image.load("imagenes/pacman.png")
	amarillo=pygame.image.load("imagenes/amarillo.png")
	azul=pygame.image.load("imagenes/asul.png")
	rojo=pygame.image.load("imagenes/rojo.png")
	rosa=pygame.image.load("imagenes/rosa.png")
	ventana.blit(fondo, (0,0))
	ventana.blit(ceresa, posicionPersonaje[b"ceresa"])
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
	socket.send_multipart([b"nuevoJugador", identidad])
	posicionPersonaje = {b"pacman":(500,350),b"fantasmaAmarillo":(0,0),b"fantasmaAzul":(0,650),b"fantasmaRojo":(950,0),b"fantasmaRosa":(950,650),b"ceresa":(300,300)}
	alto=700
	ancho=1000
	pygame.init()
	ventana=pygame.display.set_mode((ancho, alto))
	pygame.display.set_caption("figuras de pacman moviendose")
	
	while True:
		try:
			operacion, *mensaje = socket.recv_multipart(zmq.NOBLOCK)
			if operacion == b"personaje":
				miPersonaje=mensaje[0]
				print("tu personaje es: " + miPersonaje.decode("ascii"))
			if operacion == b"iniciarJuego":
				iniciarJuego = True
				mostrarImagenes(ventana,posicionPersonaje)
			if operacion == b"actualizarPosicion":
				personaje = mensaje[0]
				posx = int(mensaje[1].decode("ascii"))
				posy = int(mensaje[2].decode("ascii"))
				posicionPersonaje[personaje]=(posx,posy)		
				mostrarImagenes(ventana,posicionPersonaje)
			if operacion == b"ganaPacman":
				print("el ganador es pacman")
				exit()
			if operacion == b"pierdePacman":
				print("los ganadores son los fantasmas")
				exit()
		except zmq.ZMQError as e:
			pass

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					socket.send_multipart([b"movimiento", b"arriba"])
				if event.key== pygame.K_DOWN:
					socket.send_multipart([b"movimiento", b"abajo"])
				if event.key== pygame.K_LEFT:
					socket.send_multipart([b"movimiento", b"izquierda"])
				if event.key== pygame.K_RIGHT:
					socket.send_multipart([b"movimiento", b"derecha"])

if __name__ == '__main__':
	main()