"""Global Injector for dependency injection.

Creates and configures the application-wide Injector instance using python-injector.
Aggregates all module configurations.
"""

from injector import Injector

from app.modules.identity.module import IdentityModule
from app.modules.posts.module import PostsModule
from app.modules.social.module import SocialModule
from app.shared.module import SharedModule

# Create global injector instance with all modules
injector = Injector(
    [
        SharedModule(),
        IdentityModule(),
        SocialModule(),
        PostsModule(),
    ]
)
