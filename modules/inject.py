# modules/inject.py
import re

def inject_producer_and_context(content: str) -> str:
    lines = content.splitlines()

    # ========= 1. Agregar imports necesarios si faltan ==========
    required_imports = [
        'import org.apache.camel.ProducerTemplate;',
        'import jakarta.inject.Inject;',
        'import jakarta.ws.rs.core.Context;',
        'import jakarta.ws.rs.core.HttpHeaders;'
    ]

    existing_imports = re.findall(r'^import .*?;', content, re.MULTILINE)
    missing_imports = [imp for imp in required_imports if imp not in content]

    if missing_imports:
        # Buscar el último import o el package
        last_import = None
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                last_import = i

        if last_import is not None:
            for imp in reversed(missing_imports):
                lines.insert(last_import + 1, imp)
        else:
            # Insertar después del package si no hay imports
            for i, line in enumerate(lines):
                if line.strip().startswith('package '):
                    for imp in reversed(missing_imports):
                        lines.insert(i + 1, imp)
                    break

    # ========= 2. Inyectar ProducerTemplate si no existe ==========
    if 'ProducerTemplate' not in content:
        for i, line in enumerate(lines):
            if re.match(r'.*class\s+\w+\s*\{', line):
                indent = ' ' * (len(line) - len(line.lstrip()))
                lines.insert(i + 1, indent + '@Inject')
                lines.insert(i + 2, indent + 'ProducerTemplate producerTemplate;')
                lines.insert(i + 3, '')
                break

    # ========= 3. Insertar @Context HttpHeaders como último parámetro ==========
    def fix_signature_params(signature):
        if 'HttpHeaders' in signature:
            return signature

        open_parens = signature.count('(')
        close_parens = signature.count(')')
        if open_parens != close_parens:
            return signature

        parts = signature.rsplit(')', 1)
        if len(parts) == 2:
            before, after = parts
            if before.strip().endswith('('):
                return before + '@Context HttpHeaders httpHeaders)' + after
            elif before.strip().endswith(','):
                return before + ' @Context HttpHeaders httpHeaders)' + after
            else:
                return before + ', @Context HttpHeaders httpHeaders)' + after
        return signature

    new_lines = []
    for line in lines:
        if re.match(r'\s*public\s+Response\s+\w+\s*\(.*\).*', line):
            line = fix_signature_params(line)
        new_lines.append(line)

    return '\n'.join(new_lines)
