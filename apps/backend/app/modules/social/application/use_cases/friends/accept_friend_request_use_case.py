"""Accept Friend Request Use Case"""
from app.modules.social.domain.entities.chat_room import ChatRoom
from app.modules.social.domain.repositories.chat_room_repository import ChatRoomRepository
from app.modules.social.domain.repositories.friendship_repository import FriendshipRepository
import uuid
from datetime import datetime


class AcceptFriendRequestUseCase:
    """
    Use case for accepting a friend request
    
    Business Rules:
    - Only the recipient of the request can accept it
    - Request must be in pending status
    - Automatically creates a chat room for the two friends
    """
    
    def __init__(
        self,
        friendship_repository: FriendshipRepository,
        chat_room_repository: ChatRoomRepository
    ):
        self.friendship_repository = friendship_repository
        self.chat_room_repository = chat_room_repository
    
    async def execute(self, friendship_id: str, accepting_user_id: str) -> tuple:
        """
        Accept a friend request and create a chat room
        
        Args:
            friendship_id: ID of the friendship to accept
            accepting_user_id: ID of the user accepting the request
            
        Returns:
            Tuple of (updated_friendship, created_chat_room)
            
        Raises:
            ValueError: If request is invalid or not found
        """
        # Get the friendship
        friendship = await self.friendship_repository.get_by_id(friendship_id)
        
        if not friendship:
            raise ValueError("Friend request not found")
        
        # Verify the accepting user is the recipient
        if friendship.friend_id != accepting_user_id:
            raise ValueError("Only the recipient can accept a friend request")
        
        # Verify status is pending
        if not friendship.is_pending():
            raise ValueError(f"Friend request is not pending (status: {friendship.status})")
        
        # Accept the friendship
        friendship.accept()
        updated_friendship = await self.friendship_repository.update(friendship)
        
        # Create chat room for the two friends (if doesn't exist)
        existing_room = await self.chat_room_repository.get_by_participants(
            friendship.user_id, friendship.friend_id
        )
        
        if existing_room:
            chat_room = existing_room
        else:
            chat_room = ChatRoom(
                id=str(uuid.uuid4()),
                participant_ids=[friendship.user_id, friendship.friend_id],
                created_at=datetime.utcnow()
            )
            chat_room = await self.chat_room_repository.create(chat_room)
        
        return updated_friendship, chat_room
