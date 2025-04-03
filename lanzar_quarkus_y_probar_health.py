import subprocess
import time
import requests
import sys
import re
from pathlib import Path

def leer_puerto_desde_properties(ruta_proyecto):
    propiedades = Path(ruta_proyecto) / "src" / "main" / "resources" / "application.properties"
    if propiedades.exists():
        with open(propiedades, "r", encoding="utf-8") as f:
            for linea in f:
                if "quarkus.http.port" in linea and not linea.strip().startswith("#"):
                    _, valor = linea.split("=", 1)
                    return int(valor.strip())
    return 8080

def extraer_rutas_healthcheck(path_proyecto):
    base = Path(path_proyecto)
    archivos = list(base.rglob("*Service.java"))
    rutas = []

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            if '@Path("/health")' not in contenido:
                continue

            paths = re.findall(r'@Path\("([^"]+)"\)', contenido)
            if not paths:
                continue

            paths = [p.strip("/") for p in paths if p.strip()]
            if not paths:
                continue

            base_path = "/".join(paths[:-1])  # todos menos /health
            full_path = f"/{base_path}/health"
            rutas.append(full_path)

        except Exception as e:
            print(f"[WARN] No se pudo analizar {archivo}: {e}")

    return rutas

def lanzar_quarkus_y_probar_health(ruta_proyecto):
    puerto = leer_puerto_desde_properties(ruta_proyecto)
    rutas = extraer_rutas_healthcheck(ruta_proyecto)
    if not rutas:
        print("[WARN] No se encontraron endpoints health para probar.")
        return False

    jar_path = Path(ruta_proyecto) / "target" / "quarkus-app" / "quarkus-run.jar"
    if not jar_path.exists():
        print(f"[ERROR] No se encontró el JAR ejecutable en: {jar_path}")
        return False

    print("\n[STEP] Ejecutando JAR de Quarkus...")
    proceso = subprocess.Popen(
        f"java -jar {jar_path}",
        cwd=ruta_proyecto,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    iniciado = False
    for _ in range(180):  # 180 seg máximo
        linea = proceso.stdout.readline()
        if not linea:
            break
        print(linea, end="")
        if "Listening on" in linea or f":{puerto}" in linea:
            iniciado = True
            break
        time.sleep(1)

    if not iniciado:
        print("[ERROR] No se detectó inicio exitoso de Quarkus")
        proceso.terminate()
        return False

    time.sleep(5)  # dar tiempo adicional para inicializar rutas

    # Probar cada ruta /health detectada
    exitosos = 0
    for ruta in rutas:
        url = f"http://localhost:{puerto}{ruta}"
        print(f"[INFO] Probar: {url}")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(f"[OK] Healthcheck OK: {url}")
                exitosos += 1
            else:
                print(f"[ERROR] Falló healthcheck {url} - Código: {r.status_code}")
        except Exception as e:
            print(f"[ERROR] Excepción en {url}: {e}")

    proceso.terminate()
    return exitosos == len(rutas)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python lanzar_quarkus_y_probar_health.py <ruta_proyecto>")
        sys.exit(1)

    ruta = sys.argv[1]
    exito = lanzar_quarkus_y_probar_health(ruta)
    if exito:
        print("\n[OK] Todos los endpoints health respondieron exitosamente.")
        sys.exit(0)
    else:
        print("\n[ERROR] Uno o más endpoints health fallaron.")
        sys.exit(1)
