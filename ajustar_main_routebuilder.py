import sys
from pathlib import Path

BLOQUE_INTERCEPT_SEGURO = (
    '        if (restEndpoint != null && !restEndpoint.isEmpty()) {\n'
    '            onIntercept(restEndpoint);\n'
    '        } else {\n'
    '            log.warn("Rest endpoint not set, skipping onIntercept()");\n'
    '        }\n'
)

BLOQUE_REST_CONFIGURATION = (
    '        restConfiguration()\n'
    '            .host(host) // Especifica el host desde properties\n'
    '            .port(port) // Especifica el puerto desde properties\n'
    '            //.contextPath("/api") // Define el prefijo base para las rutas\n'
    '            .apiContextPath("/q/openapi") // Documentación OpenAPI\n'
    '            .apiProperty("api.title", "RESTful Service :: Campaign")\n'
    '            .apiProperty("api.version", "1.0")\n'
    '            .apiProperty("openapi.version", "3.0.0")\n'
    '            .apiProperty("cors", "true");\n'
    '            // .apiProperty("openapi.path", "/openapi");\n'
)

BLOQUE_IMPORTS_EXTRA = [
    'import org.eclipse.microprofile.config.inject.ConfigProperty;',
    'import jakarta.enterprise.context.ApplicationScoped;',
]

BLOQUE_CONFIG_PROPERTIES = [
    '    @ConfigProperty(name = "quarkus.http.host")',
    '    String host;',
    '',
    '    @ConfigProperty(name = "quarkus.http.port")',
    '    int port;',
    '',
    '    private String restEndpoint;',
    ''
]

def obtener_health_routes(path_proyecto: str):
    base = Path(path_proyecto)
    bloques = []
    for archivo in base.rglob("*Service.java"):
        nombre = archivo.stem.replace("Service", "")
        ruta = (
            f'        from("direct:health{nombre}")\n'
            f'            .setBody(constant("OK"));\n'
        )
        bloques.append(ruta)
    return bloques

def ajustar_main_routebuilder(path_proyecto):
    base = Path(path_proyecto)
    archivos = list(base.rglob("MainRouteBuilder.java"))
    health_routes = obtener_health_routes(path_proyecto)

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            nuevas_lineas = []
            intercepto = False
            insert_rest_config = True
            config_inyectado = False
            inject_scope_done = False
            ya_importados = set()
            clase_ya_anotada = False
            dentro_de_configure = False
            brace_balance = 0
            health_inserted = False

            for i, linea in enumerate(lineas):
                if "private String restEndpoint;" in linea:
                    continue

                if "restConfiguration()" in linea:
                    insert_rest_config = False

                if "onIntercept(restEndpoint);" in linea and not intercepto:
                    nuevas_lineas.append(BLOQUE_INTERCEPT_SEGURO)
                    intercepto = True
                    continue

                if linea.strip().startswith("import"):
                    ya_importados.add(linea.strip())

                if not inject_scope_done and "public class MainRouteBuilder" in linea:
                    for imp in BLOQUE_IMPORTS_EXTRA:
                        if imp not in ya_importados:
                            nuevas_lineas.append(imp + "\n")
                    if not clase_ya_anotada:
                        nuevas_lineas.append("\n@ApplicationScoped\n")
                        clase_ya_anotada = True
                    nuevas_lineas.append(linea)
                    nuevas_lineas.extend(l + "\n" for l in BLOQUE_CONFIG_PROPERTIES)
                    config_inyectado = True
                    inject_scope_done = True
                    continue

                # Detectar apertura del configure()
                if "public void configure()" in linea:
                    dentro_de_configure = True

                if dentro_de_configure:
                    brace_balance += linea.count("{") - linea.count("}")
                    # Insertar config y health antes del cierre del método configure()
                    if brace_balance == 0 and not health_inserted:
                        if insert_rest_config:
                            nuevas_lineas.append("\n" + BLOQUE_REST_CONFIGURATION + "\n")
                            insert_rest_config = False
                        nuevas_lineas.extend(health_routes)
                        health_inserted = True

                nuevas_lineas.append(linea)

            with open(archivo, "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)

            print(f"[OK] Ajustado correctamente: {archivo}")

        except Exception as e:
            print(f"[ERROR] No se pudo ajustar {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_main_routebuilder.py <ruta_proyecto>")
        sys.exit(1)

    ajustar_main_routebuilder(sys.argv[1])
