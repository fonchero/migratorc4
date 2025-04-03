import sys
import re
from pathlib import Path

def agregar_healthcheck(path_proyecto):
    base = Path(path_proyecto)
    archivos = list(base.rglob("*.java"))

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            # Verifica si es un servicio REST
            if "@Path" not in contenido:
                continue

            # Verifica si ya tiene health
            if re.search(r'@Path\("/health"\)', contenido):
                continue

            # Encuentra el último cierre de clase fuera de otros métodos
            lineas = contenido.splitlines()
            apertura = 0
            ultima_llave_clase = -1
            for i, linea in enumerate(lineas):
                apertura += linea.count("{") - linea.count("}")
                if apertura == 0:
                    ultima_llave_clase = i

            if ultima_llave_clase == -1:
                print(f"[WARN] Clase sin cierre válido: {archivo}")
                continue

            metodo_health = (
                "    @GET\n"
                "    @Path(\"/health\")\n"
                "    @Produces(MediaType.TEXT_PLAIN)\n"
                "    public Response health() {\n"
                "        return Response.ok(\"OK\").build();\n"
                "    }\n\n"
            )

            # Verifica si tiene los imports necesarios, si no, los agrega
            nuevos_imports = ""
            if "import jakarta.ws.rs.GET;" not in contenido:
                nuevos_imports += "import jakarta.ws.rs.GET;\n"
            if "import jakarta.ws.rs.Path;" not in contenido:
                nuevos_imports += "import jakarta.ws.rs.Path;\n"
            if "import jakarta.ws.rs.Produces;" not in contenido:
                nuevos_imports += "import jakarta.ws.rs.Produces;\n"
            if "import jakarta.ws.rs.core.MediaType;" not in contenido:
                nuevos_imports += "import jakarta.ws.rs.core.MediaType;\n"
            if "import jakarta.ws.rs.core.Response;" not in contenido:
                nuevos_imports += "import jakarta.ws.rs.core.Response;\n"

            if nuevos_imports:
                contenido = re.sub(r'(package .*?;\s+)', r"\1" + nuevos_imports, contenido, count=1)

            # Inserta el método justo antes del cierre final de la clase
            lineas.insert(ultima_llave_clase, metodo_health)

            with open(archivo, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas))

            print(f"[OK] Método health agregado en: {archivo}")

        except Exception as e:
            print(f"[ERROR] No se pudo modificar {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python agregar_healthcheck_service.py <ruta_proyecto>")
        sys.exit(1)

    agregar_healthcheck(sys.argv[1])
