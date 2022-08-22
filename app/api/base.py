from fastapi import APIRouter

from .jobs import jobs
from .users import users

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="", tags=["jobs"])
api_router.include_router(users.router, prefix="", tags=["users"])
