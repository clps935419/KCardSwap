# 下一階段測試工作規劃

## 📊 當前狀態總結

### Priority 5 已完成 ✅
- **E2E 測試數**: 173 tests
- **端點覆蓋**: 37/37 (100%)
- **路由器覆蓋**: 14/14 (100%)
- **預估覆蓋率**: 95%+
- **狀態**: ✅ 完成

---

## 🎯 下一階段工作建議

### Priority 6: 效能與安全測試 (建議階段)

#### 📋 測試類型與目標

##### 1. 負載測試 (Load Testing)
**工具**: Locust 或 Apache JMeter

**測試場景** (建議 15-20 個測試):
- ✅ API 端點併發測試
  - 登入端點: 100-500 併發用戶
  - 列表端點: 100-1000 併發請求
  - 創建端點: 50-200 併發請求
- ✅ 資料庫連接池測試
  - 最大連接數測試
  - 連接超時處理
  - 連接洩漏檢測
- ✅ 回應時間測試
  - P50, P95, P99 延遲測試
  - 平均回應時間 < 200ms
  - 最大回應時間 < 2s

**實作範例**:
```python
# locustfile.py
from locust import HttpUser, task, between

class APILoadTest(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def list_posts(self):
        self.client.get("/api/v1/posts")
    
    @task(1)
    def create_post(self):
        self.client.post("/api/v1/posts", json={
            "scope": "global",
            "category": "trade",
            "title": "Load Test Post",
            "content": "Testing"
        })
```

**預估工作量**: 8-12 小時

---

##### 2. 壓力測試 (Stress Testing)
**目標**: 找出系統崩潰點

**測試場景** (建議 10-15 個測試):
- ✅ 漸進式增加負載
  - 從 10 用戶到 10000 用戶
  - 觀察系統降級點
- ✅ 峰值測試
  - 突發流量處理
  - 系統恢復能力
- ✅ 耐久測試
  - 24 小時持續負載
  - 記憶體洩漏檢測

**預估工作量**: 6-10 小時

---

##### 3. 安全測試 (Security Testing)
**工具**: OWASP ZAP, Bandit, Safety

**測試類型** (建議 20-30 個測試):

**A. SQL Injection 測試** (5-8 tests):
```python
def test_sql_injection_login():
    """Test SQL injection in login endpoint"""
    payload = {
        "email": "admin'--",
        "password": "' OR '1'='1"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code in [400, 401]  # Should not succeed
```

**B. XSS (Cross-Site Scripting) 測試** (5-8 tests):
- 測試用戶輸入清理
- HTML/JavaScript 注入防護
- 回應 Header 驗證

**C. CSRF (Cross-Site Request Forgery) 測試** (3-5 tests):
- CSRF token 驗證
- Referer header 檢查
- Same-site cookie 測試

**D. 認證與授權測試** (5-8 tests):
- JWT token 篡改測試
- Token 過期處理
- 權限提升攻擊防護
- Rate limiting 測試

**E. 敏感資料暴露測試** (3-5 tests):
- 密碼不應在回應中
- API key 保護
- 錯誤訊息不洩露系統資訊

**預估工作量**: 10-15 小時

---

##### 4. 輸入驗證與模糊測試 (Fuzzing)
**工具**: Hypothesis, AFL

**測試場景** (建議 15-20 個測試):
- ✅ 邊界值測試
- ✅ 特殊字符測試
- ✅ 超大輸入測試
- ✅ 型別混淆測試

**實作範例**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=0, max_size=10000))
def test_post_content_fuzzing(content):
    """Fuzz test for post content field"""
    response = client.post("/api/v1/posts", json={
        "scope": "global",
        "category": "trade",
        "title": "Test",
        "content": content
    })
    # Should handle any input gracefully
    assert response.status_code in [201, 400, 422]
```

**預估工作量**: 8-12 小時

---

### Priority 7: 整合測試完善 (建議階段)

#### 真實資料庫整合測試增強

**目前狀態**:
- 有 44 個測試因為需要真實資料庫而失敗
- 現有整合測試主要使用 Mock

**建議改善** (20-30 個測試):

##### 1. Testcontainers 整合
```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture
def test_db(postgres_container):
    """Provide test database"""
    engine = create_async_engine(postgres_container.get_connection_url())
    # Run migrations
    # Return session
    pass
```

**預估工作量**: 12-16 小時

##### 2. 外部服務整合測試
- Google OAuth 整合測試 (使用測試帳號)
- GCS 整合測試 (使用測試 bucket)
- FCM 整合測試 (使用測試 topic)

**預估工作量**: 10-15 小時

---

### Priority 8: 效能優化驗證 (建議階段)

#### N+1 查詢檢測與測試

**測試類型** (10-15 個測試):
```python
def test_list_posts_no_n_plus_1():
    """Verify no N+1 queries when listing posts"""
    with assert_query_count(max_queries=5):
        response = client.get("/api/v1/posts?limit=100")
    assert response.status_code == 200
```

**預估工作量**: 6-10 小時

---

### Priority 9: 端到端業務流程測試 (建議階段)

#### 完整用戶旅程測試

**測試場景** (15-25 個測試):

##### 1. 新用戶註冊到交易流程
```python
@pytest.mark.e2e
async def test_complete_user_journey():
    """Test complete user journey from signup to trade"""
    # 1. User signs up via Google OAuth
    # 2. Creates profile
    # 3. Uploads card images
    # 4. Creates trade post
    # 5. Receives message request
    # 6. Accepts and starts conversation
    # 7. Completes trade
    pass
```

##### 2. 訂閱功能完整流程
##### 3. 舉報與審核流程
##### 4. 好友系統完整流程

**預估工作量**: 12-18 小時

---

## 📊 優先級建議

### 🔴 高優先級 (應該做)
1. **安全測試** (Priority 6 - Security)
   - SQL Injection 防護驗證
   - XSS 防護驗證
   - 認證授權漏洞測試
   - **原因**: 防止安全漏洞，保護用戶資料

### 🟡 中優先級 (建議做)
2. **效能測試** (Priority 6 - Performance)
   - 基本負載測試
   - 回應時間測試
   - **原因**: 確保系統能處理預期流量

3. **真實資料庫測試** (Priority 7)
   - Testcontainers 設置
   - 修復 44 個失敗的整合測試
   - **原因**: 提高測試可靠性

### 🟢 低優先級 (可選)
4. **壓力測試** (Priority 6 - Stress)
5. **模糊測試** (Priority 6 - Fuzzing)
6. **完整業務流程測試** (Priority 9)

---

## 🎯 實施建議

### 階段 1: 安全測試 (Week 1-2)
**投入**: 10-15 小時
**產出**: 20-30 個安全測試
**目標**: 確保無重大安全漏洞

### 階段 2: 基礎效能測試 (Week 3)
**投入**: 8-12 小時
**產出**: 15-20 個效能測試
**目標**: 驗證系統能承受基本負載

### 階段 3: 整合測試完善 (Week 4-5)
**投入**: 12-16 小時
**產出**: Testcontainers 設置 + 修復失敗測試
**目標**: 100% 整合測試通過率

---

## 📋 非測試類工作

除了測試，還有其他重要工作：

### 1. CI/CD 完善
- ✅ 自動化測試執行
- ✅ 覆蓋率報告生成
- ✅ 覆蓋率門檻檢查 (目標: 90%+)
- ✅ 安全掃描自動化

### 2. 文件完善
- ✅ API 文件更新 (OpenAPI)
- ✅ 測試文件撰寫
- ✅ 部署文件

### 3. 監控與日誌
- ✅ APM (Application Performance Monitoring) 整合
- ✅ 錯誤追蹤 (Sentry)
- ✅ 日誌聚合

### 4. 資料庫優化
- ✅ 索引優化
- ✅ 查詢優化
- ✅ 連接池調優

---

## 🎊 總結建議

### 最小可行方案 (MVP)
如果資源有限，**優先完成**:
1. ✅ 安全測試 (SQL Injection, XSS, 認證授權)
2. ✅ 基本負載測試 (驗證能承受預期流量)
3. ✅ 修復 Testcontainers 設置

**預估總工作量**: 30-40 小時
**預期成果**: 系統安全性得到驗證，效能符合基本需求

### 完整方案
如果有充足資源，**依序完成**:
1. Priority 6: 安全測試
2. Priority 6: 效能測試
3. Priority 7: 整合測試完善
4. Priority 6: 壓力測試
5. Priority 8: 效能優化驗證
6. Priority 9: 業務流程測試

**預估總工作量**: 80-120 小時
**預期成果**: 企業級測試品質，系統穩定可靠

---

## 📈 預期覆蓋率演進

| 階段 | 覆蓋率 | 測試類型 |
|------|--------|----------|
| Priority 5 完成 | 95% | 功能測試 (E2E) |
| Priority 6 安全 | 95% | +安全測試 |
| Priority 6 效能 | 95% | +效能測試 |
| Priority 7 整合 | 97% | +真實整合測試 |
| 全部完成 | 98%+ | 全方位測試 |

---

**創建時間**: 2026-01-25
**狀態**: Priority 5 已完成，建議進入 Priority 6 (安全與效能測試)
**建議優先級**: 安全測試 > 效能測試 > 整合測試完善
