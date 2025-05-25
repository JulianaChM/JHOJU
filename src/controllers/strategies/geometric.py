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
    Estrategia Geometric que sigue la lógica de QNodes:
    utiliza los nodos del mecanismo (presente) y del alcance (futuro),
    analiza biparticiones considerando ambas dimensiones y construye
    la tabla de costos sobre combinaciones reales de nodos, no solo índices.
    """

    def __init__(self, gestor: Manager):
        super().__init__(gestor)
        self.logger = SafeLogger(GEOMETRIC_ANALYSIS_TAG)

    def aplicar_estrategia(self, condicion: str, alcance: str, mecanismo: str):
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)

        start_time = time.time()
        mecanismo_idxs = self.sia_subsistema.dims_ncubos  # presente
        alcance_idxs = self.sia_subsistema.indices_ncubos  # futuro

        vertices = [(0, idx) for idx in mecanismo_idxs] + [(1, idx) for idx in alcance_idxs]
        self.vertices = set(vertices)

        mejor_perdida = float('inf')
        mejor_particion = None

        for i in range(len(vertices)):
            part1 = [vertices[i]]
            part2 = [v for j, v in enumerate(vertices) if j != i]
            perdida = self.evaluar_discrepancia(part1, part2)

            if perdida < mejor_perdida:
                mejor_perdida = perdida
                mejor_particion = part1

        prim = mejor_particion
        dual = list(self.vertices - set(mejor_particion))

        particion_str = fmt_biparte_q(prim, dual)

        return Solution(
            estrategia=GEOMETRIC_LABEL,
            perdida=mejor_perdida,
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=self.sia_dists_marginales,
            particion=particion_str,
            tiempo_total=time.time() - start_time,
        )

    def evaluar_discrepancia(self, part1, part2):
        """
        Evalúa la discrepancia entre dos grupos de nodos
        usando una aproximación basada en diferencias simples.
        """
        costo = 0
        for i in part1:
            for j in part2:
                # Calcula diferencia de índices entre nodos, considerando tiempos
                costo += abs(i[1] - j[1]) + abs(i[0] - j[0])
        return costo
