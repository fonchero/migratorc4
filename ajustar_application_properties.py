import os
import sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET
 
PROPIEDADES_FIJAS_TEMPLATE = """
quarkus.http.port=8484
quarkus.swagger-ui.always-include=true
quarkus.swagger-ui.path=/swagger-ui
 
# Información básica de la API
mp.openapi.extensions.smallrye.info.title=RESTful Service :: {artifactId}
mp.openapi.extensions.smallrye.info.version=V1
mp.openapi.extensions.smallrye.info.description=Api {artifactId} Compartamos
mp.openapi.extensions.smallrye.info.contact.name=Compartamos
mp.openapi.extensions.smallrye.info.contact.email=achavezca@compartamos.pe
 
quarkus.arc.enabled=true
quarkus.profile=dev
quarkus.log.level=DEBUG
quarkus.log.category."org.apache".level=DEBUG
quarkus.log.category."com.compartamos".level=INFO
"""
 
def extraer_artifact_id(path_pom):
    try:
        tree = ET.parse(path_pom)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        artifact = root.find("m:artifactId", ns)
        return artifact.text if artifact is not None else "Proyecto"
    except Exception as e:
        print(f"[WARN] No se pudo leer artifactId desde pom.xml: {e}")
        return "Proyecto"
 
def encontrar_claves_usadas(carpeta_java):
    claves = set()
    pattern_getprop = re.compile(r'getProperty\(\s*"([^"]+)"')
    pattern_curly = re.compile(r'\{\{\s*([^\}]+?)\s*\}\}')
    pattern_config = re.compile(r'@ConfigProperty\(\s*name\s*=\s*"([^"]+)"')
 
    for java_file in Path(carpeta_java).rglob("*.java"):
        with open(java_file, "r", encoding="utf-8") as f:
            contenido = f.read()
            claves.update(pattern_getprop.findall(contenido))
            claves.update(pattern_curly.findall(contenido))
            claves.update(pattern_config.findall(contenido))
    return claves
 
def leer_global_properties(path):
    props = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                clave, valor = line.strip().split("=", 1)
                props[clave.strip()] = valor.strip()
    return props
 
def encontrar_raiz_proyecto(carpeta_base):
    base = Path(carpeta_base).resolve()
    for root, dirs, _ in os.walk(base):
        if Path(root).name == "resources" and "main" in Path(root).parts:
            return Path(root)
    fallback = base / "src" / "main" / "resources"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback
 
def generar_application_properties(carpeta_proyecto, path_global_props):
    ruta_resources = encontrar_raiz_proyecto(carpeta_proyecto)
    archivo = ruta_resources / "application.properties"
 
    pom_path = Path(carpeta_proyecto) / "pom.xml"
    artifactId = extraer_artifact_id(pom_path)
 
    contenido = PROPIEDADES_FIJAS_TEMPLATE.format(artifactId=artifactId).strip() + "\n\n"
 
    ruta_java = Path(carpeta_proyecto) / "src" / "main" / "java"
    claves_usadas = encontrar_claves_usadas(ruta_java)
 
    props_global = leer_global_properties(path_global_props)
 
    propiedades_extra = []
    for clave in sorted(claves_usadas):
        if clave in props_global:
            propiedades_extra.append(f"{clave}={props_global[clave]}")
 
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(contenido)
        if propiedades_extra:
            f.write("# Propiedades adicionales detectadas en código Java\n")
            f.write("\n".join(propiedades_extra))
            f.write("\n")
 
    print(f"[OK] application.properties generado en: {archivo}")
 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ajustar_application_properties.py <carpeta_proyecto> <application-global.properties>")
        sys.exit(1)
 
    generar_application_properties(sys.argv[1], sys.argv[2])