from inspect_function import ParameterKind, inspect_function


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
