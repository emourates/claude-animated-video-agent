from pathlib import Path
from typing import Any

from app.config import settings
from app.platforms.base import PlatformPoster


class InstagramPoster(PlatformPoster):
    platform = "instagram"

    def upload(self, video_path: Path, caption: str, title: str) -> Any:
        if not settings.INSTAGRAM_ACCESS_TOKEN and not (settings.INSTAGRAM_USERNAME and settings.INSTAGRAM_PASSWORD):
            raise RuntimeError("Instagram credentials missing. Add them to .env before posting.")

        return {
            "platform": self.platform,
            "status": "queued",
            "video_path": str(video_path),
            "title": title,
            "caption": caption,
            "message": "Instagram upload flow is scaffolded; replace with a real API client for production.",
        }
