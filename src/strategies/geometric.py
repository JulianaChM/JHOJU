import time
import numpy as np
from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.funcs.format import fmt_biparticion
from src.constants.models import GEOMETRIC_LABEL
from src.constants.base import EFECTO, ACTUAL


class Geometric(SIA):
    def __init__(self, gestor):
        super().__init__(gestor)
        self.tabla_costos: np.ndarray
        self.biparticion_prim = []
        self.perdida = np.inf
        self.dist_marginal: np.ndarray = None

    def aplicar_estrategia(self, condicion, alcance, mecanismo) -> Solution:
        """
        Ejecuta el algoritmo de bipartición óptima usando el enfoque geométrico.
        """
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)

        subsistema = self.sia_subsistema
        # print(f"Subsistema: {subsistema}")
        futuros = subsistema.indices_ncubos
        presentes = subsistema.dims_ncubos
        cubos = subsistema.ncubos

        num_presentes = presentes.size
        num_futuros = futuros.size
        self.tabla_costos = np.zeros((num_presentes, num_futuros), dtype=np.float32)
        GAMMA = 0.5

        estado_inicial = np.array(
            [bit for i, bit in enumerate(subsistema.estado_inicial) if i in presentes],
            dtype=np.int8,
        )

        filas_tabla_costos = self.generar_estados_vecinos(estado_inicial)

        for col, cubo in enumerate(cubos):
            estado_inicial_str = self.array_binario_a_str(estado_inicial)
            prob_inicial = self.get_valor_cubo_estado(cubo, estado_inicial_str)

            for i, estado_vecino in enumerate(filas_tabla_costos):
                prob_vecino = self.get_valor_cubo_estado(cubo, estado_vecino)
                costo = GAMMA * abs(prob_inicial - prob_vecino)
                self.tabla_costos[i, col] = costo

        self.seleccionar_biparticion_sacando_un_presente(
            presentes, futuros, estado_inicial, filas_tabla_costos
        )
        self.seleccionar_biparticion_sacando_un_futuro(presentes, futuros, cubos)

        biparticion_formateada = fmt_biparticion(
            [
                set(presentes) - set(self.biparticion_prim[ACTUAL]),
                set(futuros) - set(self.biparticion_prim[EFECTO]),
            ],
            [self.biparticion_prim[ACTUAL], self.biparticion_prim[EFECTO]],
        )

        return Solution(
            estrategia=GEOMETRIC_LABEL,
            perdida=self.perdida,
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=self.dist_marginal,
            particion=biparticion_formateada,
            tiempo_total=time.time() - self.sia_tiempo_inicio,
        )

    def seleccionar_biparticion_sacando_un_presente(
        self, presentes, futuros, estado_inicial, estados_vecinos
    ):
        """
        Determina la bipartición con menor pérdida en la tabla de costos.
        """
        for i, fila in enumerate(self.tabla_costos):
            perdida = np.sum(fila)
            if perdida < self.perdida:
                self.perdida = perdida
                self.biparticion_prim = [
                    self.obtener_presentes_no_cambiados(
                        estado_inicial, estados_vecinos[i], presentes
                    ),
                    futuros.tolist(),
                ]
                self.dist_marginal = fila

    def seleccionar_biparticion_sacando_un_futuro(self, presentes, futuros, cubos):
        """
        Determina la bipartición con menor pérdida sacando un nodo futuro.
        """
        promedios = [x.data.mean() for x in cubos]
        diferencias = [
            np.abs(promedio - self.sia_dists_marginales[i])
            for i, promedio in enumerate(promedios)
        ]
        indice_minimo = np.argmin(diferencias)
        if diferencias[indice_minimo] < self.perdida:
            self.perdida = diferencias[indice_minimo]
            self.dist_marginal = self.sia_dists_marginales.copy()
            self.dist_marginal[indice_minimo] = promedios[indice_minimo]

            self.biparticion_prim = [
                presentes.tolist(),
                [futuros[i] for i in range(len(futuros)) if i != indice_minimo],
            ]

    @staticmethod
    def obtener_presentes_no_cambiados(
        estado_inicial, estado_vecino_str, presentes
    ) -> list:
        """
        Devuelve los índices de los nodos presentes cuyos bits no cambiaron.
        """
        estado_vecino = np.fromiter(estado_vecino_str, dtype=int)
        iguales = np.array(estado_inicial) == estado_vecino
        return np.array(presentes)[iguales].tolist()

    @staticmethod
    def get_valor_cubo_estado(cubo, estado_str: str) -> float:
        """
        Extrae el valor del cubo dado un estado binario en forma de string.
        """
        valor = cubo.data
        for bit in reversed(estado_str):
            valor = valor[int(bit)]
        return valor

    @staticmethod
    def generar_estados_vecinos(estado_inicial: np.ndarray) -> list[str]:
        """
        Genera todas las combinaciones con un solo bit cambiado.
        """
        bin_str = estado_inicial.astype(str)
        combinaciones = []
        for i in range(len(estado_inicial)):
            nuevo_bit = "1" if bin_str[i] == "0" else "0"
            combinacion = "".join([*bin_str[:i], nuevo_bit, *bin_str[i + 1 :]])
            combinaciones.append(combinacion)
        return combinaciones

    @staticmethod
    def array_binario_a_str(array: np.ndarray) -> str:
        """
        Convierte un array binario a string de forma eficiente.
        """
        return "".join(np.char.mod("%d", array))
