# Instrucción IA: Gestión de Rutas y URLs

- Define las rutas en el archivo `urls.py` correspondiente al módulo.
- Usa el sistema de namespaces para evitar conflictos entre apps.
- Nombra las rutas con el prefijo del módulo y la acción (`contabilidad:transaccion_list`).
- Usa `reverse` y `{% url %}` en templates para evitar hardcoding de URLs.
- Documenta las rutas nuevas o modificadas.
