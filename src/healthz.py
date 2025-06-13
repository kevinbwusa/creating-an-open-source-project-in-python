# coding: utf-8
"""Health check module"""
import logging

from fastapi import APIRouter


class EndpointFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Filters logging on endpoints"""

    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


logger = logging.getLogger("uvicorn.access")
for endpoint in ("/api/healthz/live", "/api/healthz/ready", "/metrics"):
    logger.addFilter(EndpointFilter(endpoint))

router = APIRouter()


@router.get(
    "/api/healthz/live",
    responses={
        200: {"description": "Successful operation"},
    },
    tags=["healthz"],
    include_in_schema=False,
)
def liveness_probe():
    """Check for liveness"""
    return 200


@router.get(
    "/api/healthz/ready",
    responses={
        200: {"description": "Successful operation"},
    },
    tags=["healthz"],
    include_in_schema=False,
)
def readiness_probe():
    """Check for readiness"""
    return 200
