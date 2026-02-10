'use client'

import Image from 'next/image'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { FileInput } from '@/components/ui/file-input'
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { Textarea } from '@/components/ui/textarea'
import { useCreateGalleryCardFlowMutation } from '@/shared/api/hooks/flows'

interface GalleryCreateCardFormProps {
  onSuccess?: () => void
}

interface CreateCardFormData {
  title: string
  idol_name: string
  era?: string
  description?: string
  image?: FileList
}

export function GalleryCreateCardForm({ onSuccess }: GalleryCreateCardFormProps) {
  const form = useForm<CreateCardFormData>({
    defaultValues: {
      title: '',
      idol_name: '',
      era: '',
      description: '',
    },
  })

  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const createCardFlowMutation = useCreateGalleryCardFlowMutation()

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        form.setError('root', { message: 'Please select an image file' })
        return
      }

      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setImagePreview(null)
    form.setValue('image', undefined)
  }

  const onSubmit = async (data: CreateCardFormData) => {
    try {
      setUploadProgress(0)
      await createCardFlowMutation.mutateAsync({
        title: data.title,
        idol_name: data.idol_name,
        era: data.era || undefined,
        description: data.description || undefined,
        imageFile: data.image?.[0],
        onUploadProgress: setUploadProgress,
      })

      onSuccess?.()
      form.reset()
      setImagePreview(null)
      setUploadProgress(0)
    } catch (error) {
      console.error('Error creating card:', error)
      form.setError('root', {
        message: error instanceof Error ? error.message : 'Failed to create card',
      })
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
          <p className="text-[10px] font-bold text-muted-foreground uppercase">標題</p>
          <FormField
            control={form.control}
            name="title"
            rules={{
              required: '請輸入標題',
              maxLength: { value: 200, message: '標題過長' },
            }}
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    placeholder="卡片標題"
                    className="bg-card border-border rounded-xl"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
          <p className="text-[10px] font-bold text-muted-foreground uppercase">偶像名稱</p>
          <FormField
            control={form.control}
            name="idol_name"
            rules={{
              required: '請輸入偶像名稱',
              maxLength: { value: 100, message: '偶像名稱過長' },
            }}
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    placeholder="例如：IU"
                    className="bg-card border-border rounded-xl"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
          <p className="text-[10px] font-bold text-muted-foreground uppercase">年代（選填）</p>
          <FormField
            control={form.control}
            name="era"
            rules={{ maxLength: { value: 100, message: '年代過長' } }}
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    placeholder="例如：Love Poem"
                    className="bg-card border-border rounded-xl"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4 space-y-2">
          <p className="text-[10px] font-bold text-muted-foreground uppercase">描述（選填）</p>
          <FormField
            control={form.control}
            name="description"
            rules={{ maxLength: { value: 1000, message: '描述過長' } }}
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Textarea
                    placeholder="補充卡片小故事..."
                    rows={3}
                    className="bg-card border-border rounded-xl"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="bg-muted/50 border border-border/30 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[10px] font-bold text-muted-foreground uppercase">圖片</p>
              <p className="text-[11px] text-muted-foreground">選擇 1 張圖片</p>
            </div>
          </div>

          <div className="space-y-2">
            {(() => {
              const imageField = form.register('image', {
                onChange: handleImageChange,
              })

              return (
                <FileInput
                  id="image"
                  label={imagePreview ? '更換圖片' : '選擇圖片'}
                  accept="image/*"
                  name={imageField.name}
                  onBlur={imageField.onBlur}
                  onChange={imageField.onChange}
                  ref={imageField.ref}
                  buttonClassName="h-12 w-full rounded-xl font-black"
                />
              )
            })()}
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

        {form.formState.errors.root && (
          <div className="rounded-2xl bg-destructive/10 border border-destructive/20 p-4">
            <p className="text-sm text-destructive font-bold">
              {form.formState.errors.root.message}
            </p>
          </div>
        )}

        <div>
          <Button
            type="submit"
            disabled={form.formState.isSubmitting || createCardFlowMutation.isPending}
            className="h-12 w-full rounded-2xl bg-slate-900 text-white font-black shadow-xl hover:bg-slate-800"
          >
            {form.formState.isSubmitting || createCardFlowMutation.isPending ? (
              <>
                <Spinner className="mr-2 h-4 w-4" />
                建立中...
              </>
            ) : (
              '建立卡片'
            )}
          </Button>
        </div>
      </form>
    </Form>
  )
}
