import re
from typing import List

def camel_to_direct(method_name: str) -> str:
    s1 = re.sub(r'([a-z])([A-Z])', r'\1-\2', method_name).lower()
    return f"direct:{s1}"

def ajustar_respuestas_genericas(java_code: str) -> str:
    def build_return_line(method_name, return_type, body_name):
        endpoint = camel_to_direct(method_name)
        body = body_name or "null"
        if return_type.startswith("List<") or return_type.startswith("Map<"):
            return f'return sendRequestToCamel("{endpoint}", {body}, httpHeaders, new TypeReference<{return_type}>() {{}});'
        else:
            return f'return sendRequestToCamel("{endpoint}", {body}, httpHeaders, {return_type}.class);'

    def clean_params(params: str) -> str:
        body_assigned = False
        cleaned_params = []

        for part in [p.strip() for p in params.split(',') if p.strip()]:
            if re.search(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)', part):
                if not body_assigned:
                    part = re.sub(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)', '@Body', part)
                    body_assigned = True
                else:
                    part = re.sub(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)\s*', '', part)
            cleaned_params.append(part)

        cleaned = ', '.join(cleaned_params)
        cleaned = re.sub(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)\s*', '', cleaned)
        return cleaned

    def extract_body_name(params: str) -> str:
        if "@Body" in params:
            body_match = re.search(r"@Body\s+[\w<>\[\]]+\s+(\w+)", params)
            if body_match:
                return body_match.group(1)
        else:
            parts = [p.strip() for p in params.split(',') if p.strip()]
            for part in parts:
                if not re.search(r"@", part):  # no annotation
                    tokens = part.split()
                    if len(tokens) == 2:
                        return tokens[1]
        return None

    def transform_method(match):
        return_type = match.group(2)
        method_name = match.group(3)
        params = clean_params(match.group(4))

        body_name = extract_body_name(params)

        if "@Context HttpHeaders" not in params:
            if params.strip():
                params += ", "
            params += "@Context HttpHeaders httpHeaders"

        method_header = f"public BaseResponse<{return_type}> {method_name}({params})"
        return_line = build_return_line(method_name, return_type, body_name)
        return f"{method_header} {{\n        {return_line}\n    }}"

    pattern = re.compile(
        r'(public\s+BaseResponse\s*<\s*([\w<>\[\]]+)\s*>\s+(\w+)\s*\((.*?)\))\s*\{\s*return\s+null;\s*\}',
        re.DOTALL
    )

    return re.sub(pattern, transform_method, java_code)
