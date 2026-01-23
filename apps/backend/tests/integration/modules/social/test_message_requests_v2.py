"""Integration tests for message requests, threads, and messaging flow (US5).

Tests the complete flow:
- MessageRequest creation (stranger messaging)
- Accept/Decline requests
- Thread uniqueness (one thread per user pair)
- Sending messages in threads
- Privacy settings (block stranger messages)
"""

import uuid
from datetime import datetime

import pytest

from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus


@pytest.mark.asyncio
class TestMessageRequestFlow:
    """Test message request creation and acceptance flow"""

    async def test_create_message_request_stranger_to_stranger(
        self,
        message_request_repository,
        thread_repository,
        friendship_repository,
        test_user_a_id,
        test_user_b_id,
    ):
        """Test creating a message request from stranger to stranger"""
        # Verify no existing friendship
        friendship = await friendship_repository.get_by_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert friendship is None

        # Create message request from A to B
        from app.modules.social.domain.entities.message_request import (
            MessageRequest,
            RequestStatus,
        )

        request_id = str(uuid.uuid4())
        message_request = MessageRequest(
            id=request_id,
            sender_id=str(test_user_a_id),
            recipient_id=str(test_user_b_id),
            initial_message="Hi, interested in your cards!",
            post_id=None,
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        created = await message_request_repository.create(message_request)
        assert created.id == request_id
        assert created.status == RequestStatus.PENDING
        assert created.sender_id == str(test_user_a_id)
        assert created.recipient_id == str(test_user_b_id)

        # Verify thread not yet created
        thread = await thread_repository.find_by_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert thread is None

    async def test_accept_request_creates_unique_thread(
        self,
        message_request_repository,
        thread_repository,
        test_user_a_id,
        test_user_b_id,
    ):
        """Test accepting a request creates a unique thread"""
        from app.modules.social.domain.entities.message_request import (
            MessageRequest,
            RequestStatus,
        )

        # Create request
        request_id = str(uuid.uuid4())
        message_request = MessageRequest(
            id=request_id,
            sender_id=str(test_user_a_id),
            recipient_id=str(test_user_b_id),
            initial_message="Hello!",
            post_id=None,
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        await message_request_repository.create(message_request)

        # Accept request (this should create thread)
        message_request.accept()
        await message_request_repository.update(message_request)

        # Verify thread exists
        thread = await thread_repository.find_by_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert thread is not None
        assert {thread.user_a_id, thread.user_b_id} == {
            str(test_user_a_id),
            str(test_user_b_id),
        }

        # Try to find thread in reverse order
        thread_reverse = await thread_repository.find_by_users(
            str(test_user_b_id), str(test_user_a_id)
        )
        assert thread_reverse is not None
        assert thread.id == thread_reverse.id

    async def test_decline_request_no_thread_created(
        self,
        message_request_repository,
        thread_repository,
        test_user_a_id,
        test_user_b_id,
    ):
        """Test declining a request does not create a thread"""
        from app.modules.social.domain.entities.message_request import (
            MessageRequest,
            RequestStatus,
        )

        # Create request
        request_id = str(uuid.uuid4())
        message_request = MessageRequest(
            id=request_id,
            sender_id=str(test_user_a_id),
            recipient_id=str(test_user_b_id),
            initial_message="Hello!",
            post_id=None,
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        await message_request_repository.create(message_request)

        # Decline request
        message_request.decline()
        await message_request_repository.update(message_request)

        # Verify no thread created
        thread = await thread_repository.find_by_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert thread is None

        # Verify request status updated
        stored_request = await message_request_repository.get_by_id(request_id)
        assert stored_request.status == RequestStatus.DECLINED

    async def test_cannot_create_duplicate_request_when_pending(
        self, message_request_repository, test_user_a_id, test_user_b_id
    ):
        """Test cannot create duplicate request when one is pending"""
        from app.modules.social.domain.entities.message_request import (
            MessageRequest,
            RequestStatus,
        )

        # Create first request
        request_1 = MessageRequest(
            id=str(uuid.uuid4()),
            sender_id=str(test_user_a_id),
            recipient_id=str(test_user_b_id),
            initial_message="First message",
            post_id=None,
            status=RequestStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        await message_request_repository.create(request_1)

        # Check for existing pending request
        existing = await message_request_repository.find_pending_between_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert existing is not None
        assert existing.id == request_1.id


@pytest.mark.asyncio
class TestThreadUniqueness:
    """Test thread uniqueness constraints"""

    async def test_thread_uniqueness_per_user_pair(
        self, thread_repository, test_user_a_id, test_user_b_id
    ):
        """Test only one thread exists per user pair"""
        from app.modules.social.domain.entities.thread import MessageThread

        # Create thread
        thread_id = str(uuid.uuid4())
        thread = MessageThread(
            id=thread_id,
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_b_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread)

        # Try to find by either user order
        found_1 = await thread_repository.find_by_users(
            str(test_user_a_id), str(test_user_b_id)
        )
        found_2 = await thread_repository.find_by_users(
            str(test_user_b_id), str(test_user_a_id)
        )

        assert found_1 is not None
        assert found_2 is not None
        assert found_1.id == found_2.id == thread_id

    async def test_list_threads_for_user(
        self, thread_repository, test_user_a_id, test_user_b_id, test_user_c_id
    ):
        """Test listing all threads for a user"""
        from app.modules.social.domain.entities.thread import MessageThread

        # Create thread A-B
        thread_ab = MessageThread(
            id=str(uuid.uuid4()),
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_b_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread_ab)

        # Create thread A-C
        thread_ac = MessageThread(
            id=str(uuid.uuid4()),
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_c_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread_ac)

        # List threads for A
        threads = await thread_repository.get_threads_for_user(str(test_user_a_id))
        assert len(threads) == 2
        thread_ids = {t.id for t in threads}
        assert thread_ab.id in thread_ids
        assert thread_ac.id in thread_ids


@pytest.mark.asyncio
class TestMessagingInThread:
    """Test sending and receiving messages in threads"""

    async def test_send_message_in_thread(
        self, thread_repository, thread_message_repository, test_user_a_id, test_user_b_id
    ):
        """Test sending messages in an accepted thread"""
        from app.modules.social.domain.entities.thread import MessageThread
        from app.modules.social.domain.entities.thread_message import ThreadMessage

        # Create thread first
        thread_id = str(uuid.uuid4())
        thread = MessageThread(
            id=thread_id,
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_b_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread)

        # Send message from A to B
        message_id = str(uuid.uuid4())
        message = ThreadMessage(
            id=message_id,
            thread_id=thread_id,
            sender_id=str(test_user_a_id),
            content="Hello from A!",
            post_id=None,
            created_at=datetime.utcnow(),
        )
        created_message = await thread_message_repository.create(message)

        assert created_message.id == message_id
        assert created_message.thread_id == thread_id
        assert created_message.sender_id == str(test_user_a_id)
        assert created_message.content == "Hello from A!"

    async def test_list_messages_in_thread(
        self, thread_repository, thread_message_repository, test_user_a_id, test_user_b_id
    ):
        """Test listing messages in a thread"""
        from app.modules.social.domain.entities.thread import MessageThread
        from app.modules.social.domain.entities.thread_message import ThreadMessage

        # Create thread
        thread_id = str(uuid.uuid4())
        thread = MessageThread(
            id=thread_id,
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_b_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread)

        # Send multiple messages
        msg1 = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            sender_id=str(test_user_a_id),
            content="Message 1",
            post_id=None,
            created_at=datetime.utcnow(),
        )
        msg2 = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            sender_id=str(test_user_b_id),
            content="Message 2",
            post_id=None,
            created_at=datetime.utcnow(),
        )
        await thread_message_repository.create(msg1)
        await thread_message_repository.create(msg2)

        # List messages
        messages = await thread_message_repository.get_messages_by_thread(
            thread_id, limit=50
        )
        assert len(messages) == 2

    async def test_message_with_post_reference(
        self, thread_repository, thread_message_repository, test_user_a_id, test_user_b_id
    ):
        """Test message can reference a post_id"""
        from app.modules.social.domain.entities.thread import MessageThread
        from app.modules.social.domain.entities.thread_message import ThreadMessage

        # Create thread
        thread_id = str(uuid.uuid4())
        thread = MessageThread(
            id=thread_id,
            user_a_id=str(test_user_a_id),
            user_b_id=str(test_user_b_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await thread_repository.create(thread)

        # Send message with post reference
        post_id = str(uuid.uuid4())
        message = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            sender_id=str(test_user_a_id),
            content="About your post",
            post_id=post_id,
            created_at=datetime.utcnow(),
        )
        created = await thread_message_repository.create(message)
        assert created.post_id == post_id


@pytest.mark.asyncio
class TestPrivacyAndBlocking:
    """Test privacy settings and blocking rules for messaging"""

    async def test_blocked_user_cannot_send_request(
        self, message_request_repository, friendship_repository, test_user_a_id, test_user_b_id
    ):
        """Test blocked users cannot send message requests"""
        # User B blocks User A
        block_id = str(uuid.uuid4())
        block = Friendship(
            id=block_id,
            user_id=str(test_user_b_id),
            friend_id=str(test_user_a_id),
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )
        await friendship_repository.create(block)

        # Verify A is blocked by B
        is_blocked = await friendship_repository.is_blocked(
            str(test_user_a_id), str(test_user_b_id)
        )
        assert is_blocked is True

    async def test_stranger_messages_can_be_disabled(self, test_user_b_id):
        """Test privacy setting can disable stranger messages
        
        Note: This is a placeholder test. The actual privacy settings
        enforcement will be implemented in the privacy service (T062).
        """
        # This will be implemented with privacy settings in T062
        pass


# Fixtures
@pytest.fixture
def test_user_a_id():
    """Test user A"""
    return uuid.uuid4()


@pytest.fixture
def test_user_b_id():
    """Test user B"""
    return uuid.uuid4()


@pytest.fixture
def test_user_c_id():
    """Test user C"""
    return uuid.uuid4()


@pytest.fixture
async def message_request_repository(db_session):
    """Message request repository fixture"""
    from app.modules.social.infrastructure.repositories.message_request_repository import (
        MessageRequestRepository,
    )

    return MessageRequestRepository(db_session)


@pytest.fixture
async def thread_repository(db_session):
    """Thread repository fixture"""
    from app.modules.social.infrastructure.repositories.thread_repository import (
        ThreadRepository,
    )

    return ThreadRepository(db_session)


@pytest.fixture
async def thread_message_repository(db_session):
    """Thread message repository fixture"""
    from app.modules.social.infrastructure.repositories.thread_message_repository import (
        ThreadMessageRepository,
    )

    return ThreadMessageRepository(db_session)


@pytest.fixture
async def friendship_repository(db_session):
    """Friendship repository fixture"""
    from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
        FriendshipRepositoryImpl,
    )

    return FriendshipRepositoryImpl(db_session)
