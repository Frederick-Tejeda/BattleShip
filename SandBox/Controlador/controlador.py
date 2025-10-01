# Controlador/controlador.py
import random
import collections
from Entidad.entidad import Tablero

class WarShipController:
    """
    Clase que maneja la lógica de negocio y el estado del juego.
    Incluye lógica para el modo 'máquina' (IA) mejorada.
    """
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.game_model = None

        # --- AI state ---
        self.ai_active = False
        self.ai_shots = set()            # celdas disparadas por la IA {(r,c),...}
        self.ai_targets = collections.deque()  # cola de objetivos por explorar (target mode)
        self.ai_hits = []                # lista de hits históricos (opcional)
        self.ai_current_hits = []        # hits del barco actual que estamos persiguiendo (cluster)
        # parity heuristic (mejor cobertura) -> True usa (r+c)%2==0
        self.ai_use_parity = True

    def start_new_game(self):
        """Inicializa un nuevo modelo de juego."""
        self.game_model = Tablero(self.board_size)
        # Reset AI al iniciar
        self.ai_reset()
        return self.game_model

    # -----------------------
    # Juego humano (existente)
    # -----------------------
    def process_shot(self, row, col):
        """
        Procesa un disparo en la coordenada (row, col).
        Retorna: (resultado, mensaje) donde resultado es "hit" o "miss" o "error".
        Los mensajes se devuelven como HTML con font-size aumentado en 150%.
        """

        def _fmt(text: str) -> str:
            # Envuelve el texto en HTML para que QLabel lo renderice con tamaño aumentado (50% más).
            # Puedes ajustar '150%' si quieres otro incremento.
            return f'<span style="font-size:150%;">{text}</span>'

        if not self.game_model:
            return "error", _fmt("El juego no ha sido inicializado.")

        # no permitir disparar dos veces (control en UI pero doble-check)
        if (row, col) in self.game_model.plays:
            return "repeat", _fmt("Ya disparaste en esa posición.")

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
            return "hit", _fmt(message)
        else:
            if self.game_model.has_run_out_of_tries():
                message = "Juego terminado ✅"
            elif self.game_model.is_game_over():
                message = "¡Felicidades! ¡Has hundido todos los barcos!"
            else:
                message = "¡Fallaste!"
            return "miss", _fmt(message)


    def is_game_finished(self):
        """Verifica si el juego ha finalizado por victoria o por intentos agotados."""
        if not self.game_model:
            return False
        return self.game_model.is_game_over() or self.game_model.has_run_out_of_tries()

    def get_board_size(self):
        """Obtiene el tamaño del tablero."""
        return self.board_size

    # -----------------------
    # Lógica AI / Máquina mejorada
    # -----------------------
    def ai_reset(self):
        """Reinicia la memoria interna de la IA."""
        self.ai_active = False
        self.ai_shots = set()
        self.ai_targets = collections.deque()
        self.ai_hits = []
        self.ai_current_hits = []

    def ai_start(self):
        """Activa la IA (preparación)."""
        self.ai_active = True
        self.ai_reset()

    def ai_neighbors(self, r, c):
        """Vecinos ortogonales válidos (no diagonales)."""
        res = []
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            if 0 <= rr < self.board_size and 0 <= cc < self.board_size:
                res.append((rr, cc))
        return res

    def ai_random_hunt_cell(self):
        """
        Escoge una celda aleatoria que no haya sido probada.
        Aplica 'parity' si está activada para mejorar eficiencia (checkerboard).
        """
        candidates = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) in self.ai_shots or (r, c) in self.game_model.plays:
                    continue
                if self.ai_use_parity:
                    if (r + c) % 2 == 0:
                        candidates.append((r, c))
                else:
                    candidates.append((r, c))

        if not candidates and self.ai_use_parity:
            # fallback: usar todas las celdas no probadas
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if (r, c) in self.ai_shots or (r, c) in self.game_model.plays:
                        continue
                    candidates.append((r, c))

        if not candidates:
            return None
        return random.choice(candidates)

    def ai_enqueue_adjacent(self, r, c):
        """Agrega vecinos válidos a la cola de objetivos si no han sido probados (prioridad alta)."""
        for nbr in self.ai_neighbors(r, c):
            if nbr not in self.ai_shots and nbr not in self.game_model.plays and nbr not in self.ai_targets:
                # agregar con prioridad delante
                self.ai_targets.appendleft(nbr)

    def ai_extend_line_from_hits(self):
        """
        Si hay >=2 hits en ai_current_hits, detecta orientación y encola
        la extensión en ambos extremos (prioridad alta).
        """
        if len(self.ai_current_hits) < 2:
            return

        # Detectar orientación: si los hits comparten fila -> horizontal, si comparten col -> vertical
        rows = {r for (r, c) in self.ai_current_hits}
        cols = {c for (r, c) in self.ai_current_hits}

        orientation = None
        if len(rows) == 1 and len(cols) >= 2:
            orientation = 'H'
            r = next(iter(rows))
            minc = min(c for (_, c) in self.ai_current_hits)
            maxc = max(c for (_, c) in self.ai_current_hits)
            candidates = [(r, maxc + 1), (r, minc - 1)]
        elif len(cols) == 1 and len(rows) >= 2:
            orientation = 'V'
            c = next(iter(cols))
            minr = min(r for (r, _) in self.ai_current_hits)
            maxr = max(r for (r, _) in self.ai_current_hits)
            candidates = [(maxr + 1, c), (minr - 1, c)]
        else:
            # sin orientación clara (p. ej. hits aislados no alineados), encolar vecinos del último hit
            last = self.ai_current_hits[-1]
            self.ai_enqueue_adjacent(last[0], last[1])
            return

        # Encolar candidatos válidos (prioridad alta)
        for cand in candidates:
            rr, cc = cand
            if 0 <= rr < self.board_size and 0 <= cc < self.board_size:
                if cand not in self.ai_shots and cand not in self.game_model.plays and cand not in self.ai_targets:
                    self.ai_targets.appendleft(cand)

    def ai_make_move(self):
        """
        Ejecuta un movimiento de la IA: selecciona celda, llama a process_shot y actualiza memoria AI.
        Retorna (row, col, result, message).
        """
        if not self.game_model:
            return None

        # elegir celda: si hay objetivos en cola (target mode), tomar de ahí, si no -> hunt
        if self.ai_targets:
            row, col = self.ai_targets.popleft()
        else:
            cell = self.ai_random_hunt_cell()
            if cell is None:
                # ninguna celda disponible
                return None
            row, col = cell

        # marcar tiro (localmente) antes de procesar para evitar duplicados
        self.ai_shots.add((row, col))
        # procesar tiro usando la lógica existente
        result, message = self.process_shot(row, col)

        # si se repite (ya jugado), tratar de escoger otra (edge-case)
        if result == "repeat":
            return self.ai_make_move()

        # Si hit -> registrar y añadir vecinos a la cola (y tratar orientación)
        if result == "hit":
            # registrar hit histórico y en cluster actual
            self.ai_hits.append((row, col))
            self.ai_current_hits.append((row, col))

            if len(self.ai_current_hits) == 1:
                # primer hit: encolar vecinos inmediatos con alta prioridad
                self.ai_enqueue_adjacent(row, col)
            else:
                # hay >=2 hits: intentar encontrar orientación y extender la línea
                self.ai_extend_line_from_hits()

        else:  # miss
            # si estamos en target mode y no quedan objetivos, resetear cluster actual
            if not self.ai_targets:
                self.ai_current_hits = []

        return (row, col, result, message)
