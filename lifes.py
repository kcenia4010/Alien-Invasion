import pygame
from pygame.sprite import Sprite

class Lifes(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        self.image = pygame.image.load('C:\\Users\\Kceni\\Desktop\\personal_projects\\Alien-Invasion\\images\\ship2.bmp')
        self.rect = self.image.get_rect()

        