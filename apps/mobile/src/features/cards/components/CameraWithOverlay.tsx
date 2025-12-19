/**
 * Camera With Overlay Component
 * POC: M201 Enhancement - 自訂相機畫面 + 框線 + 提示文字
 * 
 * 功能:
 * - 使用 expo-camera 的 CameraView 全螢幕預覽
 * - 疊加卡片框線與四角標記
 * - 固定提示文案：「請將小卡對齊框線內」
 * - 拍照後依框線區域裁切
 */

import { useState, useRef } from 'react';
import { Alert, StyleSheet, Dimensions } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImageManipulator from 'expo-image-manipulator';
import { Box, Text, Button, ButtonText, Spinner } from '@/src/shared/ui/components';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// 框線區域配置（相對比例 0..1）
const FRAME_CONFIG = {
  x: 0.15,      // 左邊距 15%
  y: 0.25,      // 上邊距 25%
  width: 0.7,   // 寬度 70%
  height: 0.525 // 高度 52.5% (維持 3:4 比例: 0.7 * (4/3) * 0.75 ≈ 0.7)
};

// 計算框線在螢幕上的像素位置
const framePixels = {
  x: SCREEN_WIDTH * FRAME_CONFIG.x,
  y: SCREEN_HEIGHT * FRAME_CONFIG.y,
  width: SCREEN_WIDTH * FRAME_CONFIG.width,
  height: SCREEN_WIDTH * FRAME_CONFIG.width * (4 / 3), // 保持 3:4 比例
};

interface CameraWithOverlayProps {
  onCapture: (uri: string) => void;
  onCancel: () => void;
}

export function CameraWithOverlay({ onCapture, onCancel }: CameraWithOverlayProps) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isCapturing, setIsCapturing] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  // 權限檢查
  if (!permission) {
    return (
      <Box className="flex-1 items-center justify-center bg-black">
        <Spinner size="large" />
      </Box>
    );
  }

  if (!permission.granted) {
    return (
      <Box className="flex-1 items-center justify-center bg-black p-4">
        <Text className="text-white text-center mb-4">需要相機權限才能拍照</Text>
        <Button onPress={requestPermission}>
          <ButtonText>開啟相機權限</ButtonText>
        </Button>
        <Button onPress={onCancel} className="mt-2" variant="outline">
          <ButtonText>取消</ButtonText>
        </Button>
      </Box>
    );
  }

  const handleCapture = async () => {
    if (!cameraRef.current || isCapturing) return;

    try {
      setIsCapturing(true);

      // 拍照
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        skipProcessing: false,
      });

      if (!photo) {
        throw new Error('拍照失敗');
      }

      // 座標映射：將相對比例轉換為照片像素座標
      const cropX = Math.floor(FRAME_CONFIG.x * photo.width);
      const cropY = Math.floor(FRAME_CONFIG.y * photo.height);
      const cropWidth = Math.floor(FRAME_CONFIG.width * photo.width);
      const cropHeight = Math.floor(FRAME_CONFIG.height * photo.height);

      // 依框線區域裁切
      const cropped = await ImageManipulator.manipulateAsync(
        photo.uri,
        [
          {
            crop: {
              originX: cropX,
              originY: cropY,
              width: cropWidth,
              height: cropHeight,
            },
          },
        ],
        { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
      );

      onCapture(cropped.uri);
    } catch (error) {
      console.error('Camera capture error:', error);
      Alert.alert('拍照失敗', error instanceof Error ? error.message : '未知錯誤');
    } finally {
      setIsCapturing(false);
    }
  };

  return (
    <Box className="flex-1 bg-black">
      {/* Camera Preview */}
      <CameraView
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        facing="back"
        ratio="4:3"
      />

      {/* Overlay Container */}
      <Box style={StyleSheet.absoluteFill} className="pointer-events-none">
        {/* Dim overlay (outside frame) */}
        <Box style={StyleSheet.absoluteFill} className="bg-black/30" />

        {/* Clear frame area */}
        <Box
          style={{
            position: 'absolute',
            left: framePixels.x,
            top: framePixels.y,
            width: framePixels.width,
            height: framePixels.height,
            backgroundColor: 'transparent',
          }}
        >
          {/* Frame border */}
          <Box
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              borderWidth: 2,
              borderColor: '#FFFFFF',
              borderRadius: 8,
            }}
          />

          {/* Corner markers */}
          <FrameCorner position="top-left" />
          <FrameCorner position="top-right" />
          <FrameCorner position="bottom-left" />
          <FrameCorner position="bottom-right" />

          {/* Prompt text */}
          <Box className="absolute -top-12 left-0 right-0 items-center">
            <Text className="text-white text-base font-semibold text-center bg-black/50 px-4 py-2 rounded-lg">
              請將小卡對齊框線內
            </Text>
          </Box>
        </Box>
      </Box>

      {/* Action buttons */}
      <Box className="absolute bottom-8 left-0 right-0 flex-row justify-center items-center gap-4 pointer-events-auto">
        <Button
          onPress={onCancel}
          variant="outline"
          className="bg-black/50 border-white"
          disabled={isCapturing}
        >
          <ButtonText className="text-white">取消</ButtonText>
        </Button>

        <Button
          onPress={handleCapture}
          className="bg-white w-16 h-16 rounded-full items-center justify-center"
          disabled={isCapturing}
        >
          {isCapturing ? (
            <Spinner size="small" />
          ) : (
            <Box className="w-14 h-14 bg-white rounded-full border-4 border-gray-800" />
          )}
        </Button>
      </Box>
    </Box>
  );
}

/**
 * Frame Corner Component
 * 框線四角標記
 */
interface FrameCornerProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

function FrameCorner({ position }: FrameCornerProps) {
  const cornerLength = 20;
  const borderWidth = 3;

  const cornerStyles = {
    'top-left': {
      top: -borderWidth,
      left: -borderWidth,
      borderTopWidth: borderWidth,
      borderLeftWidth: borderWidth,
    },
    'top-right': {
      top: -borderWidth,
      right: -borderWidth,
      borderTopWidth: borderWidth,
      borderRightWidth: borderWidth,
    },
    'bottom-left': {
      bottom: -borderWidth,
      left: -borderWidth,
      borderBottomWidth: borderWidth,
      borderLeftWidth: borderWidth,
    },
    'bottom-right': {
      bottom: -borderWidth,
      right: -borderWidth,
      borderBottomWidth: borderWidth,
      borderRightWidth: borderWidth,
    },
  };

  return (
    <Box
      style={{
        position: 'absolute',
        width: cornerLength,
        height: cornerLength,
        borderColor: '#FFFFFF',
        ...cornerStyles[position],
      }}
    />
  );
}
