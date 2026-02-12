'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { UserAvatar } from '@/components/ui/user-avatar'
import { getMyProfileApiV1ProfileMeGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

const PAGE_TITLES = {
  POSTS: '貼文',
  INBOX: '信箱',
  PROFILE: '我的檔案',
  DEFAULT: '貼文',
} as const

function getPageTitle(pathname: string): string {
  if (pathname === '/posts' || pathname.startsWith('/posts/')) return PAGE_TITLES.POSTS
  if (pathname === '/inbox' || pathname.startsWith('/inbox/')) return PAGE_TITLES.INBOX
  if (pathname === '/me' || pathname.startsWith('/me/')) return PAGE_TITLES.PROFILE
  return PAGE_TITLES.DEFAULT
}

export function AppLayoutClient({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const pageTitle = getPageTitle(pathname)

  const prefetchPosts = () => {
    if (pathname === '/posts' || pathname.startsWith('/posts/')) return
    router.prefetch('/posts')
  }

  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  const profileWrapper = profileQuery.data
  const profile = profileWrapper?.data
  const avatarUrl = profile?.avatar_url || ''
  const userDisplay = profile?.nickname || profile?.user_id?.substring(0, 1) || ''

  const navButtonBase =
    'w-full h-14 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all active:scale-95'

  return (
    <div className="min-h-screen bg-background flex flex-col relative">
      <header className="px-6 py-4 flex justify-between items-center bg-card shadow-sm z-10 sticky top-0">
        <div className="flex flex-col">
          <p className="text-sm font-black text-foreground">{pageTitle}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="px-3 py-2 rounded-xl text-[10px] font-black border border-border bg-card hover:bg-muted"
          >
            方案：<span className="text-foreground">免費</span>
          </Button>

          <Button
            asChild
            variant="ghost"
            className="p-0 rounded-full overflow-hidden transition-transform active:scale-95 hover:scale-105"
          >
            <Link href="/me" aria-label="前往我的檔案" title={userDisplay || '使用者'}>
              <UserAvatar
                nickname={profile?.nickname}
                avatarUrl={avatarUrl}
                userId={profile?.user_id}
                size="md"
                className="w-9 h-9 bg-primary-500 text-white border-2 border-white shadow-lg"
              />
            </Link>
          </Button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto pb-24 px-4 md:px-8 py-6 relative">{children}</main>

      <nav className="fixed bottom-6 left-6 right-6 md:left-1/2 md:-translate-x-1/2 md:max-w-md h-[74px] bg-card/90 backdrop-blur-md border border-border shadow-2xl rounded-[28px] px-3 z-20">
        <div className="grid grid-cols-3 items-center h-full">
          <Button
            asChild
            variant="ghost"
            className={`${navButtonBase} ${
              pathname === '/posts'
                ? 'text-primary-500 bg-accent shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
            onPointerEnter={prefetchPosts}
            onTouchStart={prefetchPosts}
            onFocus={prefetchPosts}
          >
            <Link href="/posts">
              <div className="text-xl leading-none">🏠</div>
              <div className="text-[10px] font-black tracking-wide">首頁</div>
            </Link>
          </Button>

          <Button
            asChild
            variant="ghost"
            className={`${navButtonBase} ${
              pathname === '/inbox' || pathname.startsWith('/inbox/')
                ? 'text-primary-500 bg-accent shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            <Link href="/inbox">
              <div className="text-xl leading-none">✉️</div>
              <div className="text-[10px] font-black tracking-wide">信箱</div>
            </Link>
          </Button>

          <Button
            asChild
            variant="ghost"
            className={`${navButtonBase} ${
              pathname === '/me' || pathname.startsWith('/me/')
                ? 'text-primary-500 bg-accent shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            <Link href="/me">
              <div className="text-xl leading-none">👤</div>
              <div className="text-[10px] font-black tracking-wide">我的</div>
            </Link>
          </Button>
        </div>
      </nav>
    </div>
  )
}
