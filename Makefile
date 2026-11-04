.PHONY: install run run-claude

install:
	python -m pip install -r requirements.txt

run:
	python -m app.main --storyboard examples/storyboard.example.json --dry-run

run-claude:
	python -m app.main --prompt "A playful 3D animation explaining how a wellness brand helps people build a morning routine" --platforms instagram,tiktok,youtube_shorts --dry-run
