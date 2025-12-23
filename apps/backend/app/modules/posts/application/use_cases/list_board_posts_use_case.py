"""List Board Posts Use Case - List posts for a specific city with filters"""
from typing import List, Optional

from app.modules.posts.domain.entities.post import Post, PostStatus
from app.modules.posts.domain.repositories.post_repository import PostRepository


class ListBoardPostsUseCase:
    """
    Use case for listing posts on a city board
    
    Business Rules:
    - city_code is required
    - Only show posts with status=open and not expired
    - Support filtering by idol and idol_group
    - Results ordered by created_at DESC (newest first)
    """
    
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    async def execute(
        self,
        city_code: str,
        idol: Optional[str] = None,
        idol_group: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Post]:
        """
        List posts for a city board
        
        Args:
            city_code: City code (required)
            idol: Optional idol name filter
            idol_group: Optional idol group filter
            limit: Maximum number of results (default 50)
            offset: Pagination offset (default 0)
            
        Returns:
            List of Post entities
            
        Raises:
            ValueError: If city_code is not provided
        """
        if not city_code:
            raise ValueError("City code is required")
        
        # Only show open posts
        posts = await self.post_repository.list_by_city(
            city_code=city_code,
            status=PostStatus.OPEN,
            idol=idol,
            idol_group=idol_group,
            limit=limit,
            offset=offset
        )
        
        # Filter out expired posts (business logic check)
        # Note: expired posts should be marked by a scheduled job,
        # but we do a runtime check here for safety
        valid_posts = [post for post in posts if not post.is_expired()]
        
        return valid_posts
