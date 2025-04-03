import os
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def convertir_blueprint_a_routebuilder(path_proyecto):
    path_base = Path(path_proyecto)
    blueprint_path = next(path_base.rglob("blueprint.xml"), None)

    if not blueprint_path:
        print("[WARN] No se encontró blueprint.xml")
        return

    try:
        tree = ET.parse(blueprint_path)
        root = tree.getroot()
        ns = {
            'camel': 'http://camel.apache.org/schema/blueprint'
        }

        routes = root.findall(".//camel:route", ns)
        if not routes:
            print("[WARN] No se encontraron rutas dentro de blueprint.xml")
            return

        class_name = "MigratedRoutes"
        output_dir = path_base / "src/main/java/com/migrated/routes"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{class_name}.java"

        java_code = f"""package com.migrated.routes;

import org.apache.camel.builder.RouteBuilder;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class {class_name} extends RouteBuilder {{
    @Override
    public void configure() {{
"""

        for route in routes:
            route_id = route.attrib.get("id", "")
            from_elem = route.find("camel:from", ns)
            if from_elem is not None:
                java_code += f'        from("{from_elem.attrib["uri"]}")\n'
            for step in route:
                tag = step.tag.split("}")[-1]
                if tag == "to":
                    java_code += f'            .to("{step.attrib["uri"]}")\n'
                elif tag == "log":
                    java_code += f'            .log("{step.attrib.get("message", "")}")\n'
            java_code += '            ;\n'

        java_code += "    }\n}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(java_code)

        print(f"[OK] Clase generada en: {output_path}")

        # Eliminar blueprint.xml
        blueprint_path.unlink()
        print(f"[OK] blueprint.xml eliminado: {blueprint_path}")

    except Exception as e:
        print(f"[ERROR] Fallo al procesar blueprint.xml: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python convertir_blueprint.py <ruta_proyecto_migrado>")
        sys.exit(1)

    convertir_blueprint_a_routebuilder(sys.argv[1])
