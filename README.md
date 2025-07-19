# inspect-function

[![PyPI version](https://badge.fury.io/py/inspect-function.svg)](https://badge.fury.io/py/inspect-function)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/allen2c/inspect-function/actions/workflows/ci.yml/badge.svg)](https://github.com/allen2c/inspect-function/actions/workflows/ci.yml)

Inspect Python functions and get structured metadata as Pydantic models.

**Links:**

- 🏠 [Repository](https://github.com/allen2c/inspect-function)
- 📦 [PyPI Package](https://pypi.org/project/inspect-function/)

## Installation

```bash
pip install inspect-function
```

## Quick Start

```python
from inspect_function import inspect_function

def greet(name: str, age: int = 25) -> str:
    return f"Hello {name}, you are {age} years old"

# Inspect the function
inspection = inspect_function(greet)

print(inspection.awaitable)  # False
print(len(inspection.parameters))  # 2
print(inspection.return_annotation)  # "<class 'str'>"
```

## Basic Usage

### Analyze Function Signatures

```python
from inspect_function import inspect_function

def example_func(a: int, b: str = "default", *, c: bool, **kwargs):
    pass

inspection = inspect_function(example_func)

# Check function type
print(inspection.is_function)  # True
print(inspection.is_method)    # False
print(inspection.awaitable)   # False

# Access parameters
for param in inspection.parameters:
    print(f"{param.name}: {param.annotation} (required: {not param.is_optional})")
```

### Transform Parameters for Function Calls

```python
from inspect_function import inspect_parameters

def api_endpoint(user_id: int, limit: int = 10, *, include_deleted: bool = False):
    return f"Fetching {limit} items for user {user_id}"

# Convert dict to proper args/kwargs
params = {"user_id": 123, "limit": 20, "include_deleted": True}
args, kwargs = inspect_parameters(api_endpoint, params)

# Call the function
result = api_endpoint(*args, **kwargs)
print(result)  # "Fetching 20 items for user 123"
```

### Generate JSON Schema

```python
from inspect_function import inspect_function

def create_user(name: str, email: str, age: int = 18):
    pass

inspection = inspect_function(create_user)
schema = inspection.json_schema

print(schema)
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string", "description": "Parameter 'name' of kind positional_or_keyword"},
#     "email": {"type": "string", "description": "Parameter 'email' of kind positional_or_keyword"},
#     "age": {"type": "integer", "default": "18", "description": "Parameter 'age' of kind positional_or_keyword"}
#   },
#   "required": ["name", "email"],
#   "additionalProperties": false
# }
```

## Advanced Examples

### Async Functions

```python
import asyncio
from inspect_function import inspect_function

async def fetch_data(url: str, timeout: float = 30.0) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "status": "ok"}

inspection = inspect_function(fetch_data)
print(inspection.awaitable)  # True
print(inspection.is_coroutine_function)  # True
```

### Class Methods

```python
from inspect_function import inspect_function

class DataProcessor:
    def process(self, data: list) -> list:
        return data

    @classmethod
    def from_config(cls, config: dict) -> 'DataProcessor':
        return cls()

    @staticmethod
    def validate(data: str) -> bool:
        return bool(data)

# Instance method
inspection = inspect_function(DataProcessor.process)
print(inspection.is_method)  # True

# Class method
inspection = inspect_function(DataProcessor.from_config)
print(inspection.is_classmethod)  # True

# Static method
inspection = inspect_function(DataProcessor.validate)
print(inspection.is_function)  # True (static methods are just functions)
```

### Complex Parameter Types

```python
from typing import List, Dict, Optional, Union
from inspect_function import inspect_function

def complex_func(
    items: List[str],
    mapping: Dict[str, int],
    optional_data: Optional[str] = None,
    *args: float,
    flag: bool,
    **kwargs: Union[str, int]
) -> None:
    pass

inspection = inspect_function(complex_func)

# Access different parameter types
print(f"Positional/keyword: {len(inspection.positional_or_keyword_params)}")
print(f"Keyword-only: {len(inspection.keyword_only_params)}")
print(f"*args param: {inspection.var_positional_param.name if inspection.var_positional_param else None}")
print(f"**kwargs param: {inspection.var_keyword_param.name if inspection.var_keyword_param else None}")
print(f"Required params: {[p.name for p in inspection.required_params]}")
```

## API Reference

### `inspect_function(func) -> FunctionInspection`

Returns a `FunctionInspection` object with detailed information about the function.

**Properties:**

- `awaitable: bool` - Whether the function is async
- `parameters: List[Parameter]` - List of all parameters
- `return_annotation: str` - Return type annotation
- `is_method: bool` - Instance method detection
- `is_classmethod: bool` - Class method detection
- `is_function: bool` - Regular function detection

### `inspect_parameters(func, params: dict) -> tuple[tuple, dict]`

Transforms a parameter dictionary into properly ordered `args` and `kwargs` for function calls.

### `Parameter` Model

- `name: str` - Parameter name
- `kind: ParameterKind` - Parameter type (positional, keyword, etc.)
- `annotation: str` - Type annotation
- `has_default: bool` - Whether parameter has default value
- `is_optional: bool` - Whether parameter is optional
- `position: int | None` - Position in signature

## License

MIT License - see [LICENSE](LICENSE) file for details.
