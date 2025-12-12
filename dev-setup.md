# 本機開發環境設定 (Windows / Git Bash 簡易說明)

1) 建立並啟用虛擬環境 (.venv)

Git Bash (bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) 安裝開發相依

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

3) 執行合約測試

```bash
python -m pytest specs/001-kcardswap-complete-spec/tests/contract_tests -q
```

說明：合約測試設計為 Test-First（Red），在後端實作並更新合約 JSON 的 `implemented: true` 後，測試才會通過（Green）。
