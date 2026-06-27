class Settings:
    """ Clase para guardar la configuración del juego """
    def __init__(self):
        # Configuración de la pantalla
        self.screen_width = 1000
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # Configuración de la nave
        self.ship_speed = 1.5