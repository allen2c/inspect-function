from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from inspect_function import ParameterKind, inspect_function


@dataclass
class CustomClass:
    value: int


class CustomEnum(Enum):
    OPTION_A = "a"
    OPTION_B = "b"


class TestFunctionTypes:
    def test_function(self):
        def f(a: int, b: str, c: bool = True):
            pass

        inspection = inspect_function(f)
        assert inspection.is_function
        assert inspection.is_coroutine_function is False
        assert inspection.is_method is False
        assert inspection.is_classmethod is False

        # Validate parameters
        assert len(inspection.parameters) == 3

        # Parameter 'a'
        param_a = inspection.parameters[0]
        assert param_a.name == "a"
        assert param_a.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_a.annotation == "<class 'int'>"
        assert param_a.has_default is False
        assert param_a.default_value is None
        assert param_a.position == 0
        assert param_a.is_optional is False

        # Parameter 'b'
        param_b = inspection.parameters[1]
        assert param_b.name == "b"
        assert param_b.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_b.annotation == "<class 'str'>"
        assert param_b.has_default is False
        assert param_b.default_value is None
        assert param_b.position == 1
        assert param_b.is_optional is False

        # Parameter 'c'
        param_c = inspection.parameters[2]
        assert param_c.name == "c"
        assert param_c.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_c.annotation == "<class 'bool'>"
        assert param_c.has_default is True
        assert param_c.default_value == "True"
        assert param_c.position == 2
        assert param_c.is_optional is True

    def test_method(self):
        class TestClass:
            def method(self, a: int, b: str = "default"):
                pass

        # Test unbound method (accessing from class)
        inspection = inspect_function(TestClass.method)
        assert inspection.is_method
        assert inspection.is_function is False
        assert inspection.is_classmethod is False
        assert inspection.is_coroutine_function is False

        # Validate parameters
        assert len(inspection.parameters) == 3

        # Parameter 'self'
        param_self = inspection.parameters[0]
        assert param_self.name == "self"
        assert param_self.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_self.annotation == "Any"
        assert param_self.has_default is False
        assert param_self.default_value is None
        assert param_self.position == 0
        assert param_self.is_optional is False

        # Parameter 'a'
        param_a = inspection.parameters[1]
        assert param_a.name == "a"
        assert param_a.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_a.annotation == "<class 'int'>"
        assert param_a.has_default is False
        assert param_a.default_value is None
        assert param_a.position == 1
        assert param_a.is_optional is False

        # Parameter 'b'
        param_b = inspection.parameters[2]
        assert param_b.name == "b"
        assert param_b.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_b.annotation == "<class 'str'>"
        assert param_b.has_default is True
        assert param_b.default_value == "'default'"
        assert param_b.position == 2
        assert param_b.is_optional is True

    def test_coroutine_function(self):
        async def async_func(a: int, b: str = "default"):
            return a + len(b)

        inspection = inspect_function(async_func)
        assert inspection.is_coroutine_function
        assert inspection.awaitable
        assert inspection.is_function
        assert inspection.is_method is False
        assert inspection.is_classmethod is False

        # Validate parameters
        assert len(inspection.parameters) == 2

        # Parameter 'a'
        param_a = inspection.parameters[0]
        assert param_a.name == "a"
        assert param_a.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_a.annotation == "<class 'int'>"
        assert param_a.has_default is False
        assert param_a.default_value is None
        assert param_a.position == 0
        assert param_a.is_optional is False

        # Parameter 'b'
        param_b = inspection.parameters[1]
        assert param_b.name == "b"
        assert param_b.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_b.annotation == "<class 'str'>"
        assert param_b.has_default is True
        assert param_b.default_value == "'default'"
        assert param_b.position == 1
        assert param_b.is_optional is True

    def test_classmethod(self):
        class TestClass:
            @classmethod
            def class_method(cls, a: int, b: str = "default"):
                pass

        inspection = inspect_function(TestClass.class_method)
        assert inspection.is_classmethod
        assert inspection.is_function is False
        assert inspection.is_method is False
        assert inspection.is_coroutine_function is False

        # Validate parameters - classmethod has cls automatically bound
        # so only 2 params visible
        assert len(inspection.parameters) == 2

        # Parameter 'a' (cls is automatically bound and not visible)
        param_a = inspection.parameters[0]
        assert param_a.name == "a"
        assert param_a.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_a.annotation == "<class 'int'>"
        assert param_a.has_default is False
        assert param_a.default_value is None
        assert param_a.position == 0
        assert param_a.is_optional is False

        # Parameter 'b'
        param_b = inspection.parameters[1]
        assert param_b.name == "b"
        assert param_b.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_b.annotation == "<class 'str'>"
        assert param_b.has_default is True
        assert param_b.default_value == "'default'"
        assert param_b.position == 1
        assert param_b.is_optional is True

    def test_staticmethod(self):
        class TestClass:
            @staticmethod
            def static_method(a: int, b: str = "default"):
                pass

        inspection = inspect_function(TestClass.static_method)
        assert inspection.is_function
        assert inspection.is_method is False
        assert inspection.is_classmethod is False
        assert inspection.is_coroutine_function is False

        # Validate parameters
        assert len(inspection.parameters) == 2

        # Parameter 'a'
        param_a = inspection.parameters[0]
        assert param_a.name == "a"
        assert param_a.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_a.annotation == "<class 'int'>"
        assert param_a.has_default is False
        assert param_a.default_value is None
        assert param_a.position == 0
        assert param_a.is_optional is False

        # Parameter 'b'
        param_b = inspection.parameters[1]
        assert param_b.name == "b"
        assert param_b.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param_b.annotation == "<class 'str'>"
        assert param_b.has_default is True
        assert param_b.default_value == "'default'"
        assert param_b.position == 1
        assert param_b.is_optional is True

    def test_positional_only_parameters(self):
        """Test parameters that are positional-only (before /)"""

        def func_with_pos_only(a: int, b: str, /, c: bool = True):
            pass

        inspection = inspect_function(func_with_pos_only)
        assert len(inspection.parameters) == 3

        # Parameters 'a' and 'b' should be positional-only
        assert inspection.parameters[0].kind == ParameterKind.POSITIONAL_ONLY
        assert inspection.parameters[1].kind == ParameterKind.POSITIONAL_ONLY
        assert inspection.parameters[2].kind == ParameterKind.POSITIONAL_OR_KEYWORD

        # Test properties
        pos_only_params = inspection.positional_only_params
        assert len(pos_only_params) == 2
        assert pos_only_params[0].name == "a"
        assert pos_only_params[1].name == "b"

    def test_keyword_only_parameters(self):
        """Test parameters that are keyword-only (after *)"""

        def func_with_kw_only(a: int, *, b: str, c: bool = True):
            pass

        inspection = inspect_function(func_with_kw_only)
        assert len(inspection.parameters) == 3

        # Parameter 'a' should be positional-or-keyword
        assert inspection.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD
        # Parameters 'b' and 'c' should be keyword-only
        assert inspection.parameters[1].kind == ParameterKind.KEYWORD_ONLY
        assert inspection.parameters[2].kind == ParameterKind.KEYWORD_ONLY

        # Test properties
        kw_only_params = inspection.keyword_only_params
        assert len(kw_only_params) == 2
        assert kw_only_params[0].name == "b"
        assert kw_only_params[1].name == "c"

    def test_var_positional_parameters(self):
        """Test *args parameters"""

        def func_with_args(a: int, *args: str):
            pass

        inspection = inspect_function(func_with_args)
        assert len(inspection.parameters) == 2

        # First parameter is regular
        assert inspection.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD
        # Second parameter is *args
        assert inspection.parameters[1].kind == ParameterKind.VAR_POSITIONAL
        assert inspection.parameters[1].name == "args"
        assert inspection.parameters[1].is_optional is True
        assert (
            inspection.parameters[1].position is None
        )  # Variadic params don't have position

        # Test property
        var_pos = inspection.var_positional_param
        assert var_pos is not None
        assert var_pos.name == "args"

    def test_var_keyword_parameters(self):
        """Test **kwargs parameters"""

        def func_with_kwargs(a: int, **kwargs: Any):
            pass

        inspection = inspect_function(func_with_kwargs)
        assert len(inspection.parameters) == 2

        # First parameter is regular
        assert inspection.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD
        # Second parameter is **kwargs
        assert inspection.parameters[1].kind == ParameterKind.VAR_KEYWORD
        assert inspection.parameters[1].name == "kwargs"
        assert inspection.parameters[1].is_optional is True
        assert (
            inspection.parameters[1].position is None
        )  # Variadic params don't have position

        # Test property
        var_kw = inspection.var_keyword_param
        assert var_kw is not None
        assert var_kw.name == "kwargs"

    def test_complex_parameter_combinations(self):
        """Test function with all parameter kinds"""

        def complex_func(
            pos_only: int,
            /,
            regular: str,
            *args: float,
            kw_only: bool,
            kw_with_default: Optional[List[int]] = None,
            **kwargs: Any,
        ):
            pass

        inspection = inspect_function(complex_func)
        assert len(inspection.parameters) == 6

        # Validate each parameter kind
        params = inspection.parameters
        assert params[0].kind == ParameterKind.POSITIONAL_ONLY
        assert params[1].kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert params[2].kind == ParameterKind.VAR_POSITIONAL
        assert params[3].kind == ParameterKind.KEYWORD_ONLY
        assert params[4].kind == ParameterKind.KEYWORD_ONLY
        assert params[5].kind == ParameterKind.VAR_KEYWORD

        # Test convenience properties
        assert len(inspection.positional_only_params) == 1
        assert len(inspection.positional_or_keyword_params) == 1
        assert len(inspection.keyword_only_params) == 2
        assert inspection.var_positional_param is not None
        assert inspection.var_keyword_param is not None

    def test_complex_type_annotations(self):
        """Test various complex type annotations"""

        def func_with_complex_types(
            union_param: Union[int, str],
            optional_param: Optional[float],
            list_param: List[int],
            dict_param: Dict[str, Any],
            tuple_param: Tuple[int, str, bool],
            set_param: Set[str],
            callable_param: Callable[[int, str], bool],
            custom_class: CustomClass,
            enum_param: CustomEnum,
            any_param: Any,
        ):
            pass

        inspection = inspect_function(func_with_complex_types)
        assert len(inspection.parameters) == 10

        params = inspection.parameters

        # Check that complex type annotations are preserved as strings
        assert "Union" in params[0].annotation
        assert "Optional" in params[1].annotation or "Union" in params[1].annotation
        assert "List" in params[2].annotation or "list" in params[2].annotation
        assert "Dict" in params[3].annotation or "dict" in params[3].annotation
        assert "Tuple" in params[4].annotation or "tuple" in params[4].annotation
        assert "Set" in params[5].annotation or "set" in params[5].annotation
        assert (
            "Callable" in params[6].annotation
            or "typing.Callable" in params[6].annotation
        )
        assert "CustomClass" in params[7].annotation
        assert "CustomEnum" in params[8].annotation
        assert "Any" in params[9].annotation or "typing.Any" in params[9].annotation

    def test_various_default_values(self):
        """Test functions with various types of default values"""

        def func_with_defaults(
            none_default: Optional[str] = None,
            list_default: Optional[List[int]] = None,
            dict_default: Optional[Dict[str, int]] = None,
            bool_default: bool = False,
            int_default: int = 42,
            float_default: float = 3.14,
            str_default: str = "hello",
            lambda_default: Callable = lambda x: x * 2,
        ):
            pass

        inspection = inspect_function(func_with_defaults)
        assert len(inspection.parameters) == 8

        params = inspection.parameters

        # Check default values are properly captured
        assert params[0].default_value == "None"
        assert params[1].default_value == "None"
        assert params[2].default_value == "None"
        assert params[3].default_value == "False"
        assert params[4].default_value == "42"
        assert params[5].default_value == "3.14"
        assert params[6].default_value == "'hello'"
        assert (
            params[7].default_value is not None and "lambda" in params[7].default_value
        )

        # All should have defaults
        for param in params:
            assert param.has_default is True
            assert param.is_optional is True

    def test_no_parameters(self):
        """Test function with no parameters"""

        def no_params():
            return "hello"

        inspection = inspect_function(no_params)
        assert len(inspection.parameters) == 0
        assert inspection.is_function is True
        assert len(inspection.required_params) == 0
        assert len(inspection.optional_params) == 0

    def test_only_variadic_parameters(self):
        """Test function with only *args and **kwargs"""

        def only_variadic(*args, **kwargs):
            pass

        inspection = inspect_function(only_variadic)
        assert len(inspection.parameters) == 2
        assert inspection.var_positional_param is not None
        assert inspection.var_keyword_param is not None
        assert (
            len(inspection.required_params) == 0
        )  # *args and **kwargs are not required

    def test_parameter_properties(self):
        """Test the various parameter property methods"""

        def test_func(
            required: int,
            optional: str = "default",
            *args: float,
            kw_required: bool,
            kw_optional: Optional[List[int]] = None,
            **kwargs: Any,
        ):
            pass

        inspection = inspect_function(test_func)

        # Test required_params (excludes *args/**kwargs)
        required_params = inspection.required_params
        assert len(required_params) == 2
        assert required_params[0].name == "required"
        assert required_params[1].name == "kw_required"

        # Test optional_params (has default values)
        optional_params = inspection.optional_params
        assert len(optional_params) == 2
        assert optional_params[0].name == "optional"
        assert optional_params[1].name == "kw_optional"

    def test_return_annotations(self):
        """Test various return type annotations"""

        def func_returns_int() -> int:
            return 42

        def func_returns_complex() -> Dict[str, List[Union[int, str]]]:
            return {}

        def func_no_return_annotation():
            pass

        async def async_func_returns() -> Optional[str]:
            return None

        # Test simple return annotation
        inspection1 = inspect_function(func_returns_int)
        assert inspection1.return_annotation == "<class 'int'>"

        # Test complex return annotation
        inspection2 = inspect_function(func_returns_complex)
        assert (
            "Dict" in inspection2.return_annotation
            or "dict" in inspection2.return_annotation
        )

        # Test no return annotation
        inspection3 = inspect_function(func_no_return_annotation)
        assert inspection3.return_annotation == "Any"

        # Test async function return annotation
        inspection4 = inspect_function(async_func_returns)
        assert (
            "Optional" in inspection4.return_annotation
            or "Union" in inspection4.return_annotation
        )

    def test_edge_case_annotations(self):
        """Test edge cases with type annotations"""

        def func_no_annotations(a, b=None):
            pass

        def func_mixed_annotations(a: int, b, c: str = "default"):
            pass

        # Test function with no annotations
        inspection1 = inspect_function(func_no_annotations)
        for param in inspection1.parameters:
            assert param.annotation == "Any"

        # Test function with mixed annotations
        inspection2 = inspect_function(func_mixed_annotations)
        assert inspection2.parameters[0].annotation == "<class 'int'>"
        assert inspection2.parameters[1].annotation == "Any"
        assert inspection2.parameters[2].annotation == "<class 'str'>"

    def test_nested_generic_types(self):
        """Test deeply nested generic type annotations"""

        def func_nested_generics(
            nested_dict: Dict[str, List[Tuple[int, Optional[str]]]],
            nested_callable: Callable[[List[int]], Dict[str, Any]],
            nested_union: Union[List[int], Dict[str, float], None],
        ):
            pass

        inspection = inspect_function(func_nested_generics)
        params = inspection.parameters

        # Verify complex nested types are captured
        assert len(params) == 3
        for param in params:
            # Should contain some indication of the complex types
            assert len(param.annotation) > 10  # Complex annotations should be long

    def test_bound_method_vs_unbound(self):
        """Test the difference between bound and unbound methods"""

        class TestClass:
            def instance_method(self, value: int):
                return value

        obj = TestClass()

        # Test unbound method (from class)
        unbound_inspection = inspect_function(TestClass.instance_method)
        assert unbound_inspection.is_method is True
        assert len(unbound_inspection.parameters) == 2  # self + value
        assert unbound_inspection.parameters[0].name == "self"

        # Test bound method (from instance)
        bound_inspection = inspect_function(obj.instance_method)
        assert bound_inspection.is_method is True
        # Bound methods don't show the bound 'self' parameter
        assert len(bound_inspection.parameters) == 1
        assert bound_inspection.parameters[0].name == "value"
