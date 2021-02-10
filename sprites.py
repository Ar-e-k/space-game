from copy import copy
from time import sleep
import pygame

class player:

    def __init__(self, x, y, health, mass, thrust, size, map_size):
        self.map_size=map_size
        self.life=health

        self.x_cord=x
        self.y_cord=y

        self.vertical=0
        self.horizontal=0
        self.modifier=15

        self.vertical_ac=0
        self.horizontal_ac=0

        self.acceleration_mod=thrust/mass
        self.size=size

        self.recoil=0

        self.score=0
        self.kills=0
        self.damage=0

    def load_gun(self, gun):
        self.gun=gun

    def move(self):
        self.x_cord+=(self.horizontal*self.modifier)
        self.y_cord+=(self.vertical*self.modifier)
        self.teleport()

    def update_velocity(self):
        self.vertical+=self.vertical_ac
        self.horizontal+=self.horizontal_ac-self.recoil

    def vertical_thrust(self, direction=1):
        self.vertical_ac=self.acceleration_mod*direction

    def horixontal_thrust(self, direction=1):
        self.horizontal_ac=self.acceleration_mod*direction

    def fire(self):
        if self.gun.check_fire():
            self.recoil=self.gun.get_recoil()
            self.gun.fire()
            return True
        return None

    def stop_fire(self):
        self.recoil=0

    def loose_life(self):
        self.life-=1
        if self.life==0:
            return False
        else:
            return True

    def gain_kills(self):
        self.kills+=1
        self.score+=1

    def gain_score(self):
        self.score+=1

    def gain_damage(self):
        self.damage+=self.gun.damage
        self.score+=1

    def return_box(self):
        box=pygame.Rect([self.x_cord, self.y_cord], self.size) # The actuall box
        return box

    def return_gun_box(self):
        return self.gun.return_box([self.x_cord, self.y_cord], self.size)

    def teleport(self):
        if self.x_cord>self.map_size[0]-self.size[0]:
            self.x_cord=self.map_size[0]-self.size[0]
        if self.x_cord<0:
            self.x_cord=0
        if self.y_cord>self.map_size[1]-self.size[1]:
            self.y_cord=self.map_size[1]-self.size[1]
        if self.y_cord<0:
            self.y_cord=0
        '''while self.x_cord>self.map_size[0]:
            self.x_cord-=self.map_size[0]
        while self.x_cord<0:
            self.x_cord+=self.map_size[0]
        while self.y_cord>self.map_size[1]:
            self.y_cord-=self.map_size[1]
        while self.y_cord<0:
            self.y_cord+=self.map_size[1]'''


class gun:

    def __init__(self, ammo, damage, size, reload, recoil):
        self.damage=damage

        self.max_ammo=ammo
        self.ammo=copy(ammo)

        self.reloadTime=0
        self.max_reload=reload

        self.laser_size=size

        self.recoil=recoil

    def reload(self):
        self.reloadTime=copy(self.max_reload)

    def reload_timer(self):
        if self.ammo<self.max_ammo:
            self.ammo+=int(self.max_ammo/self.reloadTime)
        else:
            self.ammo=copy(self.max_ammo)
        self.reloadTime-=1

    def check_fire(self):
        if self.reloadTime==0:
            return True
        else:
            return False

    def fire(self):
        self.ammo-=1
        if self.ammo==0:
            self.reload()

    def get_recoil(self):
        return self.recoil

    def return_box(self, position, size):
        position[0]+=(size[0]/2)
        position[1]+=(size[1]/2)-self.laser_size[1]/2
        box=pygame.Rect(position, self.laser_size)
        return box


class enemy:

    def __init__(self, health, speed, y_cord, x_cord, size):
        self.health=health
        self.speed=speed
        self.cords=[x_cord, y_cord]
        self.size=size

    def move(self):
        self.cords[0]-=self.speed

    def get_damage(self, damage):
        self.health-=damage
        if self.health<=0:
            return False
        else:
            return True

    def check_map(self):
        if self.cords[0]<0-self.size[0]:
            return True
        else:
            return False

    def return_box(self):
        box=pygame.Rect(self.cords, self.size) # The actuall box
        return box
