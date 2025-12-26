"""Close Post Use Case - Manually close a post"""

from app.modules.posts.domain.repositories.i_post_repository import IPostRepository


class ClosePostUseCase:
    """
    Use case for manually closing a post

    Business Rules:
    - Only post owner can close their post
    - Post must be open
    """

    def __init__(self, post_repository: IPostRepository):
        self.post_repository = post_repository

    async def execute(self, post_id: str, current_user_id: str) -> None:
        """
        Close a post

        Args:
            post_id: ID of the post to close
            current_user_id: ID of the current user (must be post owner)

        Raises:
            ValueError: If validation fails
        """
        # Get post
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            raise ValueError("Post not found")

        # Validate: only owner can close
        if post.owner_id != current_user_id:
            raise ValueError("Only post owner can close the post")

        # Validate: post must be open
        if not post.is_open():
            raise ValueError(f"Post is already {post.status}")

        # Close the post
        post.close()
        await self.post_repository.update(post)
