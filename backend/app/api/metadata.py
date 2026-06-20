from fastapi import APIRouter, Depends, Query

from app.deps import get_repository
from app.data.repository import RestaurantRepository

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/cities")
def list_cities(
    repository: RestaurantRepository = Depends(get_repository),
) -> dict:
    return {"cities": repository.list_cities()}


@router.get("/cuisines")
def list_cuisines(
    city: str | None = Query(default=None, description="Optional city to scope cuisines"),
    repository: RestaurantRepository = Depends(get_repository),
) -> dict:
    return {"cuisines": repository.list_cuisines(city=city)}
