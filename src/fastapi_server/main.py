"""Module providing a demonstration of the FastAPI."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from fastapi_server.apis.task_api import router as TaskApiRouter
from fastapi_server.configuration import CORS_ALLOW_ORIGIN, logger

API_CONTEXT_ROOT = os.environ.get("API_CONTEXT_ROOT", "/api")
API_VERSION = os.environ.get("API_VERSION", "v1")
API_PREFIX = f"{API_CONTEXT_ROOT}/{API_VERSION}"


@asynccontextmanager
async def lifespan(this_app: FastAPI):
    """Facilitates startup and shutdown logic"""
    # create_tables()
    instrumentor.expose(this_app, include_in_schema=False)
    yield


app = FastAPI()

# app = FastAPI(
#     title="Kevin's Utilities",
#     description="API for handling utility operations",
#     version="1.0.0",
#     docs_url=None,
#     redoc_url=None,
#     openapi_url=f"{API_PREFIX}/openapi.json",
#     lifespan=lifespan,
# )

parent_dir_path = os.path.dirname(os.path.realpath(__file__))
app.mount(
    f"{API_PREFIX}/static",
    StaticFiles(directory=f"{parent_dir_path}/static"),
    name="static",
)

if CORS_ALLOW_ORIGIN:
    corsAllowOrigin = CORS_ALLOW_ORIGIN.split(",")
    logger.info("CORS allow origin: %s", corsAllowOrigin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=corsAllowOrigin,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(TaskApiRouter, prefix=API_PREFIX)

instrumentor = Instrumentator().instrument(app)


@app.get(
    app.swagger_ui_oauth2_redirect_url or "/docs/oauth2-redirect",
    include_in_schema=False,
)
async def swagger_ui_redirect():
    """Setup docs to work with oauth2 redirect"""
    return get_swagger_ui_oauth2_redirect_html()


@app.get(f"{API_PREFIX}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Setup docs endpoint for live Swagger documentation"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or f"{API_PREFIX}/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"{API_PREFIX}/static/swagger-ui-bundle.js",
        swagger_css_url=f"{API_PREFIX}/static/swagger-ui.css",
    )


@app.get(f"{API_PREFIX}/redocs", include_in_schema=False)
async def redoc_html():
    """Setup docs endpoint for live redoc documentation"""
    return get_redoc_html(
        openapi_url=app.openapi_url or f"{API_PREFIX}/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url=f"{API_VERSION}/static/redoc.standalone.js",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
