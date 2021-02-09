import pygame
import sprites
import math
from random import randint, random

print("more than 1 day")

class game:

    def __init__(self, screen, player):
        self._screen=screen
        self.player=player

        self._font=pygame.font.Font('freesansbold.ttf', 32) #the normal font used to display stuff

        self._enemies=[sprites.enemy(100, 1, randint(0, screen_y-100), screen_x-100, [100, 100])]
        self._enemy_probability=99.9

        self.status=True

    def update_acceleration(self, dir):
        self.player.horixontal_thrust(dir[0])
        self.player.vertical_thrust(dir[1])

    def frame(self, dir, fire):
        self.update_acceleration(dir)
        self.player.update_velocity()
        self.player.move()
        self.spawn_enemis()
        fire_check=self.check_fire(fire)
        self.move_enemies()
        self.draw_background()
        self.draw_player()
        self.draw_enemy()
        self.check_colisions()
        if fire_check:
            self.draw_fire()
            self.check_colisions_laser()
        return self.status

    def spawn_enemis(self):
        number=random()*100
        if number>self._enemy_probability:
            box1=sprites.enemy(100, 1, randint(0, screen_y-100), screen_x-100, [100, 100])
            self._enemies.append(box1)
        else:
            self._enemy_probability=self._enemy_probability-0.0000001*self._enemy_probability


    def move_enemies(self):
        for enemy in self._enemies:
            enemy.move()

    def check_fire(self, fire):
        if fire==True:
            pass
        else:
            self.player.stop_fire()
            if self.player.gun.check_fire():
                return False
            else:
                self.player.gun.reload_timer()
                return False
        if self.player.fire():
            return True
        else:
            self.player.stop_fire()
            self.player.gun.reload_timer()
            return False

    def draw_background(self):
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [255,255,255], rec)

        ac=[
            self.player.vertical_ac,
            self.player.horizontal_ac
            ]
        self.get_text(str("vertical acceleration: "+str(round(ac[0], 5)*-1)), [0, 0])
        self.get_text(str("horizontal acceleration: "+str(round(ac[1], 5))), [0, 50])

        vel=[
            self.player.vertical,
            self.player.horizontal
            ]
        self.get_text(str("vertical velocity: "+str(round(vel[0], 5)*-1)), [600, 0])
        self.get_text(str("horizontal velocity: "+str(round(vel[1], 5))), [600, 50])

        amo, reload=self.player.gun.ammo, self.player.gun.reloadTime
        self.get_text(str("ammo: "+str(amo)), [1100, 0])
        self.get_text(str("reload: "+str(reload)), [1100, 50])

    def get_text(self, text, pos):
        acceleration=self._font.render(text, False, [0,0,0])
        self._screen.blit(acceleration, pos)

    def draw_player(self):
        box=self.player.return_box()
        pygame.draw.rect(self._screen, [0,0,0], box)

    def draw_fire(self):
        box=self.player.return_gun_box()
        pygame.draw.rect(self._screen, [125,0,0], box)

    def draw_enemy(self):
        for enemy in self._enemies:
            box=enemy.return_box()
            pygame.draw.rect(self._screen, [0,0,0], box)

    def check_colisions(self):
        player_box=self.player.return_box()
        for enemy in self._enemies:
            box=enemy.return_box()
            if player_box.colliderect(box):
                self.end_game()

    def check_colisions_laser(self):
        laser_box=self.player.return_gun_box()
        for index, enemy in enumerate(self._enemies):
            box=enemy.return_box()
            if box.colliderect(laser_box):
                self._enemies.pop(index)

    def end_game(self):
        self.status=False

def main():
    pygame.init()
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global screen_x, screen_y #globalises the hight and the width of the screen
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h

    playing=True #Determines is the game on or not
    player= sprites.player(100, 100, 100000, 100, [200, 100], [screen_x, screen_y])
    player.load_gun(sprites.gun(100, 1, [screen_x, 5], 400))
    play=game(screen, player)
    paused=False

    direction=[0, 0]
    fire=False

    while playing: #Main gameloop
        playing=play.frame(direction, fire)
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==27: #key 27 is escape, clicking it quits the game
                    play.end_game()
                    playing=False
                elif event.key==32: #pausing the game
                    paused=True
                elif event.key in [97, 100]:
                    val=int(event.key)
                    val=val-97
                    val=val/1.5
                    val-=1
                    direction[0]=val
                elif event.key in [119, 115]:
                    val=int(event.key)
                    val=val-115
                    val=val/2
                    val-=1
                    val*=-1
                    direction[1]=val
                elif event.key==102:
                    fire=True
            if event.type==pygame.KEYUP:
                if event.key in [97, 100]:
                    direction[0]=0
                elif event.key in [119, 115]:
                    direction[1]=0
                elif event.key==102:
                    fire=False
        while paused:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==32:
                        paused=False
        pygame.display.flip()

if __name__=="__main__":
    main()
