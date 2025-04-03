
import sys
from pathlib import Path
import re

def limpiar_y_ajustar_definicion_clase(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    nuevos_lines = []
    clase_insertada = False

    for i, line in enumerate(lines):
        # Eliminar caracteres invisibles sospechosos
        line = re.sub(r'[\x00-\x1F\x7F]', '', line)

        if "@ApplicationScoped" in line and not clase_insertada:
            nuevos_lines.append(line)
            # Buscar siguiente línea que no sea import o anotación
            for j in range(i+1, len(lines)):
                siguiente = lines[j].strip()
                if not siguiente.startswith("@") and "class" not in siguiente:
                    nuevos_lines.append("public class " + Path(file_path).stem + " {
")
                    clase_insertada = True
                    break
        elif re.match(r"^\s*class\s+", line) and not line.strip().startswith("public"):
            line = "public " + line.lstrip()
            nuevos_lines.append(line)
            clase_insertada = True
        else:
            nuevos_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(nuevos_lines)

def procesar_directorio(ruta):
    ruta = Path(ruta)
    archivos = list(ruta.rglob("*.java"))
    print(f"[INFO] Procesando {len(archivos)} archivos .java en: {ruta}")
    for archivo in archivos:
        limpiar_y_ajustar_definicion_clase(archivo)
        print(f"[FIXED] {archivo}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python limpiar_definicion_clases.py <ruta_del_proyecto>")
        sys.exit(1)

    procesar_directorio(sys.argv[1])
