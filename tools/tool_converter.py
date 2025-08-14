def clean_schema(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    cleaned = {}
    for k, v in schema.items():
        if k == "additionalProperties":
            continue
        if isinstance(v, dict):
            cleaned[k] = clean_schema(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_schema(i) for i in v]
        else:
            cleaned[k] = v
    return cleaned

def mcp_to_gemini(mcp_tools: list) -> list:
    gemini_tools = []
    for tool in mcp_tools:
        function_decl = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = clean_schema(tool.inputSchema)
            if "properties" in schema:
                function_decl["parameters"]["properties"] = schema["properties"]
            if "required" in schema:
                function_decl["parameters"]["required"] = schema["required"]
        gemini_tools.append({"function_declarations": [function_decl]})
    return gemini_tools
