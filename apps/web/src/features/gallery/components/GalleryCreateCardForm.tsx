'use client'

import Image from 'next/image'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
        <FormField
          control={form.control}
          name="title"
          rules={{
            required: 'Title is required',
            maxLength: { value: 200, message: 'Title is too long' },
          }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title *</FormLabel>
              <FormControl>
                <Input placeholder="Card title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="idol_name"
          rules={{
            required: 'Idol name is required',
            maxLength: { value: 100, message: 'Idol name is too long' },
          }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Idol Name *</FormLabel>
              <FormControl>
                <Input placeholder="e.g., IU" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="era"
          rules={{ maxLength: { value: 100, message: 'Era is too long' } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Era (Optional)</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Love Poem" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          rules={{ maxLength: { value: 1000, message: 'Description is too long' } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description (Optional)</FormLabel>
              <FormControl>
                <Textarea placeholder="Add a description..." rows={3} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Image Upload (T055) */}
        <div className="space-y-2">
          <Label htmlFor="image">Image (Optional)</Label>
          <Input
            id="image"
            type="file"
            accept="image/*"
            {...form.register('image', {
              onChange: handleImageChange,
            })}
          />
          {imagePreview && (
            <div className="relative mt-2">
              <div className="relative h-48 w-full overflow-hidden rounded-md border">
                <Image
                  src={imagePreview}
                  alt="Preview"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
              <Button
                type="button"
                variant="destructive"
                size="sm"
                className="absolute right-2 top-2"
                onClick={removeImage}
              >
                Remove
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
              <p className="mt-1 text-xs text-muted-foreground">Uploading... {uploadProgress}%</p>
            </div>
          )}
        </div>

        {form.formState.errors.root && (
          <div className="text-sm text-destructive">{form.formState.errors.root.message}</div>
        )}

        <div className="flex justify-end gap-2">
          <Button
            type="submit"
            disabled={
              form.formState.isSubmitting ||
              createCardFlowMutation.isPending
            }
          >
            {form.formState.isSubmitting ||
            createCardFlowMutation.isPending
              ? 'Creating...'
              : 'Create Card'}
          </Button>
        </div>
      </form>
    </Form>
  )
}
