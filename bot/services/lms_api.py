"""
LMS API client for calling backend endpoints.

All methods return dicts or lists that can be passed to the LLM.
"""

import httpx
from typing import Optional


class LmsApiClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    def get_items(self) -> list:
        """Get list of all labs and tasks."""
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list:
        """Get enrolled students and groups."""
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: Optional[str] = None) -> dict:
        """Get score distribution (4 buckets) for a lab."""
        params = {}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/scores", params=params)
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: Optional[str] = None) -> dict:
        """Get per-task average scores and attempt counts for a lab."""
        params = {}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/pass-rates", params=params)
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: Optional[str] = None) -> dict:
        """Get submissions per day for a lab."""
        params = {}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/timeline", params=params)
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: Optional[str] = None) -> list:
        """Get per-group scores and student counts for a lab."""
        params = {}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/groups", params=params)
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: Optional[str] = None, limit: int = 10) -> list:
        """Get top N learners by score for a lab."""
        params = {"limit": limit}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/top-learners", params=params)
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: Optional[str] = None) -> dict:
        """Get completion rate percentage for a lab."""
        params = {}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/completion-rate", params=params)
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger data sync from autochecker."""
        response = self._client.post("/pipeline/sync")
        response.raise_for_status()
        return response.json()
