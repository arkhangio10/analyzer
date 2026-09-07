"""Keep strangers from spending the operator's money.

The QC console is the part other people need: it reads stored evidence,
recomputes verdicts from stored samples, and calls no model, so it stays open.
The endpoints that reach a provider are a different thing. On a public service
with provider calls enabled, anyone holding the URL can spend the operator's
credits, and no amount of rate limiting changes that -- a limit bounds the
damage per hour and an attacker simply comes back the next hour. So these
endpoints require a token instead.

The guard is inert only when there is nothing to guard. If no token is
configured and provider calls are disabled, nothing here can spend, so the
requirement would be theatre and the endpoints stay open -- which is also what
keeps local development and the test suite working unchanged.

If provider calls are **enabled** and no token is configured, the paid
endpoints refuse rather than serve. That is the state where a deployment is
one URL away from an unbounded bill, and it is far more likely to be an
oversight than a decision. Refusing says so; quietly serving would not.
"""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from app.core.config import Settings, get_settings


SPEND_TOKEN_HEADER = "X-Aprendiz-Spend-Token"


def spend_endpoints_are_protected(settings: Settings | None = None) -> bool:
    """Report whether an unknown caller can reach an endpoint that spends."""
    settings = settings or get_settings()
    if not settings.google_genai_enabled:
        return True
    return bool(settings.spend_token)


def spend_token_is_required(settings: Settings | None = None) -> bool:
    """Report whether callers must present the token header.

    The browser cannot discover this from a failed request without first
    making one, and a paid endpoint is the wrong place to learn a header is
    missing. Reporting it says only *that* a token is configured, never what
    it is, so an unauthenticated caller learns nothing it could not learn by
    reading the 401 it would get anyway.
    """
    settings = settings or get_settings()
    return bool(settings.spend_token)


async def require_spend_authorization(
    x_aprendiz_spend_token: str | None = Header(default=None),
) -> None:
    """Refuse a request that would spend money on someone else's behalf."""
    settings = get_settings()
    expected = settings.spend_token

    if not expected:
        if settings.google_genai_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Provider calls are enabled but no spend token is "
                    "configured, so this endpoint would let any caller spend. "
                    "Set SPEND_TOKEN, or disable provider calls."
                ),
            )
        return

    provided = x_aprendiz_spend_token or ""
    # compare_digest so a wrong token cannot be discovered a character at a
    # time from how long the comparison takes.
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                f"This endpoint can spend money and requires the "
                f"{SPEND_TOKEN_HEADER} header."
            ),
            headers={"WWW-Authenticate": SPEND_TOKEN_HEADER},
        )
