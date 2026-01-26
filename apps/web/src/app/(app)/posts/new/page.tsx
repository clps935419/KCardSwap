import { Card } from '@/components/ui/card'
import { CreatePostForm } from '@/features/posts/components/CreatePostForm'

export default function NewPostPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <Card className="p-6 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="mb-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">發文</p>
          <h1 className="text-lg font-black text-foreground">發佈貼文</h1>
        </div>
        
        <CreatePostForm />
      </Card>
    </div>
  )
}
