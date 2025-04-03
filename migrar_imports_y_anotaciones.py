import os
import re
from pathlib import Path
import sys

REEMPLAZOS_IMPORTS = {
    r'^import javax\.': 'import jakarta.',
    r'^import org\.springframework\.stereotype\..*;': '',  # Eliminar @Component, @Service
    r'^import org\.osgi\.service\.component\.annotations\..*;': '',  # Eliminar OSGi
    r'^import org\.apache\.cxf\.jaxrs\.ext\.Context;': 'import jakarta.ws.rs.core.Context;',
    r'^import io.swagger.annotations.*;': '',  # Swagger antiguo
}

REEMPLAZOS_INLINE = {
    r'@Component': '',
    r'@Service': '',
    r'@OsgiServiceProvider': '',
    r'@Api\("([^"]+)"\)': r'@Tag(name = "\1", description = "\1")',
    r'@ApiOperation\(value *= *"([^"]+)"\)': r'@Operation(summary = "\1")',
    r'new DefaultCamelContext\(\)': '',
}

ANOTACIONES_IMPORTS = {
    "@ApplicationScoped": "import jakarta.enterprise.context.ApplicationScoped;",
    "@Inject": "import jakarta.inject.Inject;",
    "@Tag": "import io.swagger.v3.oas.annotations.tags.Tag;",
    "@Operation": "import io.swagger.v3.oas.annotations.Operation;",
    "@ApiResponse": "import io.swagger.v3.oas.annotations.responses.ApiResponse;",
    "@ApiResponses": "import io.swagger.v3.oas.annotations.responses.ApiResponses;",
    "@Context": "import jakarta.ws.rs.core.Context;",
    "ProducerTemplate": "import org.apache.camel.ProducerTemplate;",
}

def reemplazar_cuerpo_filters(modificado):
    if 'public Response filters' in modificado:
        bloque_filters = r'public Response filters\([^\)]*\)\s*\{[^}]*\}'
        cuerpo_funcional = '''
    public Response filters(@HeaderParam("Authorization") String token, @QueryParam("idUsuario") String usuario,
                            @QueryParam("idOficina") String oficina, @Context HttpHeaders httpHeaders) {
        sendRequestToCamel("direct:filters", null, httpHeaders);
        return null;
    }

    private Object sendRequestToCamel(String endpoint, Object body, HttpHeaders httpHeaders) {
        Map<String, Object> headers = httpHeaders.getRequestHeaders()
                .entrySet()
                .stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().get(0)));
        return producerTemplate.requestBodyAndHeaders(endpoint, body, headers);
    }'''
        modificado = re.sub(bloque_filters, cuerpo_funcional.strip(), modificado, flags=re.DOTALL)
        print("[BODY] Reemplazado método 'filters' con cuerpo funcional.")
    return modificado

def limpiar_caracteres_invalidos(texto):
    return texto.replace('\u0001', '')

def procesar_archivo_java(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    original = ''.join(lineas)
    modificado = limpiar_caracteres_invalidos(original)

    for patron, reemplazo in REEMPLAZOS_IMPORTS.items():
        modificado = re.sub(patron, reemplazo, modificado, flags=re.MULTILINE)

    for patron, reemplazo in REEMPLAZOS_INLINE.items():
        modificado = re.sub(patron, reemplazo, modificado)

    if "class" in modificado and "@ApplicationScoped" not in modificado:
        modificado = re.sub(r'(public class )', '@ApplicationScoped\n\1', modificado, count=1)

    if re.search(r'\b(ProducerTemplate|LoggerTrace)\s+\w+;', modificado):
        modificado = re.sub(r'(?<!@Inject\s)\n(\s*)(ProducerTemplate|LoggerTrace)\s+(\w+);',
                            r'\n\1@Inject\n\1\2 \3;', modificado)

    for anotacion, import_line in ANOTACIONES_IMPORTS.items():
        if anotacion in modificado and import_line not in modificado:
            modificado = re.sub(r'(import .+?;\s*)+', lambda m: m.group(0) + import_line + '\n', modificado, count=1)

    if 'public Response filters' in modificado:
        modificado = reemplazar_cuerpo_filters(modificado)

    if 'sendRequestToCamel' in modificado and 'Collectors' not in modificado:
        modificado = re.sub(r'(import .+?;\s*)+', lambda m: m.group(0) +
                            "import java.util.Map;\n"
                            "import java.util.stream.Collectors;\n", modificado, count=1)

    if modificado != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modificado)
        print(f"[OK] Actualizado: {file_path}")
    else:
        print(f"[SKIP] Sin cambios: {file_path}")

def recorrer_proyecto_y_migrar_imports(ruta_proyecto):
    ruta_base = Path(ruta_proyecto)
    archivos_java = list(ruta_base.rglob("*.java"))
    print(f"[INFO] Procesando {len(archivos_java)} archivos .java en: {ruta_proyecto}")
    for archivo in archivos_java:
        procesar_archivo_java(archivo)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python migrar_imports_y_anotaciones.py <ruta_proyecto_migrado>")
        sys.exit(1)

    ruta = sys.argv[1]
    recorrer_proyecto_y_migrar_imports(ruta)
