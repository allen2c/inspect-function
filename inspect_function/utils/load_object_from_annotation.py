"""
Utility to load any object from annotation strings.

This module provides functionality to convert string annotations back to their
original objects, including classes, functions, types, and typing constructs.
"""

import importlib
import inspect
import typing
from typing import Any, Optional, Union


def load_object_from_annotation(
    annotation_str: str, fallback_globals: Optional[dict] = None
) -> Optional[Any]:
    """
    Load any object from its string annotation representation.

    This function handles various annotation formats including:
    - Classes: "<class '__main__.ABC'>"
    - Functions: "<function 'func_name' at 0x...>"
    - Built-in types: "<class 'int'>", "<class 'str'>"
    - Typing constructs: "typing.List[int]", "Union[int, str]"
    - String literals: "Any", "None"
    - Module attributes: "np.ndarray", "pathlib.Path"

    Args:
        annotation_str: The annotation string from inspect_function
        fallback_globals: Global namespace to search (defaults to caller's globals)

    Returns:
        The actual object or None if not found

    Raises:
        ModuleNotFoundError: When annotation refers to a module attribute
            (e.g., "np.ndarray") but the module is not imported

    Examples:
        >>> class MyClass:
        ...     pass
        >>>
        >>> # Class annotation
        >>> obj = load_object_from_annotation("<class '__main__.MyClass'>")
        >>> obj is MyClass
        True

        >>> # Built-in type
        >>> obj = load_object_from_annotation("<class 'int'>")
        >>> obj is int
        True

        >>> # Typing construct
        >>> obj = load_object_from_annotation("typing.List[int]")
        >>> str(obj)
        'typing.List[int]'

        >>> # Module attribute (when module is imported)
        >>> import pathlib
        >>> obj = load_object_from_annotation("pathlib.Path")
        >>> obj is pathlib.Path
        True

        >>> # Module attribute (when module is not imported)
        >>> load_object_from_annotation("np.ndarray")  # doctest: +SKIP
        Traceback (most recent call last):
        ModuleNotFoundError: Module 'np' required for annotation 'np.ndarray'
            is not imported
    """
    if not isinstance(annotation_str, str):
        return None

    if fallback_globals is None:
        # Get caller's globals
        frame = inspect.currentframe()
        if frame and frame.f_back:
            fallback_globals = frame.f_back.f_globals
        else:
            fallback_globals = {}

    # Handle different annotation formats

    # 1. Standard object representation: "<class/function 'path'>"
    if _is_standard_repr(annotation_str):
        return _load_from_standard_repr(annotation_str, fallback_globals)

    # 2. Simple string literals like "Any", "None"
    if annotation_str in {"Any", "None"}:
        return _load_simple_literal(annotation_str)

    # 3. Typing module constructs
    if _is_typing_construct(annotation_str):
        return _load_typing_construct(annotation_str, fallback_globals)

    # 4. Module attribute format (e.g., 'np.ndarray', 'pathlib.Path')
    if "." in annotation_str and not annotation_str.startswith("<"):
        parts = annotation_str.split(".")
        module_name = parts[0]

        # Check if the module is available in globals
        if module_name not in fallback_globals:
            raise ModuleNotFoundError(
                f"Module '{module_name}' required for annotation "
                f"'{annotation_str}' is not imported"
            )

        # Try to resolve the full path using existing logic
        return _resolve_object_path(annotation_str, fallback_globals)

    # 5. Direct name lookup in globals
    return fallback_globals.get(annotation_str)


def _is_standard_repr(annotation_str: str) -> bool:
    """Check if annotation is in standard repr format like '<class 'name'>'."""
    return (
        annotation_str.startswith("<")
        and annotation_str.endswith(">")
        and " " in annotation_str
        and "'" in annotation_str
    )


def _load_from_standard_repr(
    annotation_str: str, fallback_globals: dict
) -> Optional[Any]:
    """Load object from standard repr format like '<class '__main__.ABC'>'."""
    try:
        # Extract the path from patterns like "<class '__main__.ABC'>"
        if "'" not in annotation_str:
            return None

        # Find the quoted path
        start_quote = annotation_str.find("'")
        end_quote = annotation_str.rfind("'")
        if start_quote == -1 or end_quote == -1 or start_quote == end_quote:
            return None

        object_path = annotation_str[start_quote + 1 : end_quote]
        return _resolve_object_path(object_path, fallback_globals)

    except Exception:
        return None


def _resolve_object_path(object_path: str, fallback_globals: dict) -> Optional[Any]:
    """Resolve an object path like '__main__.ABC' or 'builtins.int'."""
    if "." not in object_path:
        # Simple name - check builtins first, then globals
        builtin_types = {
            "int": int,
            "str": str,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,
            "bytes": bytes,
            "bytearray": bytearray,
            "object": object,
            "type": type,
            "NoneType": type(None),
        }
        if object_path in builtin_types:
            return builtin_types[object_path]
        if hasattr(__builtins__, object_path):
            return getattr(__builtins__, object_path)
        return fallback_globals.get(object_path)

    parts = object_path.split(".")
    object_name = parts[-1]

    if parts[0] == "__main__":
        # Current module
        return fallback_globals.get(object_name)
    elif parts[0] == "builtins":
        # Built-in object
        if hasattr(__builtins__, object_name):
            return getattr(__builtins__, object_name)
        return None
    else:
        # Try to import from other module
        module_path = ".".join(parts[:-1])
        try:
            module = importlib.import_module(module_path)
            return getattr(module, object_name, None)
        except (ImportError, AttributeError, ModuleNotFoundError):
            return None


def _load_simple_literal(annotation_str: str) -> Optional[Any]:
    """Load simple string literals like 'Any', 'None'."""
    literals = {
        "Any": typing.Any,
        "None": type(None),
    }
    return literals.get(annotation_str)


def _is_typing_construct(annotation_str: str) -> bool:
    """Check if annotation looks like a typing construct."""
    typing_indicators = [
        "typing.",
        "Union[",
        "Optional[",
        "List[",
        "Dict[",
        "Tuple[",
        "Set[",
        "FrozenSet[",
        "Callable[",
        "Literal[",
        "ClassVar[",
        "Final[",
        "Annotated[",
        "Generic[",
        "TypeVar",
        "NewType",
    ]
    return any(indicator in annotation_str for indicator in typing_indicators)


def _load_typing_construct(
    annotation_str: str, fallback_globals: dict
) -> Optional[Any]:
    """Load typing constructs like 'typing.List[int]', 'Union[int, str]'."""
    try:
        # Create a safe evaluation context with typing module and common types
        safe_context = _create_safe_typing_context(fallback_globals)

        # Try to evaluate the typing expression
        return eval(annotation_str, {"__builtins__": {}}, safe_context)

    except Exception:
        # If evaluation fails, try to parse manually for common patterns
        return _parse_typing_manually(annotation_str, fallback_globals)


def _create_safe_typing_context(fallback_globals: dict) -> dict:
    """Create a safe context for evaluating typing expressions."""
    context = {
        # Typing module
        "typing": typing,
        "Union": typing.Union,
        "Optional": typing.Optional,
        "List": typing.List,
        "Dict": typing.Dict,
        "Tuple": typing.Tuple,
        "Set": typing.Set,
        "FrozenSet": typing.FrozenSet,
        "Callable": typing.Callable,
        "Any": typing.Any,
        "NoReturn": typing.NoReturn,
        # Built-in types
        "int": int,
        "str": str,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        "frozenset": frozenset,
        "bytes": bytes,
        "bytearray": bytearray,
        # Add objects from fallback globals that look safe
        **{
            k: v
            for k, v in fallback_globals.items()
            if not k.startswith("_") and isinstance(v, type)
        },
    }

    # Add newer typing features if available
    if hasattr(typing, "Literal"):
        context["Literal"] = typing.Literal
    if hasattr(typing, "Final"):
        context["Final"] = typing.Final
    if hasattr(typing, "Annotated"):
        context["Annotated"] = typing.Annotated

    return context


def _parse_typing_manually(
    annotation_str: str, fallback_globals: dict
) -> Optional[Any]:
    """Manually parse common typing patterns when eval fails."""
    # Handle Union[type1, type2, ...]
    if annotation_str.startswith("Union[") and annotation_str.endswith("]"):
        inner = annotation_str[6:-1]  # Remove 'Union[' and ']'
        types = []
        for type_str in _split_type_args(inner):
            type_obj = load_object_from_annotation(type_str.strip(), fallback_globals)
            if type_obj is not None:
                types.append(type_obj)
        if len(types) == 1:
            return types[0]
        elif len(types) > 1:
            # For multiple types, return the first type as a fallback
            # Creating Union dynamically is complex across Python versions
            return types[0]

    # Handle Optional[type]
    if annotation_str.startswith("Optional[") and annotation_str.endswith("]"):
        inner = annotation_str[9:-1]  # Remove 'Optional[' and ']'
        type_obj = load_object_from_annotation(inner.strip(), fallback_globals)
        if type_obj is not None:
            return typing.Optional[type_obj]

    # Handle List[type], Dict[key, value], etc.
    for generic_name in ["List", "Dict", "Tuple", "Set"]:
        if annotation_str.startswith(f"{generic_name}[") and annotation_str.endswith(
            "]"
        ):
            try:
                generic_type = getattr(typing, generic_name)
                inner = annotation_str[len(generic_name) + 1 : -1]
                type_args = []
                for type_str in _split_type_args(inner):
                    type_obj = load_object_from_annotation(
                        type_str.strip(), fallback_globals
                    )
                    if type_obj is not None:
                        type_args.append(type_obj)
                if type_args:
                    return generic_type[tuple(type_args)]
            except Exception:
                continue

    return None


def _split_type_args(args_str: str) -> list[str]:
    """Split type arguments respecting nested brackets."""
    if not args_str:
        return []

    args = []
    current_arg = ""
    bracket_depth = 0

    for char in args_str:
        if char in "[(":
            bracket_depth += 1
            current_arg += char
        elif char in "])":
            bracket_depth -= 1
            current_arg += char
        elif char == "," and bracket_depth == 0:
            args.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char

    if current_arg.strip():
        args.append(current_arg.strip())

    return args


def get_annotation_info(annotation_str: str) -> dict:
    """
    Get detailed information about an annotation string.

    Args:
        annotation_str: The annotation string to analyze

    Returns:
        Dictionary with information about the annotation
    """
    info = {
        "original": annotation_str,
        "type": "unknown",
        "is_class": False,
        "is_function": False,
        "is_builtin": False,
        "is_typing_construct": False,
        "module_name": None,
        "object_name": None,
        "is_main_module": False,
        "can_load": False,
    }

    # Determine type
    if _is_standard_repr(annotation_str):
        if "<class " in annotation_str:
            info["type"] = "class"
            info["is_class"] = True
        elif "<function " in annotation_str:
            info["type"] = "function"
            info["is_function"] = True
        elif "<built-in " in annotation_str:
            info["type"] = "builtin"
            info["is_builtin"] = True

        # Extract path info
        if "'" in annotation_str:
            start_quote = annotation_str.find("'")
            end_quote = annotation_str.rfind("'")
            if start_quote != end_quote:
                object_path = annotation_str[start_quote + 1 : end_quote]
                if "." in object_path:
                    parts = object_path.split(".")
                    info["module_name"] = ".".join(parts[:-1])
                    info["object_name"] = parts[-1]
                    info["is_main_module"] = parts[0] == "__main__"
                    info["is_builtin"] = parts[0] == "builtins"
                else:
                    info["object_name"] = object_path

    elif _is_typing_construct(annotation_str):
        info["type"] = "typing_construct"
        info["is_typing_construct"] = True

    elif annotation_str in {"Any", "None"}:
        info["type"] = "literal"
        info["object_name"] = annotation_str

    # Test if we can load it
    try:
        loaded = load_object_from_annotation(annotation_str)
        info["can_load"] = loaded is not None
    except Exception:
        info["can_load"] = False

    return info


# Example usage and tests
if __name__ == "__main__":
    from typing import Dict, List, Optional

    from inspect_function import inspect_function

    class TestClass:
        def __init__(self, value: str = "default"):
            self.value = value

    def test_function(x: int) -> str:
        return str(x)

    def complex_func(
        obj: TestClass,
        numbers: List[int],
        mapping: Dict[str, Union[int, str]],
        optional_data: Optional[TestClass] = None,
    ) -> str:
        return "test"

    print("=== Object Loader Demo ===\n")

    # Test with complex function
    inspection = inspect_function(complex_func)

    for param in inspection.parameters:
        print(f"Parameter: {param.name}")
        print(f"  Annotation: {param.annotation}")

        # Get detailed info
        info = get_annotation_info(param.annotation)
        print(f"  Type: {info['type']}")
        print(f"  Can load: {info['can_load']}")

        # Try to load the object
        loaded_obj = load_object_from_annotation(param.annotation)
        print(f"  Loaded object: {loaded_obj}")

        if loaded_obj:
            print(f"  Object type: {type(loaded_obj)}")

            # Special handling for different types
            if info["is_class"] and loaded_obj == TestClass:
                try:
                    instance = loaded_obj("test_value")
                    print(f"  Created instance: {instance.value}")
                except Exception as e:
                    print(f"  Could not create instance: {e}")

        print()
