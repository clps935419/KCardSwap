import pytest


@pytest.fixture(autouse=True)
def _skip_contract_tests():
    pytest.skip(
        "contract test suite removed; file kept only as stub", allow_module_level=True
    )
