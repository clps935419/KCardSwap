'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { logout } from '@/lib/google-oauth'

export default function MeSettingsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [allowStrangerDM, setAllowStrangerDM] = useState(true)

  const toggleStrangerDM = () => {
    const nextValue = !allowStrangerDM
    setAllowStrangerDM(nextValue)
    toast({
      title: '隱私設定',
      description: `陌生人私訊：${nextValue ? '開啟' : '關閉'}`,
    })
  }

  const handleLogout = async () => {
    await logout()
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
