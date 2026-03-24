"""Share-link helper utilities.

These helpers are intentionally kept free of MCP decorators and avoid importing
`..server` to prevent circular imports.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Optional


CreateShareLinkFn = Callable[..., Awaitable[dict[str, Any]]]


async def try_create_share_link(
    create_share_link: CreateShareLinkFn,
    document_id: str,
    expiration_minutes: Optional[int] = None,
    filename: Optional[str] = None,
) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """Try to create a share link.

    Returns:
        (share_link, error)
        - share_link: dict containing shareUrl/token/expiresAt (when successful)
        - error: string message (when failed)

    Notes:
        This helper never raises; callers can keep tool success=True while
        returning shareLinkError.
    """

    try:
        result = await create_share_link(
            document_id=document_id,
            expiration_minutes=expiration_minutes,
            filename=filename,
        )
        # Normalize to dict access
        return (
            {
                "shareUrl": result.get("shareUrl"),
                "token": result.get("token"),
                "expiresAt": result.get("expiresAt"),
            },
            None,
        )
    except Exception as error:  # noqa: BLE001
        return (None, str(error))
