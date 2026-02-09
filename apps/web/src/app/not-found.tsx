import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center px-6 py-16 text-center">
        <p className="text-xs font-black text-slate-500">404</p>
        <h1 className="mt-3 text-2xl font-black tracking-tight text-slate-900 sm:text-3xl">
          這頁找不到
        </h1>
        <p className="mt-2 text-sm text-slate-600">請確認網址是否正確</p>

        <div className="mt-6 flex justify-center">
          <Button asChild className="h-11 rounded-2xl bg-primary-500 font-black text-white hover:bg-primary-500/90">
            <Link href="/">返回首頁</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
