export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold">登入 KCardSwap</h2>
          <p className="mt-2 text-muted-foreground">使用 Google 帳號登入</p>
        </div>
        <div className="mt-8">
          <button className="w-full rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90">
            Google 登入
          </button>
        </div>
      </div>
    </div>
  )
}
