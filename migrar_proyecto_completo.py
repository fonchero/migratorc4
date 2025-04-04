#migrar_proyecto_completo.py
import subprocess
import sys
from pathlib import Path

errores = []

def ejecutar(nombre_script, argumentos):
    print(f"\n[STEP] Ejecutando: {nombre_script} {argumentos}")
    try:
        proceso = subprocess.Popen(
            ["python", nombre_script] + argumentos,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for linea in proceso.stdout:
            print(linea, end='')

        proceso.wait()
        if proceso.returncode != 0:
            print(f"[ERROR] {nombre_script} terminó con código {proceso.returncode}")
            errores.append(f"{nombre_script} (código {proceso.returncode})")
    except Exception as e:
        print(f"[ERROR] Excepción al ejecutar {nombre_script}: {e}")
        errores.append(f"{nombre_script} (excepción)")

def compilar_con_maven(ruta_proyecto):
    print("\n[STEP] Compilando proyecto migrado con Maven...")
    try:
        proceso = subprocess.Popen(
            "mvn clean package -DskipTests",
            cwd=ruta_proyecto,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for linea in proceso.stdout:
            print(linea, end='')

        proceso.wait()
        if proceso.returncode != 0:
            print(f"[ERROR] Fallo al compilar con Maven (código {proceso.returncode})")
            errores.append("compilación Maven (fallida)")
    except Exception as e:
        print(f"[ERROR] Excepción al compilar con Maven: {e}")
        errores.append("compilación Maven (excepción)")

def validar_healthcheck(ruta_proyecto):
    print("\n[STEP] Validando healthcheck...")
    resultado = subprocess.run([
        sys.executable, "lanzar_quarkus_y_probar_health.py", ruta_proyecto
    ])
    if resultado.returncode != 0:
        errores.append("healthcheck fallido")

def obtener_nombre_directorio(path_str):
    return Path(path_str).resolve().name

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Uso: python migrar_proyecto_completo.py <IN> <OUT> <pom_template> <application-global.properties> <formatear(1|0)> <compilar(1|0)>")
        sys.exit(1)

    ruta_in = Path(sys.argv[1]).resolve()
    ruta_out_base = Path(sys.argv[2]).resolve()
    ruta_pom_template = Path(sys.argv[3]).resolve()
    ruta_global_properties = Path(sys.argv[4]).resolve()
    aplicar_formateo = sys.argv[5] == "1"
    compilar_maven = sys.argv[6] == "1"

    if not ruta_in.exists():
        print(f"[ERROR] Carpeta IN no existe: {ruta_in}")
        sys.exit(1)

    nombre_proyecto = obtener_nombre_directorio(ruta_in)
    ruta_out = ruta_out_base / nombre_proyecto

    # Paso 1: copiar proyecto original
    ejecutar("estructurar_proyecto_migrado.py", [str(ruta_in), str(ruta_out)])

    # Paso 2: migrar pom.xml
    ejecutar("migrar_pom.py", [str(ruta_out), str(ruta_pom_template)])

    # Paso 3: modificar imports y anotaciones
    ejecutar("migrar_clases_completas.py", [str(ruta_out)])

    # Paso 4: convertir blueprint si corresponde
    ejecutar("convertir_blueprint.py", [str(ruta_out)])

    # Paso 5: sobreescribir RootRouteBuilder
    ejecutar("ajustar_root_routebuilder.py", [str(ruta_out)])

    # Paso 5.5: sobreescribir LoggerTrace
    ejecutar("ajustar_logger_trace.py", [str(ruta_out)])

    # Paso 5.6: sobreescribir SingletonProperties
    ejecutar("ajustar_singleton_properties.py", [str(ruta_out)])

    # Paso 5.6.1: actualizar JwtContextFilter
    ejecutar("ajustar_jwt_context_filter.py", [str(ruta_out)])

    # Paso 5.7: actualizar métodos consumer (header Authorization)
    ejecutar("ajustar_metodos_consumer.py", [str(ruta_out)])

    # Paso 5.8: ajustar @Path y anotaciones de servicios REST
    #ejecutar("ajustar_services_path.py", [str(ruta_out)])

    # Paso 5.9: ajustar anotaciones en métodos de servicios REST
    #ejecutar("ajustar_anotaciones_metodos_service.py", [str(ruta_out)])

    # Paso 5.9.1: ajustar MainRouteBuilder si existe
    ejecutar("ajustar_main_routebuilder.py", [str(ruta_out)])

    # Nuevo enfoque RouteBuilder nativo para REST----------------------------<<<<<<<<<<<<<<<<<<
    ejecutar("generar_service_routebuilder.py", [str(ruta_out)])
    
    # Paso 5.9.2: reemplazar return null por llamada a producerTemplate y agregar lógica de envío
    #ejecutar("ajustar_services_llamada_camel.py", [str(ruta_out)])

    # Paso 5.9.3: ajustar clases que implementaban AggregationStrategy
    ejecutar("ajustar_clases_aggregation_strategy.py", [str(ruta_out)])

    # Paso 5.10: actualizar expresiones ${property.*} a ${exchangeProperty.*}
    ejecutar("ajustar_property_expression.py", [str(ruta_out)])

    # Paso 5.11: asegurar que Functions.java tenga getDefaultIdTrace(Exchange exchange)
    ejecutar("ajustar_functions_util.py", [str(ruta_out)])

    # Paso 5.11.1: reemplazar setProperty(routeId...) por getFromRouteId()
    ejecutar("ajustar_exchange_setproperty.py", [str(ruta_out)])

    # Paso 5.12: agregar métodos de healthcheck a los servicios
    ejecutar("agregar_healthcheck_service.py", [str(ruta_out)])

    # Paso 6: generar Dockerfile actualizado
    ejecutar("generar_dockerfile.py", [str(ruta_out)])

    # Paso 7: crear application.properties desde archivo global
    ejecutar("ajustar_application_properties.py", [str(ruta_out), str(ruta_global_properties)])

    # Paso 8: aplicar formato con google-java-format solo si se indicó
    if aplicar_formateo:
        ejecutar("google_formatter.py", [str(ruta_out)])

    # Paso 9: compilar el proyecto con maven solo si se indicó
    if compilar_maven:
        compilar_con_maven(str(ruta_out))
        # Paso 10: ejecutar healthcheck solo si compila correctamente
        if "compilación Maven (fallida)" not in errores and "compilación Maven (excepción)" not in errores:
            validar_healthcheck(str(ruta_out))
    
    if errores:
        print(f"\n[ERROR] Migración con errores para: {nombre_proyecto}")
        print("Resumen de errores:")
        for error in errores:
            print(f" - {error}")
    else:
        print(f"\n[OK] Migración completada para: {nombre_proyecto}")
