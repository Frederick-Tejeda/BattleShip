import random

class TableroDatos:
    """
    Clase de lógica estática para la gestión y colocación de barcos 
    según las reglas estándar de BattleShip.
    """
    
    @staticmethod
    def colocar_barco(tablero, tamano):
        """
        Coloca un barco de 'tamano' en el tablero de forma aleatoria (horizontal o vertical).
        Usa '*' para marcar las partes de barco en tablero.matriz.
        """
        filas = tablero.filas
        columnas = tablero.columnas
        colocado = False
        intentos = 0
        
        def es_posicion_valida_con_margen(r, c, tam, orient):
            """
            Verifica si una posición inicial (r, c) de un barco de 'tam' es válida.
            Incluye la verificación de la zona de amortiguamiento (margen) alrededor del barco.
            """
            if orient == "H":
                # Rango de filas a revisar: r-1 hasta r+1 (incluido)
                # Rango de columnas a revisar: c-1 hasta c+tam (incluido)
                r_start, r_end = max(0, r - 1), min(filas, r + 2)
                c_start, c_end = max(0, c - 1), min(columnas, c + tam + 1)
            else: # Vertical
                # Rango de filas a revisar: r-1 hasta r+tam (incluido)
                # Rango de columnas a revisar: c-1 hasta c+1 (incluido)
                r_start, r_end = max(0, r - 1), min(filas, r + tam + 1)
                c_start, c_end = max(0, c - 1), min(columnas, c + 2)

            for i in range(r_start, r_end):
                for j in range(c_start, c_end):
                    if tablero.matriz[i][j] == '*':
                        return False # Hay otro barco demasiado cerca
            
            return True # No hay barcos cercanos, la posición es válida

        # Intentamos colocar el barco
        while not colocado and intentos < 1000:
            intentos += 1
            orientacion = random.choice(["H", "V"])  # Horizontal o Vertical
            
            if orientacion == "H":
                # Intenta colocar horizontalmente
                fila = random.randint(0, filas - 1)
                col = random.randint(0, columnas - tamano)
                
                # 1. Verificar si la posición es válida (no toca a otros barcos)
                if es_posicion_valida_con_margen(fila, col, tamano, "H"):
                    # 2. Si es válida con margen, procedemos a colocar
                    for i in range(tamano):
                        tablero.matriz[fila][col + i] = "*"
                        tablero.ships.add((fila, col + i)) # Añadir al set de coordenadas
                    colocado = True
            
            else:  # Vertical
                # Intenta colocar verticalmente
                fila = random.randint(0, filas - tamano)
                col = random.randint(0, columnas - 1)
                
                # 1. Verificar si la posición es válida (no toca a otros barcos)
                if es_posicion_valida_con_margen(fila, col, tamano, "V"):
                    # 2. Si es válida con margen, procedemos a colocar
                    for i in range(tamano):
                        tablero.matriz[fila + i][col] = "*"
                        tablero.ships.add((fila + i, col)) # Añadir al set de coordenadas
                    colocado = True

        if not colocado:
            # Esta advertencia es más común ahora, ya que las restricciones son mayores
            print(f"Advertencia: No se pudo colocar un barco de tamaño {tamano} después de {intentos} intentos. Se reinicia la colocación.")
            # Es mejor levantar una excepción o forzar un reinicio completo si fallan muchos intentos
            return False
        return True

    @staticmethod
    def generar_barcos(tablero):
        """
        Coloca todos los barcos en el tablero según las reglas estándar de BattleShip:
        1 x 4, 2 x 3, 3 x 2, 4 x 1 (Total: 20 partes).
        """
        # Tamaños de los barcos a colocar
        barcos = [4] + [3, 3] + [2, 2, 2] + [1, 1, 1, 1]  
        
        # Implementar un bucle de reintento para garantizar que todos los barcos se coloquen
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            # Resetear el tablero antes de cada intento
            tablero.matriz = [['.' for _ in range(tablero.columnas)] for _ in range(tablero.filas)]
            tablero.ships = set()
            all_placed = True

            for tamano in barcos:
                if not TableroDatos.colocar_barco(tablero, tamano):
                    # Falló la colocación de un barco, reiniciar el proceso completo
                    all_placed = False
                    break 

            if all_placed:
                # Éxito: todos los barcos colocados
                tablero.total_parts = len(tablero.ships)
                return
            
            attempt += 1
        
        # Si llega aquí, significa que falló después de todos los intentos
        print("ERROR FATAL: No se pudo generar un tablero válido después de múltiples intentos.")
        # Establecer un valor por defecto o lanzar un error
        tablero.total_parts = 0
