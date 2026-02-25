"""
Resilience utilities: circuit breakers, retry logic, timeouts.
"""

import httpx
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

logger = structlog.get_logger()

# Circuit breakers for external services
# These prevent cascading failures by "opening" after too many failures
service_breakers = {}


def get_circuit_breaker(service_name: str, fail_max: int = 5, timeout_duration: int = 60) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a service.

    Args:
        service_name: Name of the service
        fail_max: Number of failures before opening circuit
        timeout_duration: Seconds before attempting to close circuit

    Returns:
        CircuitBreaker instance
    """
    if service_name not in service_breakers:
        service_breakers[service_name] = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=timeout_duration,
            name=service_name,
        )

    return service_breakers[service_name]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    reraise=True,
)
async def http_call_with_retry(url: str, method: str = "GET", timeout: float = 30.0, **kwargs) -> httpx.Response:
    """
    Make HTTP call with automatic retry on transient failures.

    Features:
    - Retries up to 3 times
    - Exponential backoff (4s, 8s, 10s)
    - Only retries on network errors and timeouts
    - Configurable timeout

    Args:
        url: URL to call
        method: HTTP method (GET, POST, PUT, DELETE)
        timeout: Request timeout in seconds
        **kwargs: Additional arguments for httpx

    Returns:
        HTTP response

    Raises:
        httpx.HTTPError: On HTTP errors after retries
        httpx.TimeoutException: On timeout after retries
    """
    logger.debug("http_call_attempt", url=url, method=method)

    async with httpx.AsyncClient(timeout=timeout) as client:
        if method == "GET":
            response = await client.get(url, **kwargs)
        elif method == "POST":
            response = await client.post(url, **kwargs)
        elif method == "PUT":
            response = await client.put(url, **kwargs)
        elif method == "DELETE":
            response = await client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response


async def call_service_with_breaker(service_name: str, url: str, method: str = "GET", **kwargs) -> httpx.Response:
    """
    Call external service with circuit breaker protection and retry logic.

    This combines:
    - Circuit breaker to prevent cascading failures
    - Automatic retry with exponential backoff
    - Timeout protection

    Args:
        service_name: Name of service (for circuit breaker)
        url: URL to call
        method: HTTP method
        **kwargs: Additional arguments for HTTP call

    Returns:
        HTTP response

    Raises:
        CircuitBreakerError: If circuit is open
        httpx.HTTPError: On HTTP errors after retries
    """
    breaker = get_circuit_breaker(service_name)

    @breaker
    async def protected_call():
        return await http_call_with_retry(url, method, **kwargs)

    try:
        return await protected_call()
    except Exception as e:
        logger.error("service_call_failed", service=service_name, url=url, error=str(e), error_type=type(e).__name__)
        raise


# Example usage in service methods:
"""
from app.utils.resilience import call_service_with_breaker

async def get_user_from_user_service(user_id: str):
    response = await call_service_with_breaker(
        service_name="user-service",
        url=f"{USER_SERVICE_URL}/api/v1/users/{user_id}",
        method="GET",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
"""
