# modules/method_parser.py
import re

def process_methods(content: str) -> str:
    method_pattern = re.compile(r'(public\s+Response\s+(\w+)\s*\((.*?)\)\s*\{)(.*?return\s+null;.*?)\}', re.DOTALL)

    used_body_annotation = False  # Flag to track if @Body was inserted

    def replace_method_body(match):
        nonlocal used_body_annotation

        method_name = match.group(2)
        raw_params = match.group(3)

        params = [p.strip() for p in raw_params.split(',') if p.strip()]
        query_params = []
        body_param = 'null'
        context_param = '@Context HttpHeaders httpHeaders'
        cleaned_params = []

        body_detected = False

        for param in params:
            if '@QueryParam' in param:
                match_q = re.search(r'@QueryParam\("(.*?)"\)\s+.*\s+(\w+)', param)
                if match_q:
                    query_params.append((match_q.group(1), match_q.group(2)))
                cleaned_params.append(param)

            elif '@HeaderParam' in param:
                cleaned_params.append(param)

            elif '@Context' in param:
                cleaned_params.append(param)

            elif re.search(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)', param):
                if not body_detected:
                    param = re.sub(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)', '@Body', param)
                    used_body_annotation = True
                    body_detected = True
                    body_param = param.split()[-1]
                else:
                    param = re.sub(r'@(?:ApiParam|TagParam)\s*\([^\)]*\)\s*', '', param)
                cleaned_params.append(param)

            else:
                if not body_detected:
                    param = f'@Body {param}'
                    used_body_annotation = True
                    body_detected = True
                    body_param = param.split()[-1]
                cleaned_params.append(param)

        if not any('@Context' in p for p in cleaned_params):
            cleaned_params.append(context_param)

        full_signature = f"public Response {method_name}({', '.join(cleaned_params)})"

        camel_call = f'        Object response = sendRequestToCamel("direct:{method_name}", {body_param}, httpHeaders, '
        if query_params:
            param_lines = ["        Map<String, String> params = Map.of(" + ", ".join(
                [f'"{k}", {v}' for k, v in query_params]) + ");"]
            camel_call += 'params);'
        else:
            param_lines = []
            camel_call += 'null);'

        return_stmt = '        return Response.ok(response).build();'
        new_body = '\n'.join(param_lines + [camel_call, return_stmt])
        return f'{full_signature} {{\n{new_body}\n    }}'

    # Apply transformation to methods
    content = method_pattern.sub(replace_method_body, content)

    # Inject import if needed
    if used_body_annotation and 'import org.apache.camel.Body;' not in content:
        import_line = 'import org.apache.camel.Body;'
        import_pos = content.find('import ')
        if import_pos != -1:
            matches = list(re.finditer(r'^import .*?;', content, re.MULTILINE))
            if matches:
                last = matches[-1]
                content = content[:last.end()] + f'\n{import_line}' + content[last.end():]

    return content
