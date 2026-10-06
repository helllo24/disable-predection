from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def check_health():
    """Health check endpoint required by Part 0."""
    return {"status": "healthy"}
