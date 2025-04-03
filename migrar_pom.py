from pathlib import Path
import sys

def generar_pom_desde_template(ruta_proyecto, ruta_template):
    ruta_proyecto = Path(ruta_proyecto)
    ruta_template = Path(ruta_template)

    nombre = ruta_proyecto.name
    group_id = "com.compartamos.process"
    artifact_id = nombre
    version = "4.0.0"
    packaging = "jar"
    name = f"Api Process {nombre.replace('process-', '').replace('-', ' ').title()}"

    with ruta_template.open("r", encoding="utf-8") as f:
        contenido = f.read()

    contenido = contenido.replace("${groupId}", group_id)
    contenido = contenido.replace("${artifactId}", artifact_id)
    contenido = contenido.replace("${version}", version)
    contenido = contenido.replace("${packaging}", packaging)
    contenido = contenido.replace("${name}", name)

    ruta_pom = ruta_proyecto / "pom.xml"
    ruta_pom.write_text(contenido, encoding="utf-8")
    print(f"[OK] pom.xml generado en: {ruta_pom}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python migrar_pom.py <carpeta_proyecto> <pom_template>")
        sys.exit(1)
    
    generar_pom_desde_template(sys.argv[1], sys.argv[2])
