'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export default function MePage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-black text-foreground">我的功能</p>
            <p className="text-[11px] text-muted-foreground">管理你的內容與收藏</p>
          </div>
          <Button asChild className="w-full h-12 rounded-2xl font-black">
            <Link href="/me/gallery">相簿小卡</Link>
          </Button>
        </div>
      </Card>

      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-black text-foreground">設定</p>
            <p className="text-[11px] text-muted-foreground">隱私與帳號管理</p>
          </div>
          <Button asChild variant="outline" className="w-full h-12 rounded-2xl font-black">
            <Link href="/me/settings">前往設定</Link>
          </Button>
        </div>
      </Card>
    </div>
  )
}
