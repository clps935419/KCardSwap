'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { logout } from '@/lib/google-oauth'
import {
  getMyProfileApiV1ProfileMeGetOptions,
  getMyProfileApiV1ProfileMeGetQueryKey,
  updateMyProfileApiV1ProfileMePutMutation,
} from '@/shared/api/generated/@tanstack/react-query.gen'

export function MeSettingsPageClient() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [allowStrangerDM, setAllowStrangerDM] = useState(true)

  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  const allowStrangerChat = profileQuery.data?.data?.privacy_flags?.allow_stranger_chat

  useEffect(() => {
    if (allowStrangerChat !== undefined) {
      setAllowStrangerDM(allowStrangerChat)
    }
  }, [allowStrangerChat])

  const updateProfile = useMutation({
    ...updateMyProfileApiV1ProfileMePutMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getMyProfileApiV1ProfileMeGetQueryKey(),
      })
    },
  })

  const toggleStrangerDM = async () => {
    const nextValue = !allowStrangerDM
    setAllowStrangerDM(nextValue)
    try {
      await updateProfile.mutateAsync({
        body: {
          privacy_flags: {
            allow_stranger_chat: nextValue,
          },
        },
      })
      toast({
        title: '隱私設定',
        description: `陌生人私訊：${nextValue ? '開啟' : '關閉'}`,
      })
    } catch (_error) {
      setAllowStrangerDM(!nextValue)
      toast({
        title: '隱私設定',
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
      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-black text-foreground">隱私設定</p>
            <p className="text-[11px] text-muted-foreground">控制誰能私訊你</p>
          </div>
          <Button
            onClick={toggleStrangerDM}
            disabled={updateProfile.isPending}
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
      </Card>

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
