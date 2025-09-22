# negocios/tablero_negocios.py
import string
from Datos.Tablero_datos import TableroDatos

class TableroNegocios:
    @staticmethod
    def crear_tablero_ascii(tablero):
        #Convierte la matriz en una representacion ASCII estilo Battleship.
        #Devuelve una lista de strings (lineas).
        
        filas = tablero.filas
        columnas = tablero.columnas
        matriz = tablero.matriz
        salida = []

        encabezado = "    " + "".join([f" {c+1:2} " for c in range(columnas)])
        salida.append(encabezado)

        for f in range(filas):
            letra = string.ascii_uppercase[f]
            if f == 0:
                salida.append("   " + "+---" * columnas + "+")
            linea = f"{letra:2} " + "".join([f"| {matriz[f][c]} " for c in range(columnas)]) + "|"
            salida.append(linea)
            salida.append("   " + "+---" * columnas + "+")
        return salida

    @staticmethod
    def mostrar_tablero(tablero_ascii):
        #Imprime la representacion ASCII (lista de líneas).
        for fila in tablero_ascii:
            print(fila)

    @staticmethod
    def generar_barcos(tablero):
        #Delegar a la capa de datos la generacion de barcos.
        TableroDatos.generar_barcos(tablero)

    @staticmethod
    def disparar(tablero_real, tablero_oculto, fila_idx, col_idx):
        #Procesa un disparo en (fila_idx, col_idx).
        #- Si ya se disparo antes en tablero_oculto, devuelve ('repeat', mensaje).
        #- Si acierta (en tablero_real hay '*'), marca '*' en tablero_oculto y devuelve ('hit', mensaje).
        #- Si falla, marca 'X' en tablero_oculto y devuelve ('miss', mensaje).
        
        # Validar índices
        if fila_idx < 0 or fila_idx >= tablero_real.filas or col_idx < 0 or col_idx >= tablero_real.columnas:
            return ("invalid", "Coordenadas fuera de rango.")

        valor_oculto = tablero_oculto.matriz[fila_idx][col_idx]
        if valor_oculto != ".":
            return ("repeat", "Ya disparaste en esa posicion.")

        if tablero_real.matriz[fila_idx][col_idx] == "*":
            tablero_oculto.matriz[fila_idx][col_idx] = "*"
            return ("hit", "Tocado!")
        else:
            tablero_oculto.matriz[fila_idx][col_idx] = "X"
            return ("miss", "Agua (fallaste).")

    @staticmethod
    def contar_partes_barco(tablero):
        #Cuenta cuantas '*' hay en el tablero (partes de barco).
        return sum(1 for fila in tablero.matriz for c in fila if c == "*")
