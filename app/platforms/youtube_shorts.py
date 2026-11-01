from pathlib import Path
from typing import Any

from app.config import settings
from app.platforms.base import PlatformPoster


class YouTubeShortsPoster(PlatformPoster):
    platform = "youtube_shorts"

    def upload(self, video_path: Path, caption: str, title: str) -> Any:
        if not settings.YOUTUBE_CLIENT_ID or not settings.YOUTUBE_CLIENT_SECRET or not settings.YOUTUBE_REFRESH_TOKEN:
            raise RuntimeError("YouTube credentials missing. Add them to .env before posting.")

        return {
            "platform": self.platform,
            "status": "queued",
            "video_path": str(video_path),
            "title": title,
            "caption": caption,
            "message": "YouTube upload flow is scaffolded; replace with a real API client for production.",
        }
