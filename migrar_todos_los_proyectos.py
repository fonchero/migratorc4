import subprocess
import sys
import shutil
import os
import stat
import time
from pathlib import Path

def eliminar_con_permisos(path):
    def onerror(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar {path}: {e}")

    for child in path.iterdir():
        try:
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child, onerror=onerror)
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar {child}: {e}")

def ejecutar_para_todos(in_path, out_path, pom_template_path, global_props_path, aplicar_format_flag, compilar_flag):
    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    pom_template_path = Path(pom_template_path).resolve()
    global_props_path = Path(global_props_path).resolve()

    inicio = time.time()

    if out_path.exists() and out_path.is_dir():
        print(f"[INFO] Limpiando carpeta de salida: {out_path}")
        eliminar_con_permisos(out_path)
    else:
        out_path.mkdir(parents=True, exist_ok=True)

    if not in_path.exists() or not in_path.is_dir():
        print(f"[ERROR] La carpeta IN no existe o no es válida: {in_path}")
        return

    proyectos = [d for d in in_path.iterdir() if d.is_dir()]
    if not proyectos:
        print("[WARN] No hay subproyectos en la carpeta IN.")
        return

    total = len(proyectos)
    exitosos = 0
    fallidos = 0

    for proyecto in proyectos:
        print(f"\n[INFO] Migrando proyecto: {proyecto.name}")
        comando = [
            sys.executable, "-u", "migrar_proyecto_completo.py",
            str(proyecto),
            str(out_path),
            str(pom_template_path),
            str(global_props_path),
            aplicar_format_flag,
            compilar_flag
        ]
        try:
            resultado = []
            proceso = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for linea in proceso.stdout:
                print(linea, end='', flush=True)
                resultado.append(linea)

            proceso.wait()
            joined_output = "".join(resultado)
            print(f"[KHAAA] joined_output {joined_output} gaaaaaaaaa")
            if "[OK] Migración completada para:" in joined_output:
                exitosos += 1
            else:
                fallidos += 1
                print(f"[ERROR] La migración de {proyecto.name} terminó con error")

        except Exception as e:
            print(f"[ERROR] Excepción al migrar {proyecto.name}: {e}")
            fallidos += 1

    fin = time.time()
    duracion_segundos = fin - inicio
    minutos = int(duracion_segundos // 60)
    segundos = int(duracion_segundos % 60)

    # Resumen final
    print("\n" + "=" * 60)
    print("[RESUMEN DE MIGRACIÓN]")
    print(f"Proyectos totales : {total}")
    print(f"[OK] Exitosos      : {exitosos}")
    print(f"[FAIL] Con errores : {fallidos}")
    print(f" Tiempo total     : {minutos} min {segundos} seg")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Uso: python migrar_todos_los_proyectos.py <carpeta_IN> <carpeta_OUT> <pom_template.xml> <application-global.properties> <aplicar_format (1|0)> <compilar_maven (1|0)>")
        sys.exit(1)

    carpeta_in = sys.argv[1]
    carpeta_out = sys.argv[2]
    pom_template = sys.argv[3]
    global_properties = sys.argv[4]
    aplicar_format_flag = sys.argv[5]
    compilar_flag = sys.argv[6]

    if aplicar_format_flag not in ("0", "1") or compilar_flag not in ("0", "1"):
        print("[ERROR] Los flags deben ser '0' o '1'")
        sys.exit(1)

    ejecutar_para_todos(carpeta_in, carpeta_out, pom_template, global_properties, aplicar_format_flag, compilar_flag)
