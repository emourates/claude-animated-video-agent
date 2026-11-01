from pathlib import Path
from typing import Any

from app.config import settings
from app.platforms.base import PlatformPoster


class TikTokPoster(PlatformPoster):
    platform = "tiktok"

    def upload(self, video_path: Path, caption: str, title: str) -> Any:
        if not settings.TIKTOK_ACCESS_TOKEN and not (settings.TIKTOK_CLIENT_KEY and settings.TIKTOK_CLIENT_SECRET):
            raise RuntimeError("TikTok credentials missing. Add them to .env before posting.")

        return {
            "platform": self.platform,
            "status": "queued",
            "video_path": str(video_path),
            "title": title,
            "caption": caption,
            "message": "TikTok upload flow is scaffolded; replace with a real API client for production.",
        }
