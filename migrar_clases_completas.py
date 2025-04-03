import os
import re
from pathlib import Path
import sys
 
CAMBIOS_IMPORTS = {
    "javax.ws.rs": "jakarta.ws.rs",
    "javax.inject": "jakarta.inject",
    "javax.annotation": "jakarta.annotation",
    "javax.enterprise.context": "jakarta.enterprise.context",
    "org.apache.camel.impl.DefaultCamelContext": "org.apache.camel.CamelContext",
}
 
REEMPLAZOS_LINEA = {
    "@ApiOperation": "@Operation",
    "@Api": "@Tag",
    "@ApiResponses": "@APIResponse",
    "@ApiResponse": "@APIResponse",
    "exchange.getOut()": "exchange.getMessage()"
}
 
IMPORTS_POR_USO = {
    "@Tag": "import io.swagger.v3.oas.annotations.tags.Tag;",
    "@Operation": "import io.swagger.v3.oas.annotations.Operation;",
    "@APIResponse": "import io.swagger.v3.oas.annotations.responses.ApiResponse;",
    "@ApplicationScoped": "import jakarta.enterprise.context.ApplicationScoped;",
    "@Inject": "import jakarta.inject.Inject;",
}
 
IMPORTS_A_ELIMINAR = [
    "import io.swagger.annotations.Api;",
    "import io.swagger.annotations.ApiOperation;",
    "import io.swagger.annotations.ApiResponses;",
    "import io.swagger.annotations.ApiResponse;",
]
 
def procesar_archivo_java(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
 
        contenido = "".join(lines)
 
        nuevos_lines = []
        for line in lines:
            if line.strip().startswith("import "):
                for viejo, nuevo in CAMBIOS_IMPORTS.items():
                    if viejo in line:
                        line = line.replace(viejo, nuevo)
                if any(swagger in line for swagger in IMPORTS_A_ELIMINAR):
                    continue
            for viejo, nuevo in REEMPLAZOS_LINEA.items():
                if viejo in line:
                    line = line.replace(viejo, nuevo)
            nuevos_lines.append(line)
 
        package_idx = -1
        for i, line in enumerate(nuevos_lines):
            if line.strip().startswith("package "):
                package_idx = i
                break
 
        if package_idx == -1:
            print(f"[WARN] No se encontró declaración de package en {path}")
            return
 
        imports_necesarios = []
        body_text = "".join(nuevos_lines)
        for key, import_stmt in IMPORTS_POR_USO.items():
            if key in body_text and import_stmt not in body_text:
                imports_necesarios.append(import_stmt + "\n")
 
        nuevos_lines = (
            nuevos_lines[:package_idx + 1]
            + ["\n"] + imports_necesarios + ["\n"]
            + nuevos_lines[package_idx + 1:]
        )
 
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(nuevos_lines)
 
        print(f"[OK] Migrado: {path}")
    except Exception as e:
        print(f"[ERROR] No se pudo procesar {path}: {e}")
 
def recorrer_y_migrar_clases(directorio_fuente):
    base = Path(directorio_fuente)
    if not base.exists():
        print(f"[ERROR] Ruta no encontrada: {directorio_fuente}")
        return
 
    for java_file in base.rglob("*.java"):
        procesar_archivo_java(java_file)
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python migrar_clases_completas_actualizado.py <carpeta_src_main_java>")
        sys.exit(1)
 
    ruta = sys.argv[1]
    recorrer_y_migrar_clases(ruta)