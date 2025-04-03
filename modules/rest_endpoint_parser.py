# modules/rest_endpoint_parser.py
import re

PARAM_TEMPLATE = '                .param().name("{name}").type(RestParamType.{type}).description("{desc}").endParam()'
ENDPOINT_TEMPLATE = '''
                .{http_method}("{subpath}")
                .description("{description}"){type_line}
                .to("direct:{route_name}")
{param_lines}'''

METHOD_MAPPING = {
    "@GET": "get",
    "@POST": "post",
    "@PUT": "put",
    "@DELETE": "delete"
}

def parse_endpoints_from_class(content: str):
    endpoints = []

    methods = re.findall(
        r'(@\w+(?:\s*\(.*?\))?(?:\s*@\w+(?:\s*\(.*?\))?)*)\s+public\s+Response\s+(\w+)\s*\((.*?)\)\s*\{',
        content, re.DOTALL)

    for annotations_block, method_name, params_block in methods:
        annotations = re.findall(r'@\w+(?:\s*\(.*?\))?', annotations_block)

        http_verb = next((METHOD_MAPPING.get(a.split("(")[0]) for a in annotations if a.split("(")[0] in METHOD_MAPPING), None)
        if not http_verb:
            continue

        path_match = next((re.search(r'\("([^"]+)"\)', a) for a in annotations if "@Path" in a), None)
        subpath = path_match.group(1).strip("/") if path_match else method_name

        # Descripción
        desc_match = next((re.search(r'value\s*=\s*"([^"]+)"', a) for a in annotations if "@ApiOperation" in a), None)
        if not desc_match:
            desc_match = next((re.search(r'description\s*=\s*"([^"]+)"', a) for a in annotations if "@Operation" in a), None)
        description = desc_match.group(1) if desc_match else f"Api para {method_name}."

        # Ignorar @HeaderParam
        param_defs = [p for p in params_block.split(',') if "@HeaderParam" not in p]
        params_filtered = ", ".join(param_defs)

        # Tipo body
        type_class_match = re.search(r'(List<\s*(\w+)\s*>|\w+\[\]|\w+Request\w*|\w+Dto)', params_filtered)
        dto_type = type_class_match.group(1) if type_class_match else None
        dto_clean = None
        if dto_type:
            if "List<" in dto_type:
                inner_type = re.sub(r'List<\s*(\w+)\s*>', r'\1', dto_type)
                dto_clean = f"{inner_type}[]"
            else:
                dto_clean = dto_type

        type_line = f'\n                .type({dto_clean}.class)' if dto_clean else ""

        param_lines = []
        if dto_type:
            name_guess = re.search(r'(\w+)(Request|Dto)?', dto_clean.replace("[]", ""))
            name_param = name_guess.group(1).lower() if name_guess else "body"
            param_lines.append(PARAM_TEMPLATE.format(name=name_param, type="body", desc="Payload"))

        for qp in re.findall(r'@QueryParam\("([^"]+)"\)', params_block):
            param_lines.append(PARAM_TEMPLATE.format(name=qp, type="query", desc=f"Parámetro {qp}"))

        for pp in re.findall(r'@PathParam\("([^"]+)"\)', params_block):
            param_lines.append(PARAM_TEMPLATE.format(name=pp, type="path", desc=f"Segmento {pp}"))

        full_block = ENDPOINT_TEMPLATE.format(
            http_method=http_verb,
            subpath=f"/{subpath}" if subpath else "/",
            description=description,
            type_line=type_line,
            param_lines="\n".join(param_lines),
            route_name=method_name
        )

        endpoints.append(full_block)

    return "\n".join(endpoints)
