# Presentacion/presentacion.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QPushButton,
                               QSplitter, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from Controlador.controlador import WarShipController # Asegúrate de que esta ruta sea correcta

class WarShipGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BattleShip")
        self.setGeometry(100, 100, 1000, 800)
        
        # Agregar ícono a la ventana
        # NOTA: Cambia "Portrait WarShip.png" por la ruta correcta o asegúrate de que esté en el directorio de ejecución.
        self.setWindowIcon(QIcon("Portrait WarShip.png")) 

        self.controller = WarShipController(board_size=10)
        self.setup_styles()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Estado UI persistente: ("game"|"t1"|"t2", row, col) -> "hit"|"miss"|"win"
        self.ui_states = {}

        # Último movimiento: tuple (board_id, row, col, actor)
        self.last_move = None
        
        # Estado HvH
        self.is_hvh_switching = False # Bloquea clics durante la transición de turno
        self.current_visible_board = 1
        self.mode = 'solo'
        
        # AI Timer (si se usan otros modos)
        self.ai_timer = QTimer(self)
        self.ai_timer_interval_ms_default = 500
        self.ai_timer_interval_ms = self.ai_timer_interval_ms_default
        self.ai_timer.setInterval(self.ai_timer_interval_ms)
        self.ai_timer.timeout.connect(self.ai_step)
        self.ai_running = False
        self.ai_paused = False
        self.ai_speed_up = False

        self.create_home_view()
        self.create_mode_selection_view()
        self.create_game_view()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a202c;
                color: #e2e8f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #e2e8f0;
            }
            QPushButton {
                background-color: #4a5568;
                border: 2px solid #2d3748;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                min-width: 120px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2d3748;
            }
            QPushButton:pressed {
                background-color: #1a202c;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #a0aec0;
            }
            #titleLabel {
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #4299e1;
            }
            .board-button {
                background-color: #1a202c;
                border: 1px solid #4a5568;
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                padding: 0;
                font-size: 18px;
                font-weight: bold;
            }
            .board-button:hover {
                background-color: #2d3748;
            }
        """)

    def create_home_view(self):
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("BattleShip")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        start_button = QPushButton("Comenzar Juego")
        start_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        start_button.setStyleSheet("font-size: 32px; padding: 20px 40px; border-radius: 12px; background-color: #48bb78;")
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(home_widget)

    def create_mode_selection_view(self):
        mode_widget = QWidget()
        layout = QVBoxLayout(mode_widget)
        layout.setAlignment(Qt.AlignCenter)
        title_label = QLabel("Selecciona el modo de juego")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        solo_button = QPushButton("Jugar Solo")
        solo_button.clicked.connect(self.start_solo_game)
        solo_button.setStyleSheet("font-size: 28px; padding: 18px 36px; border-radius: 10px;")
        layout.addWidget(solo_button, alignment=Qt.AlignCenter)

        # --- BOTÓN HvH ---
        hvh_button = QPushButton("Humano vs Humano")
        hvh_button.clicked.connect(self.start_hvh_game)
        hvh_button.setStyleSheet("font-size: 28px; padding: 18px 36px; border-radius: 10px;")
        layout.addWidget(hvh_button, alignment=Qt.AlignCenter)

        hv_button = QPushButton("Humano vs Máquina")
        hv_button.clicked.connect(self.start_hv_game)
        hv_button.setStyleSheet("font-size: 28px; padding: 18px 36px; border-radius: 10px;")
        layout.addWidget(hv_button, alignment=Qt.AlignCenter)

        mm_button = QPushButton("Máquina vs Máquina")
        mm_button.clicked.connect(self.start_mm_game)
        mm_button.setStyleSheet("font-size: 28px; padding: 18px 36px; border-radius: 10px;")
        layout.addWidget(mm_button, alignment=Qt.AlignCenter)

        back_button = QPushButton("Volver al Inicio")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        back_button.setStyleSheet("font-size: 18px; padding: 10px; margin-top: 20px; background-color: #718096;")
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(mode_widget)

    def create_game_view(self):
        # AQUI COMIENZA LA DEFINICIÓN DE LA FUNCIÓN
        self.game_widget = QWidget()
        self.main_layout = QVBoxLayout(self.game_widget)

        # --------------------------------
        # 1. Barra superior con información
        # --------------------------------
        info_bar = QHBoxLayout()
        
        # INICIALIZACIÓN DE ETIQUETAS (CORRECCIÓN CLAVE)
        self.mode_label = QLabel("Modo: -")
        self.opponent_label = QLabel("Tablero: -")
        self.turn_label = QLabel("Turno: -")
        
        info_bar.addWidget(self.mode_label)
        info_bar.addStretch(1)
        info_bar.addWidget(self.opponent_label)
        info_bar.addStretch(1)
        info_bar.addWidget(self.turn_label)
        
        self.main_layout.addLayout(info_bar)

        # --------------------------------
        # 2. Area de Mensajes (CORRECCIÓN CLAVE)
        # --------------------------------
        self.message_label = QLabel("Mensaje del sistema.")
        self.message_label.setAlignment(Qt.AlignCenter)
        # Aplicamos el estilo para que se vea bien
        self.message_label.setStyleSheet("QLabel { padding: 10px; font-size: 18px; font-weight: bold; background-color: #2d3748; border-radius: 6px; }")
        self.main_layout.addWidget(self.message_label) 

        # --------------------------------
        # 3. Panel de tableros
        # --------------------------------
        self.board_panel = QWidget()
        self.board_panel_layout = QHBoxLayout(self.board_panel)
        self.main_layout.addWidget(self.board_panel)

        # Área del tablero (opponent_board_widget y layout)
        self.opponent_board_widget = QWidget()
        self.opponent_board_layout = QGridLayout(self.opponent_board_widget)
        self.opponent_board_layout.setSpacing(1)
        self.board_panel_layout.addWidget(self.opponent_board_widget, stretch=1)

        self.btn_toggle_view = QPushButton("Alternar Vista (T1/T2)")
        self.btn_toggle_view.clicked.connect(self.on_toggle_view_clicked)
        self.btn_toggle_view.setObjectName("btn_toggle_view")
        self.btn_toggle_view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # --------------------------------
        # 4. Botones de control
        # --------------------------------
        controls_layout = QHBoxLayout()

        self.btn_back_to_mode = QPushButton("Cambiar Modo")
        self.btn_back_to_mode.clicked.connect(self.back_to_mode_selection)
        controls_layout.addWidget(self.btn_back_to_mode)
        
        self.btn_toggle_view = QPushButton("Ver mi Tablero (T1)")
        self.btn_toggle_view.clicked.connect(self.toggle_view_my_board)
        self.btn_toggle_view.hide()
        controls_layout.addWidget(self.btn_toggle_view)

        self.btn_toggle_ai_boards = QPushButton("Alternar Tableros")
        self.btn_toggle_ai_boards.clicked.connect(self.toggle_ai_boards)
        self.btn_toggle_ai_boards.hide()
        controls_layout.addWidget(self.btn_toggle_ai_boards)
        
        # Botón Mostrar/Ocultar Barcos
        self.btn_show_ships = QPushButton("Mostrar Barcos")
        self.btn_show_ships.clicked.connect(self.on_show_ships_clicked)
        self.btn_show_ships.hide()
        controls_layout.addWidget(self.btn_show_ships)

        self.btn_pause_resume = QPushButton("Pausar IA")
        self.btn_pause_resume.clicked.connect(self.pause_resume_ai)
        self.btn_pause_resume.hide()
        controls_layout.addWidget(self.btn_pause_resume)

        self.btn_speed = QPushButton("Acelerar")
        self.btn_speed.clicked.connect(self.toggle_speed)
        self.btn_speed.hide()
        controls_layout.addWidget(self.btn_speed)
        
        self.btn_end_turn = QPushButton("Finalizar Turno")
        self.btn_end_turn.clicked.connect(self.toggle_player_turn_hvh)
        self.btn_end_turn.hide()
        controls_layout.addWidget(self.btn_end_turn)

        self.btn_restart = QPushButton("Volver a Jugar")
        self.btn_restart.clicked.connect(self.start_again_wrapper)
        self.btn_restart.hide()
        controls_layout.addWidget(self.btn_restart)

        self.main_layout.addLayout(controls_layout)
        self.stacked_widget.addWidget(self.game_widget)
            # AQUÍ TERMINA LA DEFINICIÓN DE LA FUNCIÓN
        
    # ... (Otros métodos como start_solo_game, on_opponent_cell_clicked, etc.) ...
    # ------------------------------------
    # Métodos de Inicio de Juego
    # ------------------------------------

    def start_solo_game(self):
        self.ai_timer.stop()
        self.mode = 'solo'
        self.controller.start_new_game()
        self.ui_states = {}
        self.last_move = None
        self.is_hvh_switching = False

        self.recreate_board_grid(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        self.show_board(1) 

        # OCULTAR TODOS LOS BOTONES NO NECESARIOS
        self.btn_pause_resume.hide()
        self.btn_speed.hide()
        self.btn_restart.hide()
        self.btn_toggle_view.hide()
        self.btn_toggle_ai_boards.hide()
        self.btn_end_turn.hide()

        # MOSTRAR BOTONES NECESARIOS
        self.btn_show_ships.show() # <-- Este botón debe estar visible
        
        # Resetear estado de hints
        self.btn_show_ships.setText("Mostrar Barcos")
        if self.controller.get_game_model():
            self.controller.get_game_model().are_hints_shown = False 

        self.mode_label.setText("Modo: Solo")
        self.opponent_label.setText("Tablero de Juego")
        self.turn_label.setText("Turno: Jugador")
        self.message_label.setText("Comienza el juego. ¡Buena suerte!")
        self.stacked_widget.setCurrentIndex(2)

    def start_mm_game(self):
        self.ai_timer.stop()
        self.mode = 'mm'
        self.controller.start_machine_vs_machine()
        self.ui_states = {}
        self.last_move = None
        self.is_hvh_switching = False
        self.ai_timer_interval_ms = self.ai_timer_interval_ms_default
        self.ai_timer.setInterval(self.ai_timer_interval_ms)
        self.btn_speed.setText("Acelerar")
        self.ai_speed_up = False

        self.recreate_board_grid(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        self.show_board(1) # Inicialmente se muestra el tablero A

        self.mode_label.setText("Modo: Máquina vs Máquina")
        self.opponent_label.setText("Tablero Máquina A (Ataca B)")
        self.message_label.setText("Máquina A comienza a atacar.")
        self.stacked_widget.setCurrentIndex(2)

        self.btn_pause_resume.show()
        self.btn_pause_resume.setText("Pausar IA")
        self.btn_speed.show()
        self.btn_restart.hide()
        self.btn_toggle_view.hide()
        self.btn_toggle_ai_boards.show()
        self.btn_end_turn.hide()

        self.ai_running = True
        self.ai_paused = False
        self.ai_timer.start(self.ai_timer_interval_ms)

    # ------------------------------------
    # INICIO Y LÓGICA HvH 
    # ------------------------------------
    def start_hvh_game(self):
        self.ai_timer.stop()
        self.mode = 'hvh'
        # ... (Otros inicializadores) ...
        self.current_visible_board = 2 # P1 atacará T2
        self.controller.start_hvh_game() # Asume que esto inicializa tableros y self.controller.current_turn = 'P1'
        
        self.recreate_board_grid(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        
        # Muestra el tablero T2, pero con los barcos ocultos (fase de transición)
        self.show_board(2, hvh_reveal_ships=False) 

        self.mode_label.setText("Modo: Humano vs Humano")
        self.opponent_label.setText("Turno: Jugador 1 (Ataca a Jugador 2)")
        self.turn_label.setText("Bloqueado: Pulse Comenzar") 
        self.message_label.setText("Pulsa 'Comenzar' para revelar el tablero de ataque.")
        self.stacked_widget.setCurrentIndex(2)

        # Configuración de botones:
        self.btn_pause_resume.hide()
        self.btn_speed.hide()
        self.btn_restart.hide()
        self.btn_toggle_view.hide()
        self.btn_toggle_ai_boards.hide()
        self.btn_show_ships.hide()
        
        # ------------------------------------------------
        # CORRECCIÓN CLAVE: Mostrar el botón de Comenzar
        # ------------------------------------------------
        self.btn_end_turn.setText("Comenzar")
        self.btn_end_turn.show() # <-- ¡DEBE ESTAR VISIBLE!

        # Desconectar cualquier señal anterior y conectar la acción de inicio
        try:
            self.btn_end_turn.clicked.disconnect()
        except TypeError:
            pass # Si no hay conexión previa, ignorar
        
        # Conectar al método que revela el tablero y empieza el turno real (P1 ataca T2)
        self.btn_end_turn.clicked.connect(lambda: self.reveal_hvh_board_and_start_turn(2))
        
        self.is_hvh_switching = True # Mantener el bloqueo de clics hasta que se pulse "Comenzar"
    
    def start_hv_game(self):
        """Inicializa el modo Humano vs Máquina."""
        self.ai_timer.stop()
        self.mode = 'hv'
        self.controller.start_human_vs_machine()
        self.ui_states = {}
        self.last_move = None
        self.is_hvh_switching = False
        self.ai_timer_interval_ms = self.ai_timer_interval_ms_default
        self.ai_timer.setInterval(self.ai_timer_interval_ms)
        self.btn_speed.setText("Acelerar")
        self.ai_speed_up = False

        self.recreate_board_grid(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        self.show_board(2) # Mostrar T2 (Máquina) para que el humano ataque

        # Actualización de Labels
        self.mode_label.setText("Modo: Humano vs Máquina")
        self.opponent_label.setText("Tablero Máquina (Enemigo)")
        self.turn_label.setText("Turno: Humano") 
        self.message_label.setText("Turno Humano: Dispara a la Máquina.")
        self.stacked_widget.setCurrentIndex(2)

        # Configuración de botones
        self.btn_pause_resume.show()
        self.btn_pause_resume.setText("Pausar IA")
        self.btn_speed.show()
        self.btn_restart.hide()
        self.btn_toggle_view.show() # Permite ver tu tablero (T1)
        self.btn_toggle_ai_boards.hide()
        self.btn_end_turn.hide()
        
        self.btn_show_ships.show() # <-- Mostrar para ver TU tablero T1
        if self.controller.tablero1:
            self.controller.tablero1.are_hints_shown = False # Resetear estado inicial

        self.ai_running = False
        self.ai_paused = False
        
        self.show_board(2) 

    def toggle_player_turn_hvh(self):
        """Prepara la interfaz para el cambio de turno (P1 <-> P2)."""
        if self.mode != 'hvh':
            return
        
        self.is_hvh_switching = True
        self.btn_end_turn.hide()
        
        # Limpiar y mostrar una pantalla de transición
        self.recreate_board_grid(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        
        # Lógica de cambio de turno
        if self.controller.current_turn == 'P1':
            self.controller.current_turn = 'P2'
            target_board_id = 1 # P2 ataca T1
            self.message_label.setText("¡CAMBIO DE TURNO! **Jugador 2**: Pulsa 'Continuar' cuando Jugador 1 se haya alejado.")
            self.opponent_label.setText("Tablero Oculto (Tablero 1 - Oponente)")
        else: # P2
            self.controller.current_turn = 'P1'
            target_board_id = 2 # P1 ataca T2
            self.message_label.setText("¡CAMBIO DE TURNO! **Jugador 1**: Pulsa 'Continuar' cuando Jugador 2 se haya alejado.")
            self.opponent_label.setText("Tablero Oculto (Tablero 2 - Oponente)")

        # Reconfigurar el botón de reanudar
        self.btn_end_turn.setText("Continuar")
        self.btn_end_turn.show()
        try: self.btn_end_turn.clicked.disconnect()
        except: pass
        self.btn_end_turn.clicked.connect(lambda: self.reveal_hvh_board_and_start_turn(target_board_id))

    def reveal_hvh_board_and_start_turn(self, target_board_id):
        """Muestra el tablero del oponente y desbloquea el juego para el nuevo turno."""
        
        # 1. Restablecer el botón a su función de alternar turno, pero lo ocultamos.
        try: self.btn_end_turn.clicked.disconnect()
        except: pass
        self.btn_end_turn.clicked.connect(self.toggle_player_turn_hvh)
        self.btn_end_turn.setText("Finalizar Turno")
        self.btn_end_turn.hide() 
        
        self.is_hvh_switching = False
        
        # 2. Mostrar el tablero a atacar (ocultando barcos)
        self.show_board(target_board_id, hvh_reveal_ships=False)
        
        # 3. Actualizar mensajes
        target_board = "Tablero 2" if self.controller.current_turn == 'P1' else "Tablero 1"
        self.opponent_label.setText(f"{target_board} (Ataca **{self.controller.current_turn}**)")
        self.message_label.setText(f"Turno de **{self.controller.current_turn}**: ¡Dispara al {target_board}!")

    # ------------------------------------
    # Lógica de Clics y Turnos
    # ------------------------------------
    def on_board_cell_clicked(self):
        button = self.sender()
        row, col = button.property("row"), button.property("col")

        # Bloqueos de seguridad
        if self.mode in ('hv','mm') and self.ai_running: return
        # Bloquea los clics durante la pantalla de transición de turno HvH
        if self.mode == 'hvh' and self.is_hvh_switching: 
            self.message_label.setText("Espera. Pulsa 'Continuar' para iniciar el turno.")
            return
        if button.property("state") in ("hit", "miss", "win"): return

        # --- Humano vs Humano ---
        if self.mode == 'hvh':
            
            if self.controller.current_turn == 'P1':
                tablero_obj = self.controller.tablero2
                board_id = "t2"
                actor = "Jugador 1"
                expected_visible_board = 2
            else:
                tablero_obj = self.controller.tablero1
                board_id = "t1"
                actor = "Jugador 2"
                expected_visible_board = 1
            
            # Verificar que se haga clic en el tablero correcto (el actualmente visible)
            if self.current_visible_board != expected_visible_board:
                self.message_label.setText(f"Error: {actor}, debes atacar el Tablero {expected_visible_board}.")
                return

            # Procesar el disparo
            result, message = self.controller.process_shot_on(tablero_obj, row, col)
            self.last_move = (board_id, row, col, actor)

            coord = f"{chr(ord('A') + row)}{col + 1}"
            full_msg = f"Turno de **{actor}**. Disparo en {coord}: {message}"
            self.message_label.setText(full_msg)

            # ----------------------------------------------------
            # CORRECCIÓN CLAVE: Usar el método de estilización unificado
            # ----------------------------------------------------
            state_result = "hit"
            if result == "win":
                state_result = "win"
            elif result == "miss":
                state_result = "miss"
            
            self.ui_states[(board_id, row, col)] = state_result
            self._update_button_style(button, state_result) # <-- Usa la función helper
            # ----------------------------------------------------

            # Chequear fin de juego
            if self.controller.is_game_finished():
                self.end_game_ui()
                return
            
            # CAMBIO DE TURNO AUTOMÁTICO después de 1 disparo.
            # Ocultamos el botón "Finalizar Turno" (que ahora es "Continuar" para la transición)
            self.btn_end_turn.hide() 
            self.toggle_player_turn_hvh()
            return

        # --- Modo Solo / Hv (Lógica existente) ---
        if self.mode == 'solo':
            result, message = self.controller.process_shot_on(self.controller.get_game_model(), row, col)
            
            board_id = "game"
            
            # Usamos el método de estilización unificado para Solo
            state_result = "hit"
            if result == "win":
                state_result = "win"
            elif result == "miss":
                state_result = "miss"

            self.ui_states[(board_id, row, col)] = state_result
            self._update_button_style(button, state_result)
            
            if self.controller.is_game_finished():
                self.end_game_ui()
                return
            return

        elif self.mode == 'hv':
            # Si el tablero visible no es el del oponente (T2), o no es tu turno, no dispares
            if self.controller.current_turn != 'human' or self.current_visible_board != 2:
                return
            tablero_obj = self.controller.tablero2
            result, message = self.controller.process_shot_on(tablero_obj, row, col)
            
            board_id = "t2"
            
            coord = f"{chr(ord('A') + row)}{col + 1}"
            full_msg = f"Tú disparaste en {coord}: {message}"
            self.message_label.setText(full_msg)

            # Usamos el método de estilización unificado para Hv
            state_result = "hit"
            if result == "win":
                state_result = "win"
            elif result == "miss":
                state_result = "miss"

            self.ui_states[(board_id, row, col)] = state_result
            self._update_button_style(button, state_result)

            if self.controller.is_game_finished():
                self.end_game_ui()
                return

            if result != 'win':
                self.controller.current_turn = 'machine'
                self.ai_running = True
                self.ai_paused = False
                self.ai_timer.start(self.ai_timer_interval_ms)
            return

    # ------------------------------------
    # AI/Helper Methods (MODIFICADO: start_again_wrapper)
    # ------------------------------------

    def on_show_ships_clicked(self):
        """Alterna la visualización de barcos en el tablero visible actualmente."""
        
        tablero = None
        board_id_key = None
        
        # 1. Determinar el modelo de tablero a modificar basado en el MODO y la VISTA ACTUAL
        if self.mode == 'solo':
            board_id_key = 'game'
            tablero = self.controller.get_game_model()
        elif self.mode in ('hv', 'mm', 'hvh'): # Modos de doble tablero
            if self.current_visible_board == 1:
                board_id_key = 't1'
                tablero = self.controller.tablero1
            elif self.current_visible_board == 2:
                board_id_key = 't2'
                tablero = self.controller.tablero2
        
        if tablero is None or board_id_key is None: 
            # Esto puede ocurrir si el juego está en modo "mm" pero no se ha iniciado, etc.
            return 

        # 2. Llama al controlador para cambiar el estado del modelo
        # (Esto invierte el valor de tablero.are_hints_shown)
        is_shown = self.controller.toggle_hints(board_id_key)
        
        # 3. Actualizar el texto del botón
        self.btn_show_ships.setText("Ocultar Barcos" if is_shown else "Mostrar Barcos")

        # 4. REDIBUJAR EL TABLERO
        # Forzamos la actualización de la vista actual. La lógica dentro de show_board 
        # se encargará de leer el nuevo estado de 'are_hints_shown' del modelo.
        # No usamos hvh_reveal_ships para que la lógica interna de 'show_board' se mantenga limpia.
        self.show_board(self.current_visible_board) 

    def start_again_wrapper(self):
        """Reinicia el juego actual en el mismo modo."""
        if self.mode == 'solo':
            self.start_solo_game()
        elif self.mode == 'hv':
            self.start_hv_game()
        elif self.mode == 'mm':
            self.start_mm_game()
        elif self.mode == 'hvh':
            self.start_hvh_game()
        else:
            self.back_to_mode_selection() # Caso de respaldo

    def back_to_mode_selection(self):
        self.ai_timer.stop()
        self.stacked_widget.setCurrentIndex(1)
        self.message_label.setText("Selecciona el modo de juego.")
        self.btn_restart.hide()

    def recreate_board_grid(self, size):
        if self.opponent_board_layout is None: return
        for i in reversed(range(self.opponent_board_layout.count())): 
            widget = self.opponent_board_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        for r in range(size):
            for c in range(size):
                button = QPushButton(" ")
                button.setObjectName("board-button")
                button.setProperty("row", r)
                button.setProperty("col", c)
                button.setProperty("state", None) 
                button.clicked.connect(self.on_board_cell_clicked)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.opponent_board_layout.addWidget(button, r, c)

    def reset_board_buttons_ui(self):
        for r in range(self.controller.get_board_size()):
            for c in range(self.controller.get_board_size()):
                item = self.opponent_board_layout.itemAtPosition(r, c)
                if item and item.widget() is not None:
                    button = item.widget()
                    button.setText(" ")
                    button.setProperty("state", None)
                    button.setEnabled(True)
                    button.setStyleSheet("")
                    button.style().polish(button)

    def toggle_view_my_board(self):
        if self.mode != 'hv': return
        
        if self.current_visible_board == 2:
            self.show_board(1)
            self.opponent_label.setText("Tu Tablero (T1)")
            self.message_label.setText("Turno Humano: Estás viendo tus barcos. Dispara a la Máquina.")
            self.btn_toggle_view.setText("Ver Tablero Oponente (T2)")
        else:
            self.show_board(2)
            self.opponent_label.setText("Tablero Máquina (Enemigo)")
            self.message_label.setText("Turno Humano: Dispara a la Máquina.")
            self.btn_toggle_view.setText("Ver mi Tablero (T1)")

    def toggle_ai_boards(self):
        if self.mode != 'mm': return
        
        if self.current_visible_board == 2:
            self.show_board(1)
            self.opponent_label.setText("Tablero Máquina A (Ataca B)")
        else:
            self.show_board(2)
            self.opponent_label.setText("Tablero Máquina B (Ataca A)")
        
        turn = self.controller.current_turn
        self.message_label.setText(f"Turno de Máquina {turn}. Pulsa 'Pausar' para detener.")

    def pause_resume_ai(self):
        if self.ai_running and not self.ai_paused:
            self.ai_timer.stop()
            self.ai_paused = True
            self.btn_pause_resume.setText("Reanudar IA")
            self.message_label.setText("Juego Pausado.")
        elif self.ai_running and self.ai_paused:
            self.ai_timer.start(self.ai_timer_interval_ms)
            self.ai_paused = False
            self.btn_pause_resume.setText("Pausar IA")
            turn = self.controller.current_turn
            self.message_label.setText(f"Turno de Máquina {turn}.")

    def toggle_speed(self):
        if self.ai_speed_up:
            self.ai_timer_interval_ms = self.ai_timer_interval_ms_default
            self.btn_speed.setText("Acelerar")
            self.ai_speed_up = False
        else:
            self.ai_timer_interval_ms = 50 
            self.btn_speed.setText("Normal")
            self.ai_speed_up = True
        
        if self.ai_running and not self.ai_paused:
            self.ai_timer.setInterval(self.ai_timer_interval_ms)

    def ai_step(self):
        """
        Ejecuta un paso de la Inteligencia Artificial. 
        Maneja la lógica de turno y el flujo para los modos HV y MM.
        """
        if self.ai_paused:
            return

        # ----------------------------------------------------
        # 1. DETERMINAR ATACANTE Y OBJETIVO
        # ----------------------------------------------------
        board_to_attack = None
        ai_state = None
        current_actor = ""
        board_id = 0 
        next_turn = None
        
        # Lógica para el modo Humano vs Máquina (HV)
        if self.controller.mode == 'hv':
            current_actor = "Máquina"
            board_to_attack = self.controller.tablero1 # Máquina ataca al Humano (T1)
            ai_state = self.controller.ai_for_machine
            board_id = 1
            next_turn = 'human'
            
        # Lógica para el modo Máquina vs Máquina (MM)
        elif self.controller.mode == 'mm':
            if self.controller.current_turn == 'A':
                current_actor = "Máquina A"
                board_to_attack = self.controller.tablero2 # A ataca a B (T2)
                ai_state = self.controller.ai_A
                board_id = 2
                next_turn = 'B'
            else: # self.controller.current_turn == 'B'
                current_actor = "Máquina B"
                board_to_attack = self.controller.tablero1 # B ataca a A (T1)
                ai_state = self.controller.ai_B
                board_id = 1
                next_turn = 'A'
        else:
            # Modo no compatible o no inicializado (detener por seguridad)
            self.ai_timer.stop()
            self.ai_running = False
            return 

        # ----------------------------------------------------
        # 2. EJECUTAR EL MOVIMIENTO
        # ----------------------------------------------------
        
        result_tuple = self.controller.ai_make_move_on(board_to_attack, ai_state)
        row, col, result, message = result_tuple

        if row is None or col is None:
            self.message_label.setText(f"Error de IA ({current_actor}): Jugada no válida. Cediendo turno.")
        else:
            coord = f"{chr(ord('A') + row)}{col + 1}"
            full_msg = f"Turno {current_actor}. Disparo en {coord}: {message}"
            self.message_label.setText(full_msg)

            # 3. ACTUALIZAR LA INTERFAZ
            button = self.get_button_by_coords(board_id, row, col)
            
            # Solo actualiza la UI si estamos viendo el tablero atacado
            if self.current_visible_board == board_id:
                # Nota: Asumimos que tienes el método _update_button_style(button, result)
                self._update_button_style(button, result)
        
        # ----------------------------------------------------
        # 4. CHEQUEAR FIN DE JUEGO
        # ----------------------------------------------------
        if self.controller.is_game_finished():
            self.ai_timer.stop()
            self.ai_running = False
            self.end_game_ui()
            return
        
        # ----------------------------------------------------
        # 5. CAMBIO DE TURNO Y CONTROL DE FLUJO
        # ----------------------------------------------------
        self.ai_timer.stop() # Siempre detenemos el timer después de un disparo único
        self.controller.current_turn = next_turn
        
        if self.controller.mode == 'hv':
            # HV: Cede el control al Humano. El timer permanece detenido.
            self.ai_running = False 
            self.turn_label.setText("Turno: Humano")
            self.message_label.setText("Tu turno. ¡Dispara!")
            
        elif self.controller.mode == 'mm':
            # MM: Cede a la otra máquina y REINICIA el timer inmediatamente para el siguiente turno.
            self.turn_label.setText(f"Turno: Máquina {next_turn}")
            self.message_label.setText(f"Turno de {current_actor} finalizado. Máquina {next_turn} ataca...")
            
            # Iniciar el ciclo del siguiente turno de la IA
            self.ai_timer.start(self.ai_timer_interval_ms) 
            self.ai_running = True

    # ----------------------------------------------------

    def determine_winner_text(self):
        if self.mode == 'solo':
            if self.controller.get_game_model() and self.controller.get_game_model().is_game_over():
                return "Jugador"
            return None
        elif self.mode == 'hv':
            if self.controller.tablero1 and self.controller.tablero1.is_game_over():
                return "Humano"
            if self.controller.tablero2 and self.controller.tablero2.is_game_over():
                return "Máquina"
            return None
        elif self.mode == 'mm':
            if self.controller.tablero1 and self.controller.tablero1.is_game_over():
                return "Máquina B"
            if self.controller.tablero2 and self.controller.tablero2.is_game_over():
                return "Máquina A"
            return None
        elif self.mode == 'hvh':
            if self.controller.tablero1 and self.controller.tablero1.is_game_over():
                return "Jugador 2" 
            if self.controller.tablero2 and self.controller.tablero2.is_game_over():
                return "Jugador 1" 
            return None
        return None

    def end_game_ui(self):
        self.ai_timer.stop()
        self.ai_running = False
        self.ai_paused = False
        self.btn_end_turn.hide()

        winner = self.determine_winner_text()
        if winner:
            self.message_label.setText(f"¡Partida finalizada! **Ganador: {winner}**")
        else:
            self.message_label.setText("¡Partida finalizada! Empate.")

        winning_cell = self.controller.get_last_winning_cell()
        
        if winning_cell:
            row, col = winning_cell
            
            if self.mode == 'solo':
                board_num = 1
                board_id = "game"
            elif self.mode in ('hv', 'mm', 'hvh'):
                board_num = 1 if self.controller.tablero1.is_game_over() else 2
                board_id = "t1" if board_num == 1 else "t2"
                
            self.ui_states[(board_id, row, col)] = "win"

            self.show_board(board_num, hvh_reveal_ships=True)

        # Controles finales (Volver a Jugar y Cambiar Modo)
        self.btn_restart.show()
        # btn_back_to_mode (Cambiar Modo) está visible por defecto en el layout
        self.btn_speed.hide()
        self.btn_toggle_view.hide()
        self.btn_toggle_ai_boards.hide()

        try: self.btn_restart.clicked.disconnect()
        except TypeError: pass
        
        if self.mode == 'solo':
            self.btn_restart.clicked.connect(self.restart_solo_game)
        elif self.mode == 'hvh':
            self.btn_restart.clicked.connect(self.restart_hvh_game)
        elif self.mode == 'hv':
            self.btn_restart.clicked.connect(self.restart_hv_game)
        elif self.mode == 'mm':
            self.btn_restart.clicked.connect(self.restart_mm_game)
        else:
            # Si el modo no está reconocido, simplemente llevar a la selección de modo
            self.btn_restart.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    # ------------------------------------
    # UI Helpers
    # ------------------------------------
    def show_board(self, board_id, hvh_reveal_ships=False): 
        
        # ... (código para determinar tablero_obj y board_id_key) ...
        if board_id == 1:
            tablero_obj = self.controller.tablero1 if self.mode != 'solo' else self.controller.get_game_model()
            board_id_key = "t1" if self.mode != 'solo' else "game"
        else: # board_id == 2
            tablero_obj = self.controller.tablero2
            board_id_key = "t2"
            
        self.current_visible_board = board_id

        if tablero_obj is None: return

        # -----------------------------------------------------------
        # Lógica de Visibilidad de Barcos (Corrección Clave)
        # -----------------------------------------------------------
        if self.mode == 'hvh':
            # En HvH, ocultar barcos SI es un tablero enemigo (implícito) Y NO estamos en fase de revelación
            hide_ships = not hvh_reveal_ships 
        else:
            # En modos 'solo' y 'hv', ocultar barcos SI el modelo dice que *no* se muestren los hints
            hide_ships = not tablero_obj.are_hints_shown # <--- Usa el estado del modelo
        # -----------------------------------------------------------
            
        self.refresh_board_ui_for_tablero(tablero_obj, board_id=board_id_key, hvh_hide_ships=hide_ships)

    def refresh_board_ui_for_tablero(self, tablero, board_id="t1", hvh_hide_ships=False):
        if tablero is None: return
        
        # Determinar si se deben mostrar los barcos no impactados.
        # Esto ocurre si:
        # 1. El estado del modelo lo permite (tablero.are_hints_shown)
        # 2. El juego ha terminado (self.controller.is_game_finished())
        # 3. NO estamos en modo de transición HvH (not hvh_hide_ships)
        
        # La visibilidad del barco se basa en el estado del botón (tablero.are_hints_shown) 
        # O en la condición de fin de juego/transición de vista.
        should_show_ships = tablero.are_hints_shown or not hvh_hide_ships

        # EXCEPCIÓN: Si estamos viendo un tablero enemigo y el juego NO ha terminado,
        # siempre ocultamos los barcos, independientemente del estado del botón (que está oculto de todas formas).
        if board_id != 'game' and self.current_visible_board != 1 and not self.controller.is_game_finished():
            should_show_ships = False
        
        
        for row in range(self.controller.get_board_size()):
            for col in range(self.controller.get_board_size()):
                item = self.opponent_board_layout.itemAtPosition(row, col)
                if not item: continue
                button = item.widget()

                key = (board_id, row, col)
                
                # 1. ESTADO PERSISTENTE (hit/miss/win ya aplicado)
                if key in self.ui_states:
                    self._update_button_style(button, self.ui_states[key])
                    continue
                
                # 2. ESTADO EN EL MODELO (Barco golpeado o fallado) - Esto tiene prioridad
                if (row, col) in tablero.plays:
                    if tablero.is_ship_at(row, col):
                        self._update_button_style(button, "hit")
                    else:
                        self._update_button_style(button, "miss")
                # 3. BARCOS NO GOLPEADOS (Ahora usa should_show_ships)
                elif should_show_ships and tablero.is_ship_at(row, col):
                    self._update_button_style(button, "ship")
                # 4. AGUA (Por defecto)
                else:
                    self._update_button_style(button, None)

        # La visibilidad del botón de pistas se manejará en los métodos start_xxx_game y toggle_view_my_board.
        # Aquí aseguramos que el texto esté correcto si ya está visible:
        if self.btn_show_ships.isVisible():
            self.btn_show_ships.setText("Ocultar Barcos" if tablero and tablero.are_hints_shown else "Mostrar Barcos")
# En Presentacion/presentacion.py (Dentro de la clase WarShipGame)

# ... (Colócalo en la sección de métodos de utilidad/helper methods) ...

    def _update_button_style(self, button, state):
        """
        Aplica estilos al botón de la cuadrícula basado en su estado de juego.
        Estados posibles: None (agua), 'ship' (barco no golpeado), 'hit', 'miss', 'win'.
        """
        # Asegurarse de que el botón está habilitado por defecto y el texto se borra
        button.setEnabled(True)
        button.setText(" ")
        
        # Estilos base (agua/no jugado)
        base_style = "background-color: #1a202c; border: 1px solid #4a5568;"
        
        if state is None or state == 'water':
            # Estado base (agua/no jugado)
            button.setStyleSheet(base_style)
            button.setProperty("state", None)

        elif state == 'ship':
            # Barco no golpeado (usado para hints o fin de juego)
            button.setText("B")
            button.setStyleSheet("background-color: #38a169; color: white; border: 1px solid #2d3748;")
            button.setProperty("state", "ship")
            # En modos de hint, el botón debe estar deshabilitado para evitar disparar donde ya se sabe que hay barco.
            button.setEnabled(False) 
            
        elif state == 'hit':
            # Impacto (Hit)
            button.setText("O")
            button.setStyleSheet("background-color: #e53e3e; color: white; border: 1px solid #2d3748;")
            button.setProperty("state", "hit")
            button.setEnabled(False)

        elif state == 'miss':
            # Fallo (Miss)
            button.setText("X")
            button.setStyleSheet("background-color: #a0aec0; color: #1a202c; border: 1px solid #2d3748;")
            button.setProperty("state", "miss")
            button.setEnabled(False)

        elif state == 'win':
            # Impacto final (Win/Hundido completo) - Color especial para destacar
            button.setText("O")
            button.setStyleSheet("background-color: #6F00FF; color: white; border: 2px solid #fff;")
            button.setProperty("state", "win")
            button.setEnabled(False)

        # Aplicar el nuevo estilo al widget
        button.style().polish(button)

    def _reset_ui_state(self):
        """Función auxiliar para limpiar los estados persistentes de la interfaz."""
        self.ui_states = {} 
        self.last_move = None
        self.is_hvh_switching = False
        self.btn_restart.hide() # Ocultar el botón de Reinicio al terminar la limpieza

    def restart_solo_game(self):
        """Reinicia el estado de la interfaz y el controlador para el modo SOLO."""
        self._reset_ui_state()
        self.start_solo_game()

    def restart_hv_game(self):
        """Reinicia el estado de la interfaz y el controlador para el modo HV (Humano vs Máquina)."""
        self._reset_ui_state()
        self.start_hv_game()
    
    def restart_hvh_game(self):
        """Reinicia el estado de la interfaz y el controlador para el modo HVH (Humano vs Humano)."""
        self._reset_ui_state()
        self.start_hvh_game()

    def restart_mm_game(self):
        """Reinicia el estado de la interfaz y el controlador para el modo MM (Máquina vs Máquina)."""
        # Nota: El modo MM usualmente no tiene un botón 'Jugar de nuevo',
        # pero es bueno tener la función por si acaso.
        self._reset_ui_state()
        self.start_mm_game()
        self.btn_pause_resume.setText("Iniciar IA") # Asegura que la IA esté detenida

    def on_toggle_view_clicked(self):
        """Alterna entre la vista del tablero propio (T1) y el del oponente (T2).
        Solo se usa en los modos 'hv' (Humano vs Máquina) y 'mm' (Máquina vs Máquina)."""
        
        # Debe estar en modos donde se usan dos tableros separados
        if self.mode not in ('hv', 'mm'):
            return

        # 1. Determinar el ID del tablero que se debe mostrar
        # Si actualmente ves T2, cambia a T1, y viceversa.
        new_board_id = 1 if self.current_visible_board == 2 else 2
        
        # 2. Llamar a show_board para redibujar la vista
        # Esto actualiza self.current_visible_board
        self.show_board(new_board_id) 

        # 3. Obtener el modelo del nuevo tablero visible para actualizar las etiquetas/botones
        tablero_obj = self.controller.tablero1 if new_board_id == 1 else self.controller.tablero2

        # 4. Actualizar las etiquetas de la interfaz
        if new_board_id == 1:
            self.opponent_label.setText("Tu Tablero (Defensa)")
            self.message_label.setText("Viendo tu tablero. Pulsa 'Alternar Vista' para volver a atacar.")
        else: # new_board_id == 2 (Máquina)
            self.opponent_label.setText("Tablero Máquina (Enemigo)")
            # Mostrar mensaje de turno si es modo 'hv' y es turno del humano
            if self.mode == 'hv' and self.controller.current_turn == 'human':
                self.message_label.setText("Turno Humano: Dispara a la Máquina.")
            else:
                self.message_label.setText("Viendo tablero enemigo.")
        
        # ----------------------------------------------------
        # CORRECCIÓN CLAVE: Sincronizar el botón de Hints (Mostrar/Ocultar Barcos)
        # ----------------------------------------------------
        if tablero_obj:
            # Sincronizar el texto del botón de hints con el estado del nuevo tablero
            is_shown = tablero_obj.are_hints_shown
            self.btn_show_ships.setText("Ocultar Barcos" if is_shown else "Mostrar Barcos")
        
        # Otros controles visuales (solo para Hv o MM)
        self.btn_end_turn.hide()

    def get_button_by_coords(self, board_id, row, col):
        """
        Retorna el botón de la cuadrícula en las coordenadas (row, col).
        Asume que todos los botones se encuentran en self.opponent_board_layout.
        """
        # Nota: La lógica real es que board_id se usa para seleccionar el layout si hubiese dos, 
        # pero como solo usas uno (opponent_board_layout), ignoramos board_id aquí.
        if self.opponent_board_layout:
            item = self.opponent_board_layout.itemAtPosition(row, col)
            if item:
                return item.widget()
        return None

# ... (Otros métodos de la clase WarShipGame) ...

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WarShipGame()
    win.show()
    sys.exit(app.exec())