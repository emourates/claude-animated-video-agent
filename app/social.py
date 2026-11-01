from __future__ import annotations

from pathlib import Path

from app.platforms.instagram import InstagramPoster
from app.platforms.tiktok import TikTokPoster
from app.platforms.youtube_shorts import YouTubeShortsPoster
from app.platforms.base import DryRunPoster


def build_poster(platform: str):
    normalized = platform.strip().lower().replace("-", "_")

    if normalized == "instagram":
        return InstagramPoster()
    if normalized == "tiktok":
        return TikTokPoster()
    if normalized == "youtube_shorts" or normalized == "youtube":
        return YouTubeShortsPoster()
    raise ValueError(f"Unsupported platform: {platform}")


def post_video(platform: str, video_path: Path, caption: str, title: str):
    try:
        poster = build_poster(platform)
    except ValueError:
        poster = DryRunPoster()
    return poster.upload(video_path, caption, title)
