import pygame
import sys
import pickle
from copy import deepcopy
import random
import sprites
import inspect
import pygame_textinput

#random.seed(1)


class Menu:

    def __init__(self, screen, screen_size):
        pickle.dump({}, open('Scores/ship2.scores', "wb"))
        pickle.dump({}, open('Scores/ship1.scores', "wb"))

        self._screen=screen
        self.screen_size=screen_size

        self._font=pygame.font.Font('freesansbold.ttf', 32)

        self.ships=self.define_ships()
        self.guns=self.define_guns()
        self.enemies=self.define_enemies()

        self.ship_selected=None
        self.gun_selected=None
        self.secondary_gun_selected=None

        self.actions={
            "New game":lambda:self.get_text(self.infinite_runner_init),
            #"New game":self.input_seed,
            "Levels":lambda:self.get_text(self.level_rnner_init),
            "Select ship":lambda:self.pick_menu(self.ships, self.pick_ship),
            "Select gun":lambda:self.pick_menu(self.guns, self.pick_gun),
            "Select secondary gun":lambda:self.pick_menu(self.guns, self.pick_secondary_gun),
            "Exit":self.exit
        }

        self.unlocked_levels=[1, 2]
        self.levels={
            "Level 1":{
                "hardness":1,
                "enemies":self.enemies,
                "seed":1,
                "aim":Aim(kills=[10, "minimum"], distanse=[3000, "maximum"])
            },
            "Level 2":{
                "hardness":5,
                "enemies":self.enemies,
                "seed":2,
                "aim":Aim(distanse=[3000, "minimum"])
            }
        }

        self.main_menu()

    def buttons(self, options_texts):
        buttons_on_screen={}

        rect_size=[screen_x/3, screen_y/8]

        size=len(options_texts)

        if size<6:
            x_pos=screen_x/3
            for i in range(0, size):
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                self._screen.blit(self._font.render(options_texts[i], False, [0,255,0]), (screen_x/32+x_pos, (screen_y/8*1.75)+((i-0.75)*3*screen_y/16)))
        elif 5<size<11:
            x_pos=screen_x/9
            for i in range(0, int(size/2)):
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                self._screen.blit(self._font.render(options_texts[i], False, [0,255,0]), (screen_x/32+x_pos, (screen_y/8*1.75)+((i-0.75)*3*screen_y/16)))
            x_pos=5*screen_x/9
            for i in range(int(size/2), int(size/2)*2):
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-int(size/2)-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                self._screen.blit(self._font.render(options_texts[i], False, [0,255,0]), (screen_x/32+x_pos, (screen_y/8*1.75)+((i-int(size/2)-0.75)*3*screen_y/16)))
            if int(size/2)!=size/2:
                i+=1
                x_pos=screen_x/3
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-int(size/2)-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                self._screen.blit(self._font.render(options_texts[i], False, [0,255,0]), (screen_x/32+x_pos, (screen_y/8*1.75)+((i-int(size/2)-0.75)*3*screen_y/16)))
        pygame.display.flip()
        return buttons_on_screen

    def basic_menu(self, options, action):
        running=True

        buttons=self.buttons(list(options.keys()))

        while running:
            for event in pygame.event.get():
                if event.type==pygame.MOUSEBUTTONDOWN:
                    pos=pygame.mouse.get_pos()
                    for key, rec in buttons.items():
                        if rec.collidepoint(pos):
                            running=False
                            action(key)

    def main_menu(self, *args):
        pygame.mouse.set_visible(True)

        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

        action=lambda key:self.actions[key]()

        self.display_parts_picked()

        self.basic_menu(self.actions, action)

    def display_parts_picked(self):
        texts=["Ship: "+str(self.ship_selected), "Gun: "+str(self.gun_selected), "Second gun: "+str(self.secondary_gun_selected)]
        for i in range(3):
            text=texts[i]
            pos=[self.screen_size[0]/9, self.screen_size[1]/6*5+((i-4)*self.screen_size[1]/16)]
            text=self._font.render(text, False, [255,255,255])
            self._screen.blit(text, pos)

    def define_ships(self):
        ship2_gun_model=[
            [1, 0.5],
            [
                [0.35, 0.11+(1/3*0.01)],
                [0.35, 0.88+(2/3*0.01)]
            ]
        ]
        ship1_gun_model=[
            [0.86, 0.494],
            [
                [0.54, 0.29],
                [0.54, 0.69]
            ]
        ]

        ship1=([100, 10], 3, 80000, 200, [180, 150], self.screen_size, "Ship1.png", ship1_gun_model)#[[200, 75], [[70, 17], [70, 133]]])
        ship2=([100, 10], 4, 80000, 200, [104, 78], self.screen_size, "Ship2.png", ship2_gun_model)#[[104, 39], [[30, 5], [30, 71]]])
        #stelth=sprites.player([100, 10], 1, 10000, 80, [50, 20], [screen_x, screen_y], "Ship1.png", [])
        #mati=sprites.player([100, 10], 5, 100000, 800, [500,400], [screen_x, screen_y], "Ship1.png", [])

        return {"ship1":ship1, "ship2":ship2}

    def define_guns(self):
        guns={
            "Basic gun":(50, 10, [screen_x, 10], 200, 400),
            "Cleaner":(50, 10000, [screen_x, 2*screen_y], 0, 0),
            "Front recoil":(200, 5, [screen_x, 4], 100, -50),
            "Op gun":(200, 20, [screen_x, 20], 100, -50),
            "Mati gun":(69, 20, [screen_x, 45], 100, -70),
            "69 gun":(69, 69, [screen_x, 69], 69, 69),
            "No gun":(0, 0, [screen_x, 0], 1, 0)
        }

        return guns

    def define_enemies(self):
        enemies={
            "Meteor":(100, 3, [100, 100], "Meteor.png", self.screen_size[0], self.screen_size[1]),
            "Meteor2":(200, 1, [200, 200], "Meteor.png", self.screen_size[0], self.screen_size[1])
        }
        return enemies

    def pick_menu(self, feed, value):
        action=lambda key:value(key)

        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

        self.basic_menu(feed, action)

    def pick_ship(self, key):
        self.ship_selected=key
        self.main_menu()

    def pick_gun(self, key):
        self.gun_selected=key
        self.main_menu()

    def pick_secondary_gun(self, key):
        self.secondary_gun_selected=key
        self.main_menu()

    def get_text(self, game):
        running=True

        while running:
            self._screen.fill((225, 225, 225))

            events = pygame.event.get()
            for event in events:
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        running=False
                        self.main_menu()

            if textinput.update(events):
                running=False
                self.check_game(game, textinput.input_string)

            self._screen.blit(textinput.get_surface(), (self.screen_size[0]/2, self.screen_size[1]/2))

            pygame.display.update()

    def check_game(self, game, number=None):
        random.seed()

        if self.ship_selected==None:
            ship_selected=random.choice(list(self.ships.keys()))
        else:
            ship_selected=self.ship_selected
        if self.gun_selected==None:
            gun_selected="Basic gun"
        else:
            gun_selected=self.gun_selected

        ship_s=deepcopy(self.ships[ship_selected])
        player=sprites.player(ship_s)

        player.load_gun(self.guns[gun_selected])
        if self.secondary_gun_selected!=None:
            player.load_S_gun(self.guns[self.secondary_gun_selected])
        else:
            player.load_S_gun(self.guns["No gun"])

        game(player, number)

    def infinite_runner_init(self, player, seed=None):
        if not(seed.isdigit()):
            seed=random.randrange(sys.maxsize)
        play=Game(self._screen, player, 1, self.enemies, seed)

        self.game(play)

    def level_rnner_init(self, player, level):
        print(level, type(level))
        print(self.unlocked_levels)
        if int(level) in self.unlocked_levels:
            pass
        else:
            self.invalid_level()
        level="Level "+str(level)
        level=deepcopy(self.levels[level])
        play=Level(self._screen, player, level["hardness"], level["enemies"], level["seed"], aim=level["aim"])

        self.game(play)

    def game(self, play):
        pygame.mouse.set_visible(False)

        playing=True #Determines is the game on or not
        paused=False

        direction=[0, 0]
        fire=False
        s_fire=False

        FPS = 120
        fpsclock = pygame.time.Clock()

        while playing: #Main gameloop
            playing, mes=play.frame(direction, fire, s_fire, fpsclock)
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==27: #key 27 is escape, clicking it quits the game
                        play.end_game()
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
                direction[0]=0
                direction[1]=0
                fire=False
                s_fire=False
                for event in pygame.event.get():
                    if event.type==pygame.KEYDOWN:
                        if event.key==32:
                            paused=False
            pygame.display.flip()
            fpsclock.tick(FPS)

        play.end_screen(mes)
        pygame.display.flip()
        end=True

        #self.save_result(play.score, ship, gun, secondary_gun)

        while end:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        end=False
                        self.main_menu()

    def invalid_level(self):
        pygame.mouse.set_visible(True)

        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

        action=lambda key:self.actions[key]()

        pos=[self.screen_size[0]/5, self.screen_size[1]/2]
        text=self._font.render("You have no access to this level yet or the level is invalid", False, [255,255,255])
        self._screen.blit(text, pos)

        self.basic_menu({"Exit":None}, self.main_menu)

    def save_result(self, score, ship, gun, s_gun):
        name=ship+".scores"
        name=name.lower()
        results=pickle.load(open("Scores/"+name, "rb"))
        results[score]=[gun, s_gun]
        pickle.dump(results, open('Scores/'+name, "wb"))

    def load_result(self):
        name+=".gameres"
        #results=pickle.load(open(, 'rb'))

    def exit(self):
        pygame.quit()
        sys.exit()


class Game:

    def __init__(self, screen, player, hardness, enemies, seed):
        self.seed=seed
        random.seed(self.seed)

        self.code=""
        for i in range(5):
            self.code+=str(random.randint(0, 9))

        self._screen=screen
        self.player=player

        self._font=pygame.font.Font('freesansbold.ttf', 32) #the normal font used to display stuff

        self._enemies=[]
        self._possible_enemies=enemies
        #self._enemy_probability=99.8
        self._enemy_probability={}
        i=0
        for enemy in self._possible_enemies.keys():
            self._enemy_probability[enemy]=99.8+i
            i+=0.5
            self._enemies.append([])

        self.status=True

        self.hardness=hardness

        self.score=0
        self.score_change=0
        self.distanse=0

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

        self.draw_background(fps)
        self.draw_player()

        self.iterate_enemies(fire_check, s_fire_check)

        if fire_check:
            self.draw_fire("F")
        if s_fire_check:
            self.draw_fire("S")

        self.check_overspeed()

        self.update_score()

        return self.status, "You lost"

    def update_score(self):
        self.hardness+=0.0001

        self.distanse+=1

        score=1
        pos=self.player.return_cords()
        score+=(0.5*screen_x-abs(pos[0]-0.5*screen_x))
        score+=(0.5*screen_y-abs(pos[1]-0.5*screen_y))
        self.score_change=(round(score/1000, 1)**1.5)*0.5
        self.score+=self.score_change
        self.player.gain_score()

    def spawn_enemis(self):
        enemy_type=0
        for enemy, value in self._enemy_probability.items():
            value=(100-value+self.hardness)/len(list(self._enemy_probability.keys()))
            number=random.random()*100
            if number<value:
                self.spawn_enemy(enemy, enemy_type)
                #break
            else:
                pass
            enemy_type+=1

    def spawn_enemy(self, enemy, enemy_type):
        stats=deepcopy(self._possible_enemies[enemy])
        box1=sprites.enemy(stats)
        if self.check_spawn_place(box1):
            self._enemies[enemy_type].append(box1)
        else:
            pass
            #print("spawn avoided")

    def check_spawn_place(self, enemy_check):
        box_check=enemy_check.return_box()
        for enemies in self._enemies:
            for enemy in enemies:
                cords=enemy.return_cords()
                size=enemy.return_size()
                if cords[0]+size[0]>screen_x:
                    box=enemy.return_box()
                    if box.colliderect(box_check):
                        return False
        return True

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

        #return None

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

        self.get_text(str("enemies: "+str(len(self._enemies[0])+len(self._enemies[1]))), [0, 150])

        self.get_text(str("FPS: "+str(round(fps.get_fps(), 4))), [0, screen_y-100])
        self.get_text(str("Frame time: "+str(round(fps.get_time(), 4))), [0, screen_y-150])
        self.get_text(str("Raw Frame time: "+str(round(fps.get_rawtime(), 4))), [400, screen_y-150])

        value=(100-self._enemy_probability["Meteor"]+self.hardness)/len(list(self._enemy_probability.keys()))
        self.get_text(str("Probability: "+str(round(value, 4))), [400, screen_y-100])

        self.get_text(str("Level code: "+str(self.code)), [400, screen_y-50])
        self.get_text(str("Level seed: "+str(self.seed)), [400, screen_y-200])

        self.get_text(str("Score change: "+str(round(self.score_change, 2))), [1000, screen_y-50])
        self.get_text(str("Score: "+str(round(self.score, 2))), [1000, screen_y-100])
        self.get_text(str("Kills: "+str(self.player.kills)), [1000, screen_y-150])
        self.get_text(str("Damage: "+str(self.player.damage)), [1000, screen_y-200])
        self.get_text(str("Distance: "+str(self.distanse)), [1000, screen_y-250])

    def get_text(self, text, pos, colour=[255,255,255]):
        text=self._font.render(text, False, colour)
        self._screen.blit(text, pos)

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
        self.get_text(str(str(health)), cords, [255,255,255])

    def iterate_enemies(self, fire_check, s_fire_check):
        player_box=self.player.return_box()
        player=self.player.return_img()
        player=pygame.mask.from_surface(player)
        player_cords=self.player.return_cords()

        laser_box=self.player.return_gun_box()
        s_laser_box=self.player.return_S_gun_box()
        for index, enemies in enumerate(self._enemies):
            for index2, enemy in enumerate(enemies):
                enemy.move()

                alive=True
                box=enemy.return_box()

                self.draw_enemy(box, enemy)
                self.check_colision(player, player_cords, index, index2, enemy, box, player_box)
                if fire_check:
                    damage=self.player.gun.return_damage()
                    alive=self.check_colisions_laser(laser_box[0], index, index2, enemy, box, damage)

                if s_fire_check and alive:
                    damage=self.player.secondary_gun.return_damage()/5
                    alive=self.check_colisions_laser(s_laser_box[0], index, index2, enemy, box, damage)
                    if alive:
                        self.check_colisions_laser(s_laser_box[1], index, index2, enemy, box, damage)

                self.delete_enemies(index, index2, enemy)

    def delete_enemies(self, index, index2, enemy):
        if enemy.check_map():
            self._enemies[index].pop(index2)
        else:
            pass

    def check_colision(self, player, player_cords, index, index2, enemy, box, player_box):
        if box.colliderect(player_box):
            pass
        else:
            return None
        enemy_cords=enemy.return_cords()
        ofset=(int(enemy_cords[0]-player_cords[0]), int(enemy_cords[1]-player_cords[1]))

        enemy_mask=enemy.return_img()
        enemy_mask=pygame.mask.from_surface(enemy_mask)

        if player.overlap(enemy_mask, ofset)!=None:
            alive=self.player.loose_life()
            if alive:
                self._enemies[index].pop(index2)
                pass
            else:
                self.end_game()

        #if player_box.colliderect(box) or player_box1.colliderect(box):

    def check_colisions_laser(self, laser_box, index, index2, enemy, box, damage):
        if box.colliderect(laser_box):
            alive=enemy.get_damage(damage)
            self.player.gain_damage(damage)
            if alive:
                return True
            else:
                self.player.gain_kills()
                try:
                    self._enemies[index].pop(index2)
                except IndexError:
                    pass
                return False
        else:
            return True

    def end_game(self):
        #self.end_screen()
        self.status=False

    def end_screen(self, mes):
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

        self.get_text(mes, [screen_x/2-100, screen_y/2-150])

        self.get_text(str("Score: "+str(round(self.score, 2))), [screen_x/2-100, screen_y/2-100])
        self.get_text(str("Kills: "+str(self.player.kills)), [screen_x/2-100, screen_y/2-50])
        self.get_text(str("Damage: "+str(self.player.damage)), [screen_x/2-100, screen_y/2])
        self.get_text(str("Distance: "+str(self.distanse)), [screen_x/2-100, screen_y/2+50])


class Level(Game):

    def __init__(self, screen, player, hardness, enemies, seed, aim):
        super().__init__(screen, player, hardness, enemies, seed)

        self.aim=aim

    def check_aim(self):
        ret=self.aim.check_aims(
            score=self.score,
            kills=self.player.kills,
            damage=self.player.damage,
            distanse=self.distanse
        )
        return ret

    def frame(self, dir, fire, s_fire, fps):
        check2=self.check_aim()

        check=super().frame(dir, fire, s_fire, fps)

        if check[0]:
            pass
        else:
            return check

        ret=False or check[0]
        mes=""

        for ch in check2:
            ret=not(ch[0]) and ret
            if ret:
                pass
            else:
                mes=ch[1]
                break

        return ret, mes


class Aim:

    def __init__(self, score=None, kills=None, damage=None, distanse=None):
        frame=inspect.currentframe()
        args, _, _, values=inspect.getargvalues(frame)

        self.aims={
            "min_aims":[{}, self.check_min],
            "max_aims":[{}, self.check_max]
        }
        self.types={
            "minimum":self.aims["min_aims"][0],
            "maximum":self.aims["max_aims"][0]
        }

        for name in args:
            if values[name]!=None and name!="self":
                self.types[values[name][1]][name]=[values[name][0], False]

    def check_aims(self, **kwargs):
        rets=[]
        for aims in self.aims.values():
            if len(list(aims[0].values()))!=0:
                #for aim in aims[0].items():
                ret=aims[1](kwargs, aims[0])
                rets.append(ret)
        return rets

    def check_min(self, kwargs, aims):
        for name, goal in aims.items():
            if kwargs[name]>=goal[0]:
                self.aims["min_aims"][0][name][1]=True

        ret=True
        for suc in aims.values():
            ret=ret and suc[1]

        return ret, "You win"

    def check_max(self, kwargs, aims):
        for name, goal in aims.items():
            if kwargs[name]>=goal[0]:
                self.aims["max_aims"][0][name][1]=True

        ret=True
        for suc in aims.values():
            ret=ret and suc[1]

        return ret, "You lost"

def main():
    pygame.init()
    global textinput
    textinput=pygame_textinput.TextInput()
    pygame.display.set_caption("Space game")
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global screen_x, screen_y #globalises the hight and the width of the screen
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h

    current_game=Menu(screen, [screen_x, screen_y])
    #current_game.pick_ship()

if __name__=="__main__":
    main()
