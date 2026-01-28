'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Spinner } from '@/components/ui/spinner'
import { Textarea } from '@/components/ui/textarea'
import { attachMediaToPost, executeUploadFlow } from '@/lib/media/uploadFlow'
import type { CityCode, PostCategory, PostScope } from '@/shared/api/generated'
import { PostsService } from '@/shared/api/generated/services.gen'

const CATEGORIES: { value: PostCategory; label: string }[] = [
  { value: 'trade', label: '交換' },
  { value: 'giveaway', label: '贈送' },
  { value: 'group', label: '揪團' },
  { value: 'showcase', label: '展示' },
  { value: 'help', label: '求助' },
  { value: 'announcement', label: '公告' },
]

const _CITIES: { value: CityCode; label: string }[] = [
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
    mutationFn: (data: any) => PostsService.createPostApiV1PostsPost(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] })
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
    setValue('image', undefined)
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
        requestBody: {
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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Category and Scope in 2-column grid */}
      <div className="grid grid-cols-2 gap-3">
        {/* 分類 */}
        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4">
          <p className="text-[10px] font-bold text-muted-foreground uppercase mb-2">分類</p>
          <Select
            defaultValue="showcase"
            onValueChange={(value: string) => setValue('category', value as PostCategory)}
          >
            <SelectTrigger id="category" className="bg-card border-border rounded-xl font-bold">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CATEGORIES.map(category => (
                <SelectItem key={category.value} value={category.value}>
                  {category.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 範圍 */}
        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4">
          <p className="text-[10px] font-bold text-muted-foreground uppercase mb-2">範圍</p>
          <Select
            value={scope}
            onValueChange={(value: string) => {
              setScope(value as PostScope)
              setValue('scope', value as PostScope)
            }}
          >
            <SelectTrigger id="scope" className="bg-card border-border rounded-xl font-bold">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="global">全域（不限）</SelectItem>
              <SelectItem value="city">城市（指定城市）</SelectItem>
            </SelectContent>
          </Select>

          {/* 城市 - 僅在 scope=city 時顯示 */}
          {scope === 'city' && (
            <Input
              placeholder="城市代碼（例如 TPE）"
              className="mt-2 bg-card border-border rounded-xl font-bold"
              onChange={e => setValue('city_code', e.target.value as CityCode)}
            />
          )}
        </div>
      </div>

      {/* 標題與內容 */}
      <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
        <p className="text-[10px] font-bold text-muted-foreground uppercase">標題</p>
        <Input
          id="title"
          placeholder="想分享什麼？"
          className="bg-card border-border rounded-xl"
          {...register('title', {
            required: '請輸入標題',
            minLength: { value: 1, message: '標題至少需要 1 個字' },
            maxLength: { value: 100, message: '標題最多 100 個字' },
          })}
        />
        {errors.title && <p className="text-xs text-destructive mt-1">{errors.title.message}</p>}
      </div>

      <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
        <p className="text-[10px] font-bold text-muted-foreground uppercase">內容</p>
        <Textarea
          id="content"
          placeholder="分享更多細節..."
          rows={4}
          className="bg-card border-border rounded-xl"
          {...register('content', {
            required: '請輸入內容',
            minLength: { value: 1, message: '內容至少需要 1 個字' },
          })}
        />
        {errors.content && (
          <p className="text-xs text-destructive mt-1">{errors.content.message}</p>
        )}
      </div>

      {/* 圖片上傳 (T054) */}
      <div className="bg-muted/50 border border-border/30 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-[10px] font-bold text-muted-foreground uppercase">圖片</p>
            <p className="text-[11px] text-muted-foreground">每則貼文最多 1 張（免費方案）</p>
          </div>
        </div>

        <Input
          id="image"
          type="file"
          accept="image/*"
          {...register('image', {
            onChange: handleImageChange,
          })}
          className="bg-card border-border rounded-xl"
        />

        {imagePreview && (
          <div className="relative mt-3">
            <img
              src={imagePreview}
              alt="預覽"
              className="max-h-48 rounded-2xl border border-border object-contain w-full"
            />
            <Button
              type="button"
              variant="destructive"
              size="sm"
              className="absolute right-2 top-2 rounded-xl"
              onClick={removeImage}
            >
              移除
            </Button>
          </div>
        )}

        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="mt-3">
            <div className="h-2 w-full rounded-full bg-muted">
              <div
                className="h-2 rounded-full bg-primary-500 transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="mt-1 text-[11px] text-muted-foreground">上傳中... {uploadProgress}%</p>
          </div>
        )}

        <div className="mt-3 bg-card border border-border rounded-xl p-3">
          <p className="text-[11px] font-black text-foreground">上傳流程（示意）</p>
          <p className="text-[11px] text-muted-foreground">
            授權 → PUT 上傳 → 確認（confirm）→ 附加（attach）
          </p>
        </div>
      </div>

      {/* 錯誤訊息 */}
      {errorMessage && (
        <div className="rounded-2xl bg-destructive/10 border border-destructive/20 p-4">
          <p className="text-sm text-destructive font-bold">{errorMessage}</p>
        </div>
      )}

      {/* 按鈕 */}
      <div className="grid grid-cols-2 gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.back()}
          disabled={createPostMutation.isPending}
          className="h-12 rounded-2xl border-border bg-card font-black hover:bg-muted"
        >
          取消
        </Button>
        <Button
          type="submit"
          disabled={createPostMutation.isPending}
          className="h-12 rounded-2xl bg-slate-900 text-white font-black shadow-xl hover:bg-slate-800"
        >
          {createPostMutation.isPending ? (
            <>
              <Spinner className="mr-2 h-4 w-4" />
              發布中...
            </>
          ) : (
            '發布'
          )}
        </Button>
      </div>
    </form>
  )
}
