import pathlib
import typing

import pydantic

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()


class VarField(pydantic.BaseModel):
    name: str
    annotation: str


class FunctionInspection(pydantic.BaseModel):
    awaitable: bool = pydantic.Field(
        ..., description="Whether the function is awaitable"
    )
    self_param: VarField | None = pydantic.Field(
        default=None, description="For self parameter in methods"
    )
    cls_param: VarField | None = pydantic.Field(
        default=None, description="For cls parameter in classmethods"
    )
    args: typing.List[VarField] | None = pydantic.Field(
        default=None, description="For *args parameter"
    )
    star_args: typing.List[VarField] | None = pydantic.Field(
        default=None, description="For **kwargs parameter"
    )
    kwargs: typing.List[VarField] | None = pydantic.Field(
        default=None, description="For **kwargs parameter"
    )
    star_kwargs: typing.List[VarField] | None = pydantic.Field(
        default=None, description="For **kwargs parameter"
    )
    return_annotation: str

    @property
    def is_method(self) -> bool:
        return self.self_param is not None

    @property
    def is_classmethod(self) -> bool:
        return self.cls_param is not None

    @property
    def is_function(self) -> bool:
        return self.self_param is None and self.cls_param is None
