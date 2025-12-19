/**
 * Upload Card Screen
 * M201-M203A: 完整的卡片上傳流程
 * 
 * 功能：
 * - 選擇圖片來源（相機/相簿）
 * - 填寫卡片資訊
 * - 顯示上傳進度
 * - 錯誤處理（配額、檔案大小、網路等）
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useUploadCard } from '../hooks/useUploadCard';
import type { CardRarity, LimitExceededError } from '../types';

const RARITY_OPTIONS: { label: string; value: CardRarity }[] = [
  { label: '普通', value: 'common' },
  { label: '稀有', value: 'rare' },
  { label: '史詩', value: 'epic' },
  { label: '傳說', value: 'legendary' },
];

export function UploadCardScreen() {
  const router = useRouter();
  const { uploadFromCamera, uploadFromGallery, uploadProgress, isUploading, error } =
    useUploadCard();

  const [idol, setIdol] = useState('');
  const [idolGroup, setIdolGroup] = useState('');
  const [album, setAlbum] = useState('');
  const [version, setVersion] = useState('');
  const [rarity, setRarity] = useState<CardRarity>('common');
  const [lastUploadSource, setLastUploadSource] = useState<'camera' | 'gallery' | null>(null);

  const handleUpload = async (source: 'camera' | 'gallery') => {
    setLastUploadSource(source);
    
    try {
      const uploadFn = source === 'camera' ? uploadFromCamera : uploadFromGallery;

      const result = await uploadFn({
        idol: idol || undefined,
        idol_group: idolGroup || undefined,
        album: album || undefined,
        version: version || undefined,
        rarity,
      });

      if (result) {
        Alert.alert('上傳成功', '卡片已成功上傳！', [
          {
            text: '確定',
            onPress: () => router.back(),
          },
        ]);
      }
    } catch (err: any) {
      // 處理不同類型的錯誤
      handleUploadError(err);
    }
  };

  const handleUploadError = (err: any) => {
    const error = err as LimitExceededError;

    // 配額超過錯誤
    if (error.code === 'LIMIT_EXCEEDED') {
      const limitType = error.limit_type;
      let message = '上傳失敗';

      if (limitType === 'daily') {
        message = `今日上傳次數已達上限（${error.limit}張/日）。明天再來吧！`;
      } else if (limitType === 'storage') {
        message = `儲存空間已滿（${((error.limit || 0) / 1024 / 1024 / 1024).toFixed(2)}GB）。請刪除部分卡片後再試。`;
      } else if (limitType === 'size') {
        message = `檔案大小超過限制（最大 10MB）。`;
      }

      Alert.alert('配額限制', message);
      return;
    }

    // 權限錯誤
    if (error.message?.includes('權限')) {
      Alert.alert('權限不足', error.message);
      return;
    }

    // Signed URL 相關錯誤
    if (error.message?.includes('過期') || error.statusCode === 403) {
      Alert.alert('上傳失敗', '上傳連結已過期，請重試', [
        { 
          text: '重試', 
          onPress: () => lastUploadSource && handleUpload(lastUploadSource)
        },
      ]);
      return;
    }

    // 網路錯誤
    if (error.message?.includes('網路')) {
      Alert.alert('網路錯誤', '請檢查網路連線後重試', [
        { 
          text: '重試', 
          onPress: () => lastUploadSource && handleUpload(lastUploadSource)
        },
      ]);
      return;
    }

    // 一般錯誤
    Alert.alert('上傳失敗', error.message || '請稍後再試');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>上傳小卡</Text>

      {/* 卡片資訊表單 */}
      <View style={styles.form}>
        <View style={styles.formGroup}>
          <Text style={styles.label}>偶像名稱</Text>
          <TextInput
            style={styles.input}
            value={idol}
            onChangeText={setIdol}
            placeholder="例：IU"
            editable={!isUploading}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>團體/公司（選填）</Text>
          <TextInput
            style={styles.input}
            value={idolGroup}
            onChangeText={setIdolGroup}
            placeholder="例：EDAM Entertainment"
            editable={!isUploading}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>專輯名稱（選填）</Text>
          <TextInput
            style={styles.input}
            value={album}
            onChangeText={setAlbum}
            placeholder="例：Love Poem"
            editable={!isUploading}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>版本（選填）</Text>
          <TextInput
            style={styles.input}
            value={version}
            onChangeText={setVersion}
            placeholder="例：限定版"
            editable={!isUploading}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>稀有度</Text>
          <View style={styles.rarityContainer}>
            {RARITY_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[styles.rarityButton, rarity === option.value && styles.rarityButtonActive]}
                onPress={() => setRarity(option.value)}
                disabled={isUploading}
              >
                <Text
                  style={[styles.rarityText, rarity === option.value && styles.rarityTextActive]}
                >
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* 上傳進度 */}
      {isUploading && (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.progressMessage}>{uploadProgress.message}</Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${uploadProgress.progress}%` }]} />
          </View>
          <Text style={styles.progressPercent}>{uploadProgress.progress.toFixed(0)}%</Text>
        </View>
      )}

      {/* 錯誤訊息 */}
      {error && !isUploading && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>❌ {(error as Error).message}</Text>
        </View>
      )}

      {/* 上傳按鈕 */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.cameraButton, isUploading && styles.buttonDisabled]}
          onPress={() => handleUpload('camera')}
          disabled={isUploading}
        >
          <Text style={styles.buttonIcon}>📷</Text>
          <Text style={styles.buttonText}>拍照上傳</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.galleryButton, isUploading && styles.buttonDisabled]}
          onPress={() => handleUpload('gallery')}
          disabled={isUploading}
        >
          <Text style={styles.buttonIcon}>🖼️</Text>
          <Text style={styles.buttonText}>相簿選取</Text>
        </TouchableOpacity>
      </View>

      {/* 使用說明 */}
      <View style={styles.infoContainer}>
        <Text style={styles.infoTitle}>📌 上傳說明</Text>
        <Text style={styles.infoText}>• 支援 JPEG 和 PNG 格式</Text>
        <Text style={styles.infoText}>• 單檔最大 10MB</Text>
        <Text style={styles.infoText}>• 免費用戶：每日 2 張，總容量 1GB</Text>
        <Text style={styles.infoText}>• 建議比例：3:4（標準卡片比例）</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 24,
  },
  form: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#333',
    backgroundColor: '#fff',
  },
  rarityContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  rarityButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  rarityButtonActive: {
    backgroundColor: '#007AFF',
  },
  rarityText: {
    fontSize: 14,
    color: '#666',
  },
  rarityTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  progressContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  progressMessage: {
    fontSize: 16,
    color: '#333',
    marginTop: 16,
    marginBottom: 12,
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
  },
  progressPercent: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  errorContainer: {
    backgroundColor: '#FFEBEE',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 14,
    color: '#C62828',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    flexDirection: 'column',
  },
  cameraButton: {
    backgroundColor: '#4CAF50',
  },
  galleryButton: {
    backgroundColor: '#2196F3',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  infoContainer: {
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    padding: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#E65100',
    marginBottom: 4,
  },
});
