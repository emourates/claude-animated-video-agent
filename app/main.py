import argparse
import json
from pathlib import Path

from app.claude_client import generate_storyboard, load_storyboard
from app.config import settings
from app.renderer import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, render_storyboard
from app.social import post_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an animated video and post it to social platforms.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="Prompt for the AI-generated short video concept.")
    source.add_argument("--storyboard", type=Path, help="Use a hand-written storyboard JSON instead of Claude.")
    parser.add_argument("--media-dir", type=Path, help="Folder with raw images and clips used by the scenes.")
    parser.add_argument("--music", type=Path, help="Optional audio track laid under the video.")
    parser.add_argument(
        "--platforms",
        default="instagram,tiktok,youtube_shorts",
        help="Comma-separated platforms: instagram,tiktok,youtube_shorts",
    )
    parser.add_argument("--dry-run", action="store_true", help="Render locally without attempting social uploads.")
    return parser.parse_args()


def list_media(media_dir: Path | None) -> list[str]:
    if media_dir is None:
        return []
    if not media_dir.is_dir():
        raise NotADirectoryError(f"--media-dir is not a folder: {media_dir}")
    allowed = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    return sorted(p.name for p in media_dir.iterdir() if p.is_file() and p.suffix.lower() in allowed)


def main() -> None:
    args = parse_args()

    if args.storyboard:
        storyboard = load_storyboard(args.storyboard)
        media_dir = args.media_dir or args.storyboard.parent
    else:
        media_dir = args.media_dir
        storyboard = generate_storyboard(args.prompt, list_media(media_dir))

    output_dir = settings.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    video_path = render_storyboard(storyboard, output_dir, media_dir=media_dir, music=args.music)
    (video_path.with_suffix(".json")).write_text(json.dumps(storyboard, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Rendered video: {video_path}")
    print(f"Title: {storyboard.get('title')}")
    print(f"Caption: {storyboard.get('caption')}")
    print(f"Hashtags: {storyboard.get('hashtags')}")

    if args.dry_run:
        print("Dry run enabled. Not posting to any platform.")
        return

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    caption = " ".join([storyboard.get("caption", "")] + list(storyboard.get("hashtags", []))).strip()
    for p in platforms:
        try:
            result = post_video(p, video_path, caption, storyboard.get("title", "AI Short"))
            print(f"[{p}] {json.dumps(result, indent=2)}")
        except Exception as exc:
            print(f"[{p}] Failed: {exc}")


if __name__ == "__main__":
    main()
