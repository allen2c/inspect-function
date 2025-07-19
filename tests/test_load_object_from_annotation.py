import pathlib

import pytest

from inspect_function.utils.load_object_from_annotation import (
    load_object_from_annotation,
)


class TestLoadObjectFromAnnotation:
    """Test the load_object_from_annotation function."""

    def test_successful_class_loading(self):
        """Test loading a class annotation successfully."""
        result = load_object_from_annotation(
            "<class '__main__.TestLoadObjectFromAnnotation'>"
        )
        assert result is TestLoadObjectFromAnnotation

    def test_builtin_type_loading(self):
        """Test loading built-in types."""
        result = load_object_from_annotation("<class 'int'>")
        assert result is int

    def test_simple_literals(self):
        """Test loading simple literals like 'Any' and 'None'."""
        result = load_object_from_annotation("Any")
        # Should return typing.Any
        assert str(result) == "typing.Any"

        result = load_object_from_annotation("None")
        assert result is type(None)

    def test_imported_module_attribute(self):
        """Test loading attributes from imported modules."""
        result = load_object_from_annotation("pathlib.Path")
        assert result is pathlib.Path

    def test_module_not_imported_error(self):
        """Test that ModuleNotFoundError is raised for unimported modules."""
        with pytest.raises(ModuleNotFoundError) as exc_info:
            load_object_from_annotation("np.ndarray")

        assert (
            "Module 'np' required for annotation 'np.ndarray' is not imported"
            in str(exc_info.value)
        )

    def test_module_not_imported_error_nested(self):
        """Test ModuleNotFoundError for nested module paths."""
        with pytest.raises(ModuleNotFoundError) as exc_info:
            load_object_from_annotation("matplotlib.pyplot.Figure")

        expected_msg = (
            "Module 'matplotlib' required for annotation "
            "'matplotlib.pyplot.Figure' is not imported"
        )
        assert expected_msg in str(exc_info.value)

    def test_typing_constructs(self):
        """Test loading typing constructs."""
        result = load_object_from_annotation("typing.List[int]")
        # Should successfully parse typing constructs
        assert result is not None

    def test_non_string_input(self):
        """Test that non-string input returns None."""
        # Type ignore for intentional type error testing
        result = load_object_from_annotation(123)  # type: ignore
        assert result is None

    def test_direct_name_lookup(self):
        """Test direct name lookup in globals."""
        # This should return None for unknown names
        result = load_object_from_annotation("UnknownClassName")
        assert result is None

    def test_standard_repr_without_module_attribute(self):
        """Test that standard repr format doesn't trigger ModuleNotFoundError."""
        # This should not raise ModuleNotFoundError because it's in standard repr format
        result = load_object_from_annotation("<class 'some_unknown_module.SomeClass'>")
        # Should return None through normal resolution, not raise ModuleNotFoundError
        assert result is None
