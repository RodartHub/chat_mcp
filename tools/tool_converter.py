def clean_schema_for_gemini(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    
    allowed_keys = {"type", "properties", "required", "description", "enum", "items"}
    
    cleaned = {}
    for k, v in schema.items():
        # Saltar campos no permitidos
        if k not in allowed_keys:
            continue
        
        if isinstance(v, dict):
            cleaned[k] = clean_schema_for_gemini(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_schema_for_gemini(i) for i in v]
        else:
            cleaned[k] = v
    
    return cleaned

def mcp_to_gemini(mcp_tools):
    gemini_tools = []
    for t in mcp_tools:
        input_schema = getattr(t, "inputSchema", {}) or {}

        # 🔹 Limpiar el esquema para eliminar title, additionalProperties, etc.
        cleaned_schema = clean_schema_for_gemini(input_schema)

        gemini_tool = {
            "function_declarations": [
                {
                    "name": getattr(t, "name", "unnamed_tool"),
                    "description": getattr(t, "description", ""),
                    "parameters": cleaned_schema  # ✅ Ya limpio para Gemini
                }
            ]
        }
        gemini_tools.append(gemini_tool)
    return gemini_tools


