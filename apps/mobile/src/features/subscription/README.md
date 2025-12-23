# Subscription Feature

Google Play 訂閱系統整合，支援付費方案升級、收據驗證、購買恢復等功能。

## 功能概述

- ✅ 顯示訂閱方案（免費 vs 付費）
- ✅ Google Play Billing 整合
- ✅ 收據驗證（後端 server-side）
- ✅ 訂閱狀態查詢
- ✅ 購買恢復（換機/重裝）
- ✅ 防重放攻擊保護
- ✅ App 回前景自動更新狀態

## 架構設計

### 安全性設計
1. **Server-Side 驗證**：所有購買必須經過後端驗證
2. **Token 綁定**：purchase_token 與 user 永久綁定
3. **防重放**：跨用戶重放攻擊返回 409 CONFLICT
4. **冪等性**：同用戶重送返回當前狀態

### 狀態管理
- **active**: 訂閱啟用中
- **expired**: 訂閱已過期
- **inactive**: 未訂閱
- **pending**: 付款處理中

## 前置需求

### 1. Expo Development Build

Google Play Billing 需要原生模組，**無法在 Expo Go 中使用**。

```bash
# 安裝 EAS CLI
npm install -g eas-cli

# 登入 Expo
eas login

# 建立 Development Build
eas build --profile development --platform android
```

### 2. 安裝依賴

```bash
npm install react-native-iap
```

### 3. Google Play Console 配置

1. 建立應用程式並上傳 APK/AAB
2. 設定內購產品（訂閱）：
   - Product ID: `premium_monthly`
   - 價格: NT$ 120
   - 訂閱週期: 1 個月
3. 建立 Service Account 並下載 JSON 金鑰
4. 授予 Service Account「財務資料檢視者」權限

### 4. 後端配置

```bash
# 環境變數
GOOGLE_PLAY_PACKAGE_NAME=com.yourapp.package
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH=/path/to/service-account.json
```

## 使用方式

### 訂閱方案頁面

```tsx
import { SubscriptionPlansScreen } from '@/src/features/subscription';

// 在導航中使用
<Stack.Screen name="subscription-plans" component={SubscriptionPlansScreen} />
```

### 訂閱狀態頁面

```tsx
import { SubscriptionStatusScreen } from '@/src/features/subscription';

<Stack.Screen name="subscription-status" component={SubscriptionStatusScreen} />
```

### 檢查訂閱狀態

```tsx
import { useSubscriptionStatus, useIsPremium } from '@/src/features/subscription';

function MyComponent() {
  const { subscription, isPremium } = useSubscriptionStatus();
  
  // 或直接使用
  const isPremium = useIsPremium();
  
  if (isPremium) {
    return <PremiumFeature />;
  }
  
  return <FreeFeature />;
}
```

### 購買流程

```tsx
import { useGooglePlayBilling, useVerifyReceipt, SUBSCRIPTION_SKUS } from '@/src/features/subscription';

function PurchaseButton() {
  const { purchaseSubscription } = useGooglePlayBilling();
  const { verifyReceiptAsync } = useVerifyReceipt();
  
  const handlePurchase = async () => {
    // Step 1: 透過 Google Play 購買
    const purchase = await purchaseSubscription(SUBSCRIPTION_SKUS.PREMIUM_MONTHLY);
    
    if (!purchase) return; // 用戶取消
    
    // Step 2: 後端驗證收據
    const result = await verifyReceiptAsync({
      platform: 'android',
      purchase_token: purchase.purchaseToken,
      product_id: SUBSCRIPTION_SKUS.PREMIUM_MONTHLY,
    });
    
    // Step 3: 檢查是否啟用
    if (result.entitlement_active) {
      Alert.alert('訂閱成功！');
    }
  };
  
  return <Button onPress={handlePurchase}>訂閱</Button>;
}
```

### 恢復購買

```tsx
import { useGooglePlayBilling, useVerifyReceipt } from '@/src/features/subscription';

function RestoreButton() {
  const { restorePurchases } = useGooglePlayBilling();
  const { verifyReceiptAsync } = useVerifyReceipt();
  
  const handleRestore = async () => {
    // Step 1: 查詢 Google Play 現有購買
    const purchases = await restorePurchases();
    
    // Step 2: 重新驗證每筆購買
    for (const purchase of purchases) {
      await verifyReceiptAsync({
        platform: 'android',
        purchase_token: purchase.purchaseToken,
        product_id: purchase.productId,
      });
    }
    
    Alert.alert('恢復成功！');
  };
  
  return <Button onPress={handleRestore}>恢復購買</Button>;
}
```

## API 端點

### POST /api/v1/subscriptions/verify-receipt

驗證 Google Play 購買收據

```json
// Request
{
  "platform": "android",
  "purchase_token": "abc123...",
  "product_id": "premium_monthly"
}

// Response
{
  "plan": "premium",
  "status": "active",
  "expires_at": "2025-01-23T00:00:00Z",
  "entitlement_active": true,
  "source": "google_play"
}
```

### GET /api/v1/subscriptions/status

查詢訂閱狀態

```json
// Response
{
  "plan": "premium",
  "status": "active",
  "expires_at": "2025-01-23T00:00:00Z",
  "entitlement_active": true,
  "source": "google_play"
}
```

## 錯誤處理

### 常見錯誤碼

- `409_CONFLICT`: purchase_token 已被其他帳號使用
- `400_VALIDATION_FAILED`: 參數錯誤
- `503_SERVICE_UNAVAILABLE`: Google Play API 暫時不可用

### 錯誤處理範例

```tsx
try {
  await verifyReceiptAsync(request);
} catch (error) {
  if (error.message.includes('PURCHASE_TOKEN_ALREADY_USED')) {
    Alert.alert('錯誤', '此購買已被其他帳號使用');
  } else if (error.message.includes('GOOGLE_PLAY_UNAVAILABLE')) {
    Alert.alert('錯誤', '驗證暫時失敗，請稍後再試');
  } else {
    Alert.alert('購買失敗', error.message);
  }
}
```

## 測試

### 測試環境

1. 在 Google Play Console 設定測試帳號
2. 上傳 Internal Testing Track
3. 使用測試帳號購買（不會實際收費）

### 測試場景

- ✅ 成功購買並驗證
- ✅ 用戶取消購買
- ✅ 網路錯誤重試
- ✅ 換機恢復購買
- ✅ 跨帳號重放拒絕
- ✅ 訂閱到期處理

## 生產環境注意事項

1. **Service Account 金鑰**: 絕不可 commit 到 git
2. **環境變數**: 使用 Expo Secrets 或環境變數管理
3. **錯誤監控**: 整合 Sentry 追蹤購買失敗
4. **日誌**: 記錄所有購買與驗證事件
5. **用戶支援**: 提供清楚的錯誤訊息與客服管道

## 限制與已知問題

### POC 階段限制
- ❌ 不支援 iOS (Apple IAP 需另外實作)
- ❌ 無 RTDN/Webhook (採用輪詢 + 定期降級)
- ❌ 無自動續訂失敗處理 (用戶需手動重試)

### 未來擴展
- [ ] iOS Apple IAP 支援
- [ ] RTDN/Webhook 即時狀態更新
- [ ] 多種訂閱週期 (月/年)
- [ ] 試用期支援
- [ ] 促銷碼支援

## 相關文件

- [Google Play Billing Library](https://developer.android.com/google/play/billing)
- [react-native-iap](https://github.com/dooboolab/react-native-iap)
- [Expo Development Builds](https://docs.expo.dev/develop/development-builds/introduction/)

## 支援

如有問題，請聯繫：
- 技術支援：tech@kcardswap.com
- 帳務問題：billing@kcardswap.com
