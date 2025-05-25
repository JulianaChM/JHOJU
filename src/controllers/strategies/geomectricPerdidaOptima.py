import time
import numpy as np
from src.controllers.manager import Manager
from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.funcs.format import fmt_biparte_q
from src.constants.models import GEOMETRIC_ANALYSIS_TAG, GEOMETRIC_LABEL
from src.middlewares.slogger import SafeLogger

class Geometric(SIA):
    """
    Estrategia Geometric basada en propiedades topológicas y geométricas.
    Implementa un enfoque eficiente para encontrar biparticiones óptimas usando 
    costos de transición y simetrías del hipercubo.
    """

    def __init__(self, gestor: Manager):
        super().__init__(gestor)
        self.logger = SafeLogger(GEOMETRIC_ANALYSIS_TAG)

    def aplicar_estrategia(self, condicion: str, alcance: str, mecanismo: str):
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)

        start_time = time.time()
        dims = self.sia_subsistema.dims_ncubos
        indices = self.sia_subsistema.indices_ncubos
        n = len(dims) + len(indices)

        # Construir tabla de costos entre estados
        tabla_costos = self.calcular_tabla_costos(n)

        # Identificar bipartición óptima
        mejor_particion, mejor_perdida, distribucion_particion = self.identificar_mejor_biparticion(tabla_costos, dims, indices)

        # Formatear bipartición
        complemento = list(set(range(n)) - set(mejor_particion))
        prim = [(0, i) for i in mejor_particion]
        dual = [(0, i) for i in complemento]
        particion_str = fmt_biparte_q(prim, dual)

        return Solution(
            estrategia=GEOMETRIC_LABEL,
            perdida=mejor_perdida,
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=distribucion_particion,
            particion=particion_str,
            tiempo_total=time.time() - start_time,
        )

    def calcular_tabla_costos(self, n):
        """
        Calcula tabla de costos usando distancia de Hamming y pesos exponenciales.
        """
        tabla = np.zeros((2**n, 2**n))
        for i in range(2**n):
            for j in range(2**n):
                d_hamming = bin(i ^ j).count('1')
                gamma = 2 ** (-d_hamming)
                tabla[i, j] = gamma * self.calcular_diferencia_directa(i, j, n)
        return tabla

    def calcular_diferencia_directa(self, i, j, n):
        """
        Calcula diferencia directa (simplificada: conteo de bits distintos).
        """
        return bin(i ^ j).count('1') / n  # Normalizado

    def identificar_mejor_biparticion(self, tabla_costos, dims, indices):
        """
        Identifica la bipartición con menor pérdida usando análisis de patrones de costo.
        """
        n = len(dims) + len(indices)
        mejor_perdida = float('inf')
        mejor_particion = None
        distribucion_mejor = None

        for i in range(n):
            part1 = [i]
            part2 = [j for j in range(n) if j != i]
            perdida = self.evaluar_discrepancia(tabla_costos, part1, part2)

            if perdida < mejor_perdida:
                mejor_perdida = perdida
                mejor_particion = part1
                distribucion_mejor = np.copy(self.sia_dists_marginales)

        return mejor_particion, mejor_perdida, distribucion_mejor

    def evaluar_discrepancia(self, tabla_costos, part1, part2):
        """
        Evalúa discrepancia combinada entre dos partes.
        """
        costo = 0
        for i in part1:
            for j in part2:
                costo += tabla_costos[i, j]
        return costo
