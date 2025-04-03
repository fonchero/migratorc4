import sys
import re
from pathlib import Path

PATRON_ANTERIOR = r'exchange\.setProperty\((.*?)\.ROUTE_ID,\s*exchange\.getUnitOfWork\(\)\.getRouteContext\(\)\.getRoute\(\)\.getIndex\(\)\)'  # incluye group para Constants.ROUTE_ID
REEMPLAZO_NUEVO = r'exchange.setProperty(\1.ROUTE_ID, exchange.getFromRouteId())'

def reemplazar_en_archivos(path_proyecto):
    base = Path(path_proyecto)
    archivos_java = list(base.rglob("*.java"))
    reemplazos = 0

    for archivo in archivos_java:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            nuevo_contenido, cantidad = re.subn(PATRON_ANTERIOR, REEMPLAZO_NUEVO, contenido)

            if cantidad > 0:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(nuevo_contenido)
                print(f"[OK] Reemplazado en {archivo} ({cantidad} ocurrencia(s))")
                reemplazos += cantidad

        except Exception as e:
            print(f"[ERROR] No se pudo procesar {archivo}: {e}")

    if reemplazos == 0:
        print("[INFO] No se encontraron patrones a reemplazar.")
    else:
        print(f"[DONE] Total reemplazos realizados: {reemplazos}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_setproperty_routeid.py <ruta_proyecto>")
        sys.exit(1)

    reemplazar_en_archivos(sys.argv[1])
