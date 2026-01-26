'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { signOut, useSession } from 'next-auth/react'
import { Button } from '@/components/ui/button'

// Constants for page titles
const PAGE_TITLES = {
  POSTS: '貼文',
  INBOX: '信箱',
  PROFILE: '我的檔案',
  DEFAULT: '貼文',
} as const

// Get page title based on current pathname
// Note: Uses prefix matching since nested routes should inherit parent section titles
function getPageTitle(pathname: string): string {
  if (pathname === '/posts' || pathname.startsWith('/posts/')) return PAGE_TITLES.POSTS
  if (pathname === '/inbox' || pathname.startsWith('/inbox/')) return PAGE_TITLES.INBOX
  if (pathname === '/me' || pathname.startsWith('/me/')) return PAGE_TITLES.PROFILE
  return PAGE_TITLES.DEFAULT
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { data: session } = useSession()
  const pageTitle = getPageTitle(pathname)

  return (
    <div className="min-h-screen bg-background flex flex-col relative">
      {/* Header */}
      <header className="px-6 py-4 flex justify-between items-center bg-card shadow-sm z-10 sticky top-0">
        <div className="flex flex-col">
          <p className="text-sm font-black text-foreground">{pageTitle}</p>
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

          {/* User Avatar with Dropdown */}
          <div className="relative group">
            <Link href="/me/gallery">
              <button
                type="button"
                className="w-9 h-9 bg-primary-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-black transition-transform active:scale-95 hover:scale-105"
                aria-label="前往我的檔案"
                title={session?.user?.email || '使用者'}
              >
                {session?.user?.name?.[0]?.toUpperCase() ||
                  session?.user?.email?.[0]?.toUpperCase() ||
                  'U'}
              </button>
            </Link>

            {/* Logout on hover */}
            <div className="absolute right-0 top-full mt-2 hidden group-hover:block">
              <Button
                onClick={() => signOut({ callbackUrl: '/login' })}
                variant="outline"
                size="sm"
                className="whitespace-nowrap text-xs"
              >
                登出
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-24 px-4 md:px-8 py-6 relative">{children}</main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-6 left-6 right-6 md:left-1/2 md:-translate-x-1/2 md:max-w-md h-[74px] bg-card/90 backdrop-blur-md border border-border shadow-2xl rounded-[28px] px-3 z-20">
        <div className="grid grid-cols-3 items-center h-full">
          {/* Home */}
          <Link href="/posts">
            <button
              type="button"
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
              type="button"
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
              type="button"
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
