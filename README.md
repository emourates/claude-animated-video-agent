# Claude Animated Video Generator

A starter Python project for generating short animated videos from a prompt, rendering them locally, and preparing them for publishing to Instagram Reels, TikTok, and YouTube Shorts.

## What this repo includes

- Claude-powered script + storyboard generation via Anthropic API
- Local MP4 rendering with Python + PIL + moviepy
- Platform adapters for Instagram, TikTok, and YouTube Shorts
- Environment-based configuration for API keys and credentials
- A clean CLI you can extend for production automation

## Project structure

```text
.
├── README.md
├── requirements.txt
├── .env.example
├── Makefile
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── claude_client.py
│   ├── renderer.py
│   ├── social.py
│   ├── main.py
│   └── platforms/
│       ├── __init__.py
│       ├── base.py
│       ├── instagram.py
│       ├── tiktok.py
│       └── youtube_shorts.py
└── output/
```

## Quick start

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy the example environment file and add credentials

```bash
cp .env.example .env
```

4. Run the app

```bash
python -m app.main --prompt "A stylish 3D animated explainer about a coffee startup launching a sustainable capsule system" --platforms instagram,tiktok,youtube_shorts
```

This will:

- Ask Claude to generate a storyboard and caption
- Render a short MP4 locally
- Attempt to publish the video to the requested platforms
- Save output in `output/`

## Environment variables

See `.env.example` for required settings. At minimum, you need:

```bash
ANTHROPIC_API_KEY=your_key_here
```

For social posting, add the platform-specific credentials you need.

## Notes

- This repo is intentionally modular so you can replace the sample renderer with a real generative video pipeline if needed.
- Social posting integrations may require OAuth or app credentials and are scaffolded for extension.
- The default renderer creates a simple animated text-based short video suitable for prototyping.

## Production ideas

- Swap the renderer for a diffusion/video model pipeline
- Add voiceover generation via TTS
- Add automatic subtitles and captions
- Add scheduling and queue management
- Add versioning for campaign JSON and output metadata

## License

MIT
