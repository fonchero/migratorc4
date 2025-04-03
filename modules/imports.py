# modules/imports.py
import re

def fix_imports(content: str) -> str:
    # Encuentra todos los imports
    imports = re.findall(r'^import .*?;', content, flags=re.MULTILINE)
    if not imports:
        return content

    # Eliminar duplicados preservando orden
    seen = set()
    unique_imports = []
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)

    # Clasificación semántica de grupos de imports
    def import_key(line):
        if line.startswith('import java.'): return (0, line)
        if line.startswith('import javax.'): return (1, line)
        if line.startswith('import org.apache.'): return (2, line)
        if line.startswith('import com.'): return (3, line)
        if line.startswith('import com.fasterxml.jackson.'): return (4, line)
        if line.startswith('import io.swagger.'): return (5, line)
        if line.startswith('import jakarta.inject.'): return (6, line)
        if line.startswith('import jakarta.ws.rs.core.'): return (7, line)
        if line.startswith('import jakarta.ws.rs.'): return (8, line)
        if line.startswith('import jakarta.enterprise.'): return (9, line)
        return (10, line)

    sorted_imports = sorted(unique_imports, key=import_key)

    # Reconstruir bloque de imports ordenado
    ordered_block = '\n'.join(sorted_imports) + '\n\n'

    # Reemplazar el bloque original en el contenido
    content = re.sub(r'(^import .*?;\s*)+', ordered_block, content, flags=re.MULTILINE)
    return content
