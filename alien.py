import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """ Una clase para representar a un solo alien de la flota """

    def __init__(self, ai_game):
        """ Inicializa el alien y establece su posición inicial """
        super().__init__()
        self.screen = ai_game.screen

        # Carga la imagen del alien y configura su atributo rect
        self.image = pygame.image.load("images/alien.bmp")
        self.rect = self.image.get_rect()

        # Inicia un nuevo alien cerca de la parte superior izquierda de la pantalla
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Guarda la posición horizontal exacta del alien
        self.x = float(self.rect.x)
