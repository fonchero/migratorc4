import sys
from pathlib import Path
import re
 
NUEVO_METODO = """\
public Claims validateToken(String jwtToken) {
        try {
            return Jwts.parser() // Usar el builder para el parser
                    .setSigningKey(KEY.getBytes(StandardCharsets.UTF_8)) // Establecer la clave de firma
                    .build() // Construir el parser
                    .parseClaimsJws(jwtToken) // Parsear el JWT
                    .getBody(); // Obtener el cuerpo (claims)
        } catch (JwtException e) {
            // Manejo de excepciones si el token es inválido
            throw new IllegalArgumentException("JWT Token no válido", e);
        }
    }
"""
 
def ajustar_jwt_context_filter(path_proyecto):
    for java_file in Path(path_proyecto).rglob("JwtContextFilter.java"):
        with open(java_file, "r", encoding="utf-8") as f:
            contenido = f.read()
 
        # Reemplazar el método validateToken completo
        contenido_actualizado = re.sub(
            r'private\s+Claims\s+validateToken\s*\([^)]*\)\s*\{.*?\n\s*\}',
            NUEVO_METODO,
            contenido,
            flags=re.DOTALL
        )
 
        # Asegurar que los imports necesarios estén
        if "import java.nio.charset.StandardCharsets;" not in contenido_actualizado:
            match_import = re.search(r'(import\s+[a-zA-Z0-9\.\*]+;\s*)+', contenido_actualizado)
            if match_import:
                insert_pos = match_import.end()
                contenido_actualizado = (
                    contenido_actualizado[:insert_pos]
                    + "import java.nio.charset.StandardCharsets;\n"
                    + contenido_actualizado[insert_pos:]
                )
 
        if "import io.jsonwebtoken.JwtException;" not in contenido_actualizado:
            contenido_actualizado = contenido_actualizado.replace(
                "import io.jsonwebtoken.Claims;",
                "import io.jsonwebtoken.Claims;\nimport io.jsonwebtoken.JwtException;"
            )
 
        with open(java_file, "w", encoding="utf-8") as f:
            f.write(contenido_actualizado)
 
        print(f"[OK] JwtContextFilter ajustado en: {java_file}")
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ajustar_jwt_context_filter.py <ruta_proyecto_migrado>")
        sys.exit(1)
 
    ajustar_jwt_context_filter(sys.argv[1])