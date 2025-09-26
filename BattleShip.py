# # main.py
# from Entidad.Tablero import Tablero
# from Negocios.Tablero_negocios import TableroNegocios
# import string
# import re
# import os
# def clear_console():
#     #Limpia la consola de forma cross-platform.
#     try:
#         os.system('cls' if os.name == 'nt' else 'clear')
#     except Exception:
#         print("\n" * 50)

# def pedir_coordenada(filas, columnas):
    
#     #Pide al usuario fila+columna en formato combinado (ej: B5 o b10) o separado (B 5).
#     #Retorna (fila_idx, col_idx) o None si el usuario desea salir.
#     #Variante sin usar `re`.
    
#     while True:
#         entrada = input("Ingresa coordenada (ej: B5) o 'salir' para terminar: ").strip()
#         if not entrada:
#             continue
#         if entrada.lower() in ("salir", "exit", "quit"):
#             return None

#         s = entrada.replace(" ", "").upper()  # elimina espacios y pasa a mayusculas
#         if len(s) < 2:
#             print("Formato invalido. Usa: LETRA+NUM (ej: A3).")
#             continue

#         fila_str = s[0]
#         col_str = s[1:]

#         if not fila_str.isalpha() or fila_str not in string.ascii_uppercase[:filas]:
#             print(f"Fila invalida. Debe ser una letra entre A y {string.ascii_uppercase[filas-1]}.")
#             continue

#         if not col_str.isdigit():
#             print("Columna invalida. Debe ser un numero.")
#             continue

#         col = int(col_str)
#         if not (1 <= col <= columnas):
#             print(f"Columna fuera de rango. Debe ser entre 1 y {columnas}.")
#             continue

#         fila_idx = ord(fila_str) - ord("A")
#         col_idx = col - 1
#         return (fila_idx, col_idx)


# def mostrar_ambos_tableros(tablero_real, tablero_oculto):
    
#     #Limpia la consola y muestra primero el tablero real (con barcos),
#     #y debajo el tablero oculto (el que tiene el jugador).
    
#     clear_console()
#     print("=== TABLERO REAL (todos los barcos visibles) ===")
#     TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_real))
#     print("\n=== TABLERO DEL JUGADOR (Oculto / actualizado) ===")
#     TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_oculto))


# def main():
#     filas, columnas = 10, 10

#     # Crear tableros
#     tablero_real = Tablero(filas, columnas)   # contiene '*' donde hay barcos
#     tablero_oculto = Tablero(filas, columnas) # lo ve el jugador (inicialmente '.')

#     # Generar barcos en el tablero real
#     TableroNegocios.generar_barcos(tablero_real)
#     total_partes = TableroNegocios.contar_partes_barco(tablero_real)
#     encontrados = 0

#     # Mostrar inicialmente ambos tableros
#     mostrar_ambos_tableros(tablero_real, tablero_oculto)
#     print(f"\nComienza el juego. Total de partes de barco a hundir: {total_partes}\n")

#     # Bucle de juego
#     while encontrados < total_partes:
#         # Pedir coordenada
#         coordenada = pedir_coordenada(filas, columnas)
#         if coordenada is None:
#             print("Has salido del juego. Hasta luego!")
#             return

#         fila_idx, col_idx = coordenada
#         # Procesar disparo (no imprimimos mensajes de "Tocado" ni pausas)
#         resultado, _ = TableroNegocios.disparar(tablero_real, tablero_oculto, fila_idx, col_idx)

#         # Actualizamos contador si hubo impacto
#         if resultado == "hit":
#             encontrados = TableroNegocios.contar_partes_barco(tablero_oculto)

#         # Despues de la jugada limpiamos y mostramos ambos tableros inmediatamente
#         mostrar_ambos_tableros(tablero_real, tablero_oculto)
#         print(f"Partes hundidas: {encontrados}/{total_partes}")

#     # Juego terminado: limpiar y mostrar tableros finales
#     mostrar_ambos_tableros(tablero_real, tablero_oculto)
#     print("\nFelicidades! Has encontrado todas las partes de los barcos.")
#     print("=== TABLERO REAL (todos los barcos) ===")
#     TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_real))


# if __name__ == "__main__":
#     main()

import random
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                               QSplitter, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt
import random

class WarShipGame(QMainWindow):
    """
    Main class for the WarShip game application.
    This class sets up the user interface by creating and arranging widgets
    for different views of the game.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WarShip")
        self.setGeometry(100, 100, 1000, 800)
        self.board_size = 5
        self.shipsCount = 0
        self.triesCount = int((self.board_size * self.board_size) * 0.8)
        
        # Apply the CSS style sheet directly in the code
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                color: #333;
                font-family: Arial, sans-serif;
            }
            QMainWindow {
                background-color: #f0f4f8;
            }
            QLabel#titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #1a202c;
                margin: 0 0 15px 0;
            }
            QLabel#messageLabel {
                font-size: 22px;
                font-style: italic;
                color: #4a5568;
                margin: 0 0 8px 0;
            }
            QPushButton {
                background-color: #2b6cb0;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2c5282;
            }
            QPushButton:pressed {
                background-color: #1c456a;
            }
         
            QWidget#opponentBoardWidget, QWidget#playerBoardWidget {
                background-color: #0A497B;
                border: 2px solid #c0c0c0;
                border-radius: 8px;
            }

            QLabel#opponentLabel, QLabel#playerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2d3748;
                margin: 0 0 10px 0;
            }

            .boardButton {
                background-color: #0A497B;
                border: 2px solid #ffffff;
                border-radius: 4px;
                margin: 0;
            }
            .boardButton[hit="true"] {
                background-color: #e53e3e;
            }
            .boardButton[miss="true"] {
                background-color: #a0aec0;
            }
            .boardButton[content="hit"] {
                color: #fff;
                font-weight: bold;
            }
            .boardButton[content="miss"] {
                color: #fff;
                font-weight: bold;
            }
        """)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_home_view()
        self.create_mode_selection_view()
        self.create_game_view()

    def create_home_view(self):
        """Creates the welcome screen view."""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("WarShip")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        description_label = QLabel("Welcome to the classic battleship game.\nDestroy all the ships on the opponent's board to win!")
        description_label.setObjectName("messageLabel")
        description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)

        play_button = QPushButton("Jugar")
        play_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(play_button)

        self.stacked_widget.addWidget(home_widget)
    
    def create_mode_selection_view(self):
        """Creates the game mode selection view."""
        mode_widget = QWidget()
        layout = QVBoxLayout(mode_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Selecciona el modo de juego")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        solo_button = QPushButton("Jugar Solo")
        solo_button.clicked.connect(self.start_solo_game)
        layout.addWidget(solo_button)

        ai_button = QPushButton("Jugar Automático (Próximamente)")
        layout.addWidget(ai_button)

        self.stacked_widget.addWidget(mode_widget)

    def create_game_view(self):
        """Creates the main game view with the boards."""
        self.game_widget = QWidget()
        self.main_layout = QVBoxLayout(self.game_widget)

        # Title and message labels
        self.title_label = QLabel("WarShip")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        self.message_label = QLabel("Welcome to the game!")
        self.message_label.setObjectName("messageLabel")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.message_label)

        # QSplitter for boards
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.main_layout.addWidget(self.splitter)
        
        # Player Board Container (not interactive in this example)
        self.player_container = QWidget()
        self.player_layout = QVBoxLayout(self.player_container)
        self.player_label = QLabel("Your Fleet")
        self.player_label.setObjectName("playerLabel")
        self.player_label.setAlignment(Qt.AlignCenter)
        self.player_layout.addWidget(self.player_label)
        self.player_board_widget = QWidget()
        self.player_board_widget.setObjectName("playerBoardWidget")
        self.player_board_layout = QGridLayout(self.player_board_widget)
        self.player_layout.addWidget(self.player_board_widget)
        self.splitter.addWidget(self.player_container)

        # Opponent Board Container (main interactive board)
        self.opponent_container = QWidget()
        self.opponent_container.setObjectName("opponentContainer")
        self.opponent_layout = QVBoxLayout(self.opponent_container)
        self.opponent_label = QLabel("Opponent's Waters")
        self.opponent_label.setObjectName("opponentLabel")
        self.opponent_label.setAlignment(Qt.AlignCenter)
        self.opponent_layout.addWidget(self.opponent_label)
        self.opponent_board_widget = QWidget()
        self.opponent_board_widget.setObjectName("opponentBoardWidget")
        self.opponent_board_layout = QGridLayout(self.opponent_board_widget)
        self.opponent_layout.addWidget(self.opponent_board_widget)
        self.splitter.addWidget(self.opponent_container)
        
        self.stacked_widget.addWidget(self.game_widget)
        
    def start_solo_game(self):
        """
        Starts the solo game.
        Initializes the game state and displays the game view.
        """
        self.message_label.setText("¡Es tu turno! Haz clic en una casilla para disparar.")
        
        self.opponent_ships = self.place_ships(self.board_size)
        self.init_opponent_board(self.board_size)
        self.player_container.hide() # Hide player board for solo mode
        self.stacked_widget.setCurrentIndex(2) # Switch to the game view

    def place_ships(self, board_size):
        """Randomly places a set of ships on the board."""
        # Simple ship placement for demonstration
        #Ships minimun = TableSize/2, Ships maximun = TableSize
        self.shipsCount = random.randint(int(self.board_size / 2), self.board_size)
        ships = set()
        for _ in range(self.shipsCount):
            row = random.randint(0, board_size - 1)
            col = random.randint(0, board_size - 1)
            ships.add((row, col))
        return ships

    def init_opponent_board(self, board_size):
        """Initializes the opponent's board with interactive buttons."""
        for row in range(board_size):
            for col in range(board_size):
                button = QPushButton(" ")
                button.setObjectName("boardButton")
                button.setProperty("row", row)
                button.setProperty("col", col)
                size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setSizePolicy(size_policy)
                #button.setFixedSize(40, 40)
                button.clicked.connect(self.on_opponent_cell_clicked)
                self.opponent_board_layout.addWidget(button, row, col)

    def on_opponent_cell_clicked(self):
        """Handles a click on the opponent's board."""
        button = self.sender()
        row = button.property("row")
        col = button.property("col")

        if button.property("state") in ("hit", "miss"):
            self.message_label.setText("¡Ya disparaste a esta casilla! Intenta de nuevo.")
            return
        
        self.triesCount -= 1

        if (row, col) in self.opponent_ships:
            self.message_label.setText("¡Es un impacto!")
            button.setText("O") # Hit
            button.setStyleSheet("background-color: red;")
            button.setProperty("state", "hit")
            button.setProperty("content", "hit")
            self.shipsCount -= 1
            if self.shipsCount == 0:
                self.message_label.setText("¡Felicidades! ¡Has hundido todos los barcos!")
        else:
            self.message_label.setText(f"¡Fallaste, te quedan {self.triesCount} intentos!")
            button.setText("X") # Miss
            button.setStyleSheet("background-color: grey;")
            button.setProperty("state", "miss")
            button.setProperty("content", "miss")

        if self.triesCount <= 0 and self.shipsCount > 0:
            self.message_label.setText("¡Juego terminado! No te quedan más intentos.")
            # Disable all buttons
            for i in range(self.opponent_board_layout.count()):
                btn = self.opponent_board_layout.itemAt(i).widget()
                btn.setEnabled(False)
        
        button.setEnabled(False) # Disable button after click

    def on_fire_clicked(self):
        """Handle the 'Fire!' button click. (Not used in this version)"""
        pass
    
    def on_reset_clicked(self):
        """Handle the 'Reset Game' button click. (Not used in this version)"""
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarShipGame()
    window.show()
    sys.exit(app.exec())
