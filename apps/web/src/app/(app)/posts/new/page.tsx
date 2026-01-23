import { Card } from '@/components/ui/card'
import { CreatePostForm } from '@/features/posts/components/CreatePostForm'

export default function NewPostPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">發表貼文</h1>
        <p className="mt-1 text-sm text-muted-foreground">分享您的想法或資訊給社群</p>
      </div>

      <Card className="p-6">
        <CreatePostForm />
      </Card>
    </div>
  )
}
