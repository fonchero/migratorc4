# generar_service_routebuilder.py
import re
import sys
from pathlib import Path

from modules.rest_configuration_generator import generar_configuracion_rest
from modules.rest_endpoint_parser import parse_endpoints_from_class


# Plantilla base para el archivo RouteBuilder generado
TEMPLATE_ROUTE_BUILDER = '''\
package {package};

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.model.rest.RestParamType;

{imports}

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class {class_name} extends RouteBuilder {{

    @Override
    public void configure() throws Exception {{

{rest_config}

        rest("{base_path}")
        .tag("{tag}")
        .description("{description}")
{rest_endpoints}
        ;
    }}
}}
'''

def leer_puerto_desde_properties(path_proyecto):
    properties_path = Path(path_proyecto) / "src" / "main" / "resources" / "application.properties"
    if properties_path.exists():
        with open(properties_path, encoding="utf-8") as f:
            for line in f:
                if "quarkus.http.port" in line and not line.strip().startswith("#"):
                    try:
                        return int(line.split("=")[1].strip())
                    except:
                        break
    return 8080  # valor por defecto

def extraer_info_api(content: str, default_tag: str):
    api_match = re.search(r'@Api\s*\(.*?value\s*=\s*"([^"]+)".*?tags\s*=\s*\{\s*"([^"]+)"\s*}', content, re.DOTALL)
    if api_match:
        api_value = api_match.group(1)
        api_tag = api_match.group(2)
        plural = api_value.lower()
        if not plural.endswith("s"):
            plural += "s"
        return api_tag, f"API para gestionar {plural}"
    if not default_tag.lower().endswith("s"):
        plural = default_tag.lower() + "s"
    else:
        plural = default_tag.lower()
    return default_tag, f"API para gestionar {plural}"

def procesar_archivo_service(path_file: Path, ruta_proyecto: Path):
    with open(path_file, encoding="utf-8") as f:
        content = f.read()

    if "@Path" not in content or "public class" not in content:
        return

    # 1. Deducción de metadatos
    class_name = path_file.stem
    package_match = re.search(r'package\s+([\w\.]+);', content)
    package = package_match.group(1) if package_match else "com.example"

    tag_default = class_name.replace("Service", "")
    tag, description = extraer_info_api(content, tag_default)
    base_path = f"/api/process/campaign/{tag_default.lower()}"

    # 2. Imports
    imports = sorted(set(re.findall(r'import\s+[\w\.]+;', content)))
    imports = "\n".join(imp for imp in imports if package not in imp)

    # 3. Puerto dinámico desde properties
    puerto = leer_puerto_desde_properties(ruta_proyecto)

    # 4. Rest Configuration block
    rest_config = generar_configuracion_rest(ruta_proyecto, tag)

    # 5. Endpoints block
    rest_endpoints = parse_endpoints_from_class(content)

    # 6. Composición final
    resultado = TEMPLATE_ROUTE_BUILDER.format(
        package=package,
        imports=imports,
        class_name=class_name,
        rest_config=rest_config,
        base_path=base_path,
        tag=tag,
        description=description,
        rest_endpoints=rest_endpoints
    )

    destino = path_file.with_name(path_file.name.replace("Service", "RouteBuilder"))
    with open(destino, "w", encoding="utf-8") as f:
        f.write(resultado)

    print(f"[OK] Generado nuevo RouteBuilder en {destino}")
    path_file.unlink()

def procesar_proyecto(ruta_proyecto):
    ruta = Path(ruta_proyecto)
    for archivo in ruta.rglob("*Service.java"):
        procesar_archivo_service(archivo, ruta_proyecto)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generar_service_routebuilder.py <ruta_proyecto>")
        sys.exit(1)

    procesar_proyecto(sys.argv[1])
