# KCardSwap Color Theme - Korean Minimalist Girl Aesthetic

## 設計理念 (Design Philosophy)

本主題色彩靈感來自韓系女孩風格，專為 KCardSwap 卡片交換應用設計。
符合關鍵字：**韓系、女孩、卡片、簡約**

This color theme is inspired by Korean minimalist girl aesthetic, designed specifically for the KCardSwap card trading app.
Keywords: **Korean style, Girl, Card, Minimalist**

---

## 主色調 (Primary Colors)

### 1. Primary - Soft Lavender (柔和薰衣草紫)

**色彩靈感：** 韓系夢幻薰衣草色，象徵溫柔與浪漫
**使用場景：** 主要品牌色、按鈕、連結、重要元素

- **主色**: `#A98ED8` (rgb(169, 142, 216))
- **範圍**: 從極淺薰衣草 (#FCF8FF) 到深紫 (#33264)
- **特點**: 柔和不刺眼，適合長時間使用

```css
/* Example usage */
.primary-button {
  background: rgb(169, 142, 216);  /* primary-500 */
}
```

### 2. Secondary - Blush Pink (櫻花粉)

**色彩靈感：** 韓國櫻花季的粉嫩色調 (#FFB7C5, #FEC5E5)
**使用場景：** 副色、強調元素、卡片裝飾

- **主色**: `#FEC5E5` (rgb(254, 197, 229))
- **範圍**: 從淡粉 (#FFFBFC) 到深粉紅 (#723949)
- **特點**: 甜美可愛，增添女性化氣息

```css
/* Example usage */
.accent-card {
  border-color: rgb(254, 197, 229);  /* secondary-500 */
}
```

### 3. Tertiary - Dreamy Mint (夢幻薄荷綠)

**色彩靈感：** 清新薄荷綠 (#B8E4DC, #E4F1CB)
**使用場景：** 輔助色、背景、清新元素

- **主色**: `#8CCFC1` (rgb(140, 207, 193))
- **範圍**: 從極淺薄荷 (#F7FEFC) 到深綠 (#25423D)
- **特點**: 清新舒適，平衡粉紫色調

```css
/* Example usage */
.fresh-section {
  background: rgb(184, 228, 220);  /* tertiary-300 */
}
```

---

## 功能色彩 (Functional Colors)

### Error - Soft Coral (柔和珊瑚紅)
- **主色**: `#F26A5B` (rgb(242, 106, 91))
- **特點**: 溫和的錯誤提示，不會過於刺眼

### Success - Soft Sage Green (柔和鼠尾草綠)
- **主色**: `#5CB879` (rgb(92, 184, 121))
- **特點**: 清新的成功提示，自然舒適

### Warning - Soft Peach (柔和蜜桃色)
- **主色**: `#FF9E58` (rgb(255, 158, 88))
- **特點**: 溫暖的警告色，友善提醒

### Info - Soft Sky Blue (柔和天空藍)
- **主色**: `#52BAF0` (rgb(82, 186, 240))
- **特點**: 清澈的資訊提示色

---

## 中性色彩 (Neutral Colors)

### Typography (文字色)
- 採用溫暖的灰褐色調，避免純黑過於冷硬
- **主要文字**: `#857F7E` (rgb(133, 130, 127)) - typography-500
- **深色文字**: `#262320` (rgb(38, 35, 32)) - typography-900

### Background (背景色)
- 以奶油白和米色為基調，營造溫暖舒適感
- **主背景**: `#FFFFFF` (rgb(255, 255, 255)) - Pure white
- **卡片背景**: `#FCFBF9` (rgb(252, 251, 249)) - Creamy white (#FCFEDB inspired)
- **柔和背景**: `#FAF8F6` (rgb(250, 248, 246)) - Warm muted

### Outline (邊框色)
- 柔和的邊框，不會過於突兀
- **主要邊框**: `#A5A29F` (rgb(165, 162, 159)) - outline-500

---

## 色彩組合建議 (Color Combinations)

### 1. 主要界面 (Main UI)
```
背景: background-0 (#FFFFFF)
卡片: background-50 (#FCFBF9)
主按鈕: primary-500 (#A98ED8)
次按鈕: secondary-500 (#FEC5E5)
```

### 2. 卡片詳情 (Card Details)
```
卡片背景: background-50 (#FCFBF9)
標題文字: typography-900 (#262320)
內容文字: typography-600 (#66635F)
強調元素: primary-400 (#B9A4E4) or secondary-300 (#FFC5D5)
```

### 3. 按鈕變化 (Button Variants)
```
Solid Primary: primary-500 背景 + white 文字
Outline Primary: transparent 背景 + primary-500 邊框和文字
Solid Secondary: secondary-500 背景 + typography-900 文字
Subtle: background-100 背景 + typography-800 文字
```

---

## 設計原則 (Design Principles)

### 1. 柔和優先 (Softness First)
- 避免使用純黑 (#000000) 和高對比度
- 所有色彩都經過柔化處理，適合長時間觀看

### 2. 溫暖舒適 (Warm & Comfortable)
- 背景色偏向溫暖的奶油色系
- 中性色帶有微妙的米色調

### 3. 女性化美學 (Feminine Aesthetic)
- 粉紫色調營造溫柔浪漫氛圍
- 薄荷綠增添清新感
- 整體色調柔和甜美

### 4. 韓系簡約 (Korean Minimalism)
- 色彩搭配簡潔不複雜
- 大量留白和淺色背景
- 重點使用主色，避免過度裝飾

---

## 無障礙考量 (Accessibility)

### 對比度標準
- **主要文字**: typography-900 在 background-0 上達到 WCAG AA 標準 (4.5:1)
- **大文字/標題**: typography-700 在 background-0 上達到 WCAG AA 標準 (3:1)
- **按鈕文字**: White 在 primary-500 上達到 WCAG AA 標準

### 色盲友善
- 不單獨依賴顏色傳達資訊
- 配合圖示和文字說明
- 功能色（success/error/warning）有足夠區分度

---

## 實際應用範例 (Usage Examples)

### 首頁卡片
```tsx
<Card className="bg-[rgb(252,251,249)] border-[rgb(240,237,234)]">
  <Heading className="text-[rgb(38,35,32)]">我的卡冊</Heading>
  <Text className="text-[rgb(133,130,127)]">共 24 張卡片</Text>
  <Button className="bg-[rgb(169,142,216)]">
    <ButtonText className="text-white">查看全部</ButtonText>
  </Button>
</Card>
```

### 登入按鈕
```tsx
<Button 
  variant="solid" 
  className="bg-[rgb(169,142,216)] shadow-md"
>
  <ButtonText>使用 Google 登入</ButtonText>
</Button>
```

### 個人資料卡片
```tsx
<Box className="bg-[rgb(255,247,249)] p-4 rounded-lg">
  <Heading size="lg" className="text-[rgb(254,197,229)] mb-2">
    個人檔案
  </Heading>
  <Text className="text-[rgb(133,130,127)]">
    編輯你的個人資訊
  </Text>
</Box>
```

---

## 色彩趨勢參考 (Color Trend References)

本主題色彩參考以下 2024-2025 年韓系流行趨勢：

1. **Soft Pastel Movement** - 柔和粉彩風潮
2. **Clean Girl Aesthetic** - 清爽女孩美學
3. **Monochrome Minimalism** - 單色系簡約風
4. **Korean Street Fashion** - 韓國街頭時尚

**色彩關鍵字：**
- Lavender (#B984DF, #C095E4)
- Blush Pink (#FEC5E5, #FFB7C5)
- Mint (#B8E4DC, #E4F1CB)
- Cream Beige (#FCFEDB)

---

## 維護與更新 (Maintenance)

### 色彩定義檔案
- **主要配置**: `src/shared/ui/components/gluestack-ui-provider/config.ts`
- **代幣文件**: `src/shared/ui/theme/tokens.ts`

### 更新原則
1. 保持色彩和諧度
2. 維護無障礙標準
3. 確保跨平台一致性
4. 定期檢視流行趨勢

---

**Last Updated**: 2024-12-19  
**Version**: 1.0.0  
**Theme**: Korean Minimalist Girl Aesthetic
