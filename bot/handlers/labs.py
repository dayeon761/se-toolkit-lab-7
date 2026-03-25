import httpx
from config import load_config


def handle_labs(command: str) -> str:
    """Handle /labs command - lists available labs."""
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
        
        if not items:
            return "No labs available in the system."
        
        # Group items by type (lab vs task)
        labs = []
        for item in items:
            if item.get("type") == "lab":
                labs.append(item)
        
        if not labs:
            # If no labs found, show all items
            return "Available items:\n" + "\n".join(
                f"- {item.get('name', item.get('id', 'Unknown'))}" 
                for item in items[:20]
            )
        
        return "Available labs:\n" + "\n".join(
            f"- {lab.get('name', lab.get('id', 'Unknown'))}" 
            for lab in labs
        )
    except httpx.ConnectError:
        return f"Backend error: connection refused ({config.lms_api_base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"Backend error: {str(e)}"

