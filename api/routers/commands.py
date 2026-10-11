"""
CareerOS API: REST Command Control Channel Router
==================================================
Provides HTTP JSON endpoints to discover and dispatch all unified CareerOS commands.

Endpoints:
- GET /api/commands: List available commands, descriptions, and parameter schemas.
- POST /api/commands: Dispatch a command with arbitrary payload.
- POST /api/commands/{name}: Dispatch a specific command by name.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field

from engine.commands.registry import CommandRegistry, execute_command

router = APIRouter(prefix="/api/commands", tags=["Command Control Channel"])


class CommandDispatchPayload(BaseModel):
    command: Optional[str] = Field(None, description="Command name if invoking via generic POST /api/commands")
    args: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of keyword arguments for the command")


@router.get("", summary="List available CareerOS commands")
@router.get("/", summary="List available CareerOS commands")
async def list_available_commands():
    """Returns schemas, parameter requirements, and descriptors for all registered CareerOS commands."""
    res = execute_command("list_commands")
    return res


@router.post("", summary="Dispatch a generic CareerOS command")
async def dispatch_generic_command(payload: CommandDispatchPayload):
    """Executes a command by name with provided arguments dictionary."""
    if not payload.command:
        raise HTTPException(status_code=400, detail="Missing required 'command' field in payload.")

    res = execute_command(payload.command, **payload.args)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res)
    return res


@router.post("/{command_name}", summary="Dispatch a specific CareerOS command by path")
async def dispatch_command_by_name(
    command_name: str = Path(..., description="Name of the registered command to execute"),
    args: Dict[str, Any] = Body(default_factory=dict, description="Keyword arguments for the command")
):
    """Executes a specific named CareerOS command."""
    res = execute_command(command_name, **args)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res)
    return res
