# Contract tests

這個資料夾包含契約測試（Contract tests）的範例。測試會掃描 `../contracts/*.json` 的所有 JSON 檔案，並驗證每個契約檔案的 `implemented` 欄位為 `true`。

目前我們預期測試為 Red（失敗），表示契約已定義但尚未實作。當後端實作並更新對應 contract JSON 的 `implemented: true` 時，測試將會轉為 Green。

執行：
```bash
python -m pytest specs/001-kcardswap-complete-spec/tests/contract_tests -q
```
