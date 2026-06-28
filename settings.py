class Settings:
    """ Una clase para guardar toda la configuración del juego """

    def __init__(self):
        """ Incicializa la configuración de juego """

        # Configuración de la pantalla
        self.screen_width = 1000
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # Configuración de la nave
        self.ship_speed = 1.5

        # Configuración de las balas
        self.bullet_speed = 1
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3