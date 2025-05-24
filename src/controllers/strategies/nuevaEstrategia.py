import time
import numpy as np
from src.funcs.base import ABECEDARY, lil_endian
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
    STR_ONE,
)
from src.constants.models import (
    DUMMY_ARR,
    DUMMY_PARTITION,
    PYPHI_LABEL,
    PYPHI_STRAREGY_TAG,
    PYPHI_ANALYSIS_TAG,
    
)


class NuevaEstrategia(SIA):
    def __init__(self, config: Manager) -> None:
        super().__init__(config)
        profiler_manager.start_session(
            f"{NET_LABEL}{len(config.estado_inicial)}{config.pagina}"
        )
        self.logger = SafeLogger(PYPHI_STRAREGY_TAG)

    @profile(context={TYPE_TAG: PYPHI_ANALYSIS_TAG})
    def aplicar_estrategia(self, condiciones: str, alcance: str, mecanismo: str):
        self.sia_tiempo_inicio = time.time()
        estado_inicial = tuple(int(s) for s in self.sia_gestor.estado_inicial)
        tamanho = len(estado_inicial)

        indices = tuple(range(tamanho))
        etiquetas = tuple(ABECEDARY[:tamanho])

        completo = NodeLabels(etiquetas, indices)
        mpt_estados_nodos_on = self.sia_cargar_tpm()
        red = Network(tpm=mpt_estados_nodos_on, node_labels=completo)

        mejor_phi = float('inf')
        mejor_biparticion = None
        mejor_distribucion_subsistema = np.array([])
        mejor_distribucion_particion = np.array([])

        for i in range(tamanho):
            for conjunto in [alcance, mecanismo]:
                candidato = list(completo)
                candidato.pop(i)

                alcance_tupla = tuple([ind for ind, (bit, cond) in enumerate(zip(alcance, condiciones)) if (bit == STR_ONE) and (cond == STR_ONE)])
                mecanismo_tupla = tuple([ind for ind, (bit, cond) in enumerate(zip(mecanismo, condiciones)) if (bit == STR_ONE) and (cond == STR_ONE)])

                if not alcance_tupla or not mecanismo_tupla:
                    self.logger.info("Alcance o mecanismo vacío, omitiendo partición.")
                    continue

                subsistema = Subsystem(network=red, state=estado_inicial, nodes=candidato)
                small_phi = float('inf')
                try:
                    mip = (
                        subsistema.effect_mip(mecanismo_tupla, alcance_tupla)
                        if aplicacion.distancia_metrica == MetricDistance.EMD_EFECTO.value
                        else subsistema.cause_mip(mecanismo_tupla, alcance_tupla)
                    )
                    print("mip", mip)
                    small_phi = mip.phi
                    distribucion_subsistema = mip.repertoire.flatten() if mip.repertoire is not None else np.array([])
                    distribucion_particion = mip.partitioned_repertoire.flatten() if mip.partitioned_repertoire is not None else np.array([])
                except KeyError as e:
                    self.logger.error(f"Error al calcular mip: {e}")
                    continue

                if small_phi == 0:
                    self.logger.info(f"Phi cero encontrado, nodo removido: {completo[i]}")
                    self.mostrar_biparticion(mip)
                    return Solution(
                        estrategia=PYPHI_LABEL,
                        perdida=small_phi,
                        distribucion_subsistema=distribucion_subsistema,
                        distribucion_particion=distribucion_particion,
                        particion=completo[i],
                        tiempo_total=time.time() - self.sia_tiempo_inicio
                    )

                if small_phi < mejor_phi:
                    mejor_phi = small_phi
                    mejor_biparticion = completo[i]
                    mejor_distribucion_subsistema = distribucion_subsistema
                    mejor_distribucion_particion = distribucion_particion

        self.logger.info(f"Mejor partición encontrada: {mejor_biparticion} con phi: {mejor_phi}")
        self.mostrar_biparticion(mip)
        return Solution(
            estrategia=PYPHI_LABEL,
            perdida=mejor_phi,
            distribucion_subsistema=mejor_distribucion_subsistema,
            distribucion_particion=mejor_distribucion_particion,
            particion=mejor_biparticion,
            tiempo_total=time.time() - self.sia_tiempo_inicio
        )

    def mostrar_biparticion(self, mip):
        self.logger.info("Mejor Bi-Partición:")
        self.logger.info("(")
        self.logger.info(f"    {mip.partition.parts[False].mechanism}")
        self.logger.info("    (" + ", ".join(map(str, mip.partition.parts[False].purview)) + ")")
        self.logger.info(")(")
        self.logger.info(f"    {mip.partition.parts[True].mechanism}")
        self.logger.info("    (" + ", ".join(map(str, mip.partition.parts[True].purview)) + ")")
        self.logger.info(")")
