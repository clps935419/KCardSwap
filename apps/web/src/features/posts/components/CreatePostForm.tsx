'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createPostApiV1PostsPostMutation, listPostsApiV1PostsGetQueryKey } from '@/shared/api/generated/@tanstack/react-query.gen'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Spinner } from '@/components/ui/spinner'
import { executeUploadFlow, attachMediaToPost } from '@/lib/media/uploadFlow'
import type { PostCategory, PostScope, CityCode } from '@/shared/api/generated'

const CATEGORIES: { value: PostCategory; label: string }[] = [
  { value: 'trade', label: '交換' },
  { value: 'giveaway', label: '贈送' },
  { value: 'group', label: '揪團' },
  { value: 'showcase', label: '展示' },
  { value: 'help', label: '求助' },
  { value: 'announcement', label: '公告' },
]

const CITIES: { value: CityCode; label: string }[] = [
  { value: 'TPE', label: '台北市' },
  { value: 'NTP', label: '新北市' },
  { value: 'TXG', label: '台中市' },
  { value: 'TNN', label: '台南市' },
  { value: 'KHH', label: '高雄市' },
]

interface FormData {
  title: string
  content: string
  scope: PostScope
  city_code?: CityCode
  category: PostCategory
  image?: FileList
}

export function CreatePostForm() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [scope, setScope] = useState<PostScope>('global')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      scope: 'global',
      category: 'showcase',
    },
  })

  const createPostMutation = useMutation({
    ...createPostApiV1PostsPostMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: listPostsApiV1PostsGetQueryKey() })
      router.push('/posts')
    },
    onError: (error: any) => {
      if (error?.response?.status === 422) {
        const errorData = error.response.data
        if (errorData?.detail?.error_code === 'LIMIT_EXCEEDED') {
          const limitInfo = errorData.detail
          setErrorMessage(
            `已達配額上限：${limitInfo.limit_key}（上限：${limitInfo.limit_value}，目前：${limitInfo.current_value}）。重置時間：${new Date(limitInfo.reset_at).toLocaleString('zh-TW')}`
          )
        } else {
          setErrorMessage('資料驗證失敗，請檢查欄位是否正確')
        }
      } else {
        setErrorMessage('發文失敗，請稍後再試')
      }
    },
  })

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrorMessage('請選擇圖片檔案')
        return
      }
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const onSubmit = async (data: FormData) => {
    setErrorMessage('')
    setUploadProgress(0)
    
    if (data.scope === 'city' && !data.city_code) {
      setErrorMessage('當範圍為「指定城市」時，必須選擇城市')
      return
    }

    try {
      let mediaId: string | undefined

      // Step 1: Upload image if selected (T054)
      if (data.image && data.image.length > 0) {
        const file = data.image[0]
        mediaId = await executeUploadFlow({
          file,
          onProgress: setUploadProgress,
        })
      }

      // Step 2: Create post
      const postResponse = await createPostMutation.mutateAsync({
        body: {
          title: data.title,
          content: data.content,
          scope: data.scope,
          city_code: data.scope === 'city' ? data.city_code || null : null,
          category: data.category,
        },
      })

      // Step 3: Attach media to post if uploaded
      if (mediaId && postResponse?.data?.id) {
        await attachMediaToPost(mediaId, postResponse.data.id)
      }

      // Success - mutations will handle navigation
    } catch (error: any) {
      if (error?.response?.status === 422) {
        const errorData = error.response.data
        if (errorData?.detail?.error_code === 'LIMIT_EXCEEDED') {
          const limitInfo = errorData.detail
          setErrorMessage(
            `已達配額上限：${limitInfo.limit_key}（上限：${limitInfo.limit_value}，目前：${limitInfo.current_value}）。重置時間：${new Date(limitInfo.reset_at).toLocaleString('zh-TW')}`
          )
        } else {
          setErrorMessage('資料驗證失敗，請檢查欄位是否正確')
        }
      } else {
        setErrorMessage(error.message || '發文失敗，請稍後再試')
      }
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 標題 */}
      <div className="space-y-2">
        <Label htmlFor="title">
          標題 <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          placeholder="輸入貼文標題"
          {...register('title', {
            required: '請輸入標題',
            minLength: { value: 1, message: '標題至少需要 1 個字' },
            maxLength: { value: 100, message: '標題最多 100 個字' },
          })}
        />
        {errors.title && <p className="text-sm text-destructive">{errors.title.message}</p>}
      </div>

      {/* 內容 */}
      <div className="space-y-2">
        <Label htmlFor="content">
          內容 <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="content"
          placeholder="分享您的想法..."
          rows={6}
          {...register('content', {
            required: '請輸入內容',
            minLength: { value: 1, message: '內容至少需要 1 個字' },
          })}
        />
        {errors.content && <p className="text-sm text-destructive">{errors.content.message}</p>}
      </div>

      {/* 範圍 */}
      <div className="space-y-2">
        <Label htmlFor="scope">
          發布範圍 <span className="text-destructive">*</span>
        </Label>
        <Select
          value={scope}
          onValueChange={(value: string) => {
            setScope(value as PostScope)
            setValue('scope', value as PostScope)
          }}
        >
          <SelectTrigger id="scope">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="global">不限（全域）</SelectItem>
            <SelectItem value="city">指定城市</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 城市 - 僅在 scope=city 時顯示 */}
      {scope === 'city' && (
        <div className="space-y-2">
          <Label htmlFor="city_code">
            城市 <span className="text-destructive">*</span>
          </Label>
          <Select onValueChange={(value: string) => setValue('city_code', value as CityCode)}>
            <SelectTrigger id="city_code">
              <SelectValue placeholder="選擇城市" />
            </SelectTrigger>
            <SelectContent>
              {CITIES.map((city) => (
                <SelectItem key={city.value} value={city.value}>
                  {city.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* 分類 */}
      <div className="space-y-2">
        <Label htmlFor="category">
          分類 <span className="text-destructive">*</span>
        </Label>
        <Select
          defaultValue="showcase"
          onValueChange={(value: string) => setValue('category', value as PostCategory)}
        >
          <SelectTrigger id="category">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 圖片上傳 (T054) */}
      <div className="space-y-2">
        <Label htmlFor="image">圖片 (選填)</Label>
        <Input
          id="image"
          type="file"
          accept="image/*"
          ref={fileInputRef}
          {...register('image')}
          onChange={handleImageChange}
        />
        {imagePreview && (
          <div className="relative mt-2">
            <img
              src={imagePreview}
              alt="預覽"
              className="max-h-48 rounded-md border object-contain"
            />
            <Button
              type="button"
              variant="destructive"
              size="sm"
              className="absolute right-2 top-2"
              onClick={removeImage}
            >
              移除
            </Button>
          </div>
        )}
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="mt-2">
            <div className="h-2 w-full rounded-full bg-secondary">
              <div
                className="h-2 rounded-full bg-primary transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-muted-foreground">上傳中... {uploadProgress}%</p>
          </div>
        )}
      </div>

      {/* 錯誤訊息 */}
      {errorMessage && (
        <div className="rounded-md bg-destructive/10 p-4">
          <p className="text-sm text-destructive">{errorMessage}</p>
        </div>
      )}

      {/* 按鈕 */}
      <div className="flex gap-4">
        <Button type="submit" disabled={createPostMutation.isPending}>
          {createPostMutation.isPending ? (
            <>
              <Spinner className="mr-2 h-4 w-4" />
              發布中...
            </>
          ) : (
            '發布貼文'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => router.back()}
          disabled={createPostMutation.isPending}
        >
          取消
        </Button>
      </div>
    </form>
  )
}
