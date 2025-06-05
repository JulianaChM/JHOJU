from src.controllers.manager import Manager

from src.strategies.force import BruteForce
from src.strategies.q_nodes import QNodes
from src.strategies.geometric import Geometric


def iniciar():
    """Punto de entrada principal"""
    # ABCD #
    estado_inicial = "1000"
    condiciones =    "1111"
    alcance =        "1111"
    mecanismo =      "1111"

    gestor_sistema = Manager(estado_inicial)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    # analizador = QNodes(gestor_sistema)
    analizador = Geometric(gestor_sistema)
    # analizador = BruteForce(gestor_sistema)

    sia_cero = analizador.aplicar_estrategia(
        condiciones,
        alcance,
        mecanismo,
    )

    print(sia_cero)
