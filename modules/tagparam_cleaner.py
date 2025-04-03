import re

def clean_tagparam_annotations(content: str) -> str:
    # 1. Remover importaciones de TagParam y ApiParam si existen
    content = re.sub(
        r'^\s*import\s+io\.swagger\.v3\.oas\.annotations\.tags\.TagParam;\s*\n?', 
        '', 
        content, 
        flags=re.MULTILINE
    )

    content = re.sub(
        r'^\s*import\s+io\.swagger\.annotations\.ApiParam;\s*\n?', 
        '', 
        content, 
        flags=re.MULTILINE
    )

    # 2. Reemplazar @TagParam(...) o @ApiParam(...) por @Body si no hay ya un @Body
    def replace_to_body(match):
        line = match.group(0)
        if '@Body' in line:
            return re.sub(r'@(TagParam|ApiParam)\s*\([^\)]*\)', '', line)
        return re.sub(r'@(TagParam|ApiParam)\s*\([^\)]*\)', '@Body', line)

    content = re.sub(
        r'@(TagParam|ApiParam)\s*\([^\)]*\)\s*[\w<>\[\]]+\s+\w+',
        replace_to_body,
        content
    )

    # 3. Si quedaron sueltos sin tipo, también limpiarlos
    content = re.sub(r'@(TagParam|ApiParam)\s*\([^\)]*\)\s*', '', content)

    # 4. Eliminar duplicados de @Body por si acaso
    content = re.sub(r'@Body\s+@Body\s+', '@Body ', content)

    return content
