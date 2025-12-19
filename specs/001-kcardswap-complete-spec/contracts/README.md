# Contracts (API 契約測試規格)

目的：集中定義各模組 API 契約（請求/回應結構、狀態碼、邊界情境），作為契約測試的唯一來源，符合 Integration‑First Gate。

## Guardrails（硬性約束）

- **禁止縮圖欄位**：所有契約（request/response）不得出現任何 `thumb_*` / `thumbnail_*` 欄位（例如 `thumb_url`, `thumbnail_url`）。
- **縮圖責任邊界**：縮圖為 Mobile 端本機產生（`200x200` WebP）並本機快取；**不上傳、不入後端 DB、後端不回傳**。
- **後端只負責原圖**：後端僅提供「原圖上傳 Signed URL」與配額/限制檢查；物件路徑僅允許 `cards/{user_id}/{uuid}.jpg`，禁止 `thumbs/`。

結構：
- auth/
- cards/
- posts/
- nearby/
- social/
- chat/
- trade/
- biz/

posts/（城市/行政區佈告欄貼文）建議契約：
- create_post.json
- list_board_posts.json
- express_interest.json
- accept_interest.json
- reject_interest.json
- close_post.json

約定：
- 每模組至少 3–5 個契約用例，覆蓋成功、驗證失敗、權限不足/限流。
- 回應格式遵循 `{ data, error }` 規範與標準錯誤碼。
- 若契約更新，須同步更新對應測試與 `specs/001-kcardswap-complete-spec/plan.md`。
