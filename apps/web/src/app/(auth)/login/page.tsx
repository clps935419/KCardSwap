export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-between flex-col bg-gradient-to-b from-slate-50 to-white p-8 py-20">
      {/* Logo Section */}
      <div className="text-center">
        <div className="w-20 h-20 bg-secondary-50 rounded-3xl mx-auto flex items-center justify-center shadow-2xl shadow-secondary-300/30 mb-4 ring-4 ring-secondary-50">
          <div className="w-14 h-14 bg-gradient-to-br from-secondary-500 to-rose-400 rounded-2xl flex items-center justify-center text-white font-black text-xl">
            S!
          </div>
        </div>
        <h2 className="text-2xl font-black text-secondary-500">小卡Show!</h2>
        <p className="text-xs text-muted-foreground mt-1 tracking-wide font-medium">
          貼文優先 POC • Web 流程
        </p>
      </div>

      {/* Content Section */}
      <div className="w-full max-w-md space-y-3">
        {/* Info Card */}
        <div className="bg-card border border-border/30 rounded-2xl p-4">
          <p className="text-xs text-muted-foreground">
            <span className="font-black text-foreground">所有瀏覽需登入（V2 決策）</span>
          </p>
          <p className="text-[11px] text-muted-foreground mt-1">
            登入後才能瀏覽貼文、相簿與信箱
          </p>
        </div>

        {/* Google Login Button */}
        <button className="w-full h-16 bg-gradient-to-r from-secondary-50 to-rose-50 border-2 border-secondary-300 rounded-2xl flex items-center justify-center px-6 hover:from-secondary-50/80 hover:to-rose-50/80 transition-all shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-xl shadow flex items-center justify-center font-black">
              G
            </div>
            <div className="text-left">
              <p className="text-sm font-black text-foreground">使用 Google 登入</p>
              <p className="text-[10px] text-muted-foreground">
                登入後才能瀏覽貼文、相簿與信箱
              </p>
            </div>
          </div>
        </button>

        {/* POC Info */}
        <div className="bg-slate-900 text-slate-200 rounded-2xl p-4">
          <p className="text-xs font-bold text-white">POC 互動路徑</p>
          <p className="text-[11px] mt-1 opacity-80">
            貼文 → 私信作者（送出請求）→ 收件者接受 → 信箱對話
          </p>
        </div>
      </div>
    </div>
  )
}
