'use client'

import { useQuery } from '@tanstack/react-query'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { FileInput } from '@/components/ui/file-input'
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
import { MAX_UPLOAD_BYTES_FREE_LIMIT, prepareUploadFile } from '@/lib/media/prepareUploadFile'
import { mapApiError } from '@/shared/api/errorMapper'
import type { CityCode, CityResponse, PostCategory, PostScope } from '@/shared/api/generated'
import {
  getCategoriesApiV1PostsCategoriesGetOptions,
  getCitiesApiV1LocationsCitiesGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'
import { useCreatePostFlowMutation } from '@/shared/api/hooks/flows'

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
  const [scope, setScope] = useState<PostScope>('global')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [imageName, setImageName] = useState<string | null>(null)
  const [preparedImageFile, setPreparedImageFile] = useState<File | null>(null)
  const createPostFlowMutation = useCreatePostFlowMutation()

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      scope: 'global',
      category: 'showcase',
    },
  })

  const selectedCityCode = watch('city_code')
  const citiesQuery = useQuery({
    ...getCitiesApiV1LocationsCitiesGetOptions(),
    staleTime: 1000 * 60 * 60 * 24,
    gcTime: 1000 * 60 * 60 * 24 * 7,
  })
  const categoriesQuery = useQuery({
    ...getCategoriesApiV1PostsCategoriesGetOptions(),
    staleTime: 1000 * 60 * 60 * 24,
  })

  const cities = (citiesQuery.data?.data?.cities ?? []) as CityResponse[]
  const categories = categoriesQuery.data?.data?.categories ?? []

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setErrorMessage('')
      setPreparedImageFile(null)

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrorMessage('請選擇圖片檔案')
        return
      }
      try {
        const preparedFile = await prepareUploadFile(file, MAX_UPLOAD_BYTES_FREE_LIMIT)
        setPreparedImageFile(preparedFile)
        setImageName(preparedFile.name)

        // Create preview
        const reader = new FileReader()
        reader.onloadend = () => {
          setImagePreview(reader.result as string)
        }
        reader.readAsDataURL(preparedFile)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '圖片處理失敗，請稍後再試')
        setImagePreview(null)
        setImageName(null)
        setValue('image', undefined)
      }
    }
  }

  const removeImage = () => {
    setImagePreview(null)
    setImageName(null)
    setPreparedImageFile(null)
    setErrorMessage('')
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
      const imageFile = preparedImageFile ?? data.image?.[0]
      await createPostFlowMutation.mutateAsync({
        title: data.title,
        content: data.content,
        scope: data.scope,
        city_code: data.scope === 'city' ? data.city_code || null : null,
        category: data.category,
        imageFile,
        onUploadProgress: setUploadProgress,
      })

      router.push('/posts')
    } catch (error: unknown) {
      const apiError = mapApiError(error)
      setErrorMessage(apiError.message)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Category and Scope in stacked rows */}
      <div className="space-y-3">
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
              {categoriesQuery.isLoading && (
                <SelectItem value="__loading__" disabled>
                  分類載入中...
                </SelectItem>
              )}
              {categoriesQuery.isError && (
                <SelectItem value="__error__" disabled>
                  分類載入失敗
                </SelectItem>
              )}
              {!categoriesQuery.isError && categories.length === 0 && (
                <SelectItem value="__empty__" disabled>
                  沒有可用分類
                </SelectItem>
              )}
              {categories.map(category => (
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
              if (value !== 'city') {
                setValue('city_code', undefined)
              }
            }}
          >
            <SelectTrigger id="scope" className="bg-card border-border rounded-xl font-bold">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="global">全部（不限）</SelectItem>
              <SelectItem value="city">城市（指定城市）</SelectItem>
            </SelectContent>
          </Select>

          {/* 城市 - 僅在 scope=city 時顯示 */}
          {scope === 'city' && (
            <Select
              value={selectedCityCode}
              onValueChange={(value: string) => setValue('city_code', value as CityCode)}
            >
              <SelectTrigger
                id="city_code"
                className="mt-2 bg-card border-border rounded-xl font-bold"
                disabled={citiesQuery.isLoading}
              >
                <SelectValue placeholder={citiesQuery.isLoading ? '城市載入中...' : '請選擇城市'} />
              </SelectTrigger>
              <SelectContent>
                {citiesQuery.isError && (
                  <SelectItem value="__error__" disabled>
                    城市載入失敗
                  </SelectItem>
                )}
                {!citiesQuery.isError && cities.length === 0 && (
                  <SelectItem value="__empty__" disabled>
                    沒有可用城市
                  </SelectItem>
                )}
                {cities.map(city => (
                  <SelectItem key={city.code} value={city.code}>
                    {city.name_zh}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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

        <div className="space-y-2">
          {(() => {
            const imageField = register('image', {
              onChange: handleImageChange,
            })

            return (
              <FileInput
                id="image"
                label={imageName ? '更換圖片' : '選擇圖片'}
                accept="image/*"
                name={imageField.name}
                onBlur={imageField.onBlur}
                onChange={imageField.onChange}
                ref={imageField.ref}
                buttonClassName="h-12 w-full rounded-xl font-black"
              />
            )
          })()}

          {imageName && (
            <p className="text-xs text-muted-foreground truncate" title={imageName}>
              {imageName}
            </p>
          )}
          <p className="text-[11px] text-muted-foreground">
            免費方案單張上限 2MB，超過會自動壓縮
          </p>
        </div>

        {imagePreview && (
          <div className="relative mt-3">
            <div className="relative h-48 w-full overflow-hidden rounded-2xl border border-border bg-muted">
              <Image src={imagePreview} alt="預覽" fill className="object-contain" unoptimized />
            </div>
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
          disabled={createPostFlowMutation.isPending}
          className="h-12 rounded-2xl border-border bg-card font-black hover:bg-muted"
        >
          取消
        </Button>
        <Button
          type="submit"
          disabled={createPostFlowMutation.isPending}
          className="h-12 rounded-2xl bg-slate-900 text-white font-black shadow-xl hover:bg-slate-800"
        >
          {createPostFlowMutation.isPending ? (
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
