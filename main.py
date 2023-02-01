global runs, telp, hor
runs=80
telp=True
hor=False

import sys
import os

import pygame
import pickle
import dill

from copy import copy
from copy import deepcopy as dp

import neat

import multiprocessing as mp
from multiprocessing import Pool

import math
from matplotlib import pyplot as plt
import time
import numpy as np
import random
from random import randint, uniform, choice

import inspect

import pygame_textinput
import sprites
import visualise as vis

def evolv_Smain2(ge, games, nets, props, rng):
    playing=True
    or_rng=dp(rng)

    while playing:
        rem=[]
        for i in rng:
            ret=True
            try:
                game=games[i]
            except IndexError:
                rem.append(i)
                continue

            ins=props[i]

            plr=game.player

            inputs_2=tuple([i[0] for i in game.closest.values()])+tuple(i[1] for i in game.closest.values())
            pot_vals=game.vision
            inputs_3=tuple(pot_vals.values())

            if hor:
                inputs_4=tuple([pot_vals[i] for i in [0, 45, 90, 135, 180]])
                inputs_5=[pot_vals[i] for i in [0, 315, 270, 225, 180]]
                inputs_5[0]=0
                inputs_5[4]=0
                inputs_5=tuple(inputs_5)

            else:
                inputs_4=tuple([pot_vals[i] for i in [11.25, 45, 90, 135, 168.75]])
                inputs_5=tuple([pot_vals[i] for i in [348.75, 315, 270, 225, 191.25]])

            if telp:
                spec_inputs=(
                    plr.cords[0]-game.target[0],
                    plr.cords[1]-game.target[1]
                )+inputs_3

                if True:
                    outs=nets[i].activate(inputs_4)
                    outs2=nets[i].activate(inputs_5)

                    x=outs[0] if abs(outs[0])>abs(outs2[0]) else outs2[0]
                    y=outs[1] if abs(outs[1])>abs(outs2[1]) else -outs2[1]
                else:
                    outs=nets[i].activate(inputs_3)
                    #outs=nets[i].activate(spec_inputs)
                    x, y=[round(i) for i in outs[0:2]]

                dirn=[0, 0]

                ret=game.spec_move(x, y)
            else:
                inputs_1=(
                    plr.cords[0]-game.target[0],
                    plr.cords[1]-game.target[1],
                    plr.vertical,
                    plr.horizontal
                )
                inputs=inputs_1+inputs_2

                outs=nets[i].activate(inputs_1)
                dirn=[round(i) for i in outs[0:2]]

            pl, mes=game.frame(dir=dirn, fire=ins["fire"],  s_fire=ins["s_fire"], special=ins["spc"], fps=None, dis=False)

            if not(pl) or not(ret):
                rem.append(i)

            if telp and False:
                ge[i].fitness=games[i].distanse
            else:
                vals=list(pot_vals.values())
                #ge[i].fitness+=sum([(pos**2)*i/5 for pos, i in enumerate(vals[::-1])])/16000
                #ge[i].fitness+=sum([(pos**2.5)*i/11.7 for pos, i in enumerate(vals[::-1])])/16000
                #ge[i].fitness+=sum([(pos**3)*i/28 for pos, i in enumerate(vals[::-1])])/16000
                #ge[i].fitness+=sum([(i**(pos/6)) for pos, i in enumerate(vals[::-1])])/2200
                #ge[i].fitness=games[i].score

                #ge[i].fitness+=sum([(pos**2.5)*i/11.7 for pos, i in enumerate(vals[-3::-1])])/16000
                mins=[]
                for key in [11.25, 45, 90, 135, 168.75]:
                    mins.append(round(game.vision[key]+game.vision[key+180]-abs(game.vision[key]-game.vision [key+180])))
                ge[i].fitness+=(sum(mins)/10000)

            if ge[i].fitness>50000:
                print(games[i].seed)
                rem.append(i)

            if pl and games[i].multiplier<0:
                rem.append(i)
                ge[i].fitness=-1000

        for j in rem:
            rng.pop(rng.index(j))

        if rng==[]:
            playing=False
            return [ge, or_rng]

    print("out of while, how")
    return None


def evolv_Smain(ge, games, nets, props, rng, fpsclock=None, dis=False):
    rem=[]
    trans=dict(zip([i for i in rng], [i for i in rng]))
    playing=True
    or_rng=dp(rng)
    start=min(or_rng)
    ln=len(or_rng)

    while playing:
        rem=[]
        sk=0
        for i in range(start, start+ln):
            ret=True
            try:
                game=games[i]
            except IndexError:
                sk+=1
                continue
            ins=props[i]

            plr=game.player

            inputs_2=tuple([i[0] for i in game.closest.values()])+tuple(i[1] for i in game.closest.values())
            inputs_3=tuple(game.vision.values())

            if telp:
                spec_inputs=(
                    plr.cords[0]-game.target[0],
                    plr.cords[1]-game.target[1]
                )+inputs_3

                outs=nets[i].activate(inputs_3)
                #outs=nets[i].activate(spec_inputs)
                dirn=[0, 0]
                x, y=[round(i) for i in outs[0:2]]

                ret=plr.spec_move(x, y)
            else:
                inputs_1=(
                    plr.cords[0] -game.target[0],
                    plr.cords[1] -game.target[1],
                    plr.vertical,
                    plr.horizontal
                )
                inputs=inputs_1+inputs_2

                outs=nets[i].activate(inputs_1)
                dirn=[round(i) for i in outs[0:2]]

            pl, mes=game.frame(dir=dirn, fire=ins["fire"],  s_fire=ins["s_fire"], special=ins["spc"], fps=fpsclock, dis=dis)

            if not(pl) or not(ret):
                rem.append(i)

            if telp:
                ge[trans[i]].fitness=game.distanse
            else:
                ge[trans[i]].fitness=game.score

            if pl and game.multiplier<0:
                rem.append(i)
                ge[trans[i]].fitness=-1000

        rem.sort()

        for j in rem[::-1]:
            ln-=1
            for key, val in trans.items():
                if key>j:
                    trans[key-1]=val

            #ge.pop(j)
            nets.pop(j)
            games.pop(j)
            props.pop(j)

        if ln==0 or sk==ln:
            playing=False
            return [ge, or_rng]



class Menu:

    def __init__(self, screen, screen_size, sc_x):
        self._screen=screen
        self.screen_size=screen_size
        self.sc_x=sc_x

        self._font=pygame.font.Font('freesansbold.ttf', int(32*self.sc_x))

        self.ships=self.define_ships()
        self.guns=self.define_guns()
        self.enemies=self.define_enemies()

        self.ship_selected=None
        self.gun_selected=None
        self.secondary_gun_selected=None

        self.actions={
            "New game":lambda:self.get_input(lambda x: self.check_game(self.infinite_runner_init, x), self.infinite_runner_display),
            "Levels":lambda:self.get_input(lambda x: self.check_game(self.level_runner_init, x), self.level_runner_display),
            "Evolv":lambda:self.get_input(lambda x: self.evolv_init(x), self.evolv_display, True),
            "Op play":lambda:self.get_input(lambda x: self.run_winner(x), self.evolv_display, True),
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
            pygame.display.flip()
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


    def evolv_display(self, textinput, cursor_pos, mouse_pos, mos):
        text, cursor_vis, cursor=textinput.return_info_needed()
        text_width, text_height=self._font.size(text)

        rect_size=[self.screen_size[0]/4+text_width, self.screen_size[1]/6]
        rec=pygame.Rect(self.screen_size[0]/2-rect_size[0]/2, self.screen_size[1]/2, rect_size[0], rect_size[1])
        pygame.draw.rect(self._screen, [255,0,0], rec)

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4
        )
        self.get_text("Input the save names", pos, [0,255,0], True)
        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/4+text_height
        )
        self.get_text("Saves avaliable to restore", pos, [0,255,0], True)

        folders=[]
        path=str(os.getcwd()+"/evolv_info")
        dir_list=os.listdir(path)
        for name in dir_list:
            if text in name and text!=name:
                folders.append(name)
        #pos=(
        #    self.screen_size[0]/2,
        #    self.screen_size[1]/4+text_height*2
        #)
        #self.get_text(folders, pos, [0,255,0], True)

        y_start=self.screen_size[1]/2-text_height*len(folders)/2
        y_calc=lambda i: y_start+i*text_height

        for i in range(len(folders)):
            pos=(
                10,
                y_calc(i)
            )
            try:
                mes=folders[i]
            except IndexError:
                break
            size=self._font.size(mes)
            rec=pygame.Rect(pos, size)
            if rec.collidepoint(mouse_pos) and mos:
                textinput.input_string=str(mes)
            self.get_text(mes, pos, [0,255,0])

        pos=(
            self.screen_size[0]/2,
            self.screen_size[1]/2+rect_size[1]/2
            )
        self.get_text(text, pos, [0,255,0], True)

        if cursor_vis:
            pos=(
            self.screen_size[0]/2-text_width/2+cursor_pos,
            self.screen_size[1]/2+rect_size[1]/2-text_height/2
            )
            self._screen.blit(cursor, pos)


    def prp_save(self, path, name, config):
        if name in os.listdir(path):
            dir_list=os.listdir(path+"/"+name)
            if "winner.nnet" in dir_list:
                p=neat.Population(config)
            else:
                lis=[]
                for fil in dir_list:
                    if "ck_neat" in fil:
                        num=fil.split("-")[1]
                        lis.append(int(num))
                try:
                    filename="/ck_neat-"+str(max(lis))
                    print(filename)
                    p=neat.Checkpointer.restore_checkpoint(path+"/"+name+filename)
                except ValueError:
                    p=neat.Population(config)
        else:
            os.mkdir("evolv_info/"+name)
            p=neat.Population(config)

        p.add_reporter(neat.Checkpointer(generation_interval=5,filename_prefix=str("evolv_info/"+name+"/ck_neat-")))
        return p


    def evolv_init(self, name):
        local_dir=os.path.dirname(__file__)
        config_path=os.path.join(local_dir, 'config-feedforward.txt')

        config=neat.config.Config(
            neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path
        )

        if name=="":
            p=neat.Population(config)
        else:
            path=local_dir+"/evolv_info"
            p=self.prp_save(path, name, config)

        p.add_reporter(neat.StdOutReporter(True))
        stats=neat.StatisticsReporter()
        p.add_reporter(stats)

        winner=p.run(self.evolv_main2,runs)
        win=p.best_genome

        pickle.dump(win, open("evolv_info/"+name+"/ev_winner.nnet", 'wb'))
        pickle.dump(winner, open("evolv_info/"+name+"/winner.nnet", 'wb'))

        #visualize.draw_net(config, winner, True)
        #visualize.plot_stats(stats, ylog=False, view=True)
        #visualize.plot_species(stats, view=True)

        vis.plot_stats(stats, view=False, filename="stats.svg", pre=str("evolv_info/"+name+"/"))
        vis.draw_net(config, winner, view=False, filename="vis", pre=str("evolv_info/"+name+"/"))

        mes=winner.fitness

        des=lambda: self.run_winner(name)
        self.end_screen(Game(self._screen, "player", "hardness", {}, 1, dis=True), mes)


    def evolv_main2(self, genomes, config):
        nets=[]
        ge=[]
        games=[]
        props=[]
        pr_def={
            "dirn":[0, 0],
            "fire":False,
            "s_fire":False,
            "spc":False
        }
        hard=0.1

        for _, g in genomes:
            net=neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)

            g.fitness=0
            ge.append(g)

            plr=self.defult_plr()
            seed=random.randrange(sys.maxsize)
            play=Game(None, plr, hard, self.enemies, seed, self.sc_x, targeting=False)
            games.append(play)

            props.append(dp(pr_def))

        #self.games[0].init_dis(self._screen)

        workers=mp.cpu_count()
        rem=[]

        pros=(len(games)//workers)
        print(pros)
        print(workers)
        print(len(nets))
        with Pool(processes=workers) as pool:
            print("Pool started")
            mp_res=[
                pool.apply_async(
                    evolv_Smain2,
                    (dp(ge), dp(games), dp(nets), dp(props), [j+i for j in range(pros)],)
                ) for i in range(0, workers*pros, pros)
            ]
            print("Pool generated")
            rems=[res.get(timeout=60) for res in mp_res]
            print("Results in")
            pool.close()
            print("Close")
            pool.join()
            print("Joined")
        print("Pool closed")

        #for event in pygame.event.get():
        #    if event.type==pygame.QUIT:
        #       pygame.quit()
        #       quit()

        for ge_out, rng in rems:
            for i in rng:
                try:
                    ge[i].fitness=ge_out[i].fitness
                except IndexError or KeyError:
                    pass

        #self.get_text(str(len(self.games)), [0,0])
        #pygame.display.flip()
        #self.fpsclock.tick(FPS)


        #if 0 in rem:
        #    self.games[0].init_dis(self._screen)


    def evolv_main(self, genomes, config):
        nets=[]
        ge=[]
        games=[]
        props=[]
        pr_def={
            "dirn":[0, 0],
            "fire":False,
            "s_fire":False,
            "spc":False
        }
        hard=1

        for _, g in genomes:
            net=neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)

            g.fitness=0
            ge.append(g)

            plr=self.defult_plr()
            seed=random.randrange(sys.maxsize)
            play=Game(self._screen, plr, hard, self.enemies, seed, self.sc_x)
            games.append(play)

            props.append(dp(pr_def))


        #games[0].init_dis(self._screen)

        playing=True
        fpsclock=pygame.time.Clock()
        FPS=0
        all_fps=[]

        while playing:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    quit()

            rem=[]
            for i in range(len(games)):
                ins=props[i]

                dis=False
                if i==0 and False:
                    dis=True

                game=games[i]
                plr=game.player
                inputs_1=(
                        plr.cords[0]-screen_x/2,
                        plr.cords[1]-screen_y/2,
                        plr.vertical,
                        plr.horizontal
                    )
                inputs=inputs_1+tuple([i[0] for i in game.closest.values()])+tuple(i[1] for i in game.closest.values())
                outs=nets[i].activate(inputs)
                dirn=[round(i) for i in outs[0:2]]

                pl, mes=game.frame(dir=dirn, fire=ins["fire"],  s_fire=ins["s_fire"], special=ins["spc"], fps=fpsclock, dis=dis)

                if not(pl):
                    rem.append(i)

                ge[i].fitness=games[i].score
                if pl and games[i].multiplier<0:
                    rem.append(i)
                    ge[i].fitness=games[i].score-1000

            for j in rem[::-1]:
                ge.pop(j)
                nets.pop(j)
                games.pop(j)
                props.pop(j)

            rec=pygame.Rect([0, 0], [100, 100])
            pygame.draw.rect(self._screen, [0,0,0], rec)
            self.get_text(str(len(games)), [0,0])
            pygame.display.flip()
            fpsclock.tick(FPS)
            if len(games)>150:
                all_fps.append(fpsclock.get_fps())

            if len(games)==0:
                playing=False
                #print(sum(all_fps)/len(all_fps))
            else:
                if 0 in rem and False:
                    games[0].init_dis(self._screen)


    def run_winner(self, name):
        hard=0.1

        local_dir=os.path.dirname(__file__)
        config_path=os.path.join(local_dir, 'config-feedforward.txt')

        config=neat.config.Config(
            neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path
        )
        plr=self.defult_plr()
        path="evolv_info/"+name+"/ev_winner.nnet"
        path="evolv_info/"+name+"/winner.nnet"
        try:
            fil=open(path, "rb")
        except FileNotFoundError:
            print(path, "no file")
            self.main_menu()
            return "Invalid file"
        g=pickle.load(fil)
        net=neat.nn.FeedForwardNetwork.create(g, config)

        random.seed(42069)
        dis=False
        test_amt=200
        test_amt=0
        tests=[random.randrange(sys.maxsize) for i in range(test_amt)]
        avg_sc=[]
        avg_dis=[]
        print("Now testing: "+name+" - "+str(dis))

        start=time.time()
        for pos, seed in enumerate(tests):
            if int(test_amt/5)==0 or pos%int(test_amt/5)==int(test_amt/5)-1:
                print("Test num: "+str(pos)+" took "+str(time.time()-start))
                start=time.time()
            game=Game(self._screen, plr, hard, self.enemies, seed, self.sc_x, dis=dis, draw=False, targeting=True)
            scr, dis=self.run_ai(game, net)
            avg_sc.append(scr)
            avg_dis.append(dis)

        if test_amt!=0:
            print("Average score: "+str(int(sum(avg_sc)/len(tests))))
            print("Minimum/Maximum score: "+str(int(min(avg_sc)))+"/"+str(int(max(avg_sc))))
            print("Average distance: "+str(int(sum(avg_dis)/len(tests))))
            print("Minimum/Maximum distance: "+str(int(min(avg_dis)))+"/"+str(int(max(avg_dis))))
            print("Best seed: "+str(tests[avg_dis.index(max(avg_dis))]))

            new_data=[i//1000 for i in avg_dis]
            print(new_data)
            plt.hist(new_data)
            plt.show()
            path="evolv_info/"+name+"/testdata"+str(test_amt)
            with open(path, "wb") as file:
                pickle.dump(avg_dis, file)

        random.seed(time.time())
        seed=random.randrange(sys.maxsize)
        #seed=7018639715332314491
        seed=4855103173990346366
        seed=2594094090975880053
        #seed=246612780681178354
        print(seed)
        game=Game(self._screen, plr, hard, self.enemies, seed, self.sc_x, dis=True, targeting=True)
        self.run_ai(game, net)


    def run_ai(self, game, net):
        plr=game.player
        ins={
            "dirn":[0, 0],
            "fire":False,
            "s_fire":False,
            "spc":False
        }

        playing=True
        fpsclock=pygame.time.Clock()
        FPS=120

        while playing:
            ret=True
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    quit()

            inputs_1=(
                plr.cords[0]-game.target[0],
                plr.cords[1]-game.target[1],
                plr.vertical,
                plr.horizontal
            )

            inputs_2=tuple([i[0] for i in game.closest.values()])+tuple(i[1] for i in game.closest.values())
            inputs_3=tuple(game.vision.values())

            pot_vals=game.vision

            if hor:
                inputs_4=tuple([pot_vals[i] for i in [0, 45, 90, 135, 180]])
                inputs_5=[pot_vals[i] for i in [0, 315, 270, 225, 180]]
                inputs_5[0]=0
                inputs_5[4]=0
                inputs_5=tuple(inputs_5)
            else:
                inputs_4=tuple([pot_vals[i] for i in [11.25, 45, 90, 135, 168.75]])
                inputs_5=tuple([pot_vals[i] for i in [348.75, 315, 270, 225, 191.25]])

            inputs=inputs_1+inputs_2

            spec_inputs=(
                plr.cords[0]-game.target[0],
                plr.cords[1]-game.target[1]
            )+inputs_3

            if True:
                outs=net.activate(inputs_4)
                outs2=net.activate(inputs_5)

                x=outs[0] if abs(outs[0])>abs(outs2[0]) else outs2[0]
                y=outs[1] if abs(outs[1])>abs(outs2[1]) else -outs2[1]
            else:
                #outs=net.activate(inputs_1)
                outs=net.activate(inputs_3)
                #outs=nets[i].activate(spec_inputs)
                x, y=[round(i) for i in outs[0:2]]

            dirn=[0, 0]

            ret=game.spec_move(x, y)
            pl, mes=game.frame(dir=dirn, fire=ins["fire"],  s_fire=ins["s_fire"], special=ins["spc"], fps=fpsclock, dis=game.dis)

            if game.draw:
                game.get_text(str([round(i, 2) for i in outs]), [600, 300])
                game.get_text(str([round(i, 2) for i in outs2]), [600, 250])

            pygame.display.flip()
            fpsclock.tick(FPS)

            if not(pl) or not(ret):
                playing=False

        if game.dis and game.draw:
            self.end_screen(game, mes)
        else:
            return game.score, game.distanse

            
    def defult_plr(self):
        gun_selected="Basic gun"
        ship_selected="ship2"

        ship_s=dp(self.ships[ship_selected])
        player=sprites.player(ship_s)

        player.load_gun(self.guns[gun_selected])
        player.load_S_gun(self.guns["No gun"])
        player.life=1
        return player


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


        ship1=([100, 10], 5, 160000, 200, [int(180*self.sc_x), int(150*self.sc_x)], self.screen_size, "Ship1.png", ship1_gun_model, kill)#[[200, 75], [[70, 17], [70, 133]]])
        ship2=([100, 10], 3, 80000, 200, [int(104*self.sc_x), int(78*self.sc_x)], self.screen_size, "Ship2.png", ship2_gun_model, shild)#[[104, 39], [[30, 5], [30, 71]]])
        ship3=([100, 10], -2, 40000, 300, [int(64*self.sc_x), int(78*(64/104)*self.sc_x)], self.screen_size, "Ship2.png", ship2_gun_model, multi)#[[104, 39], [[30, 5], [30, 71]]])
        #stelth=sprites.player([100, 10], 1, 10000, 80, [50, 20], [screen_x, screen_y], "Ship1.png", [])
        #mati=sprites.player([100, 10], 5, 100000, 800, [500,400], [screen_x, screen_y], "Ship1.png", [])

        return {"ship1":ship1, "ship2":ship2, "test":ship3}


    def define_guns(self):
        guns={
            "Basic gun":(50, 10, [screen_x, int(10*self.sc_x)], 200, 400),
            "Cleaner":(50, 10000, [screen_x, 2*screen_y], 0, 0),
            "Front recoil":(200, 5, [screen_x, int(4*self.sc_x)], 100, -50),
            "Op gun":(200, 20, [screen_x, int(20*self.sc_x)], 100, -50),
            "Rand gun":(5, 40, [screen_x, int(150*self.sc_x)], 300, 4000, "rand"),
            "No gun":(0, 0, [screen_x, 0], 0, 0)
        }

        return guns


    def define_enemies(self):
        de=lambda x: [int(x*self.sc_x) for i in range(2)]
        enemies={
            "Meteor":(80, 3, de(100), "Meteor.png", self.screen_size[0], self.screen_size[1]),
            "Meteor2":(150, 1, de(150), "Meteor.png", self.screen_size[0], self.screen_size[1]),
            "Meteor3":(300, 0.5, de(200), "Meteor.png", self.screen_size[0], self.screen_size[1])
        }
        if not(telp):
            return {}
        return {
            "Meteor3":(300, 1, de(200), "Meteor.png", self.screen_size[0], self.screen_size[1])
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

    def get_input(self, game, display, let=False):
        running=True

        textinput=pygame_textinput.TextInput(
            text_color=(0,255,0),
            cursor_color=(0,255,0),
            font_family='freesansbold.ttf',
            font_size=int(32*self.sc_x),
            letters_al=let
            )

        while running:
            mouse=False
            self._screen.fill((0,0,0))

            events = pygame.event.get()
            for event in events:
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        running=False
                        self.main_menu()
                elif event.type==pygame.MOUSEBUTTONDOWN:
                    mouse=True
            pos=pygame.mouse.get_pos()

            if textinput.update(events):
                running=False
                game(textinput.input_string)

            text, cursor_vis, cursor_pos=textinput.return_cursor_stuff()
            if cursor_vis:
                cursor_pos=self._font.size(text[:cursor_pos])[0]

            display(textinput, cursor_pos, pos, mouse)

            pygame.display.update()


    def infinite_runner_display(self, textinput, cursor_pos, mouse_pos, mos):
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


    def level_runner_display(self, textinput, cursor_pos, pos, mos):
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

        ship_s=dp(self.ships[ship_selected])
        player=sprites.player(ship_s)

        player.load_gun(self.guns[gun_selected])
        if self.secondary_gun_selected!=None:
            player.load_S_gun(self.guns[self.secondary_gun_selected])
        else:
            player.load_S_gun(self.guns["No gun"])

        game(player, number)


    def infinite_runner_init(self, player, seed=None):
        if not(seed.isdigit()):
            seed=4855103173990346366
            seed=random.randrange(sys.maxsize)
        hard=0.1
        play=Game(self._screen, player, hard, self.enemies, seed, self.sc_x, dis=True, targeting=True)

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
        level=dp(self.levels[level])
        play=Level(self._screen, player, level["hardness"], level["enemies"], level["seed"], aim=level["aim"], sc_x=self.sc_x, dis=True)

        self.game(play)


    #Main game loop
    def game(self, play):
        play.start_stars()
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
                pygame.display.flip()
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

        if type(Game("screen", "player", "hardness", {}, 1))==type(play):
            self.save_result(play.score, play.seed)
        elif type(Level("screen", "player", "hardness", {}, 1, "aim"))==type(play):
            self.save_level_result(play.score, play.seed)

        self.end_screen(play, mes)


    def end_screen(self, play, mes, des=None):
        end=True
        play.end_screen(mes)
        while end:
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==27:
                        end=False
                        self.main_menu()
                    elif event.key==32 and des:
                        des()

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


    def __init__(self, screen, player, hardness, enemies, seed, sc_x=1, ost=[0, 0], sc_size=None, dis=False, targeting=False, draw=True):
        self.hor=12
        self.sc_x=sc_x
        self.ost=ost
        self.dis=dis
        self.draw=draw
        if sc_size==None:
            self.screen_x, self.screen_y=screen_x, screen_y
        else:
            self.screen_x, self.screen_y=sc_size

        self.player=player

        self.targeting=targeting
        self.t_div=self.screen_x
        self.t_div=360
        if not(self.targeting):
            self.target=[screen_x/2, screen_y/2]
        else:
            self.target_counter=0
            self.target_counter_max=4800/self.t_div
            self.target=[screen_x/2, screen_y/2]

        try:
            self.player.cords=dp(self.target)
        except AttributeError:
            pass

        self.seed=seed
        random.seed(int(self.seed))

        img="star1.png"
        img="test1.png"
        #img="star2.png"
        self.img_name=img

        self.all_bc=[]

        self.code=""
        for i in range(5):
            num=str(random.randint(0, 9))
            self.code+=num

        self._enemies=[]
        self._possible_enemies=enemies
        #self._enemy_probability=99.8
        self._enemy_probability={}
        i=0
        for enemy in self._possible_enemies.keys():
            self._enemy_probability[enemy]=99.8+i
            i+=0.5
            self._enemies.append([])

        try:
            stats=dp(enemies["Meteor3"])
            en=sprites.enemy(stats)
            en.cords[1]=self.target[1]
            if self.dis:
                en.add_pygame()
            self._enemies[list(enemies.keys()).index("Meteor3")].append(en)
        except:
            pass


        self.specials={
            "kill switch": [1,1], #[lambda: self.kill_switch(), 1500],
            "shild": [1,1], #[lambda: self.player.add_shild(), 3000],
            "multi": [1,1] #[lambda: self.player.add_multi(), 2500]
        }

        self.closest={
            "for0":[0, 0],
            "bk0":[0, 0]
        }

        self.cov=8
        self.vision=dict(zip([int(360/self.cov)*i for i in range(self.cov)], [self.screen_x for i in range(self.cov)]))
        if not(hor):
            del self.vision[0]
            del self.vision[180]
            for i in [-1, 1]:
                for j in [0, 180]:
                    self.vision[self.move_hor(i, j)]=self.screen_x

        self.vis_trans=dict(zip(self.vision.keys(), [1 if (i==45 or i==225) else -1 for i in self.vision.keys()]))
        for key, val in self.vis_trans.items():
            if key%90==0:
                self.vis_trans[key]=0
            elif key!=int(key) and True:
                if key%180>90:
                    self.vis_trans[key]=-1/self.hor
                else:
                    self.vis_trans[key]=1/self.hor

        self.special_counter=1

        self.status=True

        self.hardness=hardness

        self.score=0
        self.multiplier=1
        self.hard_speed=1
        self.score_change=0
        self.pos_score_change=0
        self.distanse=0

        if self.dis:
            self.init_dis(screen)


    def init_dis(self, screen):
        self._screen=screen
        try:
            self.player.add_pygame()
        except AttributeError:
            pass
        for index, enemies in enumerate(self._enemies):
            for index2, enemy in enumerate(enemies):
                enemy.add_pygame()

        self.img=pygame.image.load("Models/Back/"+self.img_name).convert_alpha()
        self.bc=[1, 10, [int(10*self.sc_x), int(70*self.sc_x)], self.img_name, screen_x, screen_y]

        self._font=pygame.font.Font('freesansbold.ttf', int(32*self.sc_x)) #the normal font used to display stuff


    def update_acceleration(self, dir):
        self.player.horixontal_thrust(dir[0])
        self.player.vertical_thrust(dir[1])


    def frame(self, dir, fire, s_fire, special, fps, dis=True):
        for key in self.vision.keys():
            self.vision[key]=self.screen_x
        self.dis=dis

        if self.targeting:
            self.target_counter+=1
            if self.target_counter==self.target_counter_max:
                self.target_counter=0
                new_target=[-1, -1]
                while not(0<new_target[0]<self.screen_x and 0<new_target[1]<self.screen_y):
                    new_target[0]=self.target[0]+randint(-int(self.screen_x/self.t_div), int(self.screen_x/self.t_div))
                    new_target[1]=self.target[1]+randint(-int(self.screen_x/self.t_div), int(self.screen_x/self.t_div))

                self.target=new_target#[randint(0, self.screen_x), randint(0, self.screen_y)]

        self.update_acceleration(dir)
        self.player.update_velocity()
        over=self.player.move(self.sc_x, self.sc_x)
        self.multiplier=round(self.multiplier+over, 5)
        if self._possible_enemies=={}:
            self.multiplier=1

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

        if self.dis and self.draw:
            self.draw_background(fps)
            #self.add_stars(over=over)
            self.draw_player()
            if self.targeting:
                rec=pygame.Rect([i-20 for i in self.target], [40, 40])
                #pygame.draw.rect(self._screen, [255,255,0], rec)

        self.iterate_enemies(fire_check, s_fire_check, over)

        self.comp_vis()
        if  self.dis and self.draw:
            self.draw_vis()
            vals=list(self.vision.values())

            mins=[]
            for key in [11.25, 45, 90, 135, 168.75]:
                mins.append(round(self.vision[key]+self.vision[key+180]-abs(self.vision[key]-self.vision [key+180])))
            self.get_text(str(sum([(pos**2.5)*i/11.7 for pos, i in enumerate(vals[::-1])])/16000*1000-sum(mins)/10), [600, 150])
            self.get_text(str(mins), [600, 200])
            vals.sort()
            self.get_text(str(sum([(pos**2.5)*i/11.7 for pos, i in enumerate(vals[::-1])])/16000*1000), [600, 100])


        if self.dis:
            if fire_check:
                self.draw_fire("F")
            if s_fire_check:
                self.draw_fire("S")

        self.check_overspeed()

        self.update_score()

        return self.status, "You lost"


    def update_score(self):
        #self.hardness+=(0.0001/((self.hardness+0.6)**3))
        if self.hardness>1:
            self.hardness=1
        elif self.hardness==1:
            pass
        else:
            self.hardness+=(0.0001/(self.hardness*3))

        self.hard_speed+=((0.003*self.hard_speed)/((self.hard_speed**2)*4))

        self.distanse+=1

        pos=self.player.return_cords()
        score=self.score_target(pos)
        self.pos_score_change=[int(score), round(((score/1000)**1.5)*0.5, 5)]

        #self.score_change=(round(score/10, 1)**1.5)*0.5
        self.score_change=((score/10)**1.5)*0.5

        if self.score_change==0:
            self.score_change-=0.1
        self.score_change*=self.multiplier

        if self.multiplier<0:
            self.score_change=abs(self.score_change)*-1*abs(self.multiplier-1)
        if self.score_change==0:
            self.score_change-=1
        self.score+=self.score_change
        self.player.gain_score()


    def score_target(self, pos):
        score=1
        con=2.5
        div=50

        x=int(abs(pos[0]-self.target[0])/10)*10
        score_x=((math.log(self.screen_x, con+x/div)))

        y=int(abs(pos[1]-self.target[1])/10)*10
        score_y=(math.log(self.screen_y, con+y/div))

        score+=(min([score_x, score_y])*2)

        vel=[
            self.player.vertical,
            self.player.horizontal
            ]
        #score-=abs(vel[0])
        #score-=abs(vel[1])

        if score<0:
            score=0

        #score+=(self.screen_x-abs(pos[0]-self.target[0]))
        #score+=(self.screen_y-abs(pos[1]-self.target[1]))

        return score


    def spawn_enemis(self):
        if self._possible_enemies=={}:
            alive=self.player.count_life()
            if alive:
                return None
            else:
                self.end_game()

        enemy_type=0
        for enemy, value in self._enemy_probability.items():
            value=(100-value+(self.hardness*self.multiplier**2))/len(list(self._enemy_probability.keys()))
            number=random.random()*100
            if number<value:
                self.spawn_enemy(enemy, enemy_type)
                #break
            else:
                pass
            enemy_type+=1


    def spawn_enemy(self, enemy, enemy_type):
        stats=dp(self._possible_enemies[enemy])
        lis=[sprites.enemy]*10+[sprites.enemyH]
        en=random.choice(lis)
        stats=list(stats)
        #stats[1]+=self.multiplier-1
        stats[1]+=self.hard_speed-1
        box1=en(stats)
        if self.check_spawn_place(box1):
            if self.dis:
                box1.add_pygame()
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


    def spec_move(self, x, y):
        x*=(self.screen_x/self.t_div)
        y*=(self.screen_x/self.t_div)
        return self.player.spec_move(x, y)


    def start_stars(self):
        stats=copy(self.bc)
        stats=list(stats)
        max_x=stats[4]
        cur_x=0
        speed=stats[1]
        while cur_x<max_x:
            self.add_stars(x_cord=cur_x)
            cur_x+=speed


    def add_stars(self, over=0, x_cord=False):
        rem=[]
        if randint(0, 100)>40:
            stats=copy(self.bc)
            stats=list(stats)
            stats[1]+=self.multiplier-1
            if x_cord:
                stats[4]=x_cord
            new_bc=sprites.star(stats, self.img)
            for bc in self.all_bc:
                if bc.return_box().colliderect(new_bc.return_box()):
                    break
                else:
                    pass
            else:
                self.all_bc.append(new_bc)

        if x_cord:
            return None

        for pos, bc in enumerate(self.all_bc):
            bc.change_speed(self.multiplier)
            bc.move(self.sc_x)
            if bc.check_map():
                rem.append(pos)
            self.draw_enemy(bc.return_box(), bc)
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

        return None
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

        self.writing(fps)

        self.add_controls()

        return None


    def gun_slider(self, gun, hight, width, pos):
        amo, reload1, mx, mxr=gun.return_slides()

        if mx==mxr==0:
            return 0

        self.show_slider(mx, amo, pos, hight, width)
        self.show_slider(mxr, reload1, [width*1.2+pos[0], pos[1]], hight, width)
        return 2


    def writing(self, fps):
        multi=self.multiplier
        pos=self.player.return_cords()
        x=int(abs(pos[0]-self.target[0])/10)*10
        y=int(abs(pos[1]-self.target[1])/10)*10

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

        self.get_text(str("X dis: "+str(x)), [1200, 0])
        self.get_text(str("Y dis: "+str(y)), [1200, 50])

        self.get_text(str("FPS: "+str(round(fps.get_fps(), 4))), [400, screen_y-100])
        self.get_text(str("Raw Frame time: "+str(round(fps.get_rawtime(), 4))), [400, screen_y-150])

        self.get_text(str("Level code: "+str(self.code)), [400, screen_y-50])
        self.get_text(str("Level seed: "+str(self.seed)), [400, screen_y-200])

        self.get_text(str("Score: "+str(round(self.score, 2))), [1000, screen_y-100])
        self.get_text(str("Kills: "+str(self.player.kills)), [1000, screen_y-150])
        self.get_text(str("Damage: "+str(self.player.damage)), [1000, screen_y-200])
        self.get_text(str("Distance: "+str(self.distanse)), [1000, screen_y-250])
        self.get_text(str("Pos Score change: "+str(self.pos_score_change)), [0, screen_y-300])
        self.get_text(str("Hardness: "+str(self.hardness)), [0, screen_y-350])

        self.get_text(str("Special recharge: "+str(self.special_counter)), [1000, screen_y-300])
        self.get_text(str("Multi: "+str(multi)), [0, 100])
        self.get_text(str("Score change: "+str(round(self.score_change, 3))), [0, 200])


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
        if self.dis:
            self._screen.blit(text, pos)


    def draw_vis(self):
        pl_cords=dp(self.player.return_cords())
        for key, val in self.vision.items():
            ang_norm=key%90
            ang_dir=key//90
            if ang_dir%2==0:
                x, y=self.angs(ang_norm)
                if ang_dir==2:
                    x=-x
                    y=-y
            else:
                y, x=self.angs(ang_norm)
                if ang_dir==1:
                    x=-x
                else:
                    y=-y

            end_cords=[]
            end_cords.append(pl_cords[0]+int(val*x))
            end_cords.append(pl_cords[1]+int(val*y))

            pygame.draw.line(self._screen, [255,0,0], pl_cords, end_cords)
            pygame.draw.circle(self._screen, [255,0,0], end_cords, 10)

            end_cords=[]
            end_cords.append(pl_cords[0]+int(150*x))
            end_cords.append(pl_cords[1]+int(150*y))
            #self.get_text(str(key)+" "+str(x)+" "+str(y), end_cords)


    def draw_player(self):
        box=self.player.return_box()
        ship=self.player.return_img()
        #pygame.draw.rect(self._screen, [255,255,255], box)
        #pygame.draw.rect(self._screen, [255,255,255], box2)
        self._screen.blit(ship, self.player.return_img_cords())
        if self.target:
            rec=pygame.Rect([i-10 for i in self.player.return_cords()], [20, 20])
            #pygame.draw.rect(self._screen, [255,0,0], rec)
            pass


    def draw_fire(self, box):
        if box=="F":
            boxes=self.player.return_gun_box()
        elif box=="S":
            boxes=self.player.return_S_gun_box()
        for box in boxes:
            pygame.draw.rect(self._screen, [125,0,0], box)


    def draw_enemy(self, box, enemy):
        #pygame.draw.rect(self._screen, [255,255,0], box)
        try:
            self._screen.blit(enemy.return_img(), enemy.return_img_cords())
            pass
        except AttributeError:
            pass
        health=enemy.speed
        cords=enemy.cords
        #self.get_text(str(str(health)), cords, [255,255,255])


    def iterate_enemies(self, fire_check, s_fire_check, over):
        if self._enemies==[[] for i in self._enemies]:
            return None
        player_box=self.player.return_box()
        player=self.player.return_img()
        if self.dis:
            player=pygame.mask.from_surface(player)
        player_cords=self.player.return_img_cords()

        self.closest={
            "for0":[-1,-1],
            "bk0":[-1,-1]
        }
        a_player_cords=dp(self.player.return_cords())

        laser_box=self.player.return_gun_box()
        s_laser_box=self.player.return_S_gun_box()
        for index, enemies in enumerate(self._enemies):
            for index2, enemy in enumerate(enemies):
                enemy.change_speed(self.multiplier)
                enemy.move(self.sc_x)

                alive=True
                box=enemy.return_box()

                if self.dis and self.draw:
                    self.draw_enemy(box, enemy)
                self.check_colision(player, player_cords, index, index2, enemy, box, player_box)

                x_dif=player_cords[0]-enemy.cords[0]
                y_dif=player_cords[1]-enemy.cords[1]

                self.update_close(x_dif, y_dif)
                self.update_vis(x_dif, y_dif, a_player_cords, enemy.return_cords(), enemy.return_size())

                if fire_check:
                    damage=self.player.return_damage()
                    alive=self.check_colisions_laser(laser_box[0], index, index2, enemy, box, damage)

                if s_fire_check and alive:
                    damage=self.player.return_S_damage()
                    alive=self.check_colisions_laser(s_laser_box[0], index, index2, enemy, box, damage)
                    if alive:
                        self.check_colisions_laser(s_laser_box[1], index, index2, enemy, box, damage)

                self.delete_enemies(index, index2, enemy)


    def comp_vis(self):
        pl_cords=dp(self.player.return_cords())
        rev_cords=[self.screen_x-pl_cords[0], self.screen_y-pl_cords[1]]
        for key, val in self.vision.items():
            if key==0:
                new_val=self.screen_x-pl_cords[0]
            elif key==180:
                new_val=pl_cords[0]
            elif key==90:
                new_val=self.screen_y-pl_cords[1]
            elif key==270:
                new_val=pl_cords[1]
            elif key==45:
                tri_side=min(rev_cords[0], rev_cords[1])
                new_val=((tri_side**2)*2)**0.5
            elif key==135:
                tri_side=min(pl_cords[0], rev_cords[1])
                new_val=((tri_side**2)*2)**0.5
            elif key==315:
                tri_side=min(rev_cords[0], pl_cords[1])
                new_val=((tri_side**2)*2)**0.5
            elif key==225:
                tri_side=min(pl_cords[0], pl_cords[1])
                new_val=((tri_side**2)*2)**0.5
            elif key==11.25:
                new_val=min(
                    ((rev_cords[0])**2+(rev_cords[0]/self.hor)**2)**0.5,
                    ((rev_cords[1]*self.hor)**2+(rev_cords[1])**2)**0.5
                )
            elif key==168.75:
                new_val=min(
                    ((pl_cords[0])**2+(pl_cords[0]/self.hor)**2)**0.5,
                    ((rev_cords[1]*self.hor)**2+(rev_cords[1])**2)**0.5
                )
            elif key==191.25:
                new_val=min(
                    ((pl_cords[0])**2+(pl_cords[0]/self.hor)**2)**0.5,
                    ((pl_cords[1]*self.hor)**2+(pl_cords[1])**2)**0.5
                )
            elif key==348.75:
                new_val=min(
                    ((rev_cords[0])**2+(rev_cords[0]/self.hor)**2)**0.5,
                    ((pl_cords[1]*self.hor)**2+(pl_cords[1])**2)**0.5
                )


            self.vision[key]=min(new_val, val)


    def move_hor(self, ang, cur):
        if ang%180<90:
            ad=45/4
        else:
            ad=-45/4
        cur=(cur+ad)%360
        return cur


    def update_close(self, x_dif, y_dif):
        if x_dif>0:
            key="for"
        else:
            key="bk"

        rgn=int(len(self.closest.keys())/2)

        for i in range(rgn):
            u_key=str(key+str(i))
            if self.closest[u_key][0]==-1:
                self.closest[u_key]=[x_dif, y_dif]
                break
        for i in range(rgn):
            u_key=str(key+str(i))
            if abs(self.closest[u_key][0])>abs(x_dif):
                self.closest[u_key]=[x_dif, y_dif]
                break

        #if self.closest[key]==-1 or abs(self.closest[key])>abs(x_dif):
        #    self.closest[key]=abs(x_dif)

        '''
        if y_dif>0:
            key="up"
        else:
            key="bot"
        if self.closest[key]==-1 or abs(self.closest[key])>abs(y_dif):
            self.closest[key]=abs(y_dif)
        '''


    def update_vis(self, x_dif, y_dif, cords, box, size):
        x_dif=-x_dif
        y_dif=-y_dif
        #x=90*(x_dif<0 and y_dif>0)
        #y=180*(y_dif<0)
        #x2=90*(x_dif>0 and y_dif<0)
        #lims=[x+y+x2, (x+y+x2+90)]
        box=[box[i]-(size[i]*0.7)/2 for i in range(2)]
        size=[size[i]*0.7 for i in range(2)]

        if x_dif==0:
            ang=90
        else:
            ang=np.arctan(abs(y_dif/x_dif))*180/np.pi
        if x_dif<0 and y_dif<0:
            ang+=180
        elif x_dif<0:
            ang=180-ang
        elif y_dif<0:
            ang=360-ang
        sc=360/self.cov
        ang=(ang//sc)*sc
        ang%=360
        angs=[(ang-sc)%360, ang, (ang+sc)%360]

        for cur in angs:
            if not(hor) and cur in [0, 180]:
                for i in [-1, 1]:
                    cur2=self.move_hor(i, cur)
                    val=self.check_vis3(cords, cur2, [box[0], box[0]+size[0]], [box[1], box[1]+size[1]])
                    if val:
                        self.vision[cur2%360]=min(self.vision[cur2%360], val)
                continue

        #for cur in self.vision.keys():
            #val=self.check_vis2(cords, cur, box, self.vision[cur])
            val=self.check_vis3(cords, cur, [box[0], box[0]+size[0]], [box[1], box[1]+size[1]])
            if val:
                self.vision[cur%360]=min(self.vision[cur%360], val)


    def check_vis(self, cords, ang, xs, ys):
        ang_norm=ang%90
        ang_dir=ang//90
        if ang_dir%2==0:
            x, y=self.angs(ang_norm)
            multi=1
        else:
            y, x=self.angs(ang_norm)
            multi=-1

        c=multi*(y/(x+0.000001))
        print(c)

        outs=[]
        for i in range(1):
            if y==0:
                x_check=cords[1]
            elif y==0:
                y_check=cords[0]
            else:
                x_check=c*(xs[i]-cords[0])+cords[1]
                y_check=(1/c)*(ys[i]-cords[1])+cords[0]

            if x!=0 and ys[0]<x_check<ys[1]:
                if (xs[i]>=cords[1] and ang_dir in [0, 1]) or (xs[i]<=cords[1] and ang_dir in [2, 3]):
                    val=round(
                        (
                            (cords[0]-xs[i])**2+
                            (cords[1]-x_check)**2
                        )**0.5, 4
                    )
                    outs.append(val)
            if y!=0 and xs[0]<y_check<xs[1]:
                if (ys[i]>=cords[0] and ang_dir in [0, 3]) or (ys[i]<=cords[0] and ang_dir in [1, 2]):
                    val=round(
                        (
                            (cords[0]-y_check)**2+
                            (cords[1]-ys[i])**2
                        )**0.5, 4
                    )
                    outs.append(val)

        if outs==[]:
            return None
        return min(outs)


    def check_vis2(self, cords, ang, box, mx):
        ang_norm=ang%90
        ang_dir=ang//90
        if ang_dir//2==0:
            x, y=self.angs(ang_norm)
            if ang_dir==2:
                x=-x
                y=-y
        else:
            y, x=self.angs(ang_norm)
            if ang_dir==1:
                x=-x
            else:
                y=-y

        x*=50
        y*=50
        hyp=round((x**2+y**2)**0.5, 2)
        print(hyp)
        print(x, y)
        mult=0

        while True:
            mult+=1
            cords[0]+=x
            cords[1]+=y

            if box.collidepoint(cords):
                return mult*hyp
            if mult*hyp>=mx:
                return mult*hyp


    def check_vis3(self, cords, ang, xs, ys):
        c=self.vis_trans[ang]
        outs=[]

        if ang<90 or ang>270:
            x_pos=0
        else:
            x_pos=1

        if ang<180:
            y_pos=0
        else:
            y_pos=1

        if c==0:
            if ang%180==0:
                if ys[0]<=cords[1]<=ys[1]:
                    return abs(cords[0]-xs[x_pos])
                else:
                    return None
            else:
                if xs[0]<=cords[0]<=xs[1]:
                    return abs(cords[1]-ys[y_pos])
                else:
                    return None


        x_check=c*(xs[x_pos]-cords[0])+cords[1]
        y_check=(1/c)*(ys[y_pos]-cords[1])+cords[0]

        x_dis, y_dis=0, 0

        if ys[0]<x_check<ys[1]:
            y_dis=(cords[1]-x_check)**2
            x_dis=(cords[0]-xs[x_pos])**2

        if xs[0]<y_check<xs[1]:
            x_dis=(cords[0]-y_check)**2
            y_dis=(cords[1]-ys[y_pos])**2

        if x_dis==0 and y_dis==0:
           return None
        else:
           return round((x_dis+y_dis)**0.5, 4)


    def angs(self, ang):
        if ang==11.25:
            return 1, 1/self.hor
        elif ang==78.75:
            return 1/self.hor, 1
        return round(np.cos(ang/180*np.pi), 5), round(np.sin(ang/180*np.pi), 5)


    def delete_enemies(self, index, index2, enemy):
        if enemy.check_map():
            self._enemies[index].pop(index2)
        else:
            pass


    def check_colision(self, player, player_cords, index, index2, enemy, box, player_box):
        #return None
        if box.colliderect(player_box):
            if not(self.dis):
                self.loose_life(index, index2)
                return None
        else:
            return None

        enemy_cords=enemy.return_img_cords()
        ofset=(int(enemy_cords[0]-player_cords[0]), int(enemy_cords[1]-player_cords[1]))

        enemy_mask=enemy.return_img()
        enemy_mask=pygame.mask.from_surface(enemy_mask)

        if player.overlap(enemy_mask, ofset)!=None:
            self.loose_life(index, index2)


    def loose_life(self, index, index2):
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

        base=int(50*self.sc_x)

        self.get_text(str(mes), [screen_x/2-base*2, screen_y/2-base*3])

        try:
            self.get_text(str("Kills: "+str(self.player.kills)), [screen_x/2-base*2, screen_y/2-base])
            self.get_text(str("Score: "+str(round(self.score, 2))), [screen_x/2-base*2, screen_y/2-base*2])
            self.get_text(str("Damage: "+str(self.player.damage)), [screen_x/2-base*2, screen_y/2])
            self.get_text(str("Distance: "+str(self.distanse)), [screen_x/2-base*2, screen_y/2+base])
        except AttributeError:
            pass



class Level(Game):

    def __init__(self, screen, player, hardness, enemies, seed, aim, sc_x=1):
        super().__init__(screen, player, hardness, enemies, seed, sc_x=sc_x)

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



def main(test=False, ev=False):
    pygame.init()
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    x, y=pygame.display.Info().current_w, pygame.display.Info().current_h
    pygame.quit()
    pygame.init()
    pygame.display.set_caption("Space game")

    prop=round(x/y, 1)

    if test:
        screen=pygame.display.set_mode((int(test*16/9), test))
    elif prop==1.8:
        screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    elif prop>1.8:
        screen=pygame.display.set_mode((int(y*16/9), y))#, pygame.FULLSCREEN)
    elif prop<1.8:
        screen=pygame.display.set_mode((x, int(x*9/16)))#, pygame.FULLSCREEN)

    global screen_x, screen_y #globalises the hight and the width of the screen,
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h
    print(screen_x, screen_y)

    ref_x=1366
    sc_x=screen_x/ref_x

    current_game=Menu(screen, [screen_x, screen_y], sc_x)
    if not(ev):
        current_game.main_menu()
    #current_game.pick_ship()
    return current_game


def run_evolv(data):
    try:
        _, name = data
    except ValueError:
        print("Invalid number of arguments")
        return None

    current_game = main(ev = True)
    current_game.evolv_init(name)


if __name__=="__main__":
    if len(sys.argv) == 1:
        main()
    else:
        run_evolv(sys.argv)
