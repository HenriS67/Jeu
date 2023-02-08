import random
import pygame
from support import *
from settings import *
from tile import Tile 
from player import Player
from debug import debug
from weapon import *
from UI import *
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from pytmx.util_pygame import *
import pytmx
class World:
    def __init__(self):
        #get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused=False
        #sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()
        self.floor_sprites = YSortCameraGroup()
        # attack sprites
        self.current_attack = None 
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
        # sprite setup
        self.create_map()
        #UI
        self.ui=UI()
        self.upgrade=Upgrade(self.player)
        
        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
    
    def create_map(self):
        
        tmx_data = load_pygame('map/test.tmx')
        
        #floor
        layer =  tmx_data.get_layer_by_name('ground')
        for layer.name in ('ground'):
            for x,y,surf in layer.tiles():
                Tile((x*TILESIZE,y*TILESIZE),
                    [self.floor_sprites,],
                    'ground',surf)
          
        #boundaries        
        boundaries_layer =  tmx_data.get_layer_by_name('boundaries')
        for boundaries_layer.name in ('boudaries'):
            for x,y,surf in boundaries_layer.tiles():
                Tile((x*TILESIZE,y*TILESIZE),[self.obstacles_sprites],'invisible')
            
        #grass       
        layer_grass =  tmx_data.get_layer_by_name('grass')
        for layer_grass.name in ('grass'):
            for x,y,surf in layer_grass.tiles():
                Tile((x*TILESIZE,y*TILESIZE),
                        [self.visible_sprites,
                            self.obstacles_sprites,
                            self.attackable_sprites],
                        'grass',surf)
                
        #enemy & player
        object_layer = tmx_data.get_layer_by_name('obj')     
        for ob in object_layer:
            if ob.type == 'enemy':
                print('test')
                Enemy(ob.name,
                    (int(ob.x),int(ob.y)),[self.visible_sprites,self.attackable_sprites],
                    self.obstacles_sprites,
                    self.damage_player,
                    self.trigger_death_particles,
                    self.add_xp)
            elif ob.type == 'player':
                self.player = Player(
                    (int(ob.x),int(ob.y)),
                    [self.visible_sprites],
                    self.obstacles_sprites,
                    self.create_attack,
                    self.destroy_attack,
                    self.create_magic)   
                  
        #obstacles entitys          
        obstacle_layer = tmx_data.get_layer_by_name('obs')        
        for ob in obstacle_layer:
                Tile((int(ob.x),int(ob.y)),
                     [self.visible_sprites,
                      self.obstacles_sprites],
                     'object',
                     ob.image)

    def create_attack(self):
        self.current_attack=Weapon(self.player,[self.visible_sprites,self.attack_sprites])
        
    def create_magic(self,style,strength,cost):
        if style == 'heal':
            self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])
        if style == 'flame':
            self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])
        
        print(style)
        print(strength)
        print(cost)
        
    def destroy_attack(self):
        
        if self.current_attack:
            self.current_attack.kill()   
        self.current_attack = None      
    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type =='grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,75)
                            for leaf in range(random.randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
                            target_sprite.kill()
                        elif target_sprite.sprite_type=='enemy':
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type)
                            
    def damage_player(self, amount,attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            
            #spawn particles
            self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])
    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type,pos,self.visible_sprites)
       
    def add_xp(self,amount):
        self.player.exp += amount  
    
    def toggle_menu(self):
        self.game_paused = not self.game_paused  
        
    def run(self):
        #update and draw the game
        self.floor_sprites.custom_draw(self.player)
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        if not self.game_paused:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
        else:
            self.upgrade.display()
            
        
        
        
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        #general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width=self.display_surface.get_size()[0] //2
        self.half_height=self.display_surface.get_size()[1] //2
        self.offset = pygame.math.Vector2(100,200)
        
        #creating the floor
        #self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
        #self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))
        
    def custom_draw(self,player):
        #offset
        self.offset.x=player.rect.centerx - self.half_width
        self.offset.y=player.rect.centery - self.half_height
        
        #drawing the floor
        #floor_offset_pos = self.floor_rect.topleft - self.offset
        #self.display_surface.blit(self.floor_surf,floor_offset_pos)
        
        #for sprite in self.sprites():
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)
    
    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)