import sys
import re
from pathlib import Path

METODO_REQUERIDO = """
    public static String getDefaultIdTrace(Exchange exchange) {
        DateTimeFormatter formatter = new DateTimeFormatterBuilder().parseDefaulting(ChronoField.OFFSET_SECONDS, 0)
                .appendPattern("yyyyMMddHHmmssSSS").toFormatter(Locale.ROOT);
        LocalDateTime date = LocalDateTime.now();
        String usuarioBT = (String) exchange.getIn().getHeader(Constants.USER_JWT);
        return String.join("-", date.format(formatter), usuarioBT, "00");
    }
"""

IMPORTS_REQUERIDOS = [
    "import java.time.LocalDateTime;",
    "import java.time.format.DateTimeFormatter;",
    "import java.time.format.DateTimeFormatterBuilder;",
    "import java.time.temporal.ChronoField;",
    "import java.util.Locale;",
    "import org.apache.camel.Exchange;"
]

def ajustar_functions(path_base):
    for java_file in Path(path_base).rglob("Functions.java"):
        with open(java_file, encoding="utf-8") as f:
            content = f.read()

        if "getDefaultIdTrace(Exchange exchange)" in content:
            print(f"[INFO] El método ya existe en {java_file}")
            continue

        print(f"[INFO] Ajustando archivo: {java_file}")

        # Agregar imports si faltan
        for imp in IMPORTS_REQUERIDOS:
            if imp not in content:
                content = content.replace("public class Functions {", f"{imp}\n\npublic class Functions {{")

        # Buscar la última llave de cierre que no pertenece a otro método
        ultima_llave = content.rstrip().rfind("}")
        if ultima_llave != -1:
            content = content[:ultima_llave].rstrip() + "\n" + METODO_REQUERIDO + "\n}\n"

            with open(java_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Método agregado correctamente en {java_file}")
        else:
            print(f"[ERROR] No se encontró cierre de clase en {java_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_functions_util.py <ruta_proyecto>")
        sys.exit(1)

    ajustar_functions(sys.argv[1])
