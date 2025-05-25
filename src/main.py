from src.controllers.manager import Manager

from src.controllers.strategies.q_nodes import QNodes
from src.controllers.strategies.phi import Phi
from src.controllers.strategies.geometric import Geometric

def iniciar():

    # Punto de entrada principal
        	       #  ABCDEFGHIJKLMNOPQRST #
    estado_inicial = "1000"
    condiciones =    "1110"
    alcance =        "1110" # FUTURO
    mecanismo =      "1110" # PRESENTE

    config_sistema = Manager(estado_inicial=estado_inicial)
    # config_sistema.generar_red(dimensiones=25, datos_discretos=False)
    
    # analizador_fb = Phi(config_sistema)
    # analizador_fb = QNodes(config_sistema)
    analizador_fb = Geometric(config_sistema)

    sia_uno = analizador_fb.aplicar_estrategia(condiciones, alcance, mecanismo)

    print(sia_uno)
