'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { MessageRequestsList } from '@/features/inbox/components/MessageRequestsList'
import { ThreadsList } from '@/features/inbox/components/ThreadsList'

export default function InboxPage() {
  const [activeTab, setActiveTab] = useState<'requests' | 'threads'>('requests')

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      {/* Tab Switcher */}
      <Card className="p-3 rounded-2xl border border-border/30 bg-card">
        <div className="flex gap-2">
          <Button
            variant={activeTab === 'requests' ? 'default' : 'outline'}
            onClick={() => setActiveTab('requests')}
            className={`flex-1 h-10 rounded-xl font-black text-[11px] ${
              activeTab === 'requests'
                ? 'bg-slate-900 text-white hover:bg-slate-800'
                : 'bg-card border border-border text-muted-foreground hover:bg-muted'
            }`}
          >
            請求
          </Button>
          <Button
            variant={activeTab === 'threads' ? 'default' : 'outline'}
            onClick={() => setActiveTab('threads')}
            className={`flex-1 h-10 rounded-xl font-black text-[11px] ${
              activeTab === 'threads'
                ? 'bg-slate-900 text-white hover:bg-slate-800'
                : 'bg-card border border-border text-muted-foreground hover:bg-muted'
            }`}
          >
            聊天
          </Button>
        </div>
      </Card>

      {/* Tab Content */}
      <div>
        {activeTab === 'requests' && <MessageRequestsList />}
        {activeTab === 'threads' && <ThreadsList />}
      </div>
    </div>
  )
}
