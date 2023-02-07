import pygame, sys
from settings import *
from debug import debug
from World import World
from pygame import mixer
class Game:
	def __init__(self):
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Jeu')
		self.clock = pygame.time.Clock()
		self.world=World()
  
		#sound
		#Instantiate mixer
		mixer.init()

		#Load audio file
		mixer.music.load('audio/Tundra.mp3')

		print("music started playing....")

		#Set preferred volume
		mixer.music.set_volume(0.2)

		#Play the music
		mixer.music.play()
  
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()  
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						self.world.toggle_menu()
			self.screen.fill(WATER_COLOR)
			self.world.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()	