# Contract Tests (已停用)

此目錄的合約測試流程已停用，保留檔案僅作為歷史紀錄。

目前我們預期測試為 Red（失敗），表示契約已定義但尚未實作。當後端實作並更新對應 contract JSON 的 `implemented: true` 時，測試將會轉為 Green。

執行：
```bash
python -m pytest specs/001-kcardswap-complete-spec/tests/contract_tests -q
```
