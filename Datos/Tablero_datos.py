# datos/tablero_datos.py
import random

class TableroDatos:
    @staticmethod
    def colocar_barco(tablero, tamano):
       
        #Coloca un barco en el tablero de forma aleatoria (horizontal o vertical).
        #Usa '*' para marcar las partes de barco en tablero.matriz.

        filas = tablero.filas
        columnas = tablero.columnas
        colocado = False
        intentos = 0

        while not colocado and intentos < 1000:
            intentos += 1
            orientacion = random.choice(["H", "V"])  # Horizontal o Vertical
            if orientacion == "H":
                fila = random.randint(0, filas - 1)
                col = random.randint(0, columnas - tamano)
                if all(tablero.matriz[fila][col + i] == "." for i in range(tamano)):
                    for i in range(tamano):
                        tablero.matriz[fila][col + i] = "*"
                    colocado = True
            else:  # Vertical
                fila = random.randint(0, filas - tamano)
                col = random.randint(0, columnas - 1)
                if all(tablero.matriz[fila + i][col] == "." for i in range(tamano)):
                    for i in range(tamano):
                        tablero.matriz[fila + i][col] = "*"
                    colocado = True

        if not colocado:
            raise RuntimeError(f"No se pudo colocar un barco de tamano {tamano} despues de {intentos} intentos.")

    @staticmethod
    def generar_barcos(tablero):
        #Coloca todos los barcos en el tablero segun las reglas del enunciado.
        barcos = [4] + [3, 3] + [2, 2, 2] + [1, 1, 1, 1]  # tamanos total = 20 casillas
        for tamano in barcos:
            TableroDatos.colocar_barco(tablero, tamano)
