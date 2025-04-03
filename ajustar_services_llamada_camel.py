# ajustar_services_llamada_camel.py
from modules.imports import fix_imports
from modules.method_parser import process_methods
from modules.inject import inject_producer_and_context
from modules.swagger_migration import migrate_swagger_annotations
from modules.camel_helper_inserter import ensure_camel_helper_method
from modules.ajustar_respuestas_genericas import ajustar_respuestas_genericas
from modules.tagparam_cleaner import clean_tagparam_annotations
from pathlib import Path


def process_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '@Path' not in content or 'return null;' not in content:
        return  # No es una clase candidata

    content = fix_imports(content)
    content = migrate_swagger_annotations(content)
    content = inject_producer_and_context(content)
    content = process_methods(content)
    content = ajustar_respuestas_genericas(content)
    content = ensure_camel_helper_method(content)
    content = clean_tagparam_annotations(content)
    

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Migrado: {file_path}")


def process_project(root_dir):
    for java_file in Path(root_dir).rglob('*.java'):
        process_java_file(java_file)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Uso: python main.py <ruta_proyecto>")
        sys.exit(1)
    process_project(sys.argv[1])
