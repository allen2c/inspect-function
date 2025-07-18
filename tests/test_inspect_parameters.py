from typing import Any, Dict, List, Optional, Union

import pytest

from inspect_function import inspect_parameters


class TestInspectParameters:
    def test_basic_function(self):
        """Test basic function with positional and keyword parameters"""

        def test_func(a: int, b: str, c: bool = True) -> str:
            return f"{a}-{b}-{c}"

        params = {"a": 42, "b": "hello", "c": False}
        args, kwargs = inspect_parameters(test_func, params)

        # Execute the function to verify parameters work
        result = test_func(*args, **kwargs)
        assert result == "42-hello-False"

        # Test with missing optional parameter
        params_partial = {"a": 10, "b": "world"}
        args, kwargs = inspect_parameters(test_func, params_partial)
        result = test_func(*args, **kwargs)
        assert result == "10-world-True"  # Uses default value

    def test_positional_only_parameters(self):
        """Test function with positional-only parameters (before /)"""

        def test_func(a: int, b: str, /, c: bool = True) -> str:
            return f"{a}-{b}-{c}"

        params = {"a": 1, "b": "test", "c": False}
        args, kwargs = inspect_parameters(test_func, params)

        # Positional-only params should be in args, not kwargs
        assert len(args) == 2  # a and b should be positional
        assert "c" in kwargs  # c can be keyword

        result = test_func(*args, **kwargs)
        assert result == "1-test-False"

    def test_keyword_only_parameters(self):
        """Test function with keyword-only parameters (after *)"""

        def test_func(a: int, *, b: str, c: bool = True) -> str:
            return f"{a}-{b}-{c}"

        params = {"a": 5, "b": "keyword", "c": False}
        args, kwargs = inspect_parameters(test_func, params)

        # Only 'a' should be positional, b and c must be keywords
        assert "a" in kwargs  # a can be passed as keyword
        assert "b" in kwargs
        assert "c" in kwargs

        result = test_func(*args, **kwargs)
        assert result == "5-keyword-False"

    def test_var_positional_parameters(self):
        """Test function with *args"""

        def test_func(a: int, *args: int) -> int:
            return a + sum(args)

        # Test with list for *args
        params = {"a": 10, "args": [1, 2, 3, 4]}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result == 20  # 10 + 1 + 2 + 3 + 4

        # Test with tuple for *args
        params = {"a": 5, "args": (2, 3)}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result == 10  # 5 + 2 + 3

        # Test with single value for *args
        params = {"a": 7, "args": 3}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result == 10  # 7 + 3

    def test_var_keyword_parameters(self):
        """Test function with **kwargs"""

        def test_func(a: int, **kwargs: Any) -> dict:
            result = {"a": a}
            result.update(kwargs)
            return result

        # Test with dict for **kwargs
        params = {"a": 1, "kwargs": {"x": 10, "y": 20}}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result == {"a": 1, "x": 10, "y": 20}

        # Test with individual extra parameters
        params = {"a": 2, "extra1": "value1", "extra2": "value2"}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result == {"a": 2, "extra1": "value1", "extra2": "value2"}

    def test_complex_parameter_combinations(self):
        """Test function with all parameter kinds"""

        def complex_func(
            pos_only: int,
            /,
            regular: str,
            *args: float,
            kw_only: bool,
            kw_with_default: Optional[str] = None,
            **kwargs: Any,
        ) -> dict:
            return {
                "pos_only": pos_only,
                "regular": regular,
                "args": args,
                "kw_only": kw_only,
                "kw_with_default": kw_with_default,
                "kwargs": kwargs,
            }

        params = {
            "pos_only": 1,
            "regular": "test",
            "args": [1.1, 2.2, 3.3],
            "kw_only": True,
            "kw_with_default": "custom",
            "extra_param": "extra_value",
        }

        args, kwargs = inspect_parameters(complex_func, params)
        result = complex_func(*args, **kwargs)

        assert result["pos_only"] == 1
        assert result["regular"] == "test"
        assert result["args"] == (1.1, 2.2, 3.3)
        assert result["kw_only"] is True
        assert result["kw_with_default"] == "custom"
        assert result["kwargs"]["extra_param"] == "extra_value"

    def test_method(self):
        """Test instance method"""

        class TestClass:
            def __init__(self, value: int):
                self.value = value

            def method(self, a: int, b: str = "default") -> str:
                return f"{self.value}-{a}-{b}"

        obj = TestClass(100)

        # Test unbound method (from class)
        params = {"self": obj, "a": 5, "b": "test"}
        args, kwargs = inspect_parameters(TestClass.method, params)
        result = TestClass.method(*args, **kwargs)
        assert result == "100-5-test"

        # Test bound method (from instance)
        params = {"a": 10, "b": "bound"}
        args, kwargs = inspect_parameters(obj.method, params)
        result = obj.method(*args, **kwargs)
        assert result == "100-10-bound"

    def test_classmethod(self):
        """Test class method"""

        class TestClass:
            class_var = "CLASS"

            @classmethod
            def class_method(cls, a: int, b: str = "default") -> str:
                return f"{cls.class_var}-{a}-{b}"

        params = {"a": 15, "b": "classmethod"}
        args, kwargs = inspect_parameters(TestClass.class_method, params)
        result = TestClass.class_method(*args, **kwargs)
        assert result == "CLASS-15-classmethod"

    def test_staticmethod(self):
        """Test static method"""

        class TestClass:
            @staticmethod
            def static_method(a: int, b: str = "default") -> str:
                return f"STATIC-{a}-{b}"

        params = {"a": 25, "b": "static"}
        args, kwargs = inspect_parameters(TestClass.static_method, params)
        result = TestClass.static_method(*args, **kwargs)
        assert result == "STATIC-25-static"

    def test_async_function(self):
        """Test async function"""
        import asyncio

        async def async_func(a: int, b: str = "async") -> str:
            await asyncio.sleep(0)  # Simulate async operation
            return f"ASYNC-{a}-{b}"

        params = {"a": 30, "b": "test"}
        args, kwargs = inspect_parameters(async_func, params)

        # Execute async function
        async def run_test():
            result = await async_func(*args, **kwargs)
            assert result == "ASYNC-30-test"

        # Run the async test
        asyncio.run(run_test())

    def test_default_values(self):
        """Test various default value types"""

        def test_func(
            none_val: Optional[str] = None,
            list_val: Optional[List[int]] = None,
            dict_val: Optional[Dict[str, int]] = None,
            bool_val: bool = False,
            int_val: int = 42,
            str_val: str = "default",
        ) -> dict:
            return {
                "none_val": none_val,
                "list_val": list_val or [],
                "dict_val": dict_val or {},
                "bool_val": bool_val,
                "int_val": int_val,
                "str_val": str_val,
            }

        # Test with all defaults
        params = {}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result["none_val"] is None
        assert result["list_val"] == []
        assert result["dict_val"] == {}
        assert result["bool_val"] is False
        assert result["int_val"] == 42
        assert result["str_val"] == "default"

        # Test with some overrides
        params = {"int_val": 100, "str_val": "custom"}
        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert result["int_val"] == 100
        assert result["str_val"] == "custom"

    def test_no_parameters(self):
        """Test function with no parameters"""

        def no_params() -> str:
            return "no-params"

        params = {}
        args, kwargs = inspect_parameters(no_params, params)
        result = no_params(*args, **kwargs)
        assert result == "no-params"

        # Test with extra parameters (should be ignored if no **kwargs)
        params = {"extra": "value"}
        args, kwargs = inspect_parameters(no_params, params)
        # Function should still work since extra params go to kwargs
        # but the function doesn't accept them, so this would raise TypeError
        with pytest.raises(TypeError):
            no_params(*args, **kwargs)

    def test_only_variadic_parameters(self):
        """Test function with only *args and **kwargs"""

        def only_variadic(*args, **kwargs) -> dict:
            return {"args": args, "kwargs": kwargs}

        params = {
            "args": [1, 2, 3],
            "kwargs": {"a": "A", "b": "B"},
            "extra": "extra_value",
        }

        args, kwargs = inspect_parameters(only_variadic, params)
        result = only_variadic(*args, **kwargs)

        assert result["args"] == (1, 2, 3)
        assert "a" in result["kwargs"]
        assert "b" in result["kwargs"]
        assert "extra" in result["kwargs"]
        assert result["kwargs"]["extra"] == "extra_value"

    def test_missing_required_parameters(self):
        """Test function with missing required parameters"""

        def test_func(required: int, optional: str = "default") -> str:
            return f"{required}-{optional}"

        # Missing required parameter should still work at inspect_parameters level
        # but fail when actually calling the function
        params = {"optional": "test"}
        args, kwargs = inspect_parameters(test_func, params)

        with pytest.raises(TypeError):
            test_func(*args, **kwargs)

    def test_extra_parameters_no_kwargs(self):
        """Test function with extra parameters when no **kwargs"""

        def test_func(a: int, b: str) -> str:
            return f"{a}-{b}"

        params = {"a": 1, "b": "test", "extra": "value"}
        args, kwargs = inspect_parameters(test_func, params)

        # Extra parameter should be in kwargs but function doesn't accept it
        assert "extra" in kwargs
        with pytest.raises(TypeError):
            test_func(*args, **kwargs)

    def test_extra_parameters_with_kwargs(self):
        """Test function with extra parameters when **kwargs exists"""

        def test_func(a: int, b: str, **kwargs) -> dict:
            return {"a": a, "b": b, "kwargs": kwargs}

        params = {"a": 1, "b": "test", "extra": "value", "another": 42}
        args, kwargs = inspect_parameters(test_func, params)

        result = test_func(*args, **kwargs)
        assert result["a"] == 1
        assert result["b"] == "test"
        assert result["kwargs"]["extra"] == "value"
        assert result["kwargs"]["another"] == 42

    def test_complex_type_annotations(self):
        """Test functions with complex type annotations"""

        def test_func(
            union_param: Union[int, str],
            optional_param: Optional[List[int]],
            dict_param: Dict[str, Any],
        ) -> str:
            return f"{union_param}-{optional_param}-{dict_param}"

        params = {
            "union_param": "string_value",
            "optional_param": [1, 2, 3],
            "dict_param": {"key": "value"},
        }

        args, kwargs = inspect_parameters(test_func, params)
        result = test_func(*args, **kwargs)
        assert "string_value" in result
        assert "[1, 2, 3]" in result
        assert "key" in result

    def test_mixed_parameter_order(self):
        """Test parameters provided in different order than function signature"""

        def test_func(a: int, b: str, c: bool, d: float = 3.14) -> str:
            return f"{a}-{b}-{c}-{d}"

        # Provide parameters in different order
        params = {"d": 2.71, "a": 10, "c": True, "b": "mixed"}
        args, kwargs = inspect_parameters(test_func, params)

        result = test_func(*args, **kwargs)
        assert result == "10-mixed-True-2.71"

    def test_lambda_function(self):
        """Test lambda function"""

        def lambda_func(x, y=10):
            return x * y

        params = {"x": 5, "y": 3}
        args, kwargs = inspect_parameters(lambda_func, params)

        result = lambda_func(*args, **kwargs)
        assert result == 15

        # Test with default value
        params = {"x": 7}
        args, kwargs = inspect_parameters(lambda_func, params)
        result = lambda_func(*args, **kwargs)
        assert result == 70

    def test_nested_function(self):
        """Test nested function"""

        def outer_func(multiplier: int):
            def inner_func(a: int, b: int = 1) -> int:
                return (a + b) * multiplier

            return inner_func

        inner = outer_func(3)
        params = {"a": 5, "b": 2}
        args, kwargs = inspect_parameters(inner, params)

        result = inner(*args, **kwargs)
        assert result == 21  # (5 + 2) * 3
