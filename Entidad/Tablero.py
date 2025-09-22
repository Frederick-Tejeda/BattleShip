# entidad/tablero.py

class Tablero:

    #Entidad Tablero: representa la matriz interna del tablero.
    #Cada celda puede ser:
      #'·' -> desconocido/agua (visible inicialmente)
      #'*' -> parte de barco (en tablero real)
      #'X' -> disparo fallido (marcado en tablero visible)

    def __init__(self, filas=10, columnas=10):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [["." for _ in range(columnas)] for _ in range(filas)]

    def reset(self):
        self.matriz = [["." for _ in range(self.columnas)] for _ in range(self.filas)]

    def copiar(self):
        # Devuelve una copia (nuevo Tablero) con la misma matriz.
        t = Tablero(self.filas, self.columnas)
        t.matriz = [row[:] for row in self.matriz]
        return t
