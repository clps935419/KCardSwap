'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'
import { logout } from '@/lib/google-oauth'
import {
  getMyProfileApiV1ProfileMeGetOptions,
  getMyProfileApiV1ProfileMeGetQueryKey,
  getUserProfileApiV1ProfileUserIdGetQueryKey,
  listPostsApiV1PostsGetQueryKey,
  updateMyProfileApiV1ProfileMePutMutation,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface SettingsFormValues {
  nickname: string
  bio: string
  allowStrangerDM: boolean
}

export function MeSettingsPageClient() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<SettingsFormValues>({
    defaultValues: {
      nickname: '',
      bio: '',
      allowStrangerDM: true,
    },
  })

  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  const profile = profileQuery.data?.data

  useEffect(() => {
    if (!profile) return

    reset({
      nickname: profile.nickname || '',
      bio: profile.bio || '',
      allowStrangerDM: profile.privacy_flags?.allow_stranger_chat ?? true,
    })
  }, [profile, reset])

  const updateProfile = useMutation({
    ...updateMyProfileApiV1ProfileMePutMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getMyProfileApiV1ProfileMeGetQueryKey(),
      })

      queryClient.invalidateQueries({
        queryKey: listPostsApiV1PostsGetQueryKey(),
      })

      queryClient.invalidateQueries({
        predicate: query => {
          const key = query.queryKey?.[0]
          return (
            typeof key === 'object' &&
            key !== null &&
            '_id' in key &&
            key._id === 'getPostApiV1PostsPostIdGet'
          )
        },
      })

      if (profile?.user_id) {
        queryClient.invalidateQueries({
          queryKey: getUserProfileApiV1ProfileUserIdGetQueryKey({
            path: { user_id: profile.user_id },
          }),
        })
      }
    },
  })

  const allowStrangerDM = watch('allowStrangerDM')
  const bioLength = watch('bio')?.length || 0
  const isSaving = updateProfile.isPending || isSubmitting

  const onSubmit = async (values: SettingsFormValues) => {
    const normalizedNickname = values.nickname.trim()
    const normalizedBio = values.bio.trim()

    try {
      await updateProfile.mutateAsync({
        body: {
          nickname: normalizedNickname,
          bio: normalizedBio || null,
          privacy_flags: {
            allow_stranger_chat: values.allowStrangerDM,
          },
        },
      })

      reset({
        nickname: normalizedNickname,
        bio: normalizedBio,
        allowStrangerDM: values.allowStrangerDM,
      })

      toast({
        title: '設定',
        description: '已更新個人資料與隱私設定',
      })
    } catch (_error) {
      toast({
        title: '設定',
        description: '更新失敗，請稍後再試',
        variant: 'destructive',
      })
    }
  }

  const handleLogout = async () => {
    await logout()
    queryClient.clear()
    router.push('/login')
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
          <div className="space-y-5">
            <div>
              <p className="text-sm font-black text-foreground">個人資料與隱私設定</p>
              <p className="text-[11px] text-muted-foreground">
                編輯暱稱、Bio 與私訊權限，最後一次儲存
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-xs font-bold text-foreground">暱稱</p>
              <Input
                placeholder="請輸入暱稱"
                maxLength={30}
                disabled={isSaving || profileQuery.isLoading}
                {...register('nickname', {
                  required: '暱稱不能為空',
                  maxLength: {
                    value: 30,
                    message: '暱稱最多 30 字',
                  },
                  validate: value => value.trim().length > 0 || '暱稱不能為空',
                })}
              />
              {errors.nickname && (
                <p className="text-[11px] text-destructive">{errors.nickname.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-xs font-bold text-foreground">Bio</p>
              <Textarea
                placeholder="介紹一下自己、收藏偏好或交易備註"
                maxLength={200}
                rows={4}
                disabled={isSaving || profileQuery.isLoading}
                {...register('bio', {
                  maxLength: {
                    value: 200,
                    message: 'Bio 最多 200 字',
                  },
                })}
              />
              <p className="text-[11px] text-muted-foreground text-right">{bioLength}/200</p>
              {errors.bio && <p className="text-[11px] text-destructive">{errors.bio.message}</p>}
            </div>

            <div className="border-t border-border/30 pt-4 space-y-3">
              <p className="text-sm font-black text-foreground">隱私設定</p>
              <p className="text-[11px] text-muted-foreground">
                控制誰能私訊你（會與上方資料一併儲存）
              </p>
              <Button
                type="button"
                onClick={() => setValue('allowStrangerDM', !allowStrangerDM, { shouldDirty: true })}
                disabled={isSaving || profileQuery.isLoading}
                variant="outline"
                className="w-full h-12 rounded-2xl border-border bg-card font-black hover:bg-muted"
              >
                <span className="flex w-full items-center justify-between">
                  <span>陌生人私訊</span>
                  <span className={allowStrangerDM ? 'text-emerald-600' : 'text-rose-600'}>
                    {allowStrangerDM ? '開' : '關'}
                  </span>
                </span>
              </Button>
            </div>

            <div className="border-t border-border/30 pt-4 space-y-2">
              <Button
                type="submit"
                disabled={isSaving || profileQuery.isLoading || !isDirty}
                className="w-full h-12 rounded-2xl bg-slate-900 text-white font-black hover:bg-slate-800 disabled:opacity-60"
              >
                {isSaving ? '儲存中…' : '儲存設定'}
              </Button>
              <p className="text-[11px] text-muted-foreground text-center">
                儲存時會一併更新個人資料與隱私設定
              </p>
            </div>
          </div>
        </Card>
      </form>

      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-black text-foreground">帳號管理</p>
            <p className="text-[11px] text-muted-foreground">登出後需重新登入才能使用</p>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="w-full h-12 rounded-2xl border-border bg-card font-black hover:bg-muted hover:text-destructive"
          >
            登出
          </Button>
        </div>
      </Card>
    </div>
  )
}
