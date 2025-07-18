import pathlib
import typing
from enum import StrEnum

import pydantic

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()


class ParameterKind(StrEnum):
    """Parameter kinds matching Python's inspect.Parameter.kind"""

    POSITIONAL_ONLY = "positional_only"  # before /
    POSITIONAL_OR_KEYWORD = "positional_or_keyword"  # default
    VAR_POSITIONAL = "var_positional"  # *args
    KEYWORD_ONLY = "keyword_only"  # after *
    VAR_KEYWORD = "var_keyword"  # **kwargs


class Parameter(pydantic.BaseModel):
    """Represents a function parameter"""

    name: str
    kind: ParameterKind
    annotation: str
    default_value: str | None = pydantic.Field(
        default=None, description="Default value of the parameter in repr()"
    )
    has_default: bool = pydantic.Field(
        default=False, description="Whether the parameter has a default value"
    )
    position: int | None = pydantic.Field(
        default=None, description="Parameter position in the signature"
    )
    is_optional: bool = pydantic.Field(
        default=False, description="Whether the parameter is optional"
    )


class FunctionInspection(pydantic.BaseModel):
    """Complete function inspection information"""

    awaitable: bool = pydantic.Field(
        ..., description="Whether the function is awaitable"
    )
    parameters: typing.List[Parameter] = pydantic.Field(
        default_factory=list, description="All parameters in signature order"
    )
    return_annotation: str

    @property
    def is_method(self) -> bool:
        """Check if this is an instance method (has 'self' as first parameter)"""
        return (
            len(self.parameters) > 0
            and self.parameters[0].name == "self"
            and self.parameters[0].kind
            in {ParameterKind.POSITIONAL_ONLY, ParameterKind.POSITIONAL_OR_KEYWORD}
        )

    @property
    def is_classmethod(self) -> bool:
        """Check if this is a classmethod (has 'cls' as first parameter)"""
        return (
            len(self.parameters) > 0
            and self.parameters[0].name == "cls"
            and self.parameters[0].kind
            in {ParameterKind.POSITIONAL_ONLY, ParameterKind.POSITIONAL_OR_KEYWORD}
        )

    @property
    def is_function(self) -> bool:
        """Check if this is a regular function (not method or classmethod)"""
        return not self.is_method and not self.is_classmethod

    @property
    def is_coroutine_function(self) -> bool:
        """Check if this is a coroutine function (async def)"""
        return self.awaitable

    @property
    def positional_only_params(self) -> typing.List[Parameter]:
        """Get parameters that are positional-only"""
        return [p for p in self.parameters if p.kind == ParameterKind.POSITIONAL_ONLY]

    @property
    def positional_or_keyword_params(self) -> typing.List[Parameter]:
        """Get parameters that can be passed positionally or as keyword"""
        return [
            p for p in self.parameters if p.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        ]

    @property
    def keyword_only_params(self) -> typing.List[Parameter]:
        """Get parameters that are keyword-only"""
        return [p for p in self.parameters if p.kind == ParameterKind.KEYWORD_ONLY]

    @property
    def var_positional_param(self) -> Parameter | None:
        """Get the *args parameter if present"""
        var_pos = [p for p in self.parameters if p.kind == ParameterKind.VAR_POSITIONAL]
        return var_pos[0] if var_pos else None

    @property
    def var_keyword_param(self) -> Parameter | None:
        """Get the **kwargs parameter if present"""
        var_kw = [p for p in self.parameters if p.kind == ParameterKind.VAR_KEYWORD]
        return var_kw[0] if var_kw else None

    @property
    def required_params(self) -> typing.List[Parameter]:
        """Get all parameters that don't have default values"""
        return [
            p
            for p in self.parameters
            if not p.has_default
            and p.kind not in {ParameterKind.VAR_POSITIONAL, ParameterKind.VAR_KEYWORD}
        ]

    @property
    def optional_params(self) -> typing.List[Parameter]:
        """Get all parameters that have default values"""
        return [p for p in self.parameters if p.has_default]

    @property
    def json_schema(self) -> typing.Dict[str, typing.Any]:
        """Generate OpenAPI JSON schema for the function signature"""

        from inspect_funtion.utils.get_openapi_type import get_openapi_type

        # Build properties for each parameter
        properties = {}
        required = []

        for param in self.parameters:
            # Skip 'self' and 'cls' parameters for methods
            if param.name in ("self", "cls"):
                continue

            # Handle different parameter kinds
            if param.kind == ParameterKind.VAR_POSITIONAL:
                # *args - represent as array
                properties[param.name] = {
                    "type": "array",
                    "items": {"type": "any"},
                    "description": f"Variable positional arguments (*{param.name})",
                }
            elif param.kind == ParameterKind.VAR_KEYWORD:
                # **kwargs - represent as object with additional properties
                properties[param.name] = {
                    "type": "object",
                    "additionalProperties": True,
                    "description": f"Variable keyword arguments (**{param.name})",
                }
            else:
                # Regular parameter
                param_schema = {
                    "type": get_openapi_type(param.annotation),
                    "description": f"Parameter '{param.name}' of kind "
                    f"{param.kind.value}",
                }

                if param.has_default and param.default_value is not None:
                    param_schema["default"] = param.default_value

                properties[param.name] = param_schema

                # Add to required if no default value and not optional
                if not param.has_default and param.kind not in {
                    ParameterKind.VAR_POSITIONAL,
                    ParameterKind.VAR_KEYWORD,
                }:
                    required.append(param.name)

        # Build the main schema
        schema = {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
            "x-function-metadata": {
                "awaitable": self.awaitable,
                "return_annotation": self.return_annotation,
                "is_method": self.is_method,
                "is_classmethod": self.is_classmethod,
                "is_coroutine_function": self.is_coroutine_function,
            },
        }

        # Add description based on function type
        if self.is_method:
            schema["description"] = "Parameters for instance method"
        elif self.is_classmethod:
            schema["description"] = "Parameters for class method"
        elif self.is_coroutine_function:
            schema["description"] = "Parameters for async function"
        else:
            schema["description"] = "Parameters for function"

        return schema
