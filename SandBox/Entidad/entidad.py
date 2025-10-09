from Entidad.tablero_datos import TableroDatos 

class Tablero:
    """Clase que representa el estado del tablero y los barcos."""
    
    def __init__(self, size=10):
        self.filas = size
        self.columnas = size
        
        # Matriz para la representación visual/interna: 
        # '.' = Agua, '*' = Barco (sin tocar)
        self.matriz = [['.' for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Las coordenadas de los barcos se guardan en un conjunto para búsquedas rápidas (row, col).
        self.ships = set()
        
        self.total_parts = 0 # Se actualizará después de la colocación por TableroDatos
        self.parts_hit = 0
        self.total_tries = 100 # Número máximo de intentos
        self.plays = set()
        self.are_hints_shown = False 

        # Llama a la lógica de colocación de barcos de la capa de Datos
        TableroDatos.generar_barcos(self)

    def is_ship_at(self, row, col):
        """Verifica si hay un barco en la coordenada dada usando el set de coordenadas."""
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
