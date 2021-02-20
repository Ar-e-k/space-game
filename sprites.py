from copy import copy
import pygame
from random import randint

class player:

    def __init__(self, stats):
        cords, health, mass, thrust, size, map_size, ship, gun_places=stats

        self.map_size=map_size
        self.life=health

        self.cords=cords

        self.vertical=0
        self.horizontal=0
        self.modifier=15
        self.mass=mass

        self.vertical_ac=0
        self.horizontal_ac=0

        self.acceleration_mod=thrust/mass
        self.size=size

        self.recoil=0

        self.score=0
        self.kills=0
        self.damage=0

        self.ship=pygame.image.load("Models/Ships/"+ship).convert_alpha()
        self.ship=pygame.transform.scale(self.ship, self.size)

        self.gun_places=[
            self.normalise_place(gun_places[0]),
            [
                self.normalise_place(gun_places[1][0]),
                self.normalise_place(gun_places[1][1])
            ]
        ]

    def normalise_place(self, place):
        return [place[0]*self.size[0], place[1]*self.size[1]]

    def load_gun(self, gune):
        self.gun=gun(gune, self.gun_places[0])

    def load_S_gun(self, gune):
        self.secondary_gun=secondary_gun(gune, self.gun_places[1])

    def move(self):
        self.cords[0]+=(self.horizontal*self.modifier)
        self.cords[1]+=(self.vertical*self.modifier)
        self.teleport()

    def update_velocity(self):
        self.vertical+=self.vertical_ac
        self.horizontal+=self.horizontal_ac-self.recoil

    def vertical_thrust(self, direction=1):
        self.vertical_ac=self.acceleration_mod*direction

    def horixontal_thrust(self, direction=1):
        self.horizontal_ac=self.acceleration_mod*direction

    def resert_recoil(self):
        self.recoil=0

    def fire(self, gun):
        if gun.check_fire():
            self.recoil+=(gun.get_recoil()/self.mass)
            gun.fire()
            return True
        return None

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

    def gain_damage(self, damage):
        self.damage+=damage
        self.score+=1

    def return_cords(self):
        return self.cords

    def return_box(self):
        box=pygame.Rect(self.cords, self.size) # The actuall box
        #box=pygame.Rect(self.cords, [self.size[0]*4/9, self.size[1]])
        #box2=pygame.Rect([self.cords[0]+self.size[0]/3, self.cords[1]+self.size[1]/2-self.size[1]/5], [self.size[0]*2/3, self.size[1]*2/5])
        return box#, box2, self.ship'''

    def return_img(self):
        return self.ship

    def return_gun_box(self):
        return self.gun.return_box(self.cords)

    def return_S_gun_box(self):
        return self.secondary_gun.return_box(self.cords)

    def teleport(self):
        if self.cords[0]>self.map_size[0]-self.size[0]:
            self.cords[0]=self.map_size[0]-self.size[0]
        if self.cords[0]<0:
            self.cords[0]=0
        if self.cords[1]>self.map_size[1]-self.size[1]:
            self.cords[1]=self.map_size[1]-self.size[1]
        if self.cords[1]<0:
            self.cords[1]=0
        '''while self.cords[0]>self.map_size[0]:
            self.cords[0]-=self.map_size[0]
        while self.cords[0]<0:
            self.cords[0]+=self.map_size[0]
        while self.cords[1]>self.map_size[1]:
            self.cords[1]-=self.map_size[1]
        while self.cords[1]<0:
            self.cords[1]+=self.map_size[1]'''

    def overspeed(self):
        check=[
            self.cords[0]==0 and self.horizontal<-1,
            self.cords[1]==0 and self.vertical<-1,
            self.cords[1]-self.size[1]==self.map_size[1] and self.vertical> 1
            ]
        if True in check:
            self.vertical=0
            self.horizontal=0
            print("here")
            return self.loose_life()
        return True


class gun:

    def __init__(self, lis, place):
        ammo, damage, size, reload, recoil=lis

        self.damage=damage

        self.max_ammo=ammo
        self.ammo=copy(ammo)

        self.reloadTime=0
        self.max_reload=reload

        self.laser_size=size

        self.recoil=recoil

        self.place=place

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

    def return_damage(self):
        return self.damage

    def return_box(self, pos):
        pos=[self.place[0]+pos[0], self.place[1]+pos[1]-self.laser_size[1]/2]
        box=pygame.Rect(pos, self.laser_size)
        return [box]


class secondary_gun(gun):

    def return_box(self, pos):
        pos1=[self.place[0][0]+pos[0], self.place[0][1]+pos[1]]
        pos2=[self.place[1][0]+pos[0], self.place[1][1]+pos[1]-self.laser_size[1]]
        box=pygame.Rect(pos1, self.laser_size)
        box2=pygame.Rect(pos2, self.laser_size)
        return [box, box2]


class enemy:

    def __init__(self, inputs):
        health, speed, size, img, screen_x, screen_y=inputs
        #print(health)
        #print(speed)

        self.health=health
        self.speed=speed
        self.size=size

        self.cords=[screen_x+self.size[0], randint(0, screen_y-self.size[1])]

        self.img=pygame.image.load("Models/Enemies/"+img).convert_alpha()
        self.img=pygame.transform.scale(self.img, self.size)

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

    def return_size(self):
        return self.size

    def return_cords(self):
        return self.cords

    def return_box(self):
        box=pygame.Rect(self.cords, self.size) # The actuall box
        return box

    def return_img(self):
        return self.img
