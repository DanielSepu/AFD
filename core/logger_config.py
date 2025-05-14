import logging

# Crear el formateador con detalles útiles para debugging
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | Line %(lineno)d ||> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Configurar el logger
logger_AFD = logging.getLogger("debugger")
logger_AFD.setLevel(logging.DEBUG)  # Puedes cambiar a INFO o WARNING en producción

# StreamHandler para salida en consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger_AFD.addHandler(console_handler)
