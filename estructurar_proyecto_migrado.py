import os
import shutil
from pathlib import Path
import sys

def encontrar_carpeta_raiz_valida(origen: Path) -> Path:
    """
    Busca recursivamente la carpeta que contiene src/ y pom.xml o .mvn, indicando que es la raíz real del proyecto.
    """
    for root, dirs, files in os.walk(origen):
        path_root = Path(root)
        if "src" in dirs and ("pom.xml" in files or ".mvn" in dirs):
            return path_root
    return origen  # fallback

def copiar_directorio_filtrado(origen: Path, destino: Path):
    """
    Copia el contenido del directorio origen al destino excluyendo cualquier 'src/test'
    """
    for root, dirs, files in os.walk(origen):
        path_root = Path(root)

        # Excluir carpetas src/test
        if "src" in path_root.parts and "test" in path_root.parts:
            continue

        rel_path = path_root.relative_to(origen)
        destino_actual = destino / rel_path
        destino_actual.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = path_root / file
            dst_file = destino_actual / file
            shutil.copy2(src_file, dst_file)

def estructurar_proyecto_fuera_de_subcarpeta(origen: Path, destino: Path):
    carpeta_raiz = encontrar_carpeta_raiz_valida(origen)

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True, exist_ok=True)

    copiar_directorio_filtrado(carpeta_raiz, destino)
    print(f"[OK] Proyecto copiado desde {carpeta_raiz} a {destino} (sin src/test)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python estructurar_proyecto_migrado.py <ruta_origen> <ruta_destino>")
        sys.exit(1)

    origen = Path(sys.argv[1])
    destino = Path(sys.argv[2])
    estructurar_proyecto_fuera_de_subcarpeta(origen, destino)
