import pygame
import sys
import pickle
from copy import deepcopy, copy
import random
from random import randint, uniform, choice
import sprites
import inspect
import pygame_textinput


class Menu:

    def __init__(self, screen, screen_size):
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
            "New game":lambda:self.get_input(self.infinite_runner_init, self.infinite_runner_display),
            "Levels":lambda:self.get_input(self.level_runner_init, self.level_runner_display),
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
                "aim":Aim(kills=[10, "Minimum"], score=[1, "Minimum"], distanse=[3000, "Maximum"]),
                "unlocked":True
            },
            "Level 2":{
                "hardness":5,
                "enemies":self.enemies,
                "seed":2,
                "aim":Aim(distanse=[3000, "Minimum"]),
                "unlocked":True
            },
            "Level 3":{
                "hardness":20,
                "enemies":self.enemies,
                "seed":3,
                "aim":Aim(distanse=[10000, "Minimum"]),
                "unlocked":True
            }
        }

        self.load_result()

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
                pos=(
                    screen_x/32+x_pos,
                    (screen_y/8*1.75)+((i-0.75)*3*screen_y/16)
                )
                self.get_text(options_texts[i], pos, [0,255,0])
        elif 5<size<11:
            x_pos=screen_x/9
            for i in range(0, int(size/2)):
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                pos=(
                    screen_x/32+x_pos,
                    (screen_y/8*1.75)+((i-0.75)*3*screen_y/16)
                )
                self.get_text(options_texts[i], pos, [0,255,0])
            x_pos=5*screen_x/9
            for i in range(int(size/2), int(size/2)*2):
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-int(size/2)-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                pos=(
                    screen_x/32+x_pos,
                    (screen_y/8*1.75)+((i-int(size/2)-0.75)*3*screen_y/16)
                )
                self.get_text(options_texts[i], pos, [0,255,0])
            if int(size/2)!=size/2:
                i+=1
                x_pos=screen_x/3
                rec=pygame.Rect(x_pos, (screen_y/8*1.5)+((i-int(size/2)-0.75)*3*screen_y/16), rect_size[0], rect_size[1])
                buttons_on_screen[options_texts[i]]=rec
                pygame.draw.rect(self._screen, [255,0,0], rec)
                pos=(
                    screen_x/32+x_pos,
                    (screen_y/8*1.75)+((i-int(size/2)-0.75)*3*screen_y/16)
                )
                self.get_text(options_texts[i], pos, [0,255,0])
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


    def get_text(self, text, pos, colour=[255,255,255], center=False, back=False):
        text_width, text_height=self._font.size(text)

        if center:
            pos=[
                pos[0]-(text_width/2),
                pos[1]-(text_height/2)
            ]
        elif back:
            pos=[
                pos[0]-(text_width),
                pos[1]-(text_height/2)
            ]

        text=self._font.render(text, False, colour)
        self._screen.blit(text, pos)


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

            pos=[
                self.screen_size[0]/9,
                self.screen_size[1]/6*5+((i-4)*self.screen_size[1]/16)
            ]
            self.get_text(text, pos, [255,255,255])


    #Define ships, guns and enemy stats
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

        kill="kill switch"
        shild="shild"
        multi="multi"

        ship1=([100, 10], 5, 160000, 200, [180, 150], self.screen_size, "Ship1.png", ship1_gun_model, kill)#[[200, 75], [[70, 17], [70, 133]]])
        ship2=([100, 10], 3, 80000, 200, [104, 78], self.screen_size, "Ship2.png", ship2_gun_model, shild)#[[104, 39], [[30, 5], [30, 71]]])
        ship3=([100, 10], -2, 40000, 300, [64, int(78*(64/104))], self.screen_size, "Ship2.png", ship2_gun_model, multi)#[[104, 39], [[30, 5], [30, 71]]])
        #stelth=sprites.player([100, 10], 1, 10000, 80, [50, 20], [screen_x, screen_y], "Ship1.png", [])
        #mati=sprites.player([100, 10], 5, 100000, 800, [500,400], [screen_x, screen_y], "Ship1.png", [])

        return {"ship1":ship1, "ship2":ship2, "test":ship3}


    def define_guns(self):
        guns={
            "Basic gun":(50, 10, [screen_x, 10], 200, 400),
            "Cleaner":(50, 10000, [screen_x, 2*screen_y], 0, 0),
            "Front recoil":(200, 5, [screen_x, 4], 100, -50),
            "Op gun":(200, 20, [screen_x, 20], 100, -50),
            "Rand gun":(5, 40, [screen_x, 150], 300, 4000, "rand"),
            "No gun":(0, 0, [screen_x, 0], 0, 0)
        }

        return guns


    def define_enemies(self):
        enemies={
            "Meteor":(80, 3, [100, 100], "Meteor.png", self.screen_size[0], self.screen_size[1]),
            "Meteor2":(150, 1, [150, 150], "Meteor.png", self.screen_size[0], self.screen_size[1]),
            "Meteor3":(300, 0.5, [200, 200], "Meteor.png", self.screen_size[0], self.screen_size[1])
        }
        return enemies

    ###

    #Picking menues
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

    ###

    def get_input(self, game, display):
        running=True

        textinput=pygame_textinput.TextInput(
            text_color=(0,255,0),
            cursor_color=(0,255,0),
            font_family='freesansbold.ttf',
            font_size=32
            )

        while running:
            self._screen.fill((0,0,0))

            events = pygame.event.get()
            for event in events:
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        running=False
                        self.main_menu()
            pos=pygame.mouse.get_pos()

            if textinput.update(events):
                running=False
                self.check_game(game, textinput.input_string)

            text, cursor_vis, cursor_pos=textinput.return_cursor_stuff()
            if cursor_vis:
                cursor_pos=self._font.size(text[:cursor_pos])[0]

            display(textinput, cursor_pos, pos)

            pygame.display.update()


    def infinite_runner_display(self, textinput, cursor_pos, mouse_pos):
        text, cursor_vis, cursor=textinput.return_info_needed()
        text_width, text_height=self._font.size(text)

        rect_size=[self.screen_size[0]/4+text_width, self.screen_size[1]/6]
        rec=pygame.Rect(self.screen_size[0]/2-rect_size[0]/2, self.screen_size[1]/2, rect_size[0], rect_size[1])
        pygame.draw.rect(self._screen, [255,0,0], rec)

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4
        )
        self.get_text("Define your seed, leave empty to randomise", pos, [0,255,0], True)

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/2+rect_size[1]/2
            )
        self.get_text(text, pos, [0,255,0], True)

        #results_2d=list(self.results.values())
        results_seed={}
        for seed, lis in self.results.items():
            for i in lis:
                results_seed[i]=seed
        results=list(results_seed.keys())
        results.sort()

        for i in range(1, 10):
            pos=(
                10,
                self.screen_size[1]/4+i*text_height
            )
            try:
                mes=str(i)+") "+str(results[-i])
            except IndexError:
                break
            size=self._font.size(mes)
            rec=pygame.Rect(pos, size)
            if rec.collidepoint(mouse_pos):
                if text=="":
                    textinput.input_string=str(results_seed[float(mes[3:])])
            self.get_text(mes, pos, [0,255,0])

        if text in self.results.keys():
            results=self.results[text]
            results.sort()
            for i in range(1, 11):
                pos=(
                    self.screen_size[0]-10,
                    self.screen_size[1]/4+i*text_height
                )
                try:
                    mes=str(i)+") "+str(results[-i])
                except IndexError:
                    break
                self.get_text(mes, pos, [0,255,0], back=True)

        if cursor_vis:
            pos=(
            self.screen_size[0]/2-text_width/2+cursor_pos,
            self.screen_size[1]/2+rect_size[1]/2-text_height/2
            )
            self._screen.blit(cursor, pos)


    def level_runner_display(self, textinput, cursor_pos, pos):
        text, cursor_vis, cursor=textinput.return_info_needed()
        text_width, text_height=self._font.size(text)

        rect_size=[self.screen_size[0]/4+text_width, self.screen_size[1]/6]
        rec=pygame.Rect(self.screen_size[0]/2-rect_size[0]/2, self.screen_size[1]/2, rect_size[0], rect_size[1])
        pygame.draw.rect(self._screen, [255,0,0], rec)

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4
        )
        self.get_text("Which level you you want to play", pos, [0,255,0], True)
        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4+text_height
        )
        self.get_text("You have the following levels avaliable:", pos, [0,255,0], True)

        levels=""
        for name, level in self.levels.items():
            if level["unlocked"]:
                levels+=(name+", ")
        levels=levels[:-2]
        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4+text_height*2
        )
        self.get_text(levels, pos, [0,255,0], True)

        level="Level "+str(text)
        if level in self.levels.keys():
            i=0
            for name, value in self.levels[level].items():
                if name in ["hardness", "aim", "unlocked"]:
                    if name=="hardness":
                        mes="Hardness: "+str(value)
                    elif name=="aim":
                        texts=value.return_aim()
                        for mes in texts:
                            pos=(
                                self.screen_size[0]/2,
                                self.screen_size[1]/2+rect_size[1]/2+text_height*(3+i)*1.5
                            )
                            self.get_text(mes, pos, [0,255,0], True)
                            i+=1
                        continue
                    elif name=="unlocked":
                        mes="Unlocked: "+str(value)
                    pos=(
                        self.screen_size[0]/2,
                        self.screen_size[1]/2+rect_size[1]/2+text_height*(3+i)*1.5
                    )
                    self.get_text(mes, pos, [0,255,0], True)
                    i+=1
        else:
            pos=(
                self.screen_size[0]/2,
                self.screen_size[1]/2+rect_size[1]/2+text_height*(3)
            )
            self.get_text("Invalid level", pos, [0,255,0], True)

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/2+rect_size[1]/2
            )
        self.get_text(text, pos, [0,255,0], True)

        if text in self.level_results.keys():
            results=self.level_results[text]
            results.sort()
            for i in range(1, 11):
                pos=(
                    10,
                    self.screen_size[1]/4+i*text_height
                )
                try:
                    mes=str(i)+") "+str(results[-i])
                except IndexError:
                    break
                self.get_text(mes, pos, [0,255,0])

        if cursor_vis:
            pos=(
            self.screen_size[0]/2-text_width/2+cursor_pos,
            self.screen_size[1]/2+rect_size[1]/2-text_height/2
            )
            self._screen.blit(cursor, pos)


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


    def level_runner_init(self, player, level):
        if level.isdigit():
            pass
        else:
            level=1
        level="Level "+str(level)
        if level in self.levels.keys():
            if self.levels[level]["unlocked"]:
                pass
            else:
                self.invalid_level()
        else:
            self.invalid_level()
        level=deepcopy(self.levels[level])
        play=Level(self._screen, player, level["hardness"], level["enemies"], level["seed"], aim=level["aim"])

        self.game(play)


    #Main game loop
    def game(self, play):
        pygame.mouse.set_visible(False)

        playing=True #Determines is the game on or not
        paused=False

        direction=[0, 0]
        fire=False
        s_fire=False
        special=False

        FPS = 120
        fpsclock = pygame.time.Clock()

        while playing: #Main gameloop
            playing, mes=play.frame(direction, fire, s_fire, special, fpsclock)
            special=False
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
                    elif event.key==108:
                        special=True
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

        if type(Game("screen", "player", "hardness", {}, 1))==type(play):
            self.save_result(play.score, play.seed)
        elif type(Level("screen", "player", "hardness", {}, 1, "aim"))==type(play):
            self.save_level_result(play.score, play.seed)

        while end:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        end=False
                        self.main_menu()

    ###

    def invalid_level(self):
        pygame.mouse.set_visible(True)

        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [0,0,0], rec)

        action=lambda key:self.actions[key]()

        pos=[
            self.screen_size[0]/2,
            self.screen_size[1]/2
        ]
        text="You have no access to this level yet or the level is invalid"
        self.get_text(text, pos, [255,255,255], True)

        self.basic_menu({"Exit":None}, self.main_menu)


    def save_result(self, score, seed):
        name="saves.scores"
        score=round(score, 2)
        try:
            results=pickle.load(open("Scores/"+name, "rb"))
        except FileNotFoundError:
            results={}
        if str(seed) in results.keys():
            results[str(seed)].append(score)
        else:
            results[str(seed)]=[score]
        pickle.dump(results, open('Scores/'+name, "wb"))
        self.load_result()


    def save_level_result(self, score, level):
        name="level_saves.scores"
        score=round(score, 2)
        try:
            results=pickle.load(open("Scores/"+name, "rb"))
        except FileNotFoundError:
            results={}
        if str(level) in results.keys():
            results[str(level)].append(score)
        else:
            results[str(level)]=[score]
        pickle.dump(results, open('Scores/'+name, "wb"))
        self.load_result()


    def load_result(self):
        name="saves.scores"
        try:
            results=pickle.load(open("Scores/"+name, "rb"))
        except FileNotFoundError:
            results={}
        self.results=results
        name="level_saves.scores"
        try:
            results_l=pickle.load(open("Scores/"+name, "rb"))
        except FileNotFoundError:
            results_l={}
        self.level_results=results_l


    def exit(self):
        pygame.quit()
        sys.exit()



class Game:

    def kill_switch(self):
        self._enemies=[[] for i in range(len(self._possible_enemies))]
        alive=self.player.loose_life()
        if alive:
            pass
        else:
            self.end_game()


    def __init__(self, screen, player, hardness, enemies, seed):
        self.seed=seed
        random.seed(int(self.seed))

        img="star1.png"
        img="test1.png"
        #img="star2.png"
        self.img=pygame.image.load("Models/Back/"+img).convert_alpha()
        self.bc=[1, 10, [10, 70], img, screen_x, screen_y]

        self.all_bc=[]

        self.code=""
        for i in range(5):
            num=str(random.randint(0, 9))
            self.code+=num

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


        self.specials={
            "kill switch": [lambda: self.kill_switch(), 1500],
            "shild": [lambda: self.player.add_shild(), 3000],
            "multi": [lambda: self.player.add_multi(), 2500]
        }

        self.special_counter=1

        self.status=True

        self.hardness=hardness

        self.score=0
        self.multiplier=1
        self.score_change=0
        self.pos_score_change=0
        self.distanse=0


    def update_acceleration(self, dir):
        self.player.horixontal_thrust(dir[0])
        self.player.vertical_thrust(dir[1])


    def frame(self, dir, fire, s_fire, special, fps):
        self.update_acceleration(dir)
        self.player.update_velocity()
        over=self.player.move()
        self.multiplier=round(self.multiplier+over, 5)

        self.spawn_enemis()

        name=self.player.special
        if special and self.specials[name][1]==self.special_counter:
            self.specials[name][0]()
            self.special_counter-=1
        if self.special_counter!=self.specials[name][1]:
            self.special_counter-=1
            self.player.check_special()

        if self.special_counter==0:
            self.special_counter=copy(self.specials[name][1])
            self.special=False

        self.player.resert_recoil()
        fire_check=self.check_fire(fire, "F")
        s_fire_check=self.check_fire(s_fire, "S")

        self.draw_background(fps)
        self.add_stars(over)
        self.draw_player()

        self.iterate_enemies(fire_check, s_fire_check, over)

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
        self.pos_score_change=[int(score), round(((score/1000)**1.5)*0.5, 5)]
        self.score_change=(round(score/1000, 2)**1.5)*0.5
        self.score_change*=self.multiplier
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
        lis=[sprites.enemy]*10+[sprites.enemyH]
        en=random.choice(lis)
        stats=list(stats)
        stats[1]+=self.multiplier-1
        box1=en(stats)
        if self.check_spawn_place(box1):
            self._enemies[enemy_type].append(box1)
        else:
            pass


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
        else:
            return False
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
            if not(self.player.pac):
                gun.reload_timer()
            return False


    def check_overspeed(self):
        alive=self.player.overspeed()
        if alive:
            pass
        else:
            self.end_game()


    def add_stars(self, over):
        rem=[]
        if randint(0, 100)>40:
            stats=copy(self.bc)
            stats=list(stats)
            stats[1]+=self.multiplier-1
            new_bc=sprites.star(stats, self.img)
            for bc in self.all_bc:
                if bc.return_box().colliderect(new_bc.return_box()):
                    break
                else:
                    pass
            else:
                self.all_bc.append(new_bc)

        for pos, bc in enumerate(self.all_bc):
            bc.change_speed(over)
            bc.move()
            if bc.check_map():
                rem.append(pos)
            self.draw_enemy(None, bc)
        for i in rem[-1:0:-1]:
            self.all_bc.pop(i)


    def add_controls(self):
        up_pos=lambda pos, c, w: [pos[0]+w*1.2*c, pos[1]]

        hight=screen_y*0.1
        width=screen_x*0.02
        pos=[screen_x*0.05, screen_y*0.88]

        h_mod=1.5
        pos=up_pos(pos, -h_mod, width)
        health=self.player.life
        bc=[0,255,255]
        for i in range(health):
            rect=pygame.Rect([pos[0], pos[1]+(hight-width)-(width*1.2*i)-1], [width, width])
            pygame.draw.rect(self._screen, bc, rect)
        pos=up_pos(pos, h_mod, width)

        c=self.gun_slider(self.player.gun, hight, width, pos)
        pos=up_pos(pos, c, width)

        c=self.gun_slider(self.player.secondary_gun, hight, width, pos)
        pos=up_pos(pos, c, width)

        mx=self.specials[self.player.special][1]
        val=self.special_counter
        self.show_slider(mx, val, pos, hight, width)
        pos=up_pos(pos, 1, width)

        c, vals=self.player.return_special()
        for i in range(c):
            j=2*i
            self.show_slider(vals[j+1], vals[j], pos, hight, width)
            pos=up_pos(pos, 1, width)


    def draw_background(self, fps):
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        if self.player.shild:
            col=[0,0,64]
        elif self.player.damage_multi!=1:
            col=[64,0,0]
        else:
            col=[46, 64, 83]
            col=[0,0,0]
            #col=[0, 98, 166]
        pygame.draw.rect(self._screen, col, rec)

        self.add_controls()

        health=self.multiplier
        self.get_text(str("multi "+str(health)), [0, 50])

        return None


    def gun_slider(self, gun, hight, width, pos):
        amo, reload1, mx, mxr=gun.return_slides()

        if mx==mxr==0:
            return 0

        self.show_slider(mx, amo, pos, hight, width)
        self.show_slider(mxr, reload1, [width*1.2+pos[0], pos[1]], hight, width)
        return 2


    def writing(self):
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

        self.get_text(str("ammo: "+str(amo)), [1100, 0])
        self.get_text(str("reload: "+str(reload1)), [1100, 50])

        self.get_text(str("ammo: "+str(amo2)), [1100, 100])
        self.get_text(str("reload: "+str(reload2)), [1100, 150])

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
        self.get_text(str("Pos Score change: "+str(self.pos_score_change)), [0, screen_y-300])
        self.get_text(str("Special recharge: "+str(self.special_counter)), [1000, screen_y-300])


    def show_slider(self, mx, cur, pos, size, wid):
        bc=[0,255,255]
        slid=[255,0,0]

        bor=size/20
        try:
            hight=int(cur/mx*(size-bor*2))
        except ZeroDivisionError:
            return None
        pos_y=size-hight

        rect=pygame.Rect(pos, [wid, size])
        pygame.draw.rect(self._screen, bc, rect)

        rec=pygame.Rect([pos[0]+bor, pos[1]+pos_y], [wid-bor*2, hight-bor/2])
        pygame.draw.rect(self._screen, slid, rec)


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
        health=enemy.speed
        cords=enemy.cords
        #self.get_text(str(str(health)), cords, [255,255,255])


    def iterate_enemies(self, fire_check, s_fire_check, over):
        player_box=self.player.return_box()
        player=self.player.return_img()
        player=pygame.mask.from_surface(player)
        player_cords=self.player.return_cords()

        laser_box=self.player.return_gun_box()
        s_laser_box=self.player.return_S_gun_box()
        for index, enemies in enumerate(self._enemies):
            for index2, enemy in enumerate(enemies):
                enemy.change_speed(over)
                enemy.move()

                alive=True
                box=enemy.return_box()

                self.draw_enemy(box, enemy)
                self.check_colision(player, player_cords, index, index2, enemy, box, player_box)
                if fire_check:
                    damage=self.player.return_damage()
                    alive=self.check_colisions_laser(laser_box[0], index, index2, enemy, box, damage)

                if s_fire_check and alive:
                    damage=self.player.return_S_damage()
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


    def check_colisions_laser(self, laser_box, index, index2, enemy, box, damage):
        if box.colliderect(laser_box):
            alive=enemy.get_damage(damage, self.player)
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


    def frame(self, dir, fire, s_fire, special, fps):
        check2=self.check_aim()

        check=super().frame(dir, fire, s_fire, special, fps)

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
            "Minimum":self.aims["min_aims"][0],
            "Maximum":self.aims["max_aims"][0]
        }
        self.type_expand={
            "Minimum":"Get above",
            "Maximum":"Without exciding"
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


    def return_aim(self):
        texts=[]
        for category, dic in self.types.items():
            if len(list(dic.keys()))==0:
                continue
            else:
                pass
            category=self.type_expand[category]
            text=category+": "
            for typ, val in dic.items():
                text+=typ+"="+str(val[0])+", "
            text=text[:-2]
            texts.append(text)
        return texts



def main():
    pygame.init()
    pygame.display.set_caption("Space game")
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global screen_x, screen_y #globalises the hight and the width of the screen
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h

    current_game=Menu(screen, [screen_x, screen_y])
    #current_game.pick_ship()

if __name__=="__main__":
    main()
