import os

def listar_archivos(carpeta_base):
    archivos = {}
    for dirpath, _, filenames in os.walk(carpeta_base):
        for f in filenames:
            ruta_absoluta = os.path.join(dirpath, f)
            ruta_relativa = os.path.relpath(ruta_absoluta, carpeta_base)
            tamaño = os.path.getsize(ruta_absoluta)
            archivos[ruta_relativa] = tamaño
    return archivos

def comparar_carpetas(in_dir, out_dir):
    archivos_in = listar_archivos(in_dir)
    archivos_out = listar_archivos(out_dir)

    print(f"{'Archivo':70} | {'IN (bytes)':>12} | {'OUT (bytes)':>12} | Estado")
    print("-" * 110)

    todos_los_archivos = set(archivos_in.keys()).union(archivos_out.keys())

    for archivo in sorted(todos_los_archivos):
        tamaño_in = archivos_in.get(archivo)
        tamaño_out = archivos_out.get(archivo)

        if tamaño_in is not None and tamaño_out is not None:
            estado = "Difiere" if tamaño_in != tamaño_out else "Igual"
        elif tamaño_in is None:
            estado = "Solo en OUT"
        else:
            estado = "Solo en IN"

        print(f"{archivo:70} | {str(tamaño_in or '-'):>12} | {str(tamaño_out or '-'):>12} | {estado}")

if __name__ == "__main__":
    carpeta_in = r"C:\Users\alfon\Downloads\TEST\IN\process-core-credits"
    carpeta_out = r"C:\Users\alfon\Downloads\TEST\OUT\process-core-credits"
    comparar_carpetas(carpeta_in, carpeta_out)
