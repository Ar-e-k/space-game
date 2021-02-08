import pygame
import sprites

def main():
    pygame.init()
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    playing=True #Determines is the game on or not
    play=game(screen, sprites.player(10, 10, 10, 100))
    paused=False

    while playing: #Main gameloop
        playing=play.frame()
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==27: #key 27 is escape, clicking it quits the game
                    play.end_game()
                    playing=False
                elif event.key==32: #pausing the game
                    paused=True
        while paused:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==32:
                        paused=False
        pygame.display.flip()


class game:

    def __init__(self, screen, player):
        self._screen=screen
        self.player=player

    def frame(self):
        self.draw_background()
        self.draw_player()
        return True

    def draw_background(self):
        rec=pygame.Rect([0, 0], [200, 100])
        pygame.draw.rect(self._screen, [255,255,255], rec)

    def draw_player(self):
        position=self.player.return_cords()
        self.box=pygame.Rect(position, [10, 10]) # The actuall box
        pygame.draw.rect(self._screen, [0,0,0], self.box)

    def end_game(self):
        return None


if __name__=="__main__":
    main()
