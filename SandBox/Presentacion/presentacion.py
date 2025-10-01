import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QPushButton,
                               QSplitter, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from Controlador.controlador import WarShipController

class WarShipGame(QMainWindow):
    def show_hints_to_user(self):
        if not hasattr(self.controller, "game_model") or self.controller.game_model is None:
            return

        current_state = getattr(self.controller.game_model, "are_hints_shown", False)
        new_state = not current_state
        self.controller.game_model.are_hints_shown = new_state
        self.show_hints.setText("Ocultar Pistas" if new_state else "Mostrar Pistas")

        for i in range(self.opponent_board_layout.count()):
            item = self.opponent_board_layout.itemAt(i)
            if not item:
                continue
            button = item.widget()
            if not button or button.property("state") in ("hit", "miss"):
                continue

            row, col = button.property("row"), button.property("col")
            if new_state:
                try:
                    if self.controller.game_model.is_ship_at(row, col):
                        button.setText("B")
                        button.setStyleSheet("background-color: #38a169; color: white;")
                        button.setProperty("hint", "ship")
                    else:
                        button.setText("~")
                        button.setStyleSheet("background-color: #4299e1; color: white;")
                        button.setProperty("hint", "water")
                except Exception:
                    button.setText(" ")
                    button.setStyleSheet("")
                    button.setProperty("hint", None)
            else:
                button.setText(" ")
                button.setProperty("hint", None)
                button.setStyleSheet("")
            button.style().polish(button)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WarShip")
        self.setGeometry(100, 100, 1000, 800)

        self.controller = WarShipController(board_size=10)
        self.setup_styles()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_home_view()
        self.create_mode_selection_view()
        self.create_game_view()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f4f8; color: #333; font-family: Arial, sans-serif; }
            QLabel#titleLabel { font-size: 32px; font-weight: bold; color: #1a202c; }
            QLabel#messageLabel { font-size: 18px; color: #4a5568; }
            QPushButton { background-color: #2b6cb0; color: white; border-radius: 8px; padding: 6px 10px; font-weight: bold; }
            QPushButton#boardButton { background-color: #0A497B; border: 1px solid #fff; color: white; }
        """)

    def create_home_view(self):
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)
        title_label = QLabel("BattleShip")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        play_button = QPushButton("Jugar")
        play_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        play_button.setStyleSheet("font-size: 32px; padding: 18px 36px; border-radius: 10px;")
        layout.addWidget(play_button, alignment=Qt.AlignCenter)

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
        solo_button.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        layout.addWidget(solo_button, alignment=Qt.AlignCenter)

        ai_button = QPushButton("Jugar Automático (IA)")
        ai_button.clicked.connect(self.start_ai_game)
        ai_button.setStyleSheet("font-size: 28px; padding: 18px 36px; border-radius: 10px;")
        ai_button.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        layout.addWidget(ai_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(mode_widget)

    def create_game_view(self):
        self.game_widget = QWidget()
        self.main_layout = QVBoxLayout(self.game_widget)

        # Top bar
        top_bar = QHBoxLayout()
        self.title_label = QLabel("BattleShip")
        self.title_label.setObjectName("titleLabel")
        top_bar.addWidget(self.title_label, alignment=Qt.AlignLeft)

        self.btn_back = QPushButton("Volver")
        self.btn_back.clicked.connect(self.back_to_mode_selection)
        self.btn_back.setStyleSheet("font-size: 20px; padding: 10px 16px; border-radius: 8px;")
        self.btn_back.setMinimumHeight(48)
        top_bar.addWidget(self.btn_back, alignment=Qt.AlignRight)
        self.main_layout.addLayout(top_bar)

        self.message_label = QLabel("¡Es tu turno! Haz clic en una casilla para disparar.")
        self.message_label.setObjectName("messageLabel")
        self.main_layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Player board
        self.player_container = QWidget()
        self.player_layout = QVBoxLayout(self.player_container)
        self.player_label = QLabel("Tu Tablero")
        self.player_layout.addWidget(self.player_label, alignment=Qt.AlignCenter)
        self.player_board_widget = QWidget()
        self.player_board_layout = QGridLayout(self.player_board_widget)
        self.player_layout.addWidget(self.player_board_widget)
        self.splitter.addWidget(self.player_container)
        self.player_container.hide()

        # Opponent board
        self.opponent_container = QWidget()
        self.opponent_layout = QVBoxLayout(self.opponent_container)
        self.opponent_label = QLabel("Tablero Enemigo")
        self.opponent_layout.addWidget(self.opponent_label, alignment=Qt.AlignCenter)
        self.opponent_board_widget = QWidget()
        self.opponent_board_widget.setObjectName("opponentBoardWidget")
        self.opponent_board_layout = QGridLayout(self.opponent_board_widget)
        self.opponent_layout.addWidget(self.opponent_board_widget)
        self.splitter.addWidget(self.opponent_container)

        # Controls
        controls_layout = QHBoxLayout()
        self.show_hints = QPushButton("Mostrar Pistas")
        self.show_hints.clicked.connect(self.show_hints_to_user)
        controls_layout.addWidget(self.show_hints)

        self.btn_pause_resume = QPushButton("Pausar")
        self.btn_pause_resume.clicked.connect(self.pause_resume_ai)
        self.btn_pause_resume.hide()
        controls_layout.addWidget(self.btn_pause_resume)

        self.btn_restart = QPushButton("Volver a Jugar")
        self.btn_restart.clicked.connect(self.start_again_wrapper)
        self.btn_restart.hide()
        controls_layout.addWidget(self.btn_restart)

        self.main_layout.addLayout(controls_layout)
        self.stacked_widget.addWidget(self.game_widget)

        # Timer IA (uno solo)
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.ai_step)

        self.ai_timer_interval_ms_default = 1000
        self.ai_timer_interval_ms = self.ai_timer_interval_ms_default
        self.ai_running, self.ai_paused = False, False

    # --- Navegación ---
    def back_to_mode_selection(self):
        self.ai_timer.stop()
        self.ai_running = False
        self.ai_paused = False
        try:
            self.controller.ai_reset()
        except Exception:
            pass
        self.btn_pause_resume.hide()
        self.btn_restart.hide()
        self.stacked_widget.setCurrentIndex(1)

    # --- Modo Humano ---
    def start_solo_game(self):
        self.ai_timer.stop()
        self.controller.start_new_game()
        self.init_opponent_board(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        self.message_label.setText("¡Es tu turno! Haz clic en una casilla para disparar.")
        self.player_container.hide()
        self.stacked_widget.setCurrentIndex(2)

        self.show_hints.setEnabled(True)
        self.show_hints.show()
        self.btn_pause_resume.hide()
        self.btn_restart.hide()

        try:
            self.show_hints.clicked.disconnect()
        except Exception:
            pass
        self.show_hints.clicked.connect(self.show_hints_to_user)

    def start_again_wrapper(self):
        if self.btn_pause_resume.isVisible():
            self.start_ai_game(restart=True)
        else:
            self.start_solo_game()

    def reset_board_buttons_ui(self):
        for i in range(self.opponent_board_layout.count()):
            button = self.opponent_board_layout.itemAt(i).widget()
            button.setText(" ")
            button.setProperty("state", None)
            button.setProperty("content", None)
            button.setProperty("hint", None)
            button.setEnabled(True)
            button.setStyleSheet("")
            button.style().polish(button)

    def init_opponent_board(self, board_size):
        if self.opponent_board_layout.count() > 0:
            return
        for row in range(board_size):
            for col in range(board_size):
                button = QPushButton(" ")
                button.setObjectName("boardButton")
                button.setProperty("row", row)
                button.setProperty("col", col)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self.on_opponent_cell_clicked)
                self.opponent_board_layout.addWidget(button, row, col)

    def on_opponent_cell_clicked(self):
        button = self.sender()
        row, col = button.property("row"), button.property("col")
        if button.property("state") in ("hit", "miss") or self.controller.is_game_finished():
            return

        result, message = self.controller.process_shot(row, col)
        self.message_label.setText(message)
        if result == "hit":
            button.setText("O")
            button.setProperty("state", "hit")
            button.setStyleSheet("background-color: #e53e3e;")
        elif result == "miss":
            button.setText("X")
            button.setProperty("state", "miss")
            button.setStyleSheet("background-color: #a0aec0;")
        button.setEnabled(False)

        if self.controller.is_game_finished():
            self.end_game_ui()

    # --- Modo IA ---
    def start_ai_game(self, restart=False):
        self.ai_timer.stop()
        self.ai_timer_interval_ms = self.ai_timer_interval_ms_default

        self.controller.start_new_game()
        if self.opponent_board_layout.count() == 0:
            self.init_opponent_board(self.controller.get_board_size())
        self.reset_board_buttons_ui()
        for i in range(self.opponent_board_layout.count()):
            self.opponent_board_layout.itemAt(i).widget().setEnabled(False)

        self.message_label.setText("IA en marcha...")
        self.controller.ai_start()
        self.ai_running, self.ai_paused = True, False

        self.show_hints.setText("Mostrar Pistas")
        self.show_hints.setEnabled(True)
        self.show_hints.show()
        try:
            self.show_hints.clicked.disconnect()
        except Exception:
            pass
        self.show_hints.clicked.connect(self.show_hints_to_user)

        self.btn_pause_resume.setText("Pausar")
        self.btn_pause_resume.show()

        self.btn_restart.setText("Volver a Jugar")
        self.btn_restart.show()

        self.ai_timer.start(self.ai_timer_interval_ms)
        self.player_container.hide()
        self.stacked_widget.setCurrentIndex(2)

    def pause_resume_ai(self):
        if not self.ai_running:
            return
        if not self.ai_paused:
            self.ai_paused = True
            self.ai_timer.stop()
            self.btn_pause_resume.setText("Reanudar")
            self.message_label.setText("IA en pausa.")
        else:
            self.ai_paused = False
            self.ai_timer.start(self.ai_timer_interval_ms)
            self.btn_pause_resume.setText("Pausar")
            self.message_label.setText("IA en marcha...")

    def ai_step(self):
        if not self.ai_running or self.controller.is_game_finished():
            self.ai_timer.stop()
            self.ai_running, self.ai_paused = False, False
            self.end_game_ui()
            return
        if self.ai_paused:
            return

        move = self.controller.ai_make_move()
        if not move:
            self.ai_timer.stop()
            self.ai_running = False
            self.end_game_ui()
            return

        row, col, result, message = move
        item = self.opponent_board_layout.itemAtPosition(row, col)
        if item:
            button = item.widget()
            if result == "hit":
                button.setText("O")
                button.setProperty("state", "hit")
                button.setStyleSheet("background-color: #e53e3e;")
            else:
                button.setText("X")
                button.setProperty("state", "miss")
                button.setStyleSheet("background-color: #a0aec0;")
            button.setEnabled(False)
            button.style().polish(button)

        self.message_label.setText(message)

    def end_game_ui(self):
        self.ai_timer.stop()
        self.ai_running, self.ai_paused = False, False
        self.message_label.setText("Partida finalizada.")

        for row in range(self.controller.get_board_size()):
            for col in range(self.controller.get_board_size()):
                item = self.opponent_board_layout.itemAtPosition(row, col)
                if not item:
                    continue
                button = item.widget()
                if self.controller.game_model.is_ship_at(row, col) and button.property("state") is None:
                    button.setText("B")
                    button.setStyleSheet("background-color: #38a169; color: white;")
                button.setEnabled(False)

        self.btn_restart.setText("Volver a Jugar")
        try:
            self.btn_restart.clicked.disconnect()
        except Exception:
            pass
        if self.btn_pause_resume.isVisible():
            self.btn_restart.clicked.connect(lambda: self.start_ai_game(restart=True))
        else:
            self.btn_restart.clicked.connect(self.start_solo_game)
        self.btn_restart.setEnabled(True)
        self.btn_restart.show()

        self.show_hints.setText("Mostrar Pistas")
        self.show_hints.show()
        try:
            self.show_hints.clicked.disconnect()
        except Exception:
            pass
        self.show_hints.clicked.connect(self.show_hints_to_user)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WarShipGame()
    win.show()
    sys.exit(app.exec())
