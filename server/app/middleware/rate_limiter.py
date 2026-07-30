import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_log = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        # Clean expired timestamps
        history = [t for t in self.requests_log.get(client_ip, []) if now - t < self.window_seconds]
        
        if len(history) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before trying again."
            )
            
        history.append(now)
        self.requests_log[client_ip] = history
        
        response = await call_next(request)
        return response
