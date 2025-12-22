# KCardSwap Mobile 路由架構文件 (Routing Architecture)

**版本**: 1.0  
**最後更新**: 2025-12-22

---

## 📱 應用程式路由結構概覽

KCardSwap Mobile 使用 **Expo Router** 的檔案式路由系統，結合 Tab 導航和 Stack 導航。

### 整體架構

```
App Root
├── Auth Flow (未登入時)
│   └── /auth/login
│
└── Main App (已登入時)
    └── (tabs) - 底部 Tab 導航
        ├── Home (首頁)
        ├── My Cards (我的卡冊)
        ├── Nearby (附近搜尋)
        └── Profile (個人檔案)
```

---

## 🏠 Tab 導航 (Bottom Tabs)

位於 `app/(tabs)/` 目錄，這些頁面會顯示在底部導航列。

### 1. Home (首頁) - `/`
- **檔案**: `app/(tabs)/index.tsx`
- **圖示**: 🏠 home
- **功能**: 
  - 應用程式主頁
  - 顯示最新活動、推薦卡片等
  - 快速導航入口到其他功能

### 2. My Cards (我的卡冊) - `/cards`
- **檔案**: `app/(tabs)/cards/index.tsx`
- **圖示**: 📚 albums
- **功能**:
  - 顯示使用者擁有的所有小卡
  - 卡片列表（使用本機縮圖快取）
  - 刪除卡片功能
- **子路由**:
  - `/cards/upload` - 上傳新卡片

### 3. Nearby (附近搜尋) - `/nearby`
- **檔案**: `app/(tabs)/nearby.tsx`
- **圖示**: 📍 location
- **功能**:
  - 搜尋附近的小卡
  - 地圖/列表顯示
  - 定位權限處理

### 4. Profile (個人檔案) - `/profile`
- **檔案**: `app/(tabs)/profile.tsx`
- **圖示**: 👤 person
- **功能**:
  - 顯示個人資訊
  - 編輯暱稱、簡介、頭像
  - 隱私設定
  - 登出

---

## 📄 Stack 路由 (非 Tab 頁面)

這些頁面**不在底部導航列**，需要從其他頁面導航進入。

### Friends (好友系統) - Phase 6

#### 1. Friends List - `/friends`
- **檔案**: `app/friends/index.tsx`
- **從哪裡進入**:
  - 從 **Home 首頁**的好友入口進入
  - 從聊天室列表的「查看好友」按鈕
  - 從推播通知 (friend_request 類型)
- **功能**:
  - 三個 Tab: 好友 / 待處理 / 已封鎖
  - Pull-to-refresh
  - 點擊好友進入個人檔案
  - 新增好友按鈕

#### 2. Add Friend - `/friends/add`
- **檔案**: `app/friends/add.tsx`
- **從哪裡進入**:
  - 從 Friends List 的「+ 新增」按鈕
- **功能**:
  - 輸入好友 ID 發送邀請
  - 表單驗證

#### 3. Friend Profile - `/friends/[userId]`
- **檔案**: `app/friends/[userId].tsx`
- **從哪裡進入**:
  - 從 Friends List 點擊好友
  - 從聊天室的對方資訊
- **功能**:
  - 顯示好友資訊與評分
  - 發送訊息按鈕 (導向聊天室)
  - 封鎖/解封鎖

### Chat (聊天系統) - Phase 6

#### 1. Chat Rooms List - `/chat`
- **檔案**: `app/chat/index.tsx`
- **從哪裡進入**:
  - 從 **Home 首頁**的聊天入口進入
  - 從 Friend Profile 的「發送訊息」按鈕
  - 從推播通知 (chat_message 類型)
- **功能**:
  - 顯示所有聊天室
  - 最後訊息預覽
  - 未讀徽章

#### 2. Chat Room - `/chat/[roomId]`
- **檔案**: `app/chat/[roomId].tsx`
- **從哪裡進入**:
  - 從 Chat Rooms List 點擊聊天室
  - 從 Friend Profile 的「發送訊息」
  - 從推播通知導航
- **功能**:
  - 訊息列表 (自動輪詢)
  - 發送訊息
  - 訊息狀態顯示

### Auth (認證流程)

#### Login - `/auth/login`
- **檔案**: `app/auth/login.tsx`
- **從哪裡進入**:
  - 未登入時自動導向
  - 登出後導向
  - Token 過期後導向
- **功能**:
  - Google OAuth 登入 (PKCE)

---

## 🗺️ 導航流程圖

### 主要使用者流程

```
登入
 ↓
首頁 (Home Tab)
 ├─→ 好友入口 → /friends (好友列表)
 │    ├─→ 點擊好友 → /friends/[userId] (好友個人檔案)
 │    │    └─→ 發送訊息 → /chat/[roomId] (聊天室)
 │    └─→ + 新增 → /friends/add (新增好友)
 │
 ├─→ 聊天入口 → /chat (聊天室列表)
 │    └─→ 點擊聊天室 → /chat/[roomId] (聊天室)
 │
 ├─→ My Cards Tab → /cards (我的卡冊)
 │    └─→ 上傳卡片 → /cards/upload
 │
 ├─→ Nearby Tab → /nearby (附近搜尋)
 │
 └─→ Profile Tab → /profile (個人檔案)
```

### 推播通知導航

```
推播通知
 ├─→ chat_message → /chat/[roomId] (直接進入聊天室)
 ├─→ friend_request → /friends (好友列表)
 ├─→ trade_proposal → /trade/[tradeId] (交易詳情，Phase 7)
 └─→ rating → /profile (個人檔案)
```

---

## 📂 檔案路由對應表

| 路由路徑 | 檔案位置 | 類型 | 導航方式 |
|---------|---------|------|---------|
| `/` | `app/(tabs)/index.tsx` | Tab | 底部 Tab 導航 |
| `/cards` | `app/(tabs)/cards/index.tsx` | Tab | 底部 Tab 導航 |
| `/cards/upload` | `app/(tabs)/cards/upload.tsx` | Stack | 從 /cards 進入 |
| `/nearby` | `app/(tabs)/nearby.tsx` | Tab | 底部 Tab 導航 |
| `/profile` | `app/(tabs)/profile.tsx` | Tab | 底部 Tab 導航 |
| `/friends` | `app/friends/index.tsx` | Stack | 從 Home 進入 |
| `/friends/add` | `app/friends/add.tsx` | Stack | 從 /friends 進入 |
| `/friends/[userId]` | `app/friends/[userId].tsx` | Stack | 從 /friends 進入 |
| `/chat` | `app/chat/index.tsx` | Stack | 從 Home 進入 |
| `/chat/[roomId]` | `app/chat/[roomId].tsx` | Stack | 從 /chat 或推播進入 |
| `/auth/login` | `app/auth/login.tsx` | Stack | 未登入自動導向 |

---

## 🎨 UI 建議：首頁設計

首頁 (`app/(tabs)/index.tsx`) 應該包含以下入口：

### 建議布局

```
┌─────────────────────────────┐
│  👋 Hello, [使用者名稱]      │
├─────────────────────────────┤
│  🔔 通知 (3)                 │
├─────────────────────────────┤
│  ┌──────────┐  ┌──────────┐ │
│  │ 👥 好友  │  │ 💬 聊天  │ │
│  │  (5)     │  │  (2 未讀)│ │
│  └──────────┘  └──────────┘ │
├─────────────────────────────┤
│  📊 最新活動                 │
│  • XXX 想要交換你的卡片      │
│  • YYY 給了你 5 星評分       │
├─────────────────────────────┤
│  ⭐ 推薦卡片                 │
│  [卡片輪播區]                │
└─────────────────────────────┘

底部 Tab 導航:
[🏠 Home] [📚 Cards] [📍 Nearby] [👤 Profile]
```

### 實作範例

```typescript
// app/(tabs)/index.tsx
export default function HomeScreen() {
  const router = useRouter();
  
  return (
    <ScrollView>
      {/* 快速導航 */}
      <HStack className="p-4 space-x-4">
        <Pressable 
          onPress={() => router.push('/friends')}
          className="flex-1 bg-blue-100 p-4 rounded-lg"
        >
          <Text className="text-2xl mb-2">👥</Text>
          <Text className="font-semibold">好友</Text>
          <Text className="text-sm text-gray-600">5 位好友</Text>
        </Pressable>
        
        <Pressable 
          onPress={() => router.push('/chat')}
          className="flex-1 bg-green-100 p-4 rounded-lg"
        >
          <Text className="text-2xl mb-2">💬</Text>
          <Text className="font-semibold">聊天</Text>
          <Badge>2 未讀</Badge>
        </Pressable>
      </HStack>
      
      {/* 其他內容... */}
    </ScrollView>
  );
}
```

---

## 🔄 路由保護與導航邏輯

### 認證保護

在 `app/_layout.tsx` 中實作:

```typescript
export default function RootLayout() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === 'auth';

    if (!isAuthenticated && !inAuthGroup) {
      // 未登入 → 導向登入頁
      router.replace('/auth/login');
    } else if (isAuthenticated && inAuthGroup) {
      // 已登入 → 導向主應用
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, isLoading, segments]);

  return (
    <GluestackUIProvider>
      <QueryClientProvider client={queryClient}>
        <Slot />
      </QueryClientProvider>
    </GluestackUIProvider>
  );
}
```

### 深度連結 (Deep Linking)

推播通知可以直接導向特定頁面:

```typescript
// src/features/notifications/hooks/useNotifications.ts
const responseListener = Notifications.addNotificationResponseReceivedListener(
  (response) => {
    const data = parseNotificationData(response.notification);
    
    switch (data.type) {
      case 'chat_message':
        router.push(`/chat/${data.room_id}`);
        break;
      case 'friend_request':
        router.push('/friends');
        break;
      // ... 其他類型
    }
  }
);
```

---

## 🚀 未來擴展 (Phase 7+)

### Trade (交易系統) - Phase 7

```
/trade              → 交易列表
/trade/[tradeId]    → 交易詳情
/trade/create       → 發起交易
```

**從哪裡進入**:
- 從 Home 的交易入口
- 從好友個人檔案的「發起交換」
- 從推播通知 (trade_proposal)

### Subscription (訂閱) - Phase 8

```
/subscription       → 訂閱方案
/subscription/status → 訂閱狀態
```

**從哪裡進入**:
- 從 Profile 的「升級會員」
- 從功能限制提示 (quota exceeded)

---

## 📝 開發指南

### 新增路由步驟

1. **決定路由類型**:
   - Tab 路由 → 放在 `app/(tabs)/` 目錄
   - Stack 路由 → 放在 `app/` 根目錄

2. **創建路由檔案**:
   ```bash
   # Tab 路由
   touch app/(tabs)/feature-name.tsx
   
   # Stack 路由
   mkdir app/feature-name
   touch app/feature-name/index.tsx
   ```

3. **實作 Screen 元件**:
   ```typescript
   // app/feature-name/index.tsx
   import FeatureScreen from '@/src/features/feature-name/screens/FeatureScreen';
   
   export default FeatureScreen;
   ```

4. **更新 Tab Layout** (如果是 Tab 路由):
   ```typescript
   // app/(tabs)/_layout.tsx
   <Tabs.Screen
     name="feature-name"
     options={{
       title: 'Feature Name',
       tabBarIcon: ({ color, size }) => (
         <Ionicons name="icon-name" size={size} color={color} />
       ),
     }}
   />
   ```

5. **測試導航**:
   ```typescript
   import { useRouter } from 'expo-router';
   
   const router = useRouter();
   router.push('/feature-name');
   ```

---

## 🔗 相關文件

- [Expo Router 官方文檔](https://docs.expo.dev/router/introduction/)
- [TECH_STACK.md](./TECH_STACK.md) - 技術棧說明
- [PHASE6_IMPLEMENTATION_GUIDE.md](./PHASE6_IMPLEMENTATION_GUIDE.md) - Phase 6 實作指南

---

**維護者**: Development Team  
**問題回報**: 請在 GitHub Issues 中回報路由相關問題
