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
	muro(ventana)
	muro2(ventana,100,100)
	muro2(ventana,500,100)
	muro2(ventana,100,500)
	muro2(ventana,500,500)
	muro2(ventana,300,300)
	pygame.display.flip()

def muro(ventana):
	i = 0
	x = 0
	y = 0
	for i in range(14):
		muro = pygame.image.load("imagenes/bloque.png")
		ventana.blit(muro, (x,0))
		ventana.blit(muro, (x,650))
		ventana.blit(muro, (0,y))
		ventana.blit(muro, (650,y))
		x += 50
		y +=50

def muro2(ventana, inix,iniy):
	copiax = inix
	
	i = 0
	for i in range(2):
		muro = pygame.image.load("imagenes/bloque.png")
		ventana.blit(muro, (inix,iniy))
		ventana.blit(muro, (inix+50,iniy))
		inix = copiax
		iniy +=50
	


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
	posicionPersonaje = {b"pacman":(350,400),b"fantasmaAmarillo":(50,50),b"fantasmaAzul":(50,600),b"fantasmaRojo":(600,50),b"fantasmaRosa":(600,600),b"ceresa":(350,150)}
	alto=700
	ancho=700
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