import httpx
from config import load_config


def handle_scores(command: str) -> str:
    """Handle /scores command - shows per-task pass rates for a lab."""
    parts = command.split()
    
    if len(parts) < 2:
        return "Usage: /scores <lab>\nExample: /scores lab-04"
    
    lab = parts[1].lower()
    
    # Normalize lab ID (e.g., "4" -> "lab-04", "lab4" -> "lab-04")
    if lab.startswith("lab"):
        import re
        match = re.search(r"(\d+)", lab)
        if match:
            num = int(match.group(1))
            lab = f"lab-{num:02d}"
    else:
        # If just a number, assume lab-XX format
        try:
            num = int(lab)
            lab = f"lab-{num:02d}"
        except ValueError:
            pass
    
    config = load_config()
    
    if not config.lms_api_base_url or not config.lms_api_key:
        return "Configuration error: LMS_API_BASE_URL or LMS_API_KEY not set"
    
    try:
        response = httpx.get(
            f"{config.lms_api_base_url}/analytics/pass-rates",
            params={"lab": lab},
            headers={"Authorization": f"Bearer {config.lms_api_key}"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return f"No data available for {lab}"
        
        # Format the response
        lines = [f"Pass rates for {lab}:"]
        for task in data:
            task_name = task.get("task_name", task.get("task_id", "Unknown"))
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            percentage = f"{avg_score:.1f}%" if avg_score is not None else "N/A"
            lines.append(f"- {task_name}: {percentage} ({attempts} attempts)")
        
        return "\n".join(lines)
    except httpx.ConnectError:
        return f"Backend error: connection refused ({config.lms_api_base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab '{lab}' not found. Use /labs to see available labs."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"Backend error: {str(e)}"
