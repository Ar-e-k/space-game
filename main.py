import pygame
import sprites
import math
from random import randint, random

class game:

    def __init__(self, screen, player):
        self._screen=screen
        self.player=player

        self._font=pygame.font.Font('freesansbold.ttf', 32) #the normal font used to display stuff

        self._enemies=[]
        self._enemy_probability=99.8
        #self._enemy_probability=99.5

        self.status=True

        self.score=0

    def update_acceleration(self, dir):
        self.player.horixontal_thrust(dir[0])
        self.player.vertical_thrust(dir[1])

    def frame(self, dir, fire, s_fire, fps):
        self.update_acceleration(dir)
        self.player.update_velocity()
        self.player.move()

        self.spawn_enemis()

        self.player.resert_recoil()
        fire_check=self.check_fire(fire, "F")
        s_fire_check=self.check_fire(s_fire, "S")

        self.move_enemies()
        self.draw_background(fps)
        self.draw_player()

        self.iterate_enemies(fire_check, s_fire_check)

        if fire_check:
            self.draw_fire("F")
        if s_fire_check:
            self.draw_fire("S")

        self.check_overspeed()

        self.update_score()

        return self.status

    def update_score(self):
        score=1
        pos=self.player.return_cords()
        score+=(0.5*screen_x-abs(pos[0]-0.5*screen_x))
        score+=(0.5*screen_y-abs(pos[1]-0.5*screen_y))
        self.score+=round(score/1000, 1)
        self.player.gain_score()

    def spawn_enemis(self):
        number=random()*1000
        if number>self._enemy_probability:
            box1=sprites.enemy(100, 3, [screen_x-100, randint(0, screen_y-100)], [100, 100], "try.png")
            self._enemies.append(box1)
        else:
            self._enemy_probability=self._enemy_probability-0.0000001*self._enemy_probability

    def move_enemies(self):
        for enemy in self._enemies:
            enemy.move()

    def check_fire(self, fire, gun):
        if gun=="F":
            gun=self.player.gun
        elif gun=="S":
            gun=self.player.secondary_gun
        if fire==True:
            pass
        else:
            if gun.check_fire():
                pass
            else:
                #self.player.stop_fire(gun)
                gun.reload_timer()
            return False
        if self.player.fire(gun):
            return True
        else:
            #self.player.stop_fire(gun)
            gun.reload_timer()
            return False

    def check_overspeed(self):
        alive=self.player.overspeed()
        if alive:
            pass
        else:
            self.end_game()

    def draw_background(self, fps):
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

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

        amo, reload=self.player.secondary_gun.ammo, self.player.secondary_gun.reloadTime
        self.get_text(str("ammo: "+str(amo)), [1100, 100])
        self.get_text(str("reload: "+str(reload)), [1100, 150])

        health=self.player.life
        self.get_text(str("health: "+str(health)), [0, screen_y-50])

        self.get_text(str("enemies: "+str(len(self._enemies))), [0, 150])

        self.get_text(str("FPS: "+str(round(fps.get_fps(), 4))), [0, screen_y-100])
        self.get_text(str("Frame time: "+str(round(fps.get_time(), 4))), [0, screen_y-150])
        self.get_text(str("Raw Frame time: "+str(round(fps.get_rawtime(), 4))), [400, screen_y-150])

        self.get_text(str("Score: "+str(round(self.score, 2))), [1000, screen_y-100])
        self.get_text(str("Kills: "+str(self.player.kills)), [1000, screen_y-150])
        self.get_text(str("Damage: "+str(self.player.damage)), [1000, screen_y-200])

    def get_text(self, text, pos, colour=[255,255,255]):
        acceleration=self._font.render(text, False, colour)
        self._screen.blit(acceleration, pos)

    def draw_player(self):
        ship=self.player.return_img()
        #pygame.draw.rect(self._screen, [255,255,255], box)
        #pygame.draw.rect(self._screen, [255,255,255], box2)
        self._screen.blit(ship, self.player.return_cords())

    def draw_fire(self, box):
        if box=="F":
            boxes=self.player.return_gun_box()
        elif box=="S":
            boxes=self.player.return_S_gun_box()
        for box in boxes:
            pygame.draw.rect(self._screen, [125,0,0], box)

    def draw_enemy(self, box, enemy):
        #pygame.draw.rect(self._screen, [255,255,255], box)
        self._screen.blit(enemy.img, enemy.cords)
        health=enemy.health
        cords=enemy.cords
        self.get_text(str(str(health)), cords, [0,0,0])

    def iterate_enemies(self, fire_check, s_fire_check):
        #player_box, player_box1, j=self.player.return_box()
        player=self.player.return_img()
        player=pygame.mask.from_surface(player)
        player_cords=self.player.return_cords()

        laser_box=self.player.return_gun_box()
        s_laser_box=self.player.return_S_gun_box()
        for index, enemy in enumerate(self._enemies):
            box=enemy.return_box()

            self.draw_enemy(box, enemy)
            self.check_colision(player, player_cords, index, enemy, box)
            if fire_check:
                damage=self.player.gun.return_damage()
                self.check_colisions_laser(laser_box[0], index, enemy, box, damage)

            if s_fire_check:
                damage=self.player.secondary_gun.return_damage()/5
                self.check_colisions_laser(s_laser_box[0], index, enemy, box, damage)
                self.check_colisions_laser(s_laser_box[1], index, enemy, box, damage)

            self.delete_enemies(index, enemy)

    def delete_enemies(self, index, enemy):
        if enemy.check_map():
            self._enemies.pop(index)
        else:
            pass

    def check_colision(self, player, player_cords, index, enemy, box):
        enemy_cords=enemy.return_cords()
        ofset=(int(enemy_cords[0]-player_cords[0]), int(enemy_cords[1]-player_cords[1]))

        enemy_mask=enemy.return_img()
        enemy_mask=pygame.mask.from_surface(enemy_mask)

        if player.overlap(enemy_mask, ofset)!=None:
            alive=self.player.loose_life()
            if alive:
                self._enemies.pop(index)
                pass
            else:
                self.end_game()

        #if player_box.colliderect(box) or player_box1.colliderect(box):

    def check_colisions_laser(self, laser_box, index, enemy, box, damage):
        if box.colliderect(laser_box):
            alive=enemy.get_damage(damage)
            self.player.gain_damage(damage)
            if alive:
                pass
            else:
                self.player.gain_kills()
                try:
                    self._enemies.pop(index)
                except IndexError:
                    pass

    def end_game(self):
        self.status=False


def main():
    pygame.init()
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global screen_x, screen_y #globalises the hight and the width of the screen
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h
    pygame.mouse.set_visible(False)

    playing=True #Determines is the game on or not
    paused=False

    player=sprites.player([100, 10], 10, 80000, 200, [200, 150], [screen_x, screen_y], "Ship1.png", [[200, 75], [[70, 17], [70, 133]]])
    #stelth=sprites.player([100, 10], 1, 10000, 80, [50, 20], [screen_x, screen_y], "Ship1.png", [])
    #mati=sprites.player([100, 10], 5, 100000, 800, [500,400], [screen_x, screen_y], "Ship1.png", [])

    basic_gun=(50, 10, [screen_x, 10], 200, 400)
    cleaner=(50, 10000, [screen_x, 2*screen_y], 0, 0)
    front_recoil=(200, 5, [screen_x, 2], 100, -50)
    op_gun=(200, 20, [screen_x, 20], 100, -50)
    mati_gun=(69, 20, [screen_x, 45], 100, -70)

    player.load_gun(basic_gun)
    #stelth.load_gun(front_recoil)
    #mati.load_gun(mati_gun)

    player.load_S_gun(front_recoil)

    play=game(screen, player)

    direction=[0, 0]
    fire=False
    s_fire=False

    FPS = 120
    fpsclock = pygame.time.Clock()

    while playing: #Main gameloop
        playing=play.frame(direction, fire, s_fire, fpsclock)
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
                elif event.key==106:
                    fire=True
                elif event.key==107:
                    s_fire=True
            if event.type==pygame.KEYUP:
                if event.key in [97, 100]:
                    direction[0]=0
                elif event.key in [119, 115]:
                    direction[1]=0
                elif event.key==106:
                    fire=False
                elif event.key==107:
                    s_fire=False
        while paused:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==32:
                        paused=False
        pygame.display.flip()
        fpsclock.tick(FPS)

if __name__=="__main__":
    main()
