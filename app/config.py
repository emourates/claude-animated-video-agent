import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output")).resolve()
    DEFAULT_VIDEO_WIDTH = int(os.getenv("DEFAULT_VIDEO_WIDTH", "1080"))
    DEFAULT_VIDEO_HEIGHT = int(os.getenv("DEFAULT_VIDEO_HEIGHT", "1920"))
    DEFAULT_FPS = int(os.getenv("DEFAULT_FPS", "24"))

    # Look of the text overlays (hex colours, optional .ttf font)
    FONT_PATH = os.getenv("FONT_PATH", "")
    BRAND_PRIMARY = os.getenv("BRAND_PRIMARY", "#006D77")
    BRAND_ACCENT = os.getenv("BRAND_ACCENT", "#F5A623")
    BRAND_BACKGROUND = os.getenv("BRAND_BACKGROUND", "#0B1114")

    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
    INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")

    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")

    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

settings = Settings()
