import sys
from pathlib import Path
import re
 
def reemplazar_expresiones_property(path_base):
    pattern = re.compile(r"\$\{property\.(\w+)}")
    reemplazo = lambda m: f"${{exchangeProperty.{m.group(1)}}}"
 
    for java_file in Path(path_base).rglob("*.java"):
        try:
            with open(java_file, "r", encoding="utf-8") as f:
                contenido = f.read()
 
            nuevo_contenido, num = pattern.subn(reemplazo, contenido)
 
            if num > 0:
                with open(java_file, "w", encoding="utf-8") as f:
                    f.write(nuevo_contenido)
                print(f"[OK] Reemplazado en: {java_file} ({num} ocurrencia(s))")
 
        except Exception as e:
            print(f"[ERROR] No se pudo procesar {java_file}: {e}")
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_property_expression.py <ruta_proyecto>")
        sys.exit(1)
 
    reemplazar_expresiones_property(sys.argv[1])