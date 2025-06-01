import itertools as it
import time
import numpy as np
import pandas as pd
from src.models.core.ncube import NCube
from src.funcs.base import (
    ABECEDARY,
    dec2bin,
    emd_efecto,
    lil_endian,
    count_bits,
    seleccionar_estado,
)
from src.funcs.format import fmt_biparticion
from src.controllers.manager import Manager

import math

from pyphi import Network, Subsystem
from pyphi.labels import NodeLabels
from pyphi.models.cuts import Bipartition, Part

from src.middlewares.slogger import SafeLogger
from src.middlewares.profile import profiler_manager, profile

from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.models.enums.distance import MetricDistance
from src.models.base.application import aplicacion


from src.constants.base import (
    NET_LABEL,
    TYPE_TAG,
)
from src.constants.models import (
    DUMMY_ARR,
    DUMMY_EMD,
    DUMMY_PARTITION,
    GEOMETRIC_ANALYSIS_TAG,
    GEOMETRIC_LABEL,
    GEOMETRIC_STRAREGY_TAG,
)

class Geometry(SIA):
    """Class Geometry is used as base for other strategies, bruteforce with pyphi."""

    def __init__(self, gestor: Manager) -> None:
        super().__init__(gestor)
        profiler_manager.start_session(
            f"{NET_LABEL}{len(gestor.estado_inicial)}{gestor.pagina}"
        )
        self.logger = SafeLogger(GEOMETRIC_STRAREGY_TAG)

        self.__tcubes = None
        self.__valor_estado_inicial = None
        ...

    @profile(context={TYPE_TAG: GEOMETRIC_ANALYSIS_TAG})
    def aplicar_estrategia(
        self,
        condiciones: str,
        alcance: str,
        mecanismo: str,
    ):
        self.sia_preparar_subsistema(
            condiciones,
            alcance,
            mecanismo,
        )

        inicial = tuple(
            bit
            for i, bit in enumerate(
                self.sia_subsistema.estado_inicial,
            )
            if i in self.sia_subsistema.dims_ncubos
        )
        subsistema = self.sia_subsistema
        cubos = subsistema.ncubos

        rows, cols = (
            subsistema.dims_ncubos.size,
            subsistema.indices_ncubos.size,
        )

        self.__tcubes = tuple(
            np.zeros(
                (2,) * rows,
                dtype=np.float32,
            )
            for _ in range(cols)
        )

        ejes = [tuple(1 if i == j else 0 for j in range(rows)) for i in range(rows)]

        print(inicial)

        for indice, ncubo_x in enumerate(subsistema.ncubos):
            # self.__valor_estado_inicial = ncubo_x.data[seleccionar_estado(inicial)]
            self.adyacencias(indice, inicial, ejes)

            print(f"{indice=}")

        self.identificar_biparticiones(inicial)

        return Solution(
            GEOMETRIC_LABEL,
            DUMMY_EMD,
            self.sia_dists_marginales,
            np.ndarray(DUMMY_ARR),
            DUMMY_PARTITION,
        )

    def identificar_biparticiones(self, estado_inicial: tuple[int, ...]):
        biparticiones = []

        ncubos = self.sia_subsistema.ncubos
        promedios = "promedios:", [x.data.mean() for x in ncubos]
        print(promedios)

        return biparticiones

    def adyacencias(
        self,
        posicion_cubo: int,
        estado_actual: tuple[int, ...],
        ejes_actuales: list[tuple[int, ...]],
        acarreo_ahora: float = 0,
        decrecimiento: float = 1,
    ):
        decrecimiento *= 0.5
        for iter, eje in enumerate(ejes_actuales):
            ejes_siguientes = ejes_actuales.copy()
            ejes_siguientes.pop(iter)

            estado_siguiente = self.bitwise_xor(estado_actual, eje)

            ncubo_x = self.sia_subsistema.ncubos[posicion_cubo]
            # tx = gamma [x[i] - x[j]] + acarreo (ver el costo de la transición anterior)
            coste = decrecimiento * (
                abs(
                    ncubo_x.data[seleccionar_estado(estado_siguiente)]
                    - self.sia_dists_marginales[posicion_cubo]
                )
                + acarreo_ahora
            )
            self.__tcubes[posicion_cubo][seleccionar_estado(estado_siguiente)] += coste

            self.adyacencias(
                posicion_cubo,
                estado_siguiente,
                ejes_siguientes,
                coste,
                decrecimiento,
            )

        # parts = [ adyacencias(...) for x in y ]

    def bitwise_xor(self, estado_actual: tuple[int, ...], eje_base: tuple[int, ...]):
        return tuple(
            i ^ j
            for i, j in zip(
                estado_actual,
                eje_base,
            )
        )

    def visualizar_resultados(self, tabla_t):
        # print(tabla_t, "\n")
        ultima_fila = tabla_t.iloc[-1]  # última fila
        indice_minimo = ultima_fila.idxmin()
        valor_minimo = ultima_fila.min()

        primal = self.sia_subsistema

        futuro = np.array([indice_minimo], dtype=np.int8)
        presente = np.array([], dtype=np.int8)
        bipartito = primal.bipartir(futuro, presente)
        emd_primal = emd_efecto(
            bipartito.distribucion_marginal(), self.sia_dists_marginales
        )
        # print(f"emd_primal: {emd_primal}")

        # generar una bipartición para validar:
        for index in self.sia_subsistema.indices_ncubos:
            partito = self.sia_subsistema
            futuro = np.array([index], dtype=np.int8)
            presente = np.array([], dtype=np.int8)

            bipartito = partito.bipartir(futuro, presente)
            vector_marginal = bipartito.distribucion_marginal()
            emd_resultante = emd_efecto(vector_marginal, self.sia_dists_marginales)

            # print(f"index: {index}, emd: {emd_resultante}")
        print(bipartito)