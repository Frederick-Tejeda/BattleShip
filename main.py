# main.py
from Entidad.Tablero import Tablero
from Negocios.Tablero_negocios import TableroNegocios
import string
import re
import os
def clear_console():
    #Limpia la consola de forma cross-platform.
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        print("\n" * 50)

def pedir_coordenada(filas, columnas):
    
    #Pide al usuario fila+columna en formato combinado (ej: B5 o b10) o separado (B 5).
    #Retorna (fila_idx, col_idx) o None si el usuario desea salir.
    #Variante sin usar `re`.
    
    while True:
        entrada = input("Ingresa coordenada (ej: B5) o 'salir' para terminar: ").strip()
        if not entrada:
            continue
        if entrada.lower() in ("salir", "exit", "quit"):
            return None

        s = entrada.replace(" ", "").upper()  # elimina espacios y pasa a mayusculas
        if len(s) < 2:
            print("Formato invalido. Usa: LETRA+NUM (ej: A3).")
            continue

        fila_str = s[0]
        col_str = s[1:]

        if not fila_str.isalpha() or fila_str not in string.ascii_uppercase[:filas]:
            print(f"Fila invalida. Debe ser una letra entre A y {string.ascii_uppercase[filas-1]}.")
            continue

        if not col_str.isdigit():
            print("Columna invalida. Debe ser un numero.")
            continue

        col = int(col_str)
        if not (1 <= col <= columnas):
            print(f"Columna fuera de rango. Debe ser entre 1 y {columnas}.")
            continue

        fila_idx = ord(fila_str) - ord("A")
        col_idx = col - 1
        return (fila_idx, col_idx)


def mostrar_ambos_tableros(tablero_real, tablero_oculto):
    
    #Limpia la consola y muestra primero el tablero real (con barcos),
    #y debajo el tablero oculto (el que tiene el jugador).
    
    clear_console()
    print("=== TABLERO REAL (todos los barcos visibles) ===")
    TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_real))
    print("\n=== TABLERO DEL JUGADOR (Oculto / actualizado) ===")
    TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_oculto))


def main():
    filas, columnas = 10, 10

    # Crear tableros
    tablero_real = Tablero(filas, columnas)   # contiene '*' donde hay barcos
    tablero_oculto = Tablero(filas, columnas) # lo ve el jugador (inicialmente '.')

    # Generar barcos en el tablero real
    TableroNegocios.generar_barcos(tablero_real)
    total_partes = TableroNegocios.contar_partes_barco(tablero_real)
    encontrados = 0

    # Mostrar inicialmente ambos tableros
    mostrar_ambos_tableros(tablero_real, tablero_oculto)
    print(f"\nComienza el juego. Total de partes de barco a hundir: {total_partes}\n")

    # Bucle de juego
    while encontrados < total_partes:
        # Pedir coordenada
        coordenada = pedir_coordenada(filas, columnas)
        if coordenada is None:
            print("Has salido del juego. Hasta luego!")
            return

        fila_idx, col_idx = coordenada
        # Procesar disparo (no imprimimos mensajes de "Tocado" ni pausas)
        resultado, _ = TableroNegocios.disparar(tablero_real, tablero_oculto, fila_idx, col_idx)

        # Actualizamos contador si hubo impacto
        if resultado == "hit":
            encontrados = TableroNegocios.contar_partes_barco(tablero_oculto)

        # Despues de la jugada limpiamos y mostramos ambos tableros inmediatamente
        mostrar_ambos_tableros(tablero_real, tablero_oculto)
        print(f"Partes hundidas: {encontrados}/{total_partes}")

    # Juego terminado: limpiar y mostrar tableros finales
    mostrar_ambos_tableros(tablero_real, tablero_oculto)
    print("\nFelicidades! Has encontrado todas las partes de los barcos.")
    print("=== TABLERO REAL (todos los barcos) ===")
    TableroNegocios.mostrar_tablero(TableroNegocios.crear_tablero_ascii(tablero_real))


if __name__ == "__main__":
    main()