"""Render a storyboard to a vertical MP4 using ffmpeg.

Each scene can use a raw media file (image or video clip) as its background.
Scenes without media fall back to a generated animated background. Text is
drawn with Pillow into a transparent overlay and composited by ffmpeg, so no
heavy Python video stack is needed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import settings

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg was not found on PATH. Install ffmpeg to render videos.")
    return path


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [settings.FONT_PATH] if settings.FONT_PATH else []
    for candidate in candidates + _FONT_CANDIDATES:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def _hex_to_rgb(value: str, fallback: tuple) -> tuple:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", value or "")
    if not match:
        return fallback
    raw = match.group(1)
    return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))


def scene_duration(scene: Dict[str, Any]) -> float:
    """Duration in seconds; supports `duration` or legacy `start`/`end`."""
    if "duration" in scene:
        return max(0.5, float(scene["duration"]))
    return max(0.5, float(scene.get("end", 1)) - float(scene.get("start", 0)))


def _draw_text_block(
    draw: ImageDraw.ImageDraw, width: int, y: int, text: str, size: int, fill: tuple, box: tuple
) -> int:
    font = _font(size)
    chars_per_line = max(8, int((width - 160) / (size * 0.55)))
    lines = textwrap.wrap(text, width=chars_per_line) or [""]
    line_height = int(size * 1.25)
    block_height = line_height * len(lines)
    pad = int(size * 0.5)
    draw.rounded_rectangle((60, y - pad, width - 60, y + block_height + pad), radius=28, fill=box)
    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        draw.text(((width - line_width) / 2, y + i * line_height), line, font=font, fill=fill)
    return y + block_height + 2 * pad


def make_overlay(scene: Dict[str, Any], width: int, height: int, path: Path) -> Path:
    """Write a transparent PNG with the scene's headline and subline."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    accent = _hex_to_rgb(settings.BRAND_ACCENT, (245, 166, 35))
    box = (12, 18, 22, 200)

    headline = str(scene.get("text", "")).strip()
    subline = str(scene.get("subtext", "")).strip()
    position = str(scene.get("text_position", "bottom")).lower()
    y = {"top": int(height * 0.12), "center": int(height * 0.42)}.get(position, int(height * 0.68))

    if headline:
        y = _draw_text_block(draw, width, y, headline, int(width * 0.068), (255, 255, 255), box) + 24
    if subline:
        _draw_text_block(draw, width, y, subline, int(width * 0.045), accent, box)

    img.save(path)
    return path


def _fallback_background(scene: Dict[str, Any], width: int, height: int, path: Path) -> Path:
    base = _hex_to_rgb(settings.BRAND_BACKGROUND, (11, 17, 20))
    img = Image.new("RGB", (width, height), base)
    draw = ImageDraw.Draw(img)
    accent = _hex_to_rgb(settings.BRAND_PRIMARY, (0, 109, 119))
    for i in range(0, 260, 26):
        r = 220 + i
        draw.ellipse(
            (width / 2 - r, height / 2 - r, width / 2 + r, height / 2 + r),
            outline=tuple(min(255, c + i // 4) for c in accent),
            width=3,
        )
    img.save(path)
    return path


def _media_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    # Uploaded files may come without an extension: ask ffprobe.
    probe = shutil.which("ffprobe")
    if probe:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=format_name", "-of", "csv=p=0", str(path)],
            capture_output=True,
            text=True,
        ).stdout
        if any(k in out for k in ("png", "jpeg", "image2", "webp")):
            return "image"
        if out.strip():
            return "video"
    raise ValueError(f"Unsupported media file: {path}")


def resolve_media(value: Optional[str], media_dir: Optional[Path]) -> Optional[Path]:
    if not value:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute() and media_dir is not None:
        candidate = media_dir / candidate
    if not candidate.exists():
        raise FileNotFoundError(f"Scene media not found: {candidate}")
    return candidate


def _render_scene(
    ffmpeg: str,
    scene: Dict[str, Any],
    media: Optional[Path],
    overlay: Path,
    out: Path,
    work: Path,
    index: int,
) -> None:
    w, h, fps = settings.DEFAULT_VIDEO_WIDTH, settings.DEFAULT_VIDEO_HEIGHT, settings.DEFAULT_FPS
    duration = scene_duration(scene)
    frames = int(round(duration * fps))
    cover = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
    # "contain": show the whole (e.g. landscape) shot on a blurred copy of itself.
    contain = (
        f"split[a][b];[a]{cover},boxblur=30:2,eq=brightness=-0.12[blur];"
        f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease,setsar=1[fit];"
        f"[blur][fit]overlay=(W-w)/2:(H-h)/2"
    )
    fit = str(scene.get("fit", "cover")).lower()
    framing = contain if fit == "contain" else cover

    if media is not None and _media_kind(media) == "video":
        # Short clips loop so they always fill the scene.
        inputs = ["-stream_loop", "-1", "-ss", str(float(scene.get("media_start", 0))), "-t", str(duration), "-i", str(media)]
        base = f"[0:v]fps={fps},{framing}[bg]"
    else:
        if media is None:
            media = _fallback_background(scene, w, h, work / f"bg_{index:02d}.png")
        inputs = ["-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", str(media)]
        zoom = float(scene.get("zoom", 0.08))
        # Slow push-in ("Ken Burns") so stills do not feel static.
        base = (
            f"[0:v]{framing},scale={w * 2}:{h * 2},"
            f"zoompan=z='1+{zoom}*on/{frames}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={w}x{h}:fps={fps},setsar=1[bg]"
        )

    fade = min(0.3, duration / 4)
    graph = (
        f"{base};[bg][1:v]overlay=0:0,"
        f"fade=t=in:st=0:d={fade},fade=t=out:st={duration - fade}:d={fade},format=yuv420p[v]"
    )
    cmd = [
        ffmpeg, "-y", "-v", "error", *inputs, "-i", str(overlay),
        "-filter_complex", graph, "-map", "[v]", "-t", str(duration), "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(fps), str(out),
    ]
    subprocess.run(cmd, check=True)


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "storyboard"


def render_storyboard(
    storyboard: Dict[str, Any],
    output_dir: Path | None = None,
    media_dir: Path | None = None,
    music: Path | None = None,
) -> Path:
    ffmpeg = _require_ffmpeg()
    output_dir = output_dir or settings.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{_slug(str(storyboard.get('title', 'storyboard')))}.mp4"

    scenes: List[Dict[str, Any]] = storyboard.get("scenes", [])
    if not scenes:
        raise ValueError("Storyboard does not include scenes")

    w, h = settings.DEFAULT_VIDEO_WIDTH, settings.DEFAULT_VIDEO_HEIGHT
    with tempfile.TemporaryDirectory(prefix="render_") as tmp:
        work = Path(tmp)
        segments = []
        for i, scene in enumerate(scenes):
            media = resolve_media(scene.get("media"), media_dir)
            overlay = make_overlay(scene, w, h, work / f"overlay_{i:02d}.png")
            seg = work / f"seg_{i:02d}.mp4"
            _render_scene(ffmpeg, scene, media, overlay, seg, work, i)
            segments.append(seg)

        concat_list = work / "concat.txt"
        concat_list.write_text("".join(f"file '{s}'\n" for s in segments))
        joined = work / "joined.mp4"
        subprocess.run(
            [ffmpeg, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(joined)],
            check=True,
        )

        if music:
            total = sum(scene_duration(s) for s in scenes)
            subprocess.run(
                [
                    ffmpeg, "-y", "-v", "error", "-i", str(joined), "-i", str(music),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-af", f"afade=t=out:st={max(0, total - 1)}:d=1", "-t", str(total),
                    "-movflags", "+faststart", str(output_path),
                ],
                check=True,
            )
        else:
            subprocess.run(
                [ffmpeg, "-y", "-v", "error", "-i", str(joined), "-c", "copy", "-movflags", "+faststart", str(output_path)],
                check=True,
            )
    return output_path


__all__ = ["render_storyboard", "make_overlay", "scene_duration", "IMAGE_EXTENSIONS", "VIDEO_EXTENSIONS"]
