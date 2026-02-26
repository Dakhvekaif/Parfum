"""
Auth throttle for rate-limiting login/register endpoints.
"""

from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Strict throttle for auth endpoints: 5 requests/minute."""
    scope = "auth"
