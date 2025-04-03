import sys
import re
from pathlib import Path

PLANTILLA = """package {package};

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Properties;

public class SingletonProperties {{

    private static SingletonProperties instance = null;
    protected Properties propertiesIntegration;
    protected Properties propertiesLocal;

    private static final Properties prop = propertiesSimpleLocal();
    static String password = prop.getProperty("seguridad.hash_secret_key");
    static String algorithm = prop.getProperty("seguridad.hash_algorithm");

    private SingletonProperties() {{
        this.propertiesIntegration = propertiesSimpleLocal();
        this.propertiesLocal = propertiesSimpleLocal();
    }}

    public static SingletonProperties getInstance() {{
        if (instance == null) {{
            instance = new SingletonProperties();
        }}
        return instance;
    }}

    public static Properties propertiesSimpleLocal() {{
        Properties propiedades = new Properties();
        try (InputStreamReader inputStream = new InputStreamReader(
                Functions.class.getClassLoader().getResourceAsStream("application.properties"),
                StandardCharsets.UTF_8)) {{
            propiedades.load(inputStream);
        }} catch (IOException e) {{
            return propiedades;
        }}
        return propiedades;
    }}

    public Properties getPropertiesIntegration() {{
        return propertiesIntegration;
    }}

    public Properties getPropertiesLocal() {{
        return propertiesLocal;
    }}
}}
"""

def reemplazar_singleton_properties(ruta_proyecto):
    ruta_base = Path(ruta_proyecto)
    archivos = list(ruta_base.rglob("SingletonProperties.java"))

    if not archivos:
        print("[WARN] No se encontró SingletonProperties.java")
        return

    for archivo in archivos:
        try:
            # Detectar package actual si existe
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                match = re.search(r'package\s+([\w\.]+);', contenido)
                package_name = match.group(1) if match else "com.example"

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(PLANTILLA.format(package=package_name))
            print(f"[OK] SingletonProperties sobrescrito en: {archivo}")
        except Exception as e:
            print(f"[ERROR] No se pudo sobrescribir {archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_singleton_properties.py <ruta_proyecto_migrado>")
        sys.exit(1)

    reemplazar_singleton_properties(sys.argv[1])
