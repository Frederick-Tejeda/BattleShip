import sys
from Presentacion.presentacion import WarShipGame
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    # 1. Crear la instancia de QApplication
    app = QApplication(sys.argv)
    
    # 2. Instanciar la ventana principal (Vista)
    window = WarShipGame()
    
    # 3. Mostrar la ventana al usuario
    window.show()
    
    # 4. Iniciar el bucle de eventos
    sys.exit(app.exec())