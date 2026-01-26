'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  
  return (
    <div className="min-h-screen bg-background flex flex-col relative">
      {/* Header */}
      <header className="px-6 py-4 flex justify-between items-center bg-card shadow-sm z-10 sticky top-0">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-black text-primary-500">
              KCardSwap
              <span className="text-secondary-500">.</span>
            </h1>
          </div>
          <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
            V2 貼文優先
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Plan Toggle - would be dynamic in real implementation */}
          <Button 
            variant="outline" 
            size="sm"
            className="px-3 py-2 rounded-xl text-[10px] font-black border border-border bg-card hover:bg-muted"
          >
            方案：<span className="text-foreground">免費</span>
          </Button>
          
          {/* User Avatar */}
          <Link href="/me/gallery">
            <button 
              className="w-9 h-9 bg-primary-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-black transition-transform active:scale-95 hover:scale-105"
              aria-label="前往我的檔案"
            >
              U
            </button>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-24 px-4 md:px-8 py-6 relative">
        {children}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-6 left-6 right-6 md:left-1/2 md:-translate-x-1/2 md:max-w-md h-[74px] bg-card/90 backdrop-blur-md border border-border shadow-2xl rounded-[28px] px-3 z-20">
        <div className="grid grid-cols-3 items-center h-full">
          {/* Home */}
          <Link href="/posts">
            <button 
              className={`h-14 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all active:scale-95 ${
                pathname === '/posts' 
                  ? 'text-primary-500 bg-accent shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              <div className="text-xl leading-none">🏠</div>
              <div className="text-[10px] font-black tracking-wide">首頁</div>
            </button>
          </Link>

          {/* Create Post */}
          <Link href="/posts/new" className="justify-self-center">
            <button 
              className="w-14 h-14 bg-slate-900 rounded-2xl flex flex-col items-center justify-center gap-0.5 text-white shadow-xl transition-transform active:scale-95 hover:scale-105"
              aria-label="發文"
            >
              <div className="text-2xl leading-none">+</div>
              <div className="text-[9px] font-black tracking-wide text-white/90">發文</div>
            </button>
          </Link>

          {/* Inbox */}
          <Link href="/inbox">
            <button 
              className={`h-14 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all active:scale-95 ${
                pathname === '/inbox' 
                  ? 'text-primary-500 bg-accent shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              <div className="text-xl leading-none">💬</div>
              <div className="text-[10px] font-black tracking-wide">信箱</div>
            </button>
          </Link>
        </div>
      </nav>
    </div>
  )
}
