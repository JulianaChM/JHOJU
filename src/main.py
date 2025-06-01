from src.controllers.manager import Manager

from src.controllers.strategies.q_nodes import QNodes
from src.controllers.strategies.phi import Phi
from src.controllers.strategies.geometric import Geometric
from src.controllers.strategies.force import BruteForce

def iniciar():

    # Punto de entrada principal
        	       #  ABCDEFGHIJKLMNOPQRST #
    estado_inicial = "100"
    condiciones =    "111"
    alcance =        "111" # FUTURO
    mecanismo =      "111" # PRESENTE

    config_sistema = Manager(estado_inicial=estado_inicial)
    # config_sistema.generar_red(dimensiones=25, datos_discretos=False)
    
    # analizador_fb = Phi(config_sistema)
    # analizador_fb = QNodes(config_sistema)
    analizador_fb = Geometric(config_sistema)
    # analizador_fb = BruteForce(config_sistema)

    sia_uno = analizador_fb.aplicar_estrategia(condiciones, alcance, mecanismo)

    print(sia_uno)
