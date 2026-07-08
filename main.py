import pygame
import sys

from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button

class AlienInvasion:
    """ Clase general para gestionar los recursos y el comportamiento del juego """
    
    def __init__(self):
        """ Iniciaiza el juego y genera recursos """
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Crea una instancia para guardar las estadísticas del juego
        self.stats = GameStats(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # hace el botón "Play"
        self.play_button = Button(self, "Play")

    def run_game(self):
        """ Inicia el bucle principal para el juego. """
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            
    def _check_events(self):
        """ Responde a las pulsaciones de teclas y eventos de ratón. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event) 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """ Inicia un nuevo juego cuando el usuario hace clic en "Play". """
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)

        if button_clicked and not self.stats.game_active:
            # Reestablece las estadísticas del juego
            self.stats.reset_stats()
            self.stats.game_active = True

            # Se deshace de los aliens y de las balas que quedan
            self.aliens.empty()
            self.bullets.empty()

            # Crea una flota nueva y centra la nave
            self._create_fleet()
            self.ship.center_ship()
           
    def _check_keydown_events(self, event):
        """ Pulsaciones de teclas """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        """ Liberación de teclas """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """ Crea una bala nueva y la añade al grupo de balas. """
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """ Actualiza la posición de las balas y se deshace de las viejas """
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            
            self._check_bullet_alien_collisions()
        # Busca balas que hayan dado a aliens. Si las hay se deshace tanto de bala como alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if not self.aliens:
            # Destruye las balas existentes y crea una flota nueva
            self.bullets.empty()
            self._create_fleet()

    def _check_bullet_alien_collisions(self):
        """ Responde a las colisiones bala-alien """
        # Retira todas las balas y alien que han chocado
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()

    def _create_fleet(self):
        """ Genera la flota de aliens """
        # Crea un alien y halla el número de aliens en una fila
        # El espacio entre aliens es igual a la anchura de un alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determina el número de filas de aliens que caben en la pantalla
        ship_height = self.ship.rect.height
        availabel_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = availabel_space_y // (2 * alien_height)

        # Crea la flota completa de aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """ Crea una alien y lo coloca en la fila """
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """ Responde adecuadamente si algún alien ha llegado a un borde """
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """ Baja toda la flota y cambia su dirección """
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """ 
        Comprueba si la flota está en un borde,
        después actualiza las posiciones de todos los aliens de la flota
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Busca colisiones alien-nave
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """ Comprueba si algún alien ha llegado al fondo de la pantalla """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Trata esto como si la nave hubiese dsido alcanzada
                self._ship_hit()
                break

    def _ship_hit(self):
        """ Responde al impacto de un alien en la nave """

        if self.stats.ships_left > 0:
            # Dismimuye número de naves
            self.stats.ships_left -= 1

            # Se deshace de los aliens y las balas restantes
            self.aliens.empty()
            self.bullets.empty()

            # Crea nueva flota y centra la nave
            self._create_fleet()
            self.ship.center_ship()

            # Pausa
            sleep(0.5)
        else:
            self.stats.game_active = False
    
    def _update_screen(self):
        """ Actualiza las imágenes en la pantalla y cambia a pantalla nueva """
        self.screen.fill(self.settings.bg_color)
        self.ship.blit_ship()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Dibuja el botón para jugar si el juego está inactivo
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Hace visible la última pantalla dibujada
        pygame.display.flip()

if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()