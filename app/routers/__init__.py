import importlib
from pathlib import Path
from fastapi import APIRouter
from settings import settings

base_router = APIRouter(prefix=settings.API_PREFIX)

for router_path in [
    f"routers.{router_py.stem}"
    for router_py in Path(__file__).parent.glob("*.py")
    if not router_py.name.startswith("_")
]:
    base_router.include_router(getattr(importlib.import_module(router_path), "router"))
