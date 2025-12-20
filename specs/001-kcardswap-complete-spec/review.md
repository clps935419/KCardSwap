# KCardSwap Spec Review - 001

**Date**: 2025-12-10  
**Scope**: specs/001-kcardswap-complete-spec (spec.md, plan.md, tasks.md)  
**Goal**: 在實作前完成一致性與可落地性審查，確認風險與決策。

---

## Overview
- 本次審查對象：產品規格（spec.md）、技術規劃（plan.md）、任務清單（tasks.md）。
- 審查目標：需求明確、技術方案可行、任務可交付、測試可驗收、風險可緩解。
 - 訂閱金流範圍：Android 僅用 Google Play Billing，後端僅驗證訂閱收據並同步 `subscriptions` 狀態；不直接處理金流或退款。iOS 後續採 Apple IAP，責任範圍相同（僅驗證收據）。

## Spec Findings
- 規格內容齊全，含 User Stories、Functional Requirements、Key Entities、Success Criteria、Assumptions、Out of Scope。
- BIZ 區塊已明確：
  - 免費：每日卡冊新增 3、貼文 2、總容量 100MB、單張 2MB、附近 5 次。
  - 付費：每日卡冊新增不限（受總容量 1GB）、貼文不限、單張 5MB、附近不限。
- API Gateway：Kong（POC）+ 未來可 GCP；API 前綴 `/api/v1/*`；錯誤碼集已列舉。

## Plan Assessment
- 里程碑（M0–M7）合理，與 P1/P2 對齊。
- 架構對齊：`docker-compose.yml`、`gateway/kong/kong.yaml`、`apps/backend/README.md` 已建立；與計劃一致。
- 測試策略涵蓋單元、整合、E2E、性能、安全；與 SC-001..005 呼應。

## Tasks Audit
- `tasks.md` 已分 Phase（Setup→AUTH→CARD→NEARBY→SOCIAL/CHAT→TRADE→BIZ→API→UI/UX→DB→Test→Ops）。
- 任務具體到檔案路徑與錯誤碼/驗收示例（如 `422_LIMIT_EXCEEDED`、`429_RATE_LIMITED`）。
- 建議補充：在「BIZ」任務中加入「後台配置介面占位」與「容量/貼文參數讀取來源」。

## Risks & Mitigations
- 位置隱私：不顯示精確地址、僅行政區與距離；隱身過濾（NEARBY 章節）。
- 上傳濫用：Kong request-size-limiting、後端型別/大小白名單；達上限回傳 422。
- 推播可靠性：前景輪詢兜底（3–5 秒）、背景 FCM；失敗重試策略需在 CHAT 任務補充。
- 成本控制：GCS 單價低、容量政策保守；可依營運調整。
 - 訂閱金流：Android 僅採「Google Play Billing」；後端僅執行訂閱收據驗證與狀態同步，退款由 Google Play 機制處理。iOS 未來採「Apple IAP」同樣僅驗證收據。產品不支援卡片買賣或交易金流；需在 BIZ 模組明確訂閱異常處理（重試、狀態回滾）。

## Decisions & Rationale
- API Gateway：POC 用 Kong OSS；正式可 GCP 或 Kong Enterprise on GKE（成本/治理考量）。
- 儲存策略：GCS + 固定額度；免費/付費容量與單張大小已明確，成本相對訂價可忽略。
- 錯誤碼策略：統一格式 `{ data, error }`；錯誤碼集合固定，利於前後端協作。
 - 金流範圍：訂閱支付在 Android 僅用「Google Play Billing」，未來 iOS 用「Apple IAP」。後端僅負責訂閱收據驗證與狀態管理，不直接介入金流或退款。產品不提供卡片買賣或交易金流。

## Interfaces & OpenAPI/Swagger
- Kong 宣告式路由至 `backend:8000`；CORS、rate-limit、size-limiting 已配置。
- 後端 FastAPI：建議維護 `apps/backend/openapi.yaml`（即使 FastAPI 自生 Swagger，也可導出）。
- 資料模型：cards/trades/trade_items/chats/messages/friendships/ratings/reports/subscriptions 已在 plan 中列舉；任務需同步建表與索引（T1001）。

## Validation Strategy
- 單元：權限檢查、上限計數、狀態機、錯誤碼。
- 整合：Kong+Backend JWT/限流；GCS 上傳流程。
- E2E：對齊 User Story 1–6；以 SC-001..005 測量。
- 性能：聊天延遲、附近搜尋查詢時間、圖片上傳吞吐；安全：檔案白名單、濫用防護。

## Gaps & Actions
- [ ] 在 BIZ 任務補充金流異常處理（重試、退款、狀態回滾）。
- [ ] 在 CHAT 任務補充推播失敗退回輪詢的降級策略與告警。
- [ ] 在 NEARBY 任務標注「位置來源」偏好與權限拒絕降級顯示方案。
- [ ] 在 CARD 上限檢查中明確前端 UX 指引（錯誤提示文案統一）。
- [ ] 在 API 標準章節加入 `409_CONFLICT` 的典型場景（交易狀態競態）。
- [ ] 在 DB 任務補充必要索引清單與唯一性約束（如 friendship 唯一對）。
 - [ ] 訂閱收據檢核細節：定義重試策略（次數、退避）、狀態回滾條件、監控指標（驗證失敗率、重試成功率）；退款由平台機制處理。

## Sign-off
- Reviewer(s): PM / Tech Lead / Backend / Mobile / QA
- Decision: 
  - [ ] Approve
  - [ ] Approve with changes
  - [ ] Request changes
- Notes:
  - 審查後如有變更，請同步更新 `spec.md` / `plan.md` / `tasks.md`，並將「Gaps & Actions」轉為 issue 分派。
