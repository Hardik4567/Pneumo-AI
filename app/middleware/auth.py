from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token


# Paths that do NOT require a valid Bearer token
EXEMPT_PATHS = {
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",

    # Auth endpoints
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot-password",
    "/api/auth/verify-otp",
    "/api/auth/reset-password",
    "/api/auth/refresh-token",

    # Legacy paths
    "/login",
    "/api/login",
}

# Path prefixes that bypass auth entirely
EXEMPT_PREFIXES = (
    "/static/",
    "/docs",
    "/redoc",
    "/openapi",
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        # Always allow CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow static files and exempt prefixes
        for prefix in EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # Allow exact exempt paths
        if path in EXEMPT_PATHS:
            try:
                return await call_next(request)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return JSONResponse(
                    status_code=500,
                    content={"detail": str(e)}
                )

        # All other API routes require a valid Bearer token
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized — no token provided"}
            )

        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)

        if payload is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )

        # Attach decoded payload to request state
        request.state.user = payload

        try:
            return await call_next(request)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": str(e)}
            )
