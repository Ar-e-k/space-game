from copy import copy
from random import randint, uniform
import pygame

class Player:

    def __init__(self, stats):
        (
            cords, health, mass,
            thrust, size, map_size,
            ship, gun_places, special) = stats

        self.map_size = map_size
        self.life = health
        self.max_life = health
        self.life_counter_max = 3000
        self.life_counter = 0

        self.cords = cords

        self.vertical = 0
        self.horizontal = 0
        self.modifier = 15
        self.mass = mass

        self.vertical_ac = 0
        self.horizontal_ac = 0

        self.acceleration_mod = thrust / mass
        self.size = size

        self.recoil = 0

        self.score = 0
        self.kills = 0
        self.damage = 0

        self.shild = False
        self.pac = False
        self.sh_timer = 0
        self.pac_timer = 0
        self.mx_sh = 600
        self.mx_pac = 1200

        self.damage_multi = 1
        self.thrust_multi = 1
        self.multi_timer = 0
        self.mx_multi = 1200

        self.specials = {
            "kill switch": self.return_none,
            "shild": self.check_shild,
            "multi": self.check_multi
        }
        self.spec_ret = {
            "kill switch": 1, #lambda: [0, []],
            "shild": 1,
            #lambda: [2, [self.sh_timer, self.mx_sh,
            #self.pac_timer, self.mx_pac]],
            "multi": 1 #lambda: [1, [self.multi_timer, self.mx_multi]]
        }

        self.special = special
        #self.special = "kill switch"
        #self.special = "shild"
        #self.special = "multi"

        self.ship_name = ship
        self.ship = None

        self.gun = None
        self.secondary_gun = None

        self.gun_places = [
            self.normalise_place(gun_places[0]),
            [
                self.normalise_place(gun_places[1][0]),
                self.normalise_place(gun_places[1][1])
            ]
        ]

        self.spec_guns = {
            "rand": RandGun
        }


    def return_none(self):
        return None


    def add_pygame(self):
        self.ship = pygame.image.load(
            "Models/Ships/" + self.ship_name
        ).convert_alpha()
        self.ship = pygame.transform.scale(self.ship, self.size)


    def normalise_place(self, place):
        return [place[0] * self.size[0], place[1] * self.size[1]]


    def load_gun(self, gun):
        if len(gun) != 5:
            self.gun = self.spec_guns[gun[-1]](gun[0:-1], self.gun_places[0])
            return None
        self.gun = Gun(gun, self.gun_places[0])
        return None


    def load_s_gun(self, gun):
        if len(gun) != 5:
            self.secondary_gun = SecondaryGun(
                (0, 0, [0, 0], 1, 0), self.gun_places[1]
            )
            return None
        self.secondary_gun = SecondaryGun(gun, self.gun_places[1])
        return None


    def move(self, sc_x, sc_y):
        self.cords[0] += (self.horizontal * self.modifier * sc_x)
        self.cords[1] += (self.vertical * self.modifier * sc_y)
        return self.teleport()


    def spec_move(self, sc_x, sc_y):
        self.cords[0] += sc_x
        self.cords[1] += sc_y
        return self.teleport2()


    def update_velocity(self):
        self.vertical += self.vertical_ac
        self.horizontal += self.horizontal_ac - self.recoil


    def vertical_thrust(self, direction=1):
        self.vertical_ac = (
            self.acceleration_mod * direction * self.thrust_multi
        )


    def horizontal_thrust(self, direction=1):
        self.horizontal_ac = (
            self.acceleration_mod * direction * self.thrust_multi
        )


    def resert_recoil(self):
        self.recoil = 0


    def fire(self, gun):
        if self.pac:
            return None
        if gun.check_fire():
            self.recoil += (gun.get_recoil() / self.mass)
            gun.fire()
            return True #The gun has fired
        return None #The gun cannot fire


    def add_shild(self):
        self.shild = True
        self.pac = True
        self.sh_timer = copy(self.mx_sh)
        self.pac_timer = copy(self.mx_pac)


    def add_multi(self):
        self.damage_multi = 5
        self.thrust_multi = 0.2
        self.multi_timer = copy(self.mx_multi)


    def check_special(self):
        self.specials[self.special]()


    def check_shild(self):
        if self.sh_timer == 0:
            self.shild = False
        else:
            self.sh_timer -= 1
        if self.pac_timer == 0:
            self.pac = False
        else:
            self.pac_timer -= 1


    def check_multi(self):
        if self.multi_timer == 0:
            self.damage_multi = 1
            self.thrust_multi = 1
        else:
            self.multi_timer -= 1


    def return_special(self):
        return None
        #return self.spec_ret[self.special]()


    def add_life(self, life):
        if self.life+life <= self.max_life:
            self.life += life
        else:
            self.life = copy(self.max_life)


    def loose_life(self):
        if self.shild:
            return True
        self.life -= 1
        if self.life <= 0:
            return False
        return True


    def count_life(self):
        self.life_counter += 1
        if self.life_counter == self.life_counter_max:
            self.life_counter = 0
            return self.loose_life()

        return True


    def gain_kills(self):
        self.kills += 1
        self.score += 1


    def gain_score(self):
        self.score += 1


    def gain_damage(self, damage):
        self.damage += damage
        self.score += 1


    def return_cords(self):
        return self.cords


    def return_img_cords(self):
        return [self.cords[i] - self.size[i] / 2 for i in range(2)]


    def return_box(self):
        box = pygame.Rect(self.return_img_cords(), self.size) # The actuall box
        #box = pygame.Rect(self.cords, [self.size[0] * 4 / 9, self.size[1]])
        '''box2 = pygame.Rect(
            [
                self.cords[0] + self.size[0] / 3,
                self.cords[1] + self.size[1] / 2 - self.size[1] / 5
            ],
            [self.size[0] * 2 / 3, self.size[1] * 2 / 5]
        )'''
        return box#, box2, self.ship'''


    def return_img(self):
        return self.ship


    def return_gun_box(self):
        return self.gun.return_box(self.return_img_cords())


    def return_s_gun_box(self):
        return self.secondary_gun.return_box(self.return_img_cords())


    def return_damage(self):
        return self.gun.return_damage() * self.damage_multi


    def return_s_damage(self):
        return self.secondary_gun.return_damage() * 0.2 * self.damage_multi


    def teleport(self):
        ret = 0
        if self.cords[0] > self.map_size[0] - self.size[0] / 2:
            self.cords[0] = self.map_size[0] - self.size[0] / 2
            self.horizontal = 0
            ret = self.horizontal_ac
        if self.cords[0] < self.size[0] / 2:
            self.cords[0] = self.size[0] / 2
            self.horizontal = 0
            ret = self.horizontal_ac
        if self.cords[1] > self.map_size[1] - self.size[1]:
            #self.cords[1] = self.map_size[1] - self.size[1]
            self.cords[1] -= self.map_size[1]
        if self.cords[1] < 0:
            #self.cords[1] = 0
            self.cords[1] += self.map_size[1]
        '''while self.cords[0] > self.map_size[0]:
            self.cords[0] -= self.map_size[0]
        while self.cords[0] < 0:
            self.cords[0] += self.map_size[0]
        while self.cords[1] > self.map_size[1]:
            self.cords[1] -= self.map_size[1]
        while self.cords[1] < 0:
            self.cords[1] += self.map_size[1]'''
        return ret


    def teleport2(self):
        ret = True

        if self.cords[0] > self.map_size[0] - self.size[0] / 2:
            self.cords[0] = self.map_size[0] - self.size[0] / 2
            self.horizontal = 0
            ret = self.loose_life()
        if self.cords[0] < self.size[0] / 2:
            self.cords[0] = self.size[0] / 2
            self.horizontal = 0
            ret = self.loose_life()
        if self.cords[1] > self.map_size[1] - self.size[1] / 2:
            self.cords[1] = self.map_size[1] - self.size[1] / 2
            self.vertical = 0
            ret = self.loose_life()
        if self.cords[1] < self.size[1] / 2:
            self.cords[1] = self.size[1] / 2
            self.vertical = 0
            ret = self.loose_life()

        return ret


    def overspeed(self):
        check = [
            self.cords[0] == 0 and self.horizontal <- 1,
            self.cords[1] == 0 and self.vertical <- 1,
            (
                self.cords[1] - self.size[1] == self.map_size[1]
                and self.vertical > 1
            )
            ]
        if True in check:
            self.vertical = 0
            self.horizontal = 0
            return self.loose_life()
        return True



class Gun:

    def __init__(self, lis, place):
        ammo, damage, size, reload, recoil = lis

        self.damage = damage

        self.max_ammo = ammo
        self.ammo = copy(ammo)

        self.reload_time = 0
        self.max_reload = reload

        self.laser_size = size

        self.recoil = recoil

        self.place = place


    def reload(self):
        self.reload_time = copy(self.max_reload)


    def reload_timer(self):
        if self.ammo < self.max_ammo:
            self.ammo += int(
                self.max_ammo / self.reload_time
            ) #The gun is still reloading
        else:
            self.ammo = copy(self.max_ammo) #The gun has reloaded
        self.reload_time -= 1


    def check_fire(self):
        if self.reload_time == 0:
            return True #The gun can fire
        return False #The gun is currently reloading


    def fire(self):
        self.ammo -= 1
        if self.ammo == 0:
            self.reload()


    def get_recoil(self):
        return self.recoil


    def return_damage(self):
        return self.damage


    def return_box(self, pos):
        pos = [
            self.place[0] + pos[0],
            self.place[1] + pos[1] - self.laser_size[1] / 2
        ]
        box = pygame.Rect(pos, self.laser_size)
        return [box]


    def return_slides(self):
        return self.ammo, self.reload_time, self.max_ammo, self.max_reload



class RandGun(Gun):

    def fire(self):
        self.ammo -= 1
        if self.ammo == 0:
            self.reload()
            dirn = randint(0, 1)
            dirn = dirn * 2 - 1
            self.recoil *= dirn



class SecondaryGun(Gun):

    def return_box(self, pos):
        pos1 = [self.place[0][0] + pos[0], self.place[0][1] + pos[1]]
        pos2 = [
            self.place[1][0] + pos[0],
            self.place[1][1] + pos[1] - self.laser_size[1]
        ]
        box = pygame.Rect(pos1, self.laser_size)
        box2 = pygame.Rect(pos2, self.laser_size)
        return [box, box2]



class Enemy:

    def __init__(self, inputs):
        health, speed, size, img, screen_x, screen_y = inputs

        self.health = health
        self.speed = speed
        self.base_speed = speed
        self.size = size

        self.cords = [
            screen_x + self.size[0],
            randint(-self.size[1] / 2, screen_y + self.size[1] / 2)
        ]

        self.img_name = img
        self.img = None


    def add_pygame(self):
        self.img = pygame.image.load(
            "Models/Enemies/" + self.img_name
        ).convert_alpha()
        self.img = pygame.transform.scale(self.img, self.size)


    def move(self, sc_x):
        self.cords[0] -= self.speed * sc_x


    def change_speed(self, acc):
        self.speed = self.base_speed + acc
        if self.speed == 0:
            self.speed = 1


    def get_damage(self, damage, _):
        self.health = int(self.health - damage)
        if self.health <= 0:
            return False
        return True


    def check_map(self):
        return self.cords[0] < -self.size[0]


    def return_size(self):
        return self.size


    def return_cords(self):
        return [int(self.cords[i]) for i in range(2)]


    def return_img_cords(self):
        cords = self.return_cords()
        return [cords[i] - self.size[i] / 2 for i in range(2)]


    def return_box(self):
        cords = self.return_cords()
        try:
            if self.img_name == "Meteor.png":
                box = pygame.Rect(
                    [cords[i] - (self.size[i]*0.7)/2 for i in range(2)],
                    [self.size[i] * 0.7 for i in range(2)]
                ) # The actuall box
            else:
                box = pygame.Rect(
                    self.return_img_cords(), self.size
                ) # The actuall box
        except AttributeError:
            box = pygame.Rect(
                self.return_img_cords(), self.size
            ) # The actuall box

        return box


    def return_img(self):
        return self.img



class EnemyH(Enemy):

    def get_damage(self, damage, player):
        self.health = int(self.health - damage)
        if self.health <= 0:
            player.add_life(1)
            return False
        return True



class Star(Enemy):

    def randomise(self, mn, mx, pos):
        out = uniform(mn ** pos, mx ** pos)
        out = int(out ** (1 / pos))
        return out


    def __init__(self, inputs, image):
        size = inputs[2]
        size1 = self.randomise(size[0], size[1], 1 / 2)
        size2 = self.randomise(size[0], size[1], 2)
        size = int((size1 + size2) / 2)
        inputs[2] = [size, size]

        health, speed, size, _, screen_x, screen_y = inputs

        self.health = health
        self.speed = speed
        self.size = size
        self.base_speed = speed

        self.cords = [screen_x+self.size[0], randint(0, screen_y-self.size[1])]

        self.img = image
        #self.img = pygame.image.load("Models/Back/" + img).convert_alpha()
        #self.img = pygame.image.load("Models/Enemies/" + img).convert_alpha()
        #self.img.set_alpha(128)
        #alph = self.randomise(48, 160, 1 / 3)
        self.img.set_alpha(randint(64, 160))
        self.img = pygame.transform.scale(self.img, self.size)
