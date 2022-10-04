import os
import neat
import main as main_game

def define_game():
    game=main_game.main(test=200, ev=True)
    game.check_game(game.infinite_runner_init, "")
    #game.get_input(game.infinite_runner_init, game.infinite_runner_display)
    return game


def main_neat(genomes, config):
    print(len(genome))
    nets=[]
    ge=[]
    pls=[]

    for _, g in genomes:
        print("lap")
        net=neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        pls.append(define_game())
        g.fitness=0
        ge.append(g)
 fs

def run(config_path):
    config=neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path
        )
    p=neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)

    winneer=p.run(main_neat,50)


def main():
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir, 'config-feedforward.txt')
    for i in range(1):
        print("Gen number "+str(i))
        run(config_path)


if __name__=="__main__":
    main()
