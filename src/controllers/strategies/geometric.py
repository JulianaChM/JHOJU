from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.funcs.format import fmt_biparte_q
from src.constants.models import (
    GEOMETRIC_LABEL,
    GEOMETRIC_STRATEGY_TAG,
    GEOMETRIC_ANALYSIS_TAG,
)
import time
import numpy as np


class Geometric(SIA):
    def __init__(self, gestor):
        super().__init__(gestor)

        self.tabla_costos: np.array  # Para guardar costos entre pares de estados
        self.biparticiones_candidatas = []  # Lista de biparticiones candidatas

    def aplicar_estrategia(self, condicion, alcance, mecanismo):
        """
        Implementa el algoritmo para encontrar la bipartición óptima
        utilizando el enfoque geométrico.
        """
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)

        # 1. Construir representación n-dimensional
        futuros = self.sia_subsistema.indices_ncubos
        presentes = self.sia_subsistema.dims_ncubos
        cubos = self.sia_subsistema.ncubos
        print(f"Futuros:   {futuros}")
        print(f"Presentes: {presentes}")
        print(f"Inicial:   {self.sia_subsistema.estado_inicial}")

        # 2. Calcular tabla de costos
        GAMMA = 1 / 2
        self.tabla_costos = np.zeros((futuros.size, presentes.size), dtype=np.float32)
        filas = self.get_filas_tabla_costos(self.sia_subsistema.estado_inicial)
        for cubo in cubos:
            for i, fila in enumerate(filas):
                prob_estado_inicial = self.get_valor_cubo_estado(
                    cubo, "".join(np.char.mod("%d", self.sia_subsistema.estado_inicial))
                )
                prob_estado_siguiente = self.get_valor_cubo_estado(cubo, fila)
                costo = GAMMA * np.abs(prob_estado_inicial - prob_estado_siguiente)
                # TODO: evaluar si costo cero para retornar ...
                self.tabla_costos[cubo.indice, i] = costo
        # print(self.tabla_costos)
        # 3. Identificar biparticiones candidatas
        # bipartir con nodos presentes 
        
        # 4. Evaluar y seleccionar la óptima
        # 5. Retornar resultado en formato Solution

        # Por ahora devolvemos un resultado vacío temporal

        return Solution(
            estrategia=GEOMETRIC_LABEL,
            perdida=0.0,
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=self.sia_dists_marginales,  # temporal
            particion="(sin calcular)",
            tiempo_total=time.time() - self.sia_tiempo_inicio,
        )

    def get_valor_cubo_estado(self, cubo, estado):
        """
        Retorna el valor del cubo en un estado dado.
        """
        valor = cubo.data
        for idx in reversed(estado):
            valor = valor[int(idx)]
        return valor

    def get_filas_tabla_costos(self, estado_inicial):
        """
        Retorna las filas de la tabla de costos.
        """
        n = len(estado_inicial)
        bin_str = estado_inicial.astype(str)
        combinaciones = []
        for i in range(n):
            nuevo_bit = "1" if bin_str[i] == "0" else "0"
            s = "".join([*bin_str[:i], nuevo_bit, *bin_str[i + 1 :]])
            combinaciones.append(s)
        return combinaciones