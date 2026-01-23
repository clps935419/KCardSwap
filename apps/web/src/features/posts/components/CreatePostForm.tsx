'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'
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
import type { PostCategory, PostScope, CityCode, PostResponseWrapper } from '@/shared/api/generated'

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
}

export function CreatePostForm() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [scope, setScope] = useState<PostScope>('global')
  const [errorMessage, setErrorMessage] = useState<string>('')

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
    mutationFn: async (data: FormData) => {
      const response = await apiClient.post<PostResponseWrapper>('/api/v1/posts', {
        title: data.title,
        content: data.content,
        scope: data.scope,
        city_code: data.scope === 'city' ? data.city_code || null : null,
        category: data.category,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts', 'list'] })
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

  const onSubmit = (data: FormData) => {
    setErrorMessage('')
    
    if (data.scope === 'city' && !data.city_code) {
      setErrorMessage('當範圍為「指定城市」時，必須選擇城市')
      return
    }

    createPostMutation.mutate(data)
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
