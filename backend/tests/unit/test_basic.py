"""Basic tests to verify pytest setup."""


def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2


def test_import_backend():
    """Test that backend package can be imported."""
    try:
        import src

        assert src.__version__ == "0.1.0"
    except ImportError as e:
        raise AssertionError(f"Failed to import backend: {e}") from e


def test_python_version():
    """Test Python version compatibility."""
    import sys

    # Should be 3.11 or 3.12 as per tech specs
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 11
    assert sys.version_info.minor <= 12
