'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/components/ui/use-toast'
import {
	createPostCommentApiV1PostsPostIdCommentsPost,
	listPostCommentsApiV1PostsPostIdCommentsGet,
	type CreateCommentRequest,
	type CommentResponse,
	type CommentListResponseWrapper,
	type CommentResponseWrapper,
} from '@/shared/api/generated'

/**
 * Hook to fetch comments for a post
 */
export function usePostComments(postId: string, options?: { enabled?: boolean }) {
	return useQuery<CommentListResponseWrapper>({
		queryKey: ['post-comments', postId],
		queryFn: async () => {
			const response = await listPostCommentsApiV1PostsPostIdCommentsGet({
				path: { post_id: postId },
				query: { limit: 50, offset: 0 },
			})
			return response.data as CommentListResponseWrapper
		},
		enabled: options?.enabled,
	})
}

/**
 * Hook to create a comment on a post with optimistic updates
 */
export function useCreateComment(postId: string) {
	const queryClient = useQueryClient()
	const { toast } = useToast()

	return useMutation({
		mutationFn: async (content: string) => {
			const requestBody: CreateCommentRequest = { content }
			const response = await createPostCommentApiV1PostsPostIdCommentsPost({
				path: { post_id: postId },
				body: requestBody,
			})
			// Response is CommentResponseWrapper, extract the actual comment
			const wrapper = response?.data as CommentResponseWrapper
			return wrapper?.data as CommentResponse
		},
		onMutate: async (content: string) => {
			// Cancel any outgoing refetches
			await queryClient.cancelQueries({ queryKey: ['post-comments', postId] })

			// Snapshot the previous value
			const previousComments = queryClient.getQueryData<CommentListResponseWrapper>([
				'post-comments',
				postId,
			])

			// Optimistically update to the new value
			queryClient.setQueryData<CommentListResponseWrapper>(
				['post-comments', postId],
				(old) => {
					if (!old?.data) return old

					const optimisticComment: CommentResponse & { pending?: boolean } = {
						id: `temp-${Date.now()}` as any,
						post_id: postId as any,
						user_id: 'current-user' as any, // Will be replaced with actual user ID from server
						content,
						created_at: new Date().toISOString(),
						updated_at: new Date().toISOString(),
						pending: true,
					}

					return {
						...old,
						data: {
							comments: [optimisticComment, ...(old.data.comments || [])],
							total: (old.data.total || 0) + 1,
						},
					}
				}
			)

			return { previousComments }
		},
		onError: (err, _content, context) => {
			// Rollback to previous value on error
			if (context?.previousComments) {
				queryClient.setQueryData(['post-comments', postId], context.previousComments)
			}

			toast({
				title: '錯誤',
				description: '送出留言失敗，請稍後再試',
				variant: 'destructive',
			})
		},
		onSuccess: (newComment) => {
			// Replace optimistic comment with actual comment from server
			queryClient.setQueryData<CommentListResponseWrapper>(
				['post-comments', postId],
				(old) => {
					if (!old?.data) return old

					const comments = old.data.comments || []
					// Remove the optimistic comment (marked with pending: true)
					const filteredComments = comments.filter((c: any) => !c.pending)

					return {
						...old,
						data: {
							comments: [newComment, ...filteredComments],
							total: old.data.total,
						},
					}
				}
			)
		},
		onSettled: () => {
			// Refetch to ensure we have the latest data
			queryClient.invalidateQueries({ queryKey: ['post-comments', postId] })
		},
	})
}
