import httpx
from config import load_config


def handle_health(command: str) -> str:
    """Handle /health command - checks backend status."""
    config = load_config()
    
    if not config.lms_api_base_url or not config.lms_api_key:
        return "Configuration error: LMS_API_BASE_URL or LMS_API_KEY not set"
    
    try:
        response = httpx.get(
            f"{config.lms_api_base_url}/items/",
            headers={"Authorization": f"Bearer {config.lms_api_key}"},
            timeout=10.0,
        )
        response.raise_for_status()
        items = response.json()
        count = len(items) if isinstance(items, list) else "unknown"
        return f"Backend is healthy. {count} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config.lms_api_base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.TimeoutException:
        return f"Backend error: timeout connecting to {config.lms_api_base_url}"
    except Exception as e:
        return f"Backend error: {str(e)}. Check that the services are running."
