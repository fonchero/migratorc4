import sys
import re
from pathlib import Path

PLANTILLA_FIX = """package {package};

import java.time.LocalDateTime;
import java.util.Objects;
import org.apache.hc.core5.util.Timeout;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.apache.camel.Exchange;
import org.apache.camel.LoggingLevel;
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.component.http.HttpComponent;

@ApplicationScoped
public abstract class RootRouteBuilder extends RouteBuilder {{

    @ConfigProperty(name = "seguridad.timeout")
    long time;

    @Inject
    LoggerTrace logTrace;

    public void onExceptions() {{
        onException(Exception.class)
                .handled(true)
                .logStackTrace(false)
                .logExhausted(false)
                .logHandled(true)
                .log(LoggingLevel.ERROR, Constants.LOG_ERROR)
                .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(500))
                .transform(simple(Messages.RESPONSE_ERROR_GENERIC_BASE))
                .stop();
    }}

    public void onInterceptLog() {{
        interceptSendToEndpoint("http*")
                .convertBodyTo(String.class)
                .end();
    }}

    public void onIntercept(String restEndpoint) {{
        from(restEndpoint).routeId("routeMain")
                .process(exchange -> {{
                    Object body = exchange.getIn().getBody();
                    exchange.setProperty(Constants.TOKEN, exchange.getIn().getHeader(Constants.AUTHORIZATION));
                    exchange.setProperty(Constants.USER_JWT, exchange.getIn().getHeader(Constants.USER_JWT));
                    exchange.setProperty(Constants.REQUEST, body);
                    exchange.setProperty(Constants.BODY, Functions.entityToJson(body));

                    Object uuid = exchange.getIn().getHeader(Constants.HEADER_TRACE_ID, Object.class);
                    if (Objects.isNull(uuid)) {{
                        uuid = Functions.getDefaultIdTrace(exchange);
                    }}
                    LocalDateTime startTimeRoot = LocalDateTime.now();

                    exchange.setProperty("startTimeRoot", startTimeRoot);
                    exchange.setProperty(Constants.TRACE_ID, uuid.toString());
                    exchange.setProperty(Constants.COUNT_TRACE, 0);
                }})
                .setProperty(Constants.CXF_SERVICE_URL, simple("${{" + "header.CamelCxfMessage[org.apache.cxf.request.url]" + "}}"))
                .bean(logTrace, Constants.FORMAT_REQUEST_ROOT)
                .toD("direct:${{" + "header.operationName" + "}}")
                .bean(logTrace, Constants.FORMAT_RESPONSE_ROOT)
                .end();
    }}

    public void configureTimeout() {{
        Timeout timeout = Timeout.ofMilliseconds(time);

        HttpComponent httpsComponent = getContext().getComponent(Constants.HTTPS_TIME_OUT, HttpComponent.class);
        HttpComponent httpComponent = getContext().getComponent(Constants.HTTP_TIME_OUT, HttpComponent.class);
        httpsComponent.setConnectionTimeToLive(time);
        httpsComponent.setSoTimeout(timeout);
        httpsComponent.setConnectTimeout(timeout);
        httpsComponent.setConnectionRequestTimeout(timeout);

        httpComponent.setConnectionTimeToLive(time);
        httpComponent.setSoTimeout(timeout);
        httpComponent.setConnectTimeout(timeout);
        httpComponent.setConnectionRequestTimeout(timeout);
    }}
}}
"""

def reemplazar_root_routebuilder(ruta_proyecto):
    ruta_base = Path(ruta_proyecto)
    archivos = list(ruta_base.rglob("RootRouteBuilder.java"))

    if not archivos:
        print("[WARN] No se encontró RootRouteBuilder.java")
        return

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                match = re.search(r'package\s+([\w\.]+);', contenido)
                package_name = match.group(1) if match else "com.example"

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(PLANTILLA_FIX.format(package=package_name))
            print(f"[OK] RootRouteBuilder sobrescrito en: {archivo}")

            # ===== Buscar y modificar Constants.java en el mismo paquete =====
            ruta_constants = archivo.parent / "Constants.java"
            if ruta_constants.exists():
                with open(ruta_constants, "r", encoding="utf-8") as f:
                    contenido_const = f.read()

                cambios = []
                if 'public static final String HTTP_TIME_OUT' not in contenido_const:
                    cambios.append('    public static final String HTTP_TIME_OUT = "http";')
                if 'public static final String HTTPS_TIME_OUT' not in contenido_const:
                    cambios.append('    public static final String HTTPS_TIME_OUT = "https";')

                if cambios:
                    contenido_const = re.sub(r'(public\s+class\s+Constants\s*\{)',
                                             r'\1\n' + '\n'.join(cambios),
                                             contenido_const)
                    with open(ruta_constants, "w", encoding="utf-8") as f:
                        f.write(contenido_const)
                    print(f"[OK] Constants.java actualizado con constantes TIME_OUT en: {ruta_constants}")
                else:
                    print("[INFO] Constants.java ya contenía las constantes necesarias.")

            else:
                print("[WARN] No se encontró Constants.java en el mismo paquete que RootRouteBuilder.java")

        except Exception as e:
            print(f"[ERROR] No se pudo sobrescribir {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_root_routebuilder.py <ruta_proyecto_migrado>")
        sys.exit(1)

    reemplazar_root_routebuilder(sys.argv[1])
