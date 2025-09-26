#!/usr/bin/env python3
"""
Advanced Rate Limiter Middleware
Provides enterprise-grade API protection with multiple tiers
"""
import time
import hashlib
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AdvancedRateLimiter:
    """Multi-tier rate limiting with sliding window algorithm"""

    def __init__(self):
        # Store requests with timestamps for sliding window
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}

        # Rate limits (requests per minute)
        self.limits = {
            'health': 60,     # Health endpoint - generous
            'api': 30,        # Standard API endpoints
            'ml': 10,         # ML prediction endpoints
            'data': 20,       # Data endpoints
            'global': 100     # Global per-IP limit
        }

        # Burst protection
        self.burst_limits = {
            'health': 10,     # 10 requests per 10 seconds
            'api': 5,         # 5 requests per 10 seconds
            'ml': 2,          # 2 requests per 10 seconds
            'data': 3,        # 3 requests per 10 seconds
        }

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP with proxy support"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def get_endpoint_tier(self, path: str) -> str:
        """Classify endpoint into rate limit tier"""
        if path.startswith("/health"):
            return "health"
        elif path.startswith("/api/ml/") or "predict" in path:
            return "ml"
        elif path.startswith("/api/data/") or "stock" in path:
            return "data"
        elif path.startswith("/api/"):
            return "api"
        else:
            return "api"

    def is_blocked(self, client_ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if client_ip in self.blocked_ips:
            if time.time() < self.blocked_ips[client_ip]:
                return True
            else:
                del self.blocked_ips[client_ip]
        return False

    def block_ip(self, client_ip: str, duration: int = 300):
        """Block IP for specified duration (default 5 minutes)"""
        self.blocked_ips[client_ip] = time.time() + duration
        logger.warning(f"IP {client_ip} blocked for {duration} seconds due to rate limit violation")

    def check_rate_limit(self, request: Request) -> Tuple[bool, Dict]:
        """Check if request is within rate limits"""
        client_ip = self.get_client_ip(request)
        endpoint_tier = self.get_endpoint_tier(request.url.path)
        current_time = time.time()

        # Check if IP is blocked
        if self.is_blocked(client_ip):
            return False, {
                "error": "IP temporarily blocked",
                "retry_after": int(self.blocked_ips[client_ip] - current_time),
                "reason": "Rate limit violation"
            }

        key = f"{client_ip}:{endpoint_tier}"

        # Clean old requests (older than 1 minute)
        while self.requests[key] and current_time - self.requests[key][0] > 60:
            self.requests[key].popleft()

        # Check 1-minute rate limit
        requests_in_minute = len(self.requests[key])
        minute_limit = self.limits[endpoint_tier]

        if requests_in_minute >= minute_limit:
            # Block IP for repeated violations
            if requests_in_minute >= minute_limit * 2:
                self.block_ip(client_ip)

            return False, {
                "error": "Rate limit exceeded",
                "limit": minute_limit,
                "window": 60,
                "retry_after": 60 - int(current_time - self.requests[key][0]) if self.requests[key] else 60,
                "tier": endpoint_tier
            }

        # Check burst protection (10-second window)
        burst_requests = sum(1 for t in self.requests[key] if current_time - t <= 10)
        burst_limit = self.burst_limits.get(endpoint_tier, 5)

        if burst_requests >= burst_limit:
            return False, {
                "error": "Burst rate limit exceeded",
                "burst_limit": burst_limit,
                "window": 10,
                "retry_after": 10,
                "tier": endpoint_tier
            }

        # Check global IP limit
        global_key = f"{client_ip}:global"
        while self.requests[global_key] and current_time - self.requests[global_key][0] > 60:
            self.requests[global_key].popleft()

        global_requests = len(self.requests[global_key])
        if global_requests >= self.limits['global']:
            self.block_ip(client_ip, 600)  # 10-minute block for global limit
            return False, {
                "error": "Global rate limit exceeded",
                "limit": self.limits['global'],
                "retry_after": 600,
                "reason": "IP blocked for excessive requests"
            }

        # Add request to tracking
        self.requests[key].append(current_time)
        self.requests[global_key].append(current_time)

        return True, {
            "allowed": True,
            "tier": endpoint_tier,
            "remaining": minute_limit - requests_in_minute - 1,
            "reset": int(current_time + (60 - (current_time - self.requests[key][0])) if self.requests[key] else 60)
        }

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    # Skip rate limiting for local development
    client_ip = rate_limiter.get_client_ip(request)
    if client_ip in ["127.0.0.1", "localhost", "::1"]:
        response = await call_next(request)
        response.headers["X-RateLimit-Skip"] = "development"
        return response

    # Check rate limit
    allowed, info = rate_limiter.check_rate_limit(request)

    if not allowed:
        # Return rate limit error
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "error": info.get("error"),
                "retry_after": info.get("retry_after", 60),
                "tier": info.get("tier"),
                "timestamp": int(time.time())
            },
            headers={
                "Retry-After": str(info.get("retry_after", 60)),
                "X-RateLimit-Limit": str(info.get("limit", 30)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + info.get("retry_after", 60))
            }
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Tier"] = info.get("tier", "api")
    response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
    response.headers["X-RateLimit-Reset"] = str(info.get("reset", int(time.time()) + 60))
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.limits.get(info.get("tier"), 30))

    return response