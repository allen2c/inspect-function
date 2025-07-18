def get_openapi_type(annotation: str) -> str:
    """Convert Python type annotation to OpenAPI type"""
    # Handle common Python types
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "NoneType": "null",
        "None": "null",
    }

    # Clean annotation (remove typing. prefix, generics, etc.)
    clean_annotation = annotation.replace("typing.", "").split("[")[0].strip()

    # Handle Union types and Optional
    if "Union" in annotation or "Optional" in annotation:
        return "any"

    # Handle List, Dict, etc.
    if clean_annotation in ["List", "Sequence", "Tuple"]:
        return "array"
    elif clean_annotation in ["Dict", "Mapping"]:
        return "object"

    # Return mapped type or default to "any"
    return type_mapping.get(clean_annotation, "any")
