export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center px-4">
          <h1 className="text-xl font-bold">KCardSwap</h1>
          <nav className="ml-8 flex gap-6">
            <a href="/posts" className="text-sm hover:underline">
              貼文
            </a>
            <a href="/inbox" className="text-sm hover:underline">
              信箱
            </a>
            <a href="/me/gallery" className="text-sm hover:underline">
              我的相簿
            </a>
          </nav>
        </div>
      </header>
      <main className="container mx-auto p-4">{children}</main>
    </div>
  )
}
