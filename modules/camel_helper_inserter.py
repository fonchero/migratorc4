# camel_helper_inserter.py
import re

def ensure_camel_helper_method(content: str) -> str:
    if 'private Object sendRequestToCamel' in content:
        return content  # Ya existe

    uses_base_response = 'BaseResponse<' in content or 'BaseResponse ' in content

    # ======== 1. Asegurar imports necesarios ==========    
    required_imports = [
        'import java.util.Map;',
        'import java.util.stream.Collectors;',
        'import com.fasterxml.jackson.databind.ObjectMapper;',
        'import com.fasterxml.jackson.core.JsonProcessingException;',
        'import com.fasterxml.jackson.core.type.TypeReference;'
    ]

    existing_imports = re.findall(r'^import .*?;', content, re.MULTILINE)
    missing_imports = [imp for imp in required_imports if imp not in content]

    if missing_imports:
        all_imports = list(re.finditer(r'^import .*?;', content, re.MULTILINE))
        if all_imports:
            last_import = all_imports[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + '\n' + '\n'.join(missing_imports) + content[insert_pos:]
        else:
            package_match = re.search(r'^(package .*?;)', content, re.MULTILINE)
            if package_match:
                insert_pos = package_match.end()
                content = content[:insert_pos] + '\n\n' + '\n'.join(missing_imports) + '\n' + content[insert_pos:]

    # ======== 2. Construir los métodos helper ==========

    helper_method = '''

    private Object sendRequestToCamel(String endpoint, Object body, HttpHeaders httpHeaders,
                                      Map<String, String> queryParams) {
        Map<String, Object> headers = httpHeaders.getRequestHeaders()
                .entrySet()
                .stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().get(0)));

        if (queryParams != null) {
            queryParams.forEach((key, value) -> {
                if (value != null) {
                    headers.put(key, value);
                }
            });
        }

        Object response = producerTemplate.requestBodyAndHeaders(endpoint, body, headers);

        if (response instanceof String) {
            String responseString = (String) response;
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                return objectMapper.readValue(responseString, Map.class);
            } catch (JsonProcessingException e) {
                System.err.println("⚠ Error al deserializar respuesta de Camel: " + e.getMessage());
            }
        }

        return response;
    }
'''

    if uses_base_response:
        helper_method += '''

    private <T> BaseResponse<T> sendRequestToCamel(String endpoint, Object body, HttpHeaders httpHeaders, Class<T> responseType) {
        Map<String, Object> headers = httpHeaders.getRequestHeaders()
                .entrySet()
                .stream()
                .collect(Collectors.toMap(
                    Map.Entry::getKey,
                    e -> e.getValue().get(0)
                ));

        Object response = producerTemplate.requestBodyAndHeaders(endpoint, body, headers);
        BaseResponse<T> baseResponse = new BaseResponse<>();

        if (response instanceof String) {
            String responseString = (String) response;
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                T convertedResponse = objectMapper.readValue(responseString, responseType);
                baseResponse.setData(convertedResponse);
            } catch (JsonProcessingException e) {
                System.err.println("⚠ Error al deserializar respuesta de Camel: " + e.getMessage());
                baseResponse.setData(null);
                baseResponse.setMessage("Error al procesar la respuesta JSON");
            }
        } else {
            baseResponse.setData(responseType.cast(response));
        }

        return baseResponse;
    }

    private <T> BaseResponse<T> sendRequestToCamel(String endpoint, Object body, HttpHeaders httpHeaders, TypeReference<T> typeReference) {
        Map<String, Object> headers = httpHeaders.getRequestHeaders()
                .entrySet()
                .stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().get(0)));

        Object response = producerTemplate.requestBodyAndHeaders(endpoint, body, headers);
        BaseResponse<T> baseResponse = new BaseResponse<>();

        if (response instanceof String) {
            String responseString = (String) response;
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                T convertedResponse = objectMapper.readValue(responseString, typeReference);
                baseResponse.setData(convertedResponse);
            } catch (JsonProcessingException e) {
                System.err.println("⚠ Error al deserializar respuesta de Camel: " + e.getMessage());
                baseResponse.setData(null);
                baseResponse.setMessage("Error al procesar la respuesta JSON");
            }
        } else {
            baseResponse.setData((T) response);
        }

        return baseResponse;
    }
'''
    

    # ======== 3. Insertar helper antes de la última llave de cierre de clase ==========

    brace_stack = []
    for i, char in enumerate(content):
        if char == '{':
            brace_stack.append(i)
        elif char == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack:  # Última llave de cierre de la clase
                    content = content[:i] + helper_method + '\n' + content[i:]
                    break

    return content
