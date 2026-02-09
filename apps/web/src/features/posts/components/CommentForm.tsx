'use client'

import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface CommentFormProps {
	onSubmit: (content: string) => void
	isSubmitting: boolean
	disabled?: boolean
}

export function CommentForm({ onSubmit, isSubmitting, disabled }: CommentFormProps) {
	const [content, setContent] = useState('')

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault()

		if (!content.trim()) {
			return
		}

		onSubmit(content.trim())
		setContent('') // Clear input after submission
	}

	return (
		<form onSubmit={handleSubmit} className="space-y-3">
			<Textarea
				value={content}
				onChange={(e) => setContent(e.target.value)}
				placeholder="寫下你的留言..."
				disabled={disabled || isSubmitting}
				maxLength={1000}
				rows={3}
				className="resize-none"
			/>

			<div className="flex items-center justify-between">
				<span className="text-xs text-muted-foreground">
					{content.length}/1000
				</span>

				<Button
					type="submit"
					disabled={disabled || isSubmitting || !content.trim()}
					className="px-6"
				>
					{isSubmitting ? (
						<>
							<Loader2 className="mr-2 h-4 w-4 animate-spin" />
							送出中...
						</>
					) : (
						'送出留言'
					)}
				</Button>
			</div>
		</form>
	)
}
