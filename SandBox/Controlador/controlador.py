# Controlador/controlador.py
import random
import collections
from Entidad.entidad import Tablero

class WarShipController:
    """
    Controlador que soporta:
      - Modo 'solo' (humano vs tablero estático)
      - Modo 'hv' (Humano vs Máquina)
      - Modo 'mm' (Máquina vs Máquina)
      - Modo 'hvh' (Humano vs Humano)
    """

    class AiState:
        """Estado interno de una IA (memoria de tiros/target mode)."""
        def __init__(self, board_size, use_parity=True):
            self.board_size = board_size
            self.ai_shots = set()
            self.ai_targets = collections.deque()
            self.ai_hits = []
            self.ai_current_hits = []
            self.ai_use_parity = use_parity

    def __init__(self, board_size=10):
        self.board_size = board_size

        # Modo / tableros
        self.mode = 'solo'
        self.game_model = None
        self.tablero1 = None
        self.tablero2 = None

        # IA(s)
        self.ai_for_machine = None
        self.ai_A = None
        self.ai_B = None

        # Control de turno
        self.current_turn = None # 'human', 'machine', 'A', 'B', 'P1', 'P2'

        # Nueva propiedad para resaltar casilla ganadora
        self.last_hit_win = None

    # ----------------------
    # Inicialización de juegos
    # ----------------------
    def start_new_game(self):
        self.mode = 'solo'
        self.game_model = Tablero(self.board_size)
        self.tablero1 = self.tablero2 = None
        self.ai_for_machine = None
        self.ai_A = self.ai_B = None
        self.current_turn = 'human'
        self.last_hit_win = None
        return self.game_model

    def start_human_vs_machine(self):
        self.mode = 'hv'
        self.tablero1 = Tablero(self.board_size)
        self.tablero2 = Tablero(self.board_size)
        self.ai_for_machine = WarShipController.AiState(self.board_size, use_parity=True)
        self.current_turn = 'human'
        self.last_hit_win = None
        return (self.tablero1, self.tablero2)

    def start_machine_vs_machine(self):
        self.mode = 'mm'
        self.tablero1 = Tablero(self.board_size)
        self.tablero2 = Tablero(self.board_size)
        self.ai_A = WarShipController.AiState(self.board_size, use_parity=True)
        self.ai_B = WarShipController.AiState(self.board_size, use_parity=True)
        self.current_turn = 'A'
        self.last_hit_win = None
        return (self.tablero1, self.tablero2)

    # def start_human_vs_human(self):
    #     """Inicializa los tableros para el modo Humano vs Humano."""
    #     self.mode = 'hvh'
    #     self.tablero1 = Tablero(self.board_size) # Tablero del Jugador 1
    #     self.tablero2 = Tablero(self.board_size) # Tablero del Jugador 2
    #     self.ai_for_machine = None
    #     self.ai_A = self.ai_B = None
    #     self.current_turn = 'P1' # P1 ataca a T2, P2 ataca a T1
    #     self.last_hit_win = None
    #     return (self.tablero1, self.tablero2)
    
    def start_hvh_game(self):
        self.mode = 'hvh'
        self.tablero1 = Tablero(self.board_size) # Tablero de P1
        self.tablero2 = Tablero(self.board_size) # Tablero de P2
        self.current_turn = 'P1'
        self.last_hit_win = None

    # ----------------------
    # Disparos
    # ----------------------
    def _fmt(self, message: str):
        return message.strip().replace('\n', ' ')

    def process_shot_on(self, tablero: Tablero, row: int, col: int):
        """Procesa un disparo en el tablero dado (fila, columna)."""
        if tablero is None:
            return "error", self._fmt("Tablero no inicializado.")

        if (row, col) in tablero.plays:
            return "repeat", self._fmt("Ya se disparó en esa posición.")
        
        # Registrar el intento de disparo
        tablero.plays.add((row, col))

        if tablero.is_ship_at(row, col):
            tablero.register_hit()
            
            if tablero.is_game_over():
                self.last_hit_win = (tablero, row, col)
                return "win", self._fmt("¡Barco impactado y flota enemiga hundida! ¡Victoria!")
            else:
                return "hit", self._fmt("¡Impacto!")
        else:
            # Solo descontar intento si falla (solo/hv/hvh)
            if self.mode in ('solo', 'hv', 'hvh'): 
                 tablero.decrement_tries()
            return "miss", self._fmt("Agua.")

    # ----------------------
    # IA Helpers
    # ----------------------
    def ai_neighbors(self, row, col):
        """Genera celdas adyacentes válidas para la búsqueda de la IA."""
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            r, c = row + dr, col + dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size:
                neighbors.append((r, c))
        return neighbors

    def ai_random_hunt_cell_for(self, ai_state: AiState, use_parity=True):
        """Elige una celda aleatoria que no haya sido disparada, usando paridad si es necesario."""
        valid_cells = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in ai_state.ai_shots:
                    if not use_parity or (r + c) % 2 == 0:
                        valid_cells.append((r, c))
        
        if not valid_cells:
            # Si se acaban las celdas de paridad, se relaja la regla
            if use_parity:
                return self.ai_random_hunt_cell_for(ai_state, use_parity=False)
            # Si no quedan celdas sin disparar
            return None, None
        
        row, col = random.choice(valid_cells)
        return row, col

    def ai_enqueue_adjacent_for(self, ai_state: AiState, row: int, col: int):
        """Añade las celdas adyacentes válidas a la cola de objetivos."""
        for r, c in self.ai_neighbors(row, col):
            if (r, c) not in ai_state.ai_shots and (r, c) not in ai_state.ai_targets:
                ai_state.ai_targets.append((r, c))

    def ai_extend_line_from_hits_for(self, ai_state: AiState, row: int, col: int):
        """
        Extiende la búsqueda a lo largo de una línea si ya hay dos o más golpes consecutivos.
        Esto se hace cuando se logra el segundo golpe (o más) para terminar el barco.
        """
        if len(ai_state.ai_current_hits) < 2:
            return
        
        hits = sorted(ai_state.ai_current_hits)
        is_horizontal = all(r == hits[0][0] for r, c in hits)
        
        if is_horizontal:
            r = hits[0][0]
            min_c = min(c for r, c in hits)
            max_c = max(c for r, c in hits)

            # Probar a la izquierda
            if min_c > 0 and (r, min_c - 1) not in ai_state.ai_shots:
                ai_state.ai_targets.appendleft((r, min_c - 1))
            
            # Probar a la derecha
            if max_c < self.board_size - 1 and (r, max_c + 1) not in ai_state.ai_shots:
                ai_state.ai_targets.appendleft((r, max_c + 1))
        else: # Vertical
            c = hits[0][1]
            min_r = min(r for r, c in hits)
            max_r = max(r for r, c in hits)
            
            # Probar arriba
            if min_r > 0 and (min_r - 1, c) not in ai_state.ai_shots:
                ai_state.ai_targets.appendleft((min_r - 1, c))

            # Probar abajo
            if max_r < self.board_size - 1 and (max_r + 1, c) not in ai_state.ai_shots:
                ai_state.ai_targets.appendleft((max_r + 1, c))
        
        # Eliminar duplicados si los hay (aunque la lógica de shots/targets lo evita)
        ai_state.ai_targets = collections.deque(list(dict.fromkeys(ai_state.ai_targets)))

    def ai_make_move_on(self, tablero: Tablero, ai_state: AiState):
        """Elige y procesa el siguiente movimiento de la IA en el tablero."""
        row, col = None, None
        
        # 1. Modo objetivo (Target mode)
        while ai_state.ai_targets:
            r, c = ai_state.ai_targets.popleft()
            if (r, c) not in ai_state.ai_shots:
                row, col = r, c
                break
        
        # 2. Modo caza (Hunt mode)
        if row is None:
            row, col = self.ai_random_hunt_cell_for(ai_state, ai_state.ai_use_parity)
            if row is None:
                return None, None, "error", self._fmt("IA se quedó sin movimientos.")

        ai_state.ai_shots.add((row, col))
        result, message = self.process_shot_on(tablero, row, col)

        # 3. Actualización de estado
        if result == "hit" or result == "win":
            ai_state.ai_current_hits.append((row, col))
            ai_state.ai_hits.append((row, col))
            
            if result == "win":
                # Limpiar todo si el juego termina
                ai_state.ai_targets = collections.deque()
                ai_state.ai_current_hits = []
                # El barco actual se hundió
            
            elif len(ai_state.ai_current_hits) == 1:
                # Primer golpe, pasar a modo objetivo adyacente
                self.ai_enqueue_adjacent_for(ai_state, row, col)
            
            elif len(ai_state.ai_current_hits) >= 2:
                # Segundo golpe o más, extender la línea de ataque
                # Se limpia la cola antes de extender para priorizar la línea
                ai_state.ai_targets = collections.deque()
                self.ai_extend_line_from_hits_for(ai_state, row, col)

        elif result == "miss" or result == "repeat":
            pass

        # 4. Chequear si el barco actual se hundió
        if result == "hit":
            ai_state.ai_hits.append((row, col))
            ai_state.ai_current_hits.append((row, col))
            
            # ERROR LINE: Aquí estaba la llamada a is_game_over_at_cell
            if tablero.is_game_over():
                self.last_hit_win = (row, col)
                # Si el juego ha terminado, forzamos el resultado a "win"
                result = "win" 

        # Si no quedan targets, volvemos a modo Hunt
        if not ai_state.ai_targets:
            ai_state.ai_current_hits = []
        return (row, col, result, message)

    # ----------------------
    # Estado del juego
    # ----------------------
    def is_game_finished(self):
        if self.mode == 'solo':
            return self.is_game_finished_on(self.game_model)
        elif self.mode in ('hv', 'mm', 'hvh'):
            return self.tablero1.is_game_over() or self.tablero2.is_game_over()
        return False

    def is_game_finished_on(self, tablero):
        if tablero is None:
            return False
        return tablero.is_game_over() or tablero.has_run_out_of_tries()

    def get_winner(self):
        if self.mode == 'solo':
            return "Jugador" if self.game_model.is_game_over() else None
            
        elif self.mode == 'hv':
            if self.tablero1.is_game_over(): return "Máquina"
            elif self.tablero2.is_game_over(): return "Humano"
                
        elif self.mode == 'mm':
            # Asumiendo: Máquina B ataca T1, Máquina A ataca T2
            if self.tablero1.is_game_over(): return "Máquina B"
            elif self.tablero2.is_game_over(): return "Máquina A"
            
        elif self.mode == 'hvh':
            # Jugador 2 ataca T1, Jugador 1 ataca T2
            if self.tablero1.is_game_over(): return "Jugador 2" 
            elif self.tablero2.is_game_over(): return "Jugador 1" 
            
        return None

    # ----------------------
    # Utilidades
    # ----------------------
    def get_board_size(self):
        return self.board_size

    def get_tableros(self):
        return (self.tablero1, self.tablero2)

    def get_game_model(self):
        return self.game_model

    def get_last_winning_cell(self):
        """Retorna (row, col) de la casilla ganadora o None."""
        if self.last_hit_win:
            tablero, row, col = self.last_hit_win
            if tablero.is_game_over():
                return (row, col)
        return None
    
    def toggle_hints(self, board_id):
        """Alterna el estado de are_hints_shown en el tablero especificado."""
        tablero = None
        if board_id == 'game':
            tablero = self.game_model
        elif board_id == 't1':
            tablero = self.tablero1
        elif board_id == 't2':
            tablero = self.tablero2
            
        if tablero:
            tablero.are_hints_shown = not tablero.are_hints_shown
            return tablero.are_hints_shown
        return False
    
    def start_mm_game(self):
        """Inicializa el juego para el modo Máquina vs Máquina."""
        
        # 1. Configurar el modo y crear tableros
        self.mode = 'mm'
        self.tablero1 = Tablero(self.board_size) # Tablero para Máquina A (atacado por B)
        self.tablero2 = Tablero(self.board_size) # Tablero para Máquina B (atacado por A)
        
        # 2. Inicializar los estados de ambas IA
        # Nota: Asumimos que T1 es 'Máquina A' y T2 es 'Máquina B'
        self.ai_A = self.AiState(self.board_size) # Estado de la IA A (ataca T2)
        self.ai_B = self.AiState(self.board_size) # Estado de la IA B (ataca T1)
        
        # 3. Inicializar turno
        self.current_turn = 'A' # Máquina A siempre comienza
        self.last_hit_win = None
        # Limpiar el estado de la IA de Humano vs Máquina si es que existía
        self.ai_for_machine = None 