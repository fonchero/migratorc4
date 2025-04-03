#ajustar_main_routebuilder.py
import sys
import re
from pathlib import Path

BLOQUE_INTERCEPT_SEGURO = (
    '        if (restEndpoint != null && !restEndpoint.isEmpty()) {\n'
    '            onIntercept(restEndpoint);\n'
    '        } else {\n'
    '            log.warn("Rest endpoint not set, skipping onIntercept()");\n'
    '        }\n'
)

def ajustar_main_routebuilder(path_proyecto):
    base = Path(path_proyecto)
    archivos = list(base.rglob("MainRouteBuilder.java"))

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            nuevas_lineas = []
            intercepto = False
            for linea in lineas:
                if "onIntercept(restEndpoint);" in linea and not intercepto:
                    nuevas_lineas.append(BLOQUE_INTERCEPT_SEGURO)
                    intercepto = True
                else:
                    nuevas_lineas.append(linea)

            with open(archivo, "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)

            print(f"[OK] Ajustado correctamente: {archivo}")

        except Exception as e:
            print(f"[ERROR] No se pudo ajustar {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_main_routebuilder.py <ruta_proyecto>")
        sys.exit(1)

    ajustar_main_routebuilder(sys.argv[1])
