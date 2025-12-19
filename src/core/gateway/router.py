"""
Route definitions for the API Gateway.
"""

from fastapi import APIRouter, Request, Response, HTTPException, Body
from fastapi.responses import JSONResponse

from common.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


def get_proxy(request: Request):
    """Get the service proxy from app state."""
    return request.app.state.proxy


# ==================== Roots Service Routes ====================

@router.api_route(
    "/roots{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Roots"],
)
async def proxy_roots(request: Request, path: str = ""):
    """Proxy requests to Roots Service."""
    proxy = get_proxy(request)
    full_path = f"/roots{path}" if path else "/roots"

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            pass

    response = await proxy.forward_request(
        service="roots",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


# ==================== Causality Service Routes ====================

@router.api_route(
    "/causality-links{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Causality"],
)
async def proxy_causality_links(request: Request, path: str = ""):
    """Proxy requests to Causality Service (links)."""
    proxy = get_proxy(request)
    full_path = f"/causality-links{path}" if path else "/causality-links"

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            pass

    response = await proxy.forward_request(
        service="causality",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/causality-summary", tags=["Causality"])
async def proxy_causality_summary(request: Request):
    """Proxy requests to Causality Service (summary)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="causality",
        method="GET",
        path="/causality-summary",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


# ==================== Epistemic Service Routes ====================

@router.api_route(
    "/annotations{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Epistemic"],
)
async def proxy_annotations(request: Request, path: str = ""):
    """Proxy requests to Epistemic Service."""
    proxy = get_proxy(request)
    full_path = f"/annotations{path}" if path else "/annotations"

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            pass

    response = await proxy.forward_request(
        service="epistemic",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.api_route(
    "/entities/{entity_id}/annotations",
    methods=["GET"],
    tags=["Epistemic"],
)
async def proxy_entity_annotations(request: Request, entity_id: str):
    """Proxy requests to Epistemic Service for entity annotations."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="epistemic",
        method="GET",
        path=f"/entities/{entity_id}/annotations",
        headers=dict(request.headers),
        params=dict(request.query_params),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


# ==================== MMO Service Routes ====================

@router.api_route(
    "/classes{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["MMO"],
)
async def proxy_mmo_classes(request: Request, path: str = ""):
    """Proxy requests to MMO Service (classes)."""
    proxy = get_proxy(request)
    full_path = f"/classes{path}" if path else "/classes"

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            pass

    response = await proxy.forward_request(
        service="mmo",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.api_route(
    "/slots{path:path}",
    methods=["GET", "POST", "DELETE"],
    tags=["MMO"],
)
async def proxy_mmo_slots(request: Request, path: str = ""):
    """Proxy requests to MMO Service (slots)."""
    proxy = get_proxy(request)
    full_path = f"/slots{path}" if path else "/slots"

    body = None
    if request.method in ["POST"]:
        try:
            body = await request.json()
        except:
            pass

    response = await proxy.forward_request(
        service="mmo",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/metrics", tags=["MMO"])
async def proxy_mmo_metrics(request: Request):
    """Proxy requests to MMO Service (metrics)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="mmo",
        method="GET",
        path="/metrics",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.post("/metrics/recalculate", tags=["MMO"])
async def proxy_mmo_metrics_recalculate(request: Request):
    """Proxy requests to MMO Service (recalculate metrics)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="mmo",
        method="POST",
        path="/metrics/recalculate",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/schema", tags=["MMO"])
async def proxy_mmo_schema(request: Request):
    """Proxy requests to MMO Service (schema)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="mmo",
        method="GET",
        path="/schema",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


# ==================== Global Service Routes ====================

@router.get("/global/stats", tags=["Global"])
async def proxy_global_stats(request: Request):
    """Proxy requests to Global Service (stats)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="global",
        method="GET",
        path="/global/stats",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/global/sample", tags=["Global"])
async def proxy_global_sample(request: Request):
    """Proxy requests to Global Service (sample)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="global",
        method="GET",
        path="/global/sample",
        headers=dict(request.headers),
        params=dict(request.query_params),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/global/summary", tags=["Global"])
async def proxy_global_summary(request: Request):
    """Proxy requests to Global Service (summary)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="global",
        method="GET",
        path="/global/summary",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


@router.get("/system/health", tags=["System"])
async def proxy_system_health(request: Request):
    """Proxy requests to Global Service (system health)."""
    proxy = get_proxy(request)
    response = await proxy.forward_request(
        service="global",
        method="GET",
        path="/system/health",
        headers=dict(request.headers),
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type="application/json",
    )


# ==================== SLM Service Routes ====================

@router.api_route(
    "/slm{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["SLM"],
)
async def proxy_slm(request: Request, path: str = ""):
    """Proxy requests to the SLM Service (AI)."""
    proxy = get_proxy(request)
    full_path = path if path else "/"

    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except Exception:
            body = None

    response = await proxy.forward_request(
        service="slm",
        method=request.method,
        path=full_path,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=body,
    )

    # Preserve upstream content-type where possible
    content_type = response.headers.get("content-type", "application/json")
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=content_type.split(";")[0],
    )
