import pygame
from settings import *
from random import randint
class MagicPlayer:
    def __init__(self,animation_player):
        self.animation_player=animation_player
        
    def heal(self,player,strength,cost,groups):
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('heal',player.rect.center,groups)
            self.animation_player.create_particles('aura',player.rect.center,groups)

    def flame(self,player,strength,cost,groups):
        if player.energy >= cost:
            player.energy -= cost
            
            direction = player.status.split('_')[0]
            if direction == 'right': magicDirection = pygame.math.Vector2(1,0)
            elif direction == 'left': magicDirection = pygame.math.Vector2(-1,0)
            elif direction == 'up': magicDirection = pygame.math.Vector2(0,-1)
            else: magicDirection = pygame.math.Vector2(0,1)
            
            for i in range(1,6):
                if magicDirection.x: #horizontal
                    offset_x = (magicDirection.x * i) * TILESIZE
                    x=player.rect.centerx + offset_x + randint(-TILESIZE //3,TILESIZE //3)
                    y=player.rect.centery + randint(-TILESIZE //3,TILESIZE //3)
                    self.animation_player.create_particles('flame',(x,y),groups)
                else:#vertical
                    offset_y = (magicDirection.y * i) * TILESIZE
                    y=player.rect.centery + offset_y + randint(-TILESIZE //3,TILESIZE //3)
                    x=player.rect.centerx + randint(-TILESIZE //3,TILESIZE //3)
                    self.animation_player.create_particles('flame',(x,y),groups)