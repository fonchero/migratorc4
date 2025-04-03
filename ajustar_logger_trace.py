import sys
import re
from pathlib import Path

PLANTILLA = r"""package {package};

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import org.apache.camel.spi.Synchronization;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.google.common.base.Strings;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class LoggerTrace implements Processor, Synchronization {{
    private static final Logger LOG = LoggerFactory.getLogger(LoggerTrace.class);

    @Override
    public void process(Exchange exchange) {{
        if (exchange.getMessage().getBody() == null) {{
            LocalDateTime startTime = LocalDateTime.now();
            exchange.setProperty("startTime", startTime);
            StringBuilder messageIn = new StringBuilder();
            int countTrace = exchange.getProperty(Constants.COUNT_TRACE, int.class) + 1;
            exchange.setProperty(Constants.COUNT_TRACE, countTrace);

            messageIn.append("[" + exchange.getProperty(Constants.TRACE_ID) + "] ");
            messageIn.append("#(" + countTrace + ")-REQUEST");
            messageIn.append(Constants.LOG_TRACE_METHOD + exchange.getIn().getHeader(Exchange.HTTP_METHOD, String.class));
            messageIn.append(Constants.LOG_TRACE_PATH
                    + exchange.getIn().getHeader(Exchange.INTERCEPTED_ENDPOINT, String.class).replace("%7C", "|"));
            messageIn.append(Constants.LOG_TRACE_PAYLOAD + exchange.getIn().getBody(String.class));
            if (LOG.isInfoEnabled()) {{
                LOG.info(messageIn.toString().replaceAll("assword:\\\"[^&]*\\\"", "assword:\\\"******\\\""));
            }}
        }}
    }}

    @Override
    public void onComplete(Exchange exchange) {{
        if (exchange.getMessage().getBody() == null) {{
            try {{
                String bodyOut = exchange.getMessage().getBody(String.class);
                exchange.getMessage().setBody(bodyOut);

                LocalDateTime startTime = exchange.getProperty("startTime", LocalDateTime.class);
                LocalDateTime endTime = LocalDateTime.now();
                long latence = ChronoUnit.MILLIS.between(startTime, endTime);

                int countTrace = exchange.getProperty(Constants.COUNT_TRACE, int.class);

                StringBuilder messageOut = new StringBuilder();
                messageOut.append("[" + exchange.getProperty(Constants.TRACE_ID) + "] ");
                messageOut.append("#(" + countTrace + ")-RESPONSE");
                messageOut.append(Constants.LOG_TRACE_LATENCE + latence + "ms");
                messageOut.append(Constants.LOG_TRACE_METHOD + exchange.getIn().getHeader(Exchange.HTTP_METHOD, String.class));
                messageOut.append(Constants.LOG_TRACE_PATH
                        + exchange.getIn().getHeader(Exchange.INTERCEPTED_ENDPOINT, String.class));
                messageOut.append(Constants.LOG_TRACE_STATUS
                        + exchange.getMessage().getHeader(Exchange.HTTP_RESPONSE_CODE, String.class));
                messageOut.append(Constants.LOG_TRACE_PAYLOAD + bodyOut);
                if (LOG.isInfoEnabled()) {{
                    LOG.info(messageOut.toString());
                }}
            }} catch (Exception e) {{
                LOG.error(Constants.LOG_ERROR);
            }}
        }}
    }}

    @Override
    public void onFailure(Exchange exchange) {{
        LOG.error(Constants.LOG_ERROR);
    }}

    public void formatRequestRoot(Exchange exchange) {{
        StringBuilder messageIn = new StringBuilder();
        messageIn.append("[" + exchange.getProperty(Constants.TRACE_ID) + "] ");
        messageIn.append("REQUEST");
        messageIn.append(Constants.LOG_TRACE_METHOD + exchange.getIn().getHeader(Exchange.HTTP_METHOD, String.class));
        messageIn.append(Constants.LOG_TRACE_PATH + exchange.getProperty(Constants.CXF_SERVICE_URL, String.class));
        messageIn.append(Constants.LOG_TRACE_PAYLOAD + exchange.getProperty(Constants.BODY, String.class));
        if (LOG.isInfoEnabled()) {{
            LOG.info(messageIn.toString().replaceAll("assword:\\\"[^&]*\\\"", "assword:\\\"******\\\""));
        }}
    }}

    public void formatResponseRoot(Exchange exchange) {{
        try {{
            LocalDateTime startTimeRoot = exchange.getProperty("startTimeRoot", LocalDateTime.class);

            String statusCode = Strings
                    .isNullOrEmpty(exchange.getIn().getHeader(Exchange.HTTP_RESPONSE_CODE, String.class)) ? "200"
                            : exchange.getIn().getHeader(Exchange.HTTP_RESPONSE_CODE, String.class);
            Object bodyOut = exchange.getIn().getBody(Object.class);
            exchange.getMessage().setBody(bodyOut);

            LocalDateTime endTimeRoot = LocalDateTime.now();
            long latence = ChronoUnit.MILLIS.between(startTimeRoot, endTimeRoot);

            StringBuilder messageOut = new StringBuilder();
            messageOut.append("[" + exchange.getProperty(Constants.TRACE_ID) + "] ");
            messageOut.append("RESPONSE");
            messageOut.append(Constants.LOG_TRACE_LATENCE + latence + "ms");
            messageOut.append(Constants.LOG_TRACE_PATH + exchange.getProperty(Constants.CXF_SERVICE_URL, String.class));
            messageOut.append(Constants.LOG_TRACE_STATUS + statusCode);
            messageOut.append(Constants.LOG_TRACE_PAYLOAD + Functions.entityToJson(bodyOut));
            if (LOG.isInfoEnabled()) {{
                LOG.info(messageOut.toString());
            }}
        }} catch (Exception e) {{
            LOG.error(Constants.LOG_ERROR);
        }}
    }}
}}
"""

def reemplazar_logger_trace(ruta_proyecto):
    ruta_base = Path(ruta_proyecto)
    archivos = list(ruta_base.rglob("LoggerTrace.java"))

    if not archivos:
        print("[WARN] No se encontró LoggerTrace.java")
        return

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
            match = re.search(r'package\s+([\w\.]+);', contenido)
            package_name = match.group(1) if match else "com.example"

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(PLANTILLA.format(package=package_name))
            print(f"[OK] LoggerTrace sobrescrito en: {archivo}")
        except Exception as e:
            print(f"[ERROR] No se pudo sobrescribir {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_logger_trace.py <ruta_proyecto_migrado>")
        sys.exit(1)

    reemplazar_logger_trace(sys.argv[1])
