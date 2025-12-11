from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi_view.inertia import InertiaDepends

from app.security import CurrentUser

router = APIRouter(prefix="/merge-demo", tags=["merge-demo"])


# Sample data for demonstration
ALL_POSTS = [
    {
        "id": i,
        "title": f"Post Title {i}",
        "excerpt": f"This is the excerpt for post {i}. It contains a brief summary of the content.",
        "author": f"Author {(i % 5) + 1}",
        "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
        "likes": (i * 7) % 50,
    }
    for i in range(1, 101)
]


@router.get("")
def merge_demo_index(inertia: InertiaDepends, user: CurrentUser, page: int = 1):
    """
    Merge Props Demo - Paginated Posts with "Load More" functionality

    This demonstrates the basic append merge strategy.
    On initial load, no posts are shown (merge props excluded).
    On partial reload, posts are appended to the existing list.
    """
    per_page = 10
    offset = (page - 1) * per_page
    posts = ALL_POSTS[offset : offset + per_page]
    has_more = len(ALL_POSTS) > offset + per_page

    return inertia.render(
        "MergeDemo/Index",
        {
            "posts": inertia.merge(lambda: posts),
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total": len(ALL_POSTS),
                "has_more": has_more,
            },
        },
    )
