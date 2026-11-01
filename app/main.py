import argparse
import json
from pathlib import Path

from app.claude_client import generate_storyboard
from app.config import settings
from app.renderer import render_storyboard
from app.social import post_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an animated video and post it to social platforms.")
    parser.add_argument("--prompt", required=True, help="Prompt for the AI-generated short video concept.")
    parser.add_argument(
        "--platforms",
        default="instagram,tiktok,youtube_shorts",
        help="Comma-separated platforms: instagram,tiktok,youtube_shorts",
    )
    parser.add_argument("--dry-run", action="store_true", help="Render locally without attempting social uploads.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt = args.prompt

    storyboard = generate_storyboard(prompt)
    output_dir = settings.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    video_path = render_storyboard(storyboard, output_dir)
    print(f"Rendered video: {video_path}")
    print(f"Title: {storyboard.get('title')}")
    print(f"Caption: {storyboard.get('caption')}")
    print(f"Hashtags: {storyboard.get('hashtags')}")

    if args.dry_run:
        print("Dry run enabled. Not posting to any platform.")
        return

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    for p in platforms:
        try:
            result = post_video(p, video_path, storyboard.get("caption", ""), storyboard.get("title", "AI Short"))
            print(f"[{p}] {json.dumps(result, indent=2)}")
        except Exception as exc:
            print(f"[{p}] Failed: {exc}")


if __name__ == "__main__":
    main()
