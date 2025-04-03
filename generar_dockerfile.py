import os
from pathlib import Path
import sys

DOCKERFILE_CONTENT = """FROM registry.access.redhat.com/ubi8/openjdk-21:1.20

ENV LANGUAGE='en_US:en'

# Copiar las dependencias y el código de la aplicación
COPY --chown=185 target/quarkus-app/lib/ /deployments/lib/
COPY --chown=185 target/quarkus-app/*.jar /deployments/
COPY --chown=185 target/quarkus-app/app/ /deployments/app/
COPY --chown=185 target/quarkus-app/quarkus/ /deployments/quarkus/

EXPOSE 8080
USER 185
ENV JAVA_OPTS_APPEND="-Dquarkus.http.host=0.0.0.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager"
ENV JAVA_APP_JAR="/deployments/quarkus-run.jar"

ENTRYPOINT ["java", "-jar", "/deployments/quarkus-run.jar"]
"""

def generar_dockerfile(ruta_proyecto):
    ruta = Path(ruta_proyecto)
    pom_path = next(ruta.rglob("pom.xml"), None)

    if not pom_path:
        print(f"[WARN] No se encontró pom.xml en {ruta}")
        return

    carpeta_proyecto = pom_path.parent
    dockerfile_path = carpeta_proyecto / "Dockerfile"

    if dockerfile_path.exists():
        print(f"[SKIP] Ya existe un Dockerfile en: {dockerfile_path}")
        return

    try:
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(DOCKERFILE_CONTENT)
        print(f"[OK] Dockerfile generado en: {dockerfile_path}")
    except Exception as e:
        print(f"[ERROR] No se pudo crear Dockerfile: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generar_dockerfile.py <ruta_proyecto_migrado>")
        sys.exit(1)

    generar_dockerfile(sys.argv[1])