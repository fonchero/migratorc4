# rest_configuration_generator.py
from pathlib import Path

def obtener_puerto_desde_properties(ruta_proyecto):
    ruta = Path(ruta_proyecto) / "src" / "main" / "resources" / "application.properties"
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                if "quarkus.http.port" in linea and not linea.strip().startswith("#"):
                    _, valor = linea.split("=", 1)
                    return valor.strip()
    return "8080"  # valor por defecto

def generar_configuracion_rest(ruta_proyecto, nombre_servicio):
    puerto = obtener_puerto_desde_properties(ruta_proyecto)
    titulo = f"{nombre_servicio} API"

    return f'''\
        restConfiguration()
                .host("localhost") // Especifica el host
                .port({puerto}) // Especifica el puerto
                //.contextPath("/api") // Define el prefijo base para las rutas
                .apiContextPath("/q/openapi") // El path para acceder a la documentación OpenAPI
                .apiProperty("api.title", "{titulo}")
                .apiProperty("api.version", "1.0")
                .apiProperty("openapi.version", "3.0.0")
                .apiProperty("cors", "true");
                // .apiProperty("openapi.path", "/openapi");
'''
