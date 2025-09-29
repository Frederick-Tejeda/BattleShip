from Entidad.entidad import Tablero

class WarShipController:
    """
    Clase que maneja la lógica de negocio y el estado del juego.
    Actúa como intermediario entre la Vista (Presentación) y el Modelo (Entidad).
    """
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.game_model = None

    def start_new_game(self):
        """Inicializa un nuevo modelo de juego."""
        self.game_model = Tablero(self.board_size)
        return self.game_model

    def process_shot(self, row, col):
        """
        Procesa un disparo en la coordenada (row, col).
        Retorna: ("hit" o "miss", mensaje_de_estado)
        """
        if not self.game_model:
            return "error", "El juego no ha sido inicializado."

        self.game_model.decrement_tries()
        
        is_hit = self.game_model.is_ship_at(row, col)
        self.game_model.plays.add((row, col))

        if is_hit:
            self.game_model.register_hit()
            if self.game_model.is_game_over():
                message = "¡Felicidades! ¡Has hundido todos los barcos!"
            else:
                remaining = self.game_model.get_remaining_parts()
                message = f"¡Es un impacto! Quedan {remaining} partes de barco."
            return "hit", message
        else:
            remaining_parts = self.game_model.get_remaining_parts()
            message = f"¡Fallaste!"
            
            if self.game_model.has_run_out_of_tries():
                message = "Juego terminado ✅"
            elif self.game_model.is_game_over():
                message = "¡Felicidades! ¡Has hundido todos los barcos!"

            return "miss", message
            
    def is_game_finished(self):
        """Verifica si el juego ha finalizado por victoria o por intentos agotados."""
        if not self.game_model:
            return False
        return self.game_model.is_game_over() or self.game_model.has_run_out_of_tries()

    def get_board_size(self):
        """Obtiene el tamaño del tablero."""
        return self.board_size