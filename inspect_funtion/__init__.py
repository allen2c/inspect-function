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
    default_value: str | None = None
    has_default: bool = False


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
