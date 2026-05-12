"""
GitHub capturer — extrae actividad de webhook GitHub Push events.

Sprint: ROTOR-001 (T2.1)
Trigger: POST a kernel.embrion_routes:/webhooks/github_push
"""

from __future__ import annotations

from typing import Any, Mapping

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource


class GitHubCapturer(BaseCapturer):
    """Captura un push event de GitHub y produce 1 RotorActivity por commit."""

    SOURCE: str = RotorSource.GITHUB_COMMIT.value
    DEFAULT_ACTOR: str = "github"

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (subset de GitHub Push webhook payload):
          {
            "repo": "alfredogl1804/el-monstruo",
            "ref": "refs/heads/main",
            "sha": "abc123...",
            "actor": "alfredogl1804",
            "merged_to_main": True,
            "files_changed": 5
          }
        """
        sha = str(raw_event.get("sha", ""))[:40]
        ref = str(raw_event.get("ref", ""))
        merged_to_main = bool(raw_event.get("merged_to_main", False))
        # Si ref es main y no fue declarado merged_to_main explícitamente, inferirlo
        if not merged_to_main and ref.endswith("/main"):
            merged_to_main = True

        actor = str(raw_event.get("actor", self.DEFAULT_ACTOR))

        payload = {
            "repo": str(raw_event.get("repo", "")),
            "sha": sha,
            "ref": ref,
            "merged_to_main": merged_to_main,
            "files_changed": int(raw_event.get("files_changed", 0)),
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["GitHubCapturer"]
