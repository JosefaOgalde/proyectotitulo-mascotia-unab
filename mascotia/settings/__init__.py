# Settings package
"""
Configuración de Django para Mascotia.

Este archivo importa la configuración local desde local.py.
Si local.py no existe, el proyecto no funcionará.
Esto asegura que solo usuarios autorizados puedan ejecutar el proyecto.
"""

try:
    from .local import *
except ImportError:
    raise ImportError(
        "No se encontró el archivo de configuración local (local.py).\n"
        "Por favor, copia mascotia/settings/local.py.example a mascotia/settings/local.py\n"
        "y ajusta los valores según tu entorno.\n"
        "Este archivo no está en el repositorio por razones de seguridad."
    )

