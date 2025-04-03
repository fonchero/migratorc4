
import sys
from pathlib import Path
import re

def ajustar_aggregation_strategy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "AggregationStrategy" not in content:
        return False

    content = re.sub(r'import\s+org\.apache\.camel\.processor\.aggregate\.AggregationStrategy;',
                     'import org.apache.camel.AggregationStrategy;', content)

    content = re.sub(r'import\s+org\.apache\.camel\.util\.CastUtils;\s*\n?', '', content)

    pattern = r'Map<.*?>\s+(\w+)\s*=\s*CastUtils\.cast\((.*?)\);'
    def replace_cast(match):
        var_name = match.group(1)
        value = match.group(2)
        return f'@SuppressWarnings("unchecked")\n        Map<String, Object> {var_name} = (Map<String, Object>) {value};'

    content = re.sub(pattern, replace_cast, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def procesar_directorio(ruta_base):
    for java_file in Path(ruta_base).rglob("*.java"):
        if ajustar_aggregation_strategy(java_file):
            print(f"[OK] Ajustado: {java_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_clases_aggregation_strategy.py <ruta_proyecto_migrado>")
        sys.exit(1)

    procesar_directorio(sys.argv[1])
