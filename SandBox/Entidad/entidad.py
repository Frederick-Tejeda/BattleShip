import random

class Tablero:
    """Clase que representa el estado del tablero y los barcos."""
    
    def __init__(self, size=10):
        self.size = size
        # Las coordenadas de los barcos se guardan en un conjunto para búsquedas rápidas.
        self.ships = self._place_ships_randomly()
        self.total_parts = len(self.ships)
        self.parts_hit = 0
        self.total_tries = 100 # Número máximo de intentos
        self.plays = set() # Para rastrear las jugadas realizadas
        self.are_hints_shown = False # Para rastrear si las pistas están activadas

    def _place_ships_randomly(self):
        """Genera y coloca las partes de los barcos aleatoriamente."""
        ships = set()
        # Colocamos un número fijo de partes de barco (ejemplo: 20 partes)
        # Esto simula tener varios barcos de diferentes tamaños.
        while len(ships) < 20: 
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            ships.add((row, col))
        return ships

    def is_ship_at(self, row, col):
        """Verifica si hay un barco en la coordenada dada."""
        return (row, col) in self.ships

    def register_hit(self):
        """Registra un impacto en una parte de barco."""
        self.parts_hit += 1
        
    def is_game_over(self):
        """Verifica si el juego ha terminado (todos los barcos hundidos)."""
        return self.parts_hit >= self.total_parts
        
    def decrement_tries(self):
        """Decrementa el contador de intentos restantes."""
        self.total_tries -= 1
        
    def has_run_out_of_tries(self):
        """Verifica si se han agotado los intentos."""
        return self.total_tries <= 0

    def get_remaining_parts(self):
        """Retorna las partes de barco que faltan por hundir."""
        return self.total_parts - self.parts_hit
