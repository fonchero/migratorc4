#ajustar_services_path.py
import sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET
 
SWAGGER_IMPORTS = [
    "import io.swagger.v3.oas.annotations.Operation;",
    "import io.swagger.v3.oas.annotations.responses.ApiResponse;",
    "import io.swagger.v3.oas.annotations.responses.ApiResponses;",
    "import io.swagger.v3.oas.annotations.tags.Tag;",
    "import jakarta.enterprise.context.ApplicationScoped;"
]
 
def extraer_prefijo_path_desde_blueprint(path_proyecto):
    blueprint = list(Path(path_proyecto).rglob("blueprint.xml"))
    if not blueprint:
        print("[WARN] blueprint.xml no encontrado. Usando prefijo por defecto.")
        return "/api"
 
    try:
        tree = ET.parse(blueprint[0])
        root = tree.getroot()
        for elem in root.iter():
            if 'rsServer' in elem.tag and 'address' in elem.attrib:
                return elem.attrib['address']
    except Exception as e:
        print(f"[WARN] No se pudo procesar blueprint.xml: {e}")
 
    return "/api"
 
def ajustar_clase_service(path_file, path_prefix):
    with open(path_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
 
    new_lines = []
    clase = Path(path_file).stem
    package_inserted = False
    ya_tiene_scoped = False
    path_modificado = False
 
    for i, line in enumerate(lines):
        # Insertar imports después del package
        if line.strip().startswith("package ") and not package_inserted:
            new_lines.append(line)
            new_lines.append("\n".join(SWAGGER_IMPORTS) + "\n\n")
            package_inserted = True
            continue
 
        # Insertar @ApplicationScoped si no está
        if line.strip().startswith("public class") and not ya_tiene_scoped:
            new_lines.append("@ApplicationScoped\n")
            ya_tiene_scoped = True
 
        # Reemplazar @Api o @Tag
        if "@Api(" in line or "@Tag(" in line:
            tag_value = re.search(r'value\s*=\s*"([^"]+)"', line) or re.search(r'name\s*=\s*"([^"]+)"', line)
            tag = tag_value.group(1) if tag_value else clase.replace("Service", "")
            line = f'@Tag(name = "{tag}", description = "{tag}")\n'
 
        # Modificar solo la primera anotación @Path encontrada (a nivel de clase)
        if "@Path" in line and not path_modificado:
            match = re.search(r'@Path\("([^"]+)"\)', line)
            if match:
                current_path = match.group(1).strip("/")
                full_path = f'@Path("{path_prefix.rstrip("/")}/{current_path}")'
                line = re.sub(r'@Path\(".*?"\)', full_path, line)
                path_modificado = True
 
        new_lines.append(line)
 
    with open(path_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
 
    print(f"[OK] Ajustado: {path_file}")
 
def procesar_proyecto(path_proyecto):
    prefijo = extraer_prefijo_path_desde_blueprint(path_proyecto)
    for java_file in Path(path_proyecto).rglob("*.java"):
        with open(java_file, "r", encoding="utf-8") as f:
            contenido = f.read()
            if "@Path" in contenido and "public class" in contenido:
                ajustar_clase_service(java_file, prefijo)
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_services_path.py <ruta_proyecto_migrado>")
        sys.exit(1)
 
    procesar_proyecto(sys.argv[1])