import sys
import re
from pathlib import Path
 
def reemplazar_token_en_consumer(path_proyecto):
    base_path = Path(path_proyecto)
    archivos = list(base_path.rglob("*.java"))
 
    if not archivos:
        print("[WARN] No se encontraron archivos .java")
        return
 
    patron_target = re.compile(
        r'exchange\.getMessage\(\)\.setHeader\s*\(\s*Constants\.AUTHORIZATION\s*,\s*exchange\.getProperty\s*\(\s*Constants\.TOKEN\s*,\s*String\.class\s*\)\s*\)'
    )
    reemplazo = 'exchange.getMessage().setHeader(Constants.AUTHORIZATION, exchange.getIn().getHeader(Constants.AUTHORIZATION, String.class))'
 
    for archivo in archivos:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
 
        if "extends RouteBuilder" not in contenido and "public static void consumer" not in contenido:
            continue
 
        nuevo_contenido, conteo = patron_target.subn(reemplazo, contenido)
 
        if conteo > 0:
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(nuevo_contenido)
            print(f"[OK] Reemplazo en: {archivo} ({conteo} ocurrencia(s))")
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_metodos_consumer.py <ruta_proyecto_migrado>")
        sys.exit(1)
 
    reemplazar_token_en_consumer(sys.argv[1])