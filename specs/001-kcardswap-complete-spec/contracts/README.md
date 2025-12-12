# Contracts (API 契約測試規格)

目的：集中定義各模組 API 契約（請求/回應結構、狀態碼、邊界情境），作為契約測試的唯一來源，符合 Integration‑First Gate。

結構：
- auth/
- cards/
- nearby/
- social/
- chat/
- trade/
- biz/

約定：
- 每模組至少 3–5 個契約用例，覆蓋成功、驗證失敗、權限不足/限流。
- 回應格式遵循 `{ data, error }` 規範與標準錯誤碼。
- 若契約更新，須同步更新對應測試與 `specs/001-.../plan.md`。
