"""MCP tools for Home Assistant automation configuration (experimental)."""
import json
import os
import re
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount
import uvicorn

HA_URL = "http://supervisor/core"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
ACCESS_TOKEN = os.environ["MCP_ACCESS_TOKEN"]
mcp = FastMCP("HA Automation MCP", stateless_http=True, json_response=True, streamable_http_path="/")

async def ha(method: str, path: str, data: dict | None = None) -> Any:
    if not HA_TOKEN:
        raise RuntimeError("Home Assistant supervisor API token unavailable")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(method, HA_URL + path, headers={"Authorization": f"Bearer {HA_TOKEN}"}, json=data)
    if response.is_error:
        raise RuntimeError(f"Home Assistant API error {response.status_code}: {response.text[:300]}")
    return response.json() if response.content else {"ok": True}


def validate_id(automation_id: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", automation_id):
        raise ValueError("Invalid automation ID")


def validate_config(config: dict) -> None:
    if not isinstance(config, dict) or not config.get("alias"):
        raise ValueError("Configuration must be an object with an alias")
    if not isinstance(config.get("actions", config.get("action", [])), list):
        raise ValueError("Actions must be a list")


@mcp.tool()
async def list_automations() -> Any:
    """List automation entities and their current states."""
    states = await ha("GET", "/api/states")
    return [{"entity_id": s["entity_id"], "name": s.get("attributes", {}).get("friendly_name"), "state": s["state"]} for s in states if s["entity_id"].startswith("automation.")]


@mcp.tool()
async def get_automation(automation_id: str) -> Any:
    """Read an automation configuration by its storage ID (not entity ID)."""
    validate_id(automation_id)
    return await ha("GET", f"/api/config/automation/config/{automation_id}")


@mcp.tool()
async def create_automation(automation_id: str, config: dict) -> Any:
    """Create a new automation. Choose a unique ID. Does not overwrite existing automations."""
    validate_id(automation_id)
    validate_config(config)
    try:
        await get_automation(automation_id)
    except RuntimeError as exc:
        if "404" not in str(exc):
            raise
    else:
        raise ValueError("Automation ID already exists; use update_automation")
    return await ha("POST", f"/api/config/automation/config/{automation_id}", config)


@mcp.tool()
async def update_automation(automation_id: str, config: dict, confirm: bool = False) -> Any:
    """Replace an existing automation. Only call with confirm=true after user explicitly approves the change."""
    if not confirm:
        raise ValueError("Explicit confirmation required")
    validate_id(automation_id)
    validate_config(config)
    await get_automation(automation_id)
    return await ha("POST", f"/api/config/automation/config/{automation_id}", config)


@mcp.tool()
async def delete_automation(automation_id: str, confirm: bool = False) -> Any:
    """Delete an automation permanently. Only call with confirm=true after user explicitly approves deletion."""
    if not confirm:
        raise ValueError("Explicit confirmation required")
    validate_id(automation_id)
    await get_automation(automation_id)
    return await ha("DELETE", f"/api/config/automation/config/{automation_id}")


class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("authorization") != f"Bearer {ACCESS_TOKEN}":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


app = Starlette(routes=[Mount("/mcp", app=mcp.streamable_http_app())], lifespan=lambda app: mcp.session_manager.run())
app.add_middleware(TokenAuthMiddleware)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765, proxy_headers=False)
