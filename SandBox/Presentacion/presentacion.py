import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                               QSplitter, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt
from Controlador.controlador import WarShipController 

class WarShipGame(QMainWindow):
    """
    Clase de Presentación (Vista). Maneja la UI y las interacciones del usuario.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WarShip")
        self.setGeometry(100, 100, 1000, 800)
        
        # Instancia del Controlador (Inicialización sin juego activo)
        self.controller = WarShipController(board_size=10)
        
        self.setup_styles()
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_home_view()
        self.create_mode_selection_view()
        self.create_game_view() # Crea la vista de juego y el botón de pistas/reinicio

    def setup_styles(self):
        """Define los estilos CSS (QSS) de la aplicación."""
        self.setStyleSheet("""
            QWidget { background-color: #f0f4f8; color: #333; font-family: Arial, sans-serif; }
            QMainWindow { background-color: #f0f4f8; }
            QLabel#titleLabel { font-size: 32px; font-weight: bold; color: #1a202c; margin: 0 0 15px 0; }
            QLabel#messageLabel { font-size: 22px; font-style: italic; color: #4a5568; margin: 0 0 8px 0; }
            QPushButton { background-color: #2b6cb0; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 18px; }
            QPushButton:hover { background-color: #2c5282; }
            QPushButton:disabled { background-color: #a0aec0; color: #666; }
         
            QWidget#opponentBoardWidget { background-color: #0A497B; border: 2px solid #c0c0c0; border-radius: 8px; }
            QLabel#opponentLabel { font-size: 20px; font-weight: bold; color: #2d3748; margin: 0 0 10px 0; }

            .boardButton {
                background-color: #0A497B;
                border: 2px solid #ffffff;
                border-radius: 4px;
                margin: 0;
            }
            .boardButton[hit="true"] { background-color: #e53e3e; }
            .boardButton[miss="true"] { background-color: #a0aec0; }
            /* Estilos para las pistas */
            .boardButton[hint="ship"] { background-color: #38a169; color: white; }
            .boardButton[hint="water"] { background-color: #4299e1; color: white; }
        """)

    def create_home_view(self):
        """Crea la vista de bienvenida."""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("BattleShip")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        description_label = QLabel("Bienvenido al juego clásico de BattleShip. \n¡Destruye todos los barcos del tablero enemigo para ganar!")
        description_label.setObjectName("messageLabel")
        description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)

        play_button = QPushButton("Jugar")
        play_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(play_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(home_widget)
    
    def create_mode_selection_view(self):
        """Crea la vista de selección de modo de juego."""
        mode_widget = QWidget()
        layout = QVBoxLayout(mode_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Selecciona el modo de juego")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        solo_button = QPushButton("Jugar Solo")
        solo_button.clicked.connect(self.start_solo_game)
        layout.addWidget(solo_button, alignment=Qt.AlignCenter)

        ai_button = QPushButton("Jugar Automático (Próximamente)")
        layout.addWidget(ai_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(mode_widget)

    def create_game_view(self):
        """Crea la vista principal del juego con los tableros."""
        self.game_widget = QWidget()
        self.main_layout = QVBoxLayout(self.game_widget)

        # Labels de título y mensaje
        self.title_label = QLabel("BattleShip")
        self.title_label.setObjectName("titleLabel")
        self.main_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        
        self.message_label = QLabel("¡Es tu turno! Haz clic en una casilla para disparar.")
        self.message_label.setObjectName("messageLabel")
        self.main_layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        # QSplitter para los tableros (ocultamos el tablero del jugador en modo solo)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.main_layout.addWidget(self.splitter)
        
        # Contenedor del Tablero del Jugador (Oculto en modo solo)
        self.player_container = QWidget()
        self.player_layout = QVBoxLayout(self.player_container)
        self.player_label = QLabel("Tu Tablero")
        self.player_label.setObjectName("playerLabel")
        self.player_layout.addWidget(self.player_label, alignment=Qt.AlignCenter)
        self.player_board_widget = QWidget()
        self.player_board_widget.setObjectName("playerBoardWidget")
        self.player_board_layout = QGridLayout(self.player_board_widget)
        self.player_layout.addWidget(self.player_board_widget)
        self.splitter.addWidget(self.player_container)
        self.player_container.hide() # Lo ocultamos por defecto

        # Contenedor del Tablero Enemigo (interactivo)
        self.opponent_container = QWidget()
        self.opponent_layout = QVBoxLayout(self.opponent_container)
        self.opponent_label = QLabel("Tablero Enemigo")
        self.opponent_label.setObjectName("opponentLabel")
        self.opponent_layout.addWidget(self.opponent_label, alignment=Qt.AlignCenter)
        self.opponent_board_widget = QWidget()
        self.opponent_board_widget.setObjectName("opponentBoardWidget")
        self.opponent_board_layout = QGridLayout(self.opponent_board_widget)
        self.opponent_layout.addWidget(self.opponent_board_widget)
        self.splitter.addWidget(self.opponent_container)
        
        self.stacked_widget.addWidget(self.game_widget)
        
        # Botón de Pistas / Reinicio (creado una sola vez)
        self.show_hints = QPushButton("Mostrar Pistas")
        self.show_hints.clicked.connect(self.show_hints_to_user)
        self.main_layout.addWidget(self.show_hints, alignment=Qt.AlignCenter)
        self.show_hints.hide() # Oculto hasta que inicie el juego

    def start_solo_game(self):
        """
        Inicializa el juego, genera nuevos barcos en el controlador
        y configura la vista de juego.
        """
        # Inicializa un juego nuevo (genera nuevos barcos en el Tablero)
        self.controller.start_new_game()
        
        # Inicializa o refresca los botones del tablero (crea si no existen)
        self.init_opponent_board(self.controller.get_board_size())
        
        self.message_label.setText("¡Es tu turno! Haz clic en una casilla para disparar.")
        
        # Configurar y mostrar el botón de Pistas/Reinicio
        # Restablecemos la conexión al modo 'Mostrar Pistas'
        try:
            self.show_hints.clicked.disconnect()
        except TypeError:
             pass 
             
        self.show_hints.clicked.connect(self.show_hints_to_user)
        self.show_hints.setText("Mostrar Pistas")
        self.show_hints.setEnabled(True)
        self.show_hints.show() # Mostrar el botón de pistas
        
        # Asegurarse de que solo se muestre el tablero enemigo
        self.player_container.hide()
        self.stacked_widget.setCurrentIndex(2)

    def start_again(self):
        """
        Reinicia completamente el estado del juego y la interfaz.
        """
        # 1. Resetear el juego en el Controlador (genera nuevos barcos)
        self.controller.start_new_game()

        # 2. Reiniciar la interfaz (botones)
        for i in range(self.opponent_board_layout.count()):
            button = self.opponent_board_layout.itemAt(i).widget()
            button.setText(" ")
            button.setStyleSheet("") # Limpiar QSS específicos (hit/miss)
            button.setProperty("state", None)
            button.setProperty("content", None)
            button.setProperty("hint", None)
            button.setEnabled(True) # <--- SOLUCIÓN: Habilitar el botón
            button.style().polish(button) # Reaplicar estilos base
            
        # 3. Restablecer el botón de Pistas
        self.message_label.setText("¡Es tu turno! Haz clic en una casilla para disparar.")
        self.show_hints.setText("Mostrar Pistas")
        
        # Reconectar al modo 'Mostrar Pistas'
        try:
            self.show_hints.clicked.disconnect()
        except TypeError:
             pass 
             
        self.show_hints.clicked.connect(self.show_hints_to_user)

    def show_hints_to_user(self):
        """
        Muestra u oculta las pistas de los barcos en el tablero enemigo.
        Si el juego terminó, este botón debe ser el que reinicie (manejo delegado al final).
        """
        # Lógica para mostrar/ocultar pistas
        current_state = self.controller.game_model.are_hints_shown
        # Si current_state es True, se pone a False. Si es False o no existe, se pone a True.
        new_state = not current_state if current_state is not None else True
        self.controller.game_model.are_hints_shown = new_state
        
        self.show_hints.setText(new_state and "Ocultar Pistas" or "Mostrar Pistas")
        
        for i in range(self.opponent_board_layout.count()):
            button = self.opponent_board_layout.itemAt(i).widget()
            row = button.property("row")
            col = button.property("col")
            
            # Solo cambiar la apariencia de casillas que no han sido disparadas
            if button.property("state") not in ("hit", "miss"):
                if new_state:
                    if self.controller.game_model.is_ship_at(row, col):
                        button.setText("B") # Indicar que hay un barco
                        button.setStyleSheet("background-color: #38a169; color: white;") # Verde para barco
                    else:
                        button.setText("~") # Indicar agua
                        button.setStyleSheet("background-color: #4299e1; color: white;") # Azul para agua
                else:
                    button.setText(" ") # Limpiar el texto
                    button.setProperty("hint", None)
                    button.setStyleSheet("background-color: #2b6cb0")
            
            button.style().polish(button) 

    def init_opponent_board(self, board_size):
        """Inicializa el tablero enemigo con botones interactivos (crea solo si no existen)."""
        # Si ya hay botones, simplemente salimos y start_again se encargará de resetearlos
        if self.opponent_board_layout.count() > 0:
            return 

        # Crear los botones del tablero
        for row in range(board_size):
            for col in range(board_size):
                button = QPushButton(" ")
                button.setObjectName("boardButton")
                button.setProperty("row", row)
                button.setProperty("col", col)
                
                size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setSizePolicy(size_policy)
                
                button.clicked.connect(self.on_opponent_cell_clicked)
                self.opponent_board_layout.addWidget(button, row, col)

    def on_opponent_cell_clicked(self):
        """Maneja el clic en una casilla del tablero enemigo."""
        button = self.sender()
        row = button.property("row")
        col = button.property("col")

        # Evitar clics múltiples y si el juego terminó
        if button.property("state") in ("hit", "miss") or self.controller.is_game_finished():
            return

        # Procesar el disparo en el controlador
        result, message = self.controller.process_shot(row, col)
        
        self.message_label.setText(message)

        # Actualizar la interfaz (Vista) según el resultado
        if result == "hit":
            button.setText("O") # Hit
            button.setProperty("state", "hit")
            button.setStyleSheet("background-color: #e53e3e;")
            button.setProperty("hint", None) 
            button.style().polish(button) 
            
        elif result == "miss":
            button.setText("X") # Miss
            button.setProperty("state", "miss")
            button.setStyleSheet("background-color: #a0aec0;")
            button.setProperty("hint", None) 
            button.style().polish(button) 
        
        button.setEnabled(False) # Deshabilitar botón después del disparo
        
        if self.controller.is_game_finished():
            # 1. Cambiar el texto del botón para reiniciar
            self.show_hints.setText("¿Quiere volver a jugar?")
            
            # 2. Desconectar la función de pistas y conectar la función de reinicio (SOLUCIÓN AL BUG)
            try:
                self.show_hints.clicked.disconnect(self.show_hints_to_user)
            except TypeError:
                pass 
                
            self.show_hints.clicked.connect(self.start_again)
            
            # 3. Deshabilitar los botones restantes para terminar la partida
            for i in range(self.opponent_board_layout.count()):
                 self.opponent_board_layout.itemAt(i).widget().setEnabled(False)
