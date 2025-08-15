def clean_schema_for_gemini(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    cleaned = {}
    for k, v in schema.items():
        if k == "additionalProperties":
            continue
        if isinstance(v, dict):
            cleaned[k] = clean_schema_for_gemini(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_schema_for_gemini(i) for i in v]
        else:
            cleaned[k] = v
    return cleaned


