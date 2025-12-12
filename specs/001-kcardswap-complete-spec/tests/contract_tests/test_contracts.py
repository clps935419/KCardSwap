import json
from pathlib import Path
import pytest


CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"


def _collect_contract_files():
    return sorted(CONTRACTS_DIR.rglob("*.json"))


@pytest.mark.parametrize("contract_path", _collect_contract_files())
def test_contract_marked_implemented(contract_path):
    """Contract tests (Test-First). All contracts must be marked implemented==True to pass.

    These are expected to fail (Red) until the backend implements the contract.
    """
    data = json.loads(contract_path.read_text(encoding="utf-8"))
    assert data.get("implemented", False), f"Contract {contract_path} is not implemented yet"
