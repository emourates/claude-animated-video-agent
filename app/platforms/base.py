from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class PlatformPoster(ABC):
    platform: str = "base"

    @abstractmethod
    def upload(self, video_path: Path, caption: str, title: str) -> Any:
        raise NotImplementedError


class DryRunPoster(PlatformPoster):
    platform = "dry_run"

    def upload(self, video_path: Path, caption: str, title: str) -> dict:
        return {
            "platform": self.platform,
            "status": "dry_run",
            "video_path": str(video_path),
            "title": title,
            "caption": caption,
            "message": "No upload executed because platform credentials were not configured.",
        }
