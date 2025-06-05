from src.controllers.manager import Manager

from src.strategies.geometric import Geometric

import numpy as np
import pandas as pd


def iniciar():
    # """Punto de entrada principal"""
                   # ABCDEFGHIJKLMNOPQRST 
    estado_inicio = "10000000000000000000"
    condiciones =   "11111111111111111111"
    
    alcance =       "11111111111111111111"
    
    num_nodos = len(estado_inicio)
    variables = range(num_nodos)

    config_sistema = Manager(estado_inicial=estado_inicio)
    # config_sistema.pagina = "B"
    

    archivo_excel = "datos.xlsx"
    col_particion = "Partición"
    col_perdida = "Pérdida"
    col_tiempo = "Tiempo ejecución"

    try:
        df_existente = pd.read_excel(archivo_excel)
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=[col_particion, col_perdida, col_tiempo])

    pruebas = []
    i = 0

    for presente in generar_subarreglos(variables):
        # Para vista binaria
        presente = set(presente)
        bits_mecanismo = "".join(["1" if i in presente else "0" for i in variables])
        pruebas.append(bits_mecanismo)

    for mecanismo in pruebas:
        i += 1
        print(i)
        print(f"{alcance=} {mecanismo=}")
        analizador_fi = Geometric(config_sistema)
        sia_dos = analizador_fi.aplicar_estrategia(condiciones, alcance, mecanismo)
        print(sia_dos.particion)
        print(sia_dos.perdida)
        print(sia_dos.tiempo_ejecucion)

        lineas = sia_dos.particion.split("\n")

        fila1 = pd.DataFrame(
            [[lineas[0], sia_dos.perdida, sia_dos.tiempo_ejecucion]],
            columns=[col_particion, col_perdida, col_tiempo],
        )
        fila2 = pd.DataFrame(
            [[lineas[1], "", ""]],
            columns=[col_particion, col_perdida, col_tiempo],
        )

        # Concatenar los nuevos datos con los existentes
        df_existente = pd.concat([df_existente, fila1, fila2], ignore_index=True)

        # Guardar el DataFrame actualizado en el archivo Excel
        df_existente.to_excel(archivo_excel, index=False, engine="openpyxl")

    # print(f"Datos guardados en {archivo_excel}")


def generar_subarreglos(arr):
    return [
        arr,  # 1. Todo el arreglo original
        arr[:-1],  # 2. Excluir el último elemento
        arr[1:],  # 3. Excluir el primer elemento
        arr[1:-1],  # 4. Excluir los extremos
        arr[::2],  # 5. Tomar los elementos en posiciones pares
        arr[1::2],  # 6. Tomar los elementos en posiciones impares
        np.delete(
            arr, np.arange(2, len(arr), 3)
        ),  # 7. Omitir los múltiplos de 3 (índices)
    ]
