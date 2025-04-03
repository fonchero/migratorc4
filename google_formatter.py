# modules/google_formatter.py
import subprocess
from pathlib import Path

def formatear_clases_java_con_google_format(ruta_base: Path):
    jar_path = Path("libs/google-java-format.jar").resolve()

    if not jar_path.exists():
        print(f"[WARN] No se encontró {jar_path}. Saltando formato.")
        return

    print(f"[STEP] Aplicando google-java-format en: {ruta_base}")

    java_files = list(ruta_base.rglob("*.java"))

    if not java_files:
        print(f"[WARN] No se encontraron archivos .java en {ruta_base}")
        return

    print(f"[INFO] Se encontraron {len(java_files)} archivos .java")

    for java_file in java_files:
        try:
            subprocess.run([
                "java", "-jar", str(jar_path), "--replace", str(java_file)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[OK] Formateado: {java_file.relative_to(ruta_base)}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error formateando {java_file.name}: {e.stderr.decode('utf-8')}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python google_formatter.py <ruta_proyecto>")
    else:
        ruta = Path(sys.argv[1]).resolve()
        formatear_clases_java_con_google_format(ruta)
