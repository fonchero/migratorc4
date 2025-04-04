# agregar_healthcheck_service.py
import sys
from pathlib import Path
import re

BLOQUE_HEALTH_TEMPLATE = '''
                .get("/health")
                .description("Health check del servicio.")
                .routeId("health-{route_name}")
                .to("direct:health{route_pascal}")'''  # Aquí redirigimos a una ruta camel

def agregar_healthcheck(path_proyecto):
    base = Path(path_proyecto)
    archivos = list(base.rglob("*Service.java"))

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            if 'extends RouteBuilder' not in contenido or 'rest(' not in contenido:
                continue

            if 'get("/health")' in contenido:
                continue

            class_name = archivo.stem  # ej: OpportunityService
            route_name = class_name.replace("Service", "").lower()
            route_pascal = class_name.replace("Service", "")  # ej: Opportunity

            bloque_health = BLOQUE_HEALTH_TEMPLATE.format(
                route_name=route_name,
                route_pascal=route_pascal
            )

            match = re.search(r'(rest\([^\n]+)(.*?)(\n\s*;)', contenido, flags=re.DOTALL)
            if not match:
                print(f"[WARN] No se encontró bloque rest(...) en {archivo.name}")
                continue

            bloque_rest = match.group(0)
            nuevo_bloque_rest = bloque_rest.rstrip(";\n") + bloque_health + "\n        ;"

            nuevo_contenido = contenido.replace(bloque_rest, nuevo_bloque_rest)

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(nuevo_contenido)

            print(f"[OK] Health agregado a {archivo.name}")

        except Exception as e:
            print(f"[ERROR] {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python agregar_healthcheck_service.py <ruta_proyecto>")
        sys.exit(1)

    agregar_healthcheck(sys.argv[1])
