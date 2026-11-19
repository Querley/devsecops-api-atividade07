import os
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

APP_ENV = os.getenv("APP_ENV", "production")

app = FastAPI(
    title="DevSecOps Secure API",
    description="API REST de demonstracao para esteira CI/CD DevSecOps (Atividade 07).",
    version="1.0.0",
    docs_url="/docs" if APP_ENV != "production" else None,
    redoc_url=None,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Injects defensive HTTP security headers on every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-zA-Z0-9 _-]+$")
    category: str = Field(..., min_length=2, max_length=40)
    price: float = Field(..., gt=0, le=100000)


class Item(ItemCreate):
    id: int


_ITEMS_DB: Dict[int, Item] = {
    1: Item(id=1, name="Scanner SAST", category="Security", price=0.01),
    2: Item(id=2, name="Container Hardened", category="Infra", price=10.0),
}
_NEXT_ID = 3


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """Healthcheck endpoint for container orchestration and DAST readiness."""
    return {"status": "healthy", "environment": APP_ENV}


@app.get("/api/v1/items", response_model=List[Item])
def list_items() -> List[Item]:
    """Returns all registered items."""
    return list(_ITEMS_DB.values())


@app.get("/api/v1/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    """Returns a single item by ID."""
    if item_id not in _ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return _ITEMS_DB[item_id]


@app.post("/api/v1/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    """Creates a new validated item."""
    global _NEXT_ID
    item = Item(id=_NEXT_ID, **payload.model_dump())
    _ITEMS_DB[_NEXT_ID] = item
    _NEXT_ID += 1
    return item
