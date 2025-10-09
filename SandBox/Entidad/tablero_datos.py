import random

class TableroDatos:
    """
    Clase de lógica estática para la gestión y colocación de barcos 
    según las reglas estándar de BattleShip.
    """
    
    @staticmethod
    def _es_posicion_valida_con_margen(tablero, r_start, c_start, tam, orient):
        """
        Método auxiliar: Verifica si la colocación de un barco es válida,
        incluyendo la verificación de la zona de amortiguamiento (margen)
        alrededor del barco.
        """
        filas = tablero.filas
        columnas = tablero.columnas

        if orient == "H":
            # Verificar que el barco no se salga del tablero
            if c_start + tam > columnas: return False 
            
            # Rangos a revisar (incluyendo margen de 1 celda)
            r_min, r_max = max(0, r_start - 1), min(filas, r_start + 2)
            c_min, c_max = max(0, c_start - 1), min(columnas, c_start + tam + 1)
        else: # Vertical
            # Verificar que el barco no se salga del tablero
            if r_start + tam > filas: return False
            
            # Rangos a revisar (incluyendo margen de 1 celda)
            r_min, r_max = max(0, r_start - 1), min(filas, r_start + tam + 1)
            c_min, c_max = max(0, c_start - 1), min(columnas, c_start + 2)

        # Revisar si hay un barco ('*') en la zona de margen/colocación
        for r in range(r_min, r_max):
            for c in range(c_min, c_max):
                if tablero.matriz[r][c] == '*':
                    return False
        
        return True
    
    @staticmethod
    def colocar_barco(tablero, tamano):
        """
        Coloca un barco de 'tamano' en el tablero de forma aleatoria (horizontal o vertical).
        """
        filas = tablero.filas
        columnas = tablero.columnas
        orientaciones = ['H', 'V']
        random.shuffle(orientaciones)
        max_intentos = 100

        for orient in orientaciones:
            intentos = 0
            while intentos < max_intentos:
                r_start = random.randrange(filas)
                c_start = random.randrange(columnas)
                
                if TableroDatos._es_posicion_valida_con_margen(tablero, r_start, c_start, tamano, orient):
                    # Colocar el barco
                    for i in range(tamano):
                        if orient == "H":
                            tablero.matriz[r_start][c_start + i] = '*'
                            tablero.ships.add((r_start, c_start + i))
                        else: # Vertical
                            tablero.matriz[r_start + i][c_start] = '*'
                            tablero.ships.add((r_start + i, c_start))
                    return True # Colocación exitosa

                intentos += 1
        
        return False # Falló la colocación después de intentar ambas orientaciones

    @staticmethod
    def generar_barcos(tablero):
        """
        Coloca todos los barcos en el tablero según las reglas estándar de BattleShip:
        1 x 4, 2 x 3, 3 x 2, 4 x 1 (Total: 20 partes).
        """
        # Tamaños de los barcos a colocar: 1x4, 2x3, 3x2, 4x1 (Total 10 barcos, 20 partes)
        barcos = [4] + [3, 3] + [2, 2, 2] + [1, 1, 1, 1]  
        
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            # Resetear el estado de los barcos antes de cada intento
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