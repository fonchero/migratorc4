import sys
import re
from pathlib import Path

def ajustar_anotaciones_metodos(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    se_detecto_parameter = False

    while i < len(lines):
        line = lines[i]

        # Reemplazar @Operation(httpMethod = "...", value = "...", notes = "...")
        if "@Operation" in line and "httpMethod" in line:
            op_match = re.search(r'@Operation\(httpMethod\s*=\s*"[^"]*",\s*value\s*=\s*"([^"]+)",\s*notes\s*=\s*"([^"]+)"\)', line)
            if op_match:
                summary = op_match.group(1)
                description = op_match.group(2)
                line = f'@Operation(summary = "{summary}", description = "{description}")\n'

        # Reemplazar @TagResponses con @ApiResponses
        if "@TagResponses" in line:
            buffer = []
            j = i
            while j < len(lines) and not lines[j].strip().endswith("})"):
                buffer.append(lines[j])
                j += 1
            buffer.append(lines[j])  # incluir línea final
            i = j  # avanzamos el índice para continuar después del bloque

            # Transformar @TagResponse -> @ApiResponse
            joined = "".join(buffer)
            respuestas = re.findall(r'@TagResponse\(code\s*=\s*(\d+),\s*message\s*=\s*"([^"]+)"\)', joined)
            new_lines.append("@ApiResponses(value = {\n")
            for idx, (code, msg) in enumerate(respuestas):
                coma = "," if idx < len(respuestas) - 1 else ""
                new_lines.append(f'    @ApiResponse(responseCode = "{code}", description = "{msg}"){coma}\n')
            new_lines.append("})\n")
            i += 1
            continue

        # Reemplazar @ApiParam con @Parameter
        if "@ApiParam" in line:
            param_match = re.search(r'@ApiParam\(value\s*=\s*"([^"]+)",\s*required\s*=\s*(true|false)\)', line)
            if param_match:
                desc = param_match.group(1)
                required = param_match.group(2)
                line = f'@Parameter(description = "{desc}", required = {required})\n'
                se_detecto_parameter = True

        new_lines.append(line)
        i += 1

    # Insertar import si se usó @Parameter
    if se_detecto_parameter:
        contenido_total = "".join(new_lines)
        if "import io.swagger.v3.oas.annotations.Parameter;" not in contenido_total:
            for idx, linea in enumerate(new_lines):
                if "import jakarta.ws.rs.core.Response;" in linea:
                    new_lines.insert(idx + 1, "import io.swagger.v3.oas.annotations.Parameter;\n")
                    break

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"[OK] Anotaciones ajustadas en: {file_path}")

def procesar_proyecto(path_proyecto):
    for java_file in Path(path_proyecto).rglob("*.java"):
        with open(java_file, "r", encoding="utf-8") as f:
            contenido = f.read()
            if "@Path" in contenido and ("@Operation" in contenido or "@TagResponses" in contenido or "@ApiParam" in contenido):
                ajustar_anotaciones_metodos(java_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_anotaciones_metodos_service.py <ruta_proyecto_migrado>")
        sys.exit(1)

    procesar_proyecto(sys.argv[1])
