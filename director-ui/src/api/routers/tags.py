"""Tags API router."""

from fastapi import APIRouter, Depends
from api.dependencies import get_tag_service
from api.schemas.tags import TagsListResponse, TagResponse
from services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagsListResponse)
async def get_tags(
    tag_service: TagService = Depends(get_tag_service)
):
    """Get all tags with usage counts."""
    tags = await tag_service.get_all_tags()
    return TagsListResponse(
        tags=[TagResponse(**tag) for tag in tags],
        total=len(tags)
    )
