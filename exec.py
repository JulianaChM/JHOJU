from src.models.base.application import aplicacion
from src.main import iniciar
from src.middlewares.profile import profiler_manager

def main():
    """Inicializar el aplicativo."""
    profiler_manager.enabled = True

    # aplicacion.pagina_sample_network = "A"

    # print(f"{aplicacion.pagina_sample_network=}")

    iniciar()


if __name__ == "__main__":
    main()
