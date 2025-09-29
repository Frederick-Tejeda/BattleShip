import sys
# Importamos la clase principal de la interfaz desde el archivo de Presentación
from Presentacion.presentacion import WarShipGame
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    # 1. Crear la instancia de QApplication
    app = QApplication(sys.argv)
    
    # 2. Instanciar la ventana principal de la aplicación (la Presentación/Vista)
    # Aquí se inicializa toda la estructura del proyecto (Vista -> Controlador -> Entidad)
    window = WarShipGame()
    
    # 3. Mostrar la ventana al usuario
    window.show()
    
    # 4. Iniciar el bucle de eventos de la aplicación
    sys.exit(app.exec())
