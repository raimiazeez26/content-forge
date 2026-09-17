# Content Forge — Technical README

[Back to the project overview](README.md)

Content Forge provides a local rendering service for vertical social media content,
plus a Docker Compose environment for n8n automation. It renders branded text
posters with Pillow and converts them into short, silent MP4 videos with FFmpeg.

## Project status

This repository contains the working renderer source, Docker setup, a standalone
image-rendering CLI, and the ContentForge AI test prompt pack. **n8n workflow JSON
exports are not yet included.** The prompt pack describes inputs for an external
Batch Controller workflow; it is not a runnable workflow or an input schema for
the renderer API. AI generation, Google Drive uploads, batch orchestration, and
registry updates require those additional workflows and credentials.

## Quick start

Install Docker Desktop (or Docker Engine with Compose), then:

```sh
git clone https://github.com/raimiazeez26/content-forge.git
cd content-forge
cp .env.example .env
docker compose up -d --build contentforge-renderer
```

On Windows PowerShell, use `Copy-Item .env.example .env` in place of `cp`.
The renderer needs no API keys. Check [health](http://localhost:8000/health) or
open the [interactive API documentation](http://localhost:8000/docs).

Render the sample image or video (use `curl.exe` in Windows PowerShell):

```sh
curl --fail -X POST http://localhost:8000/render/image -H "Content-Type: application/json" --data-binary @examples/render-payload.json --output sample.png
curl --fail -X POST http://localhost:8000/render/video -H "Content-Type: application/json" --data-binary @examples/render-payload.json --output sample.mp4
```

## API

| Method | Path | Response |
| --- | --- | --- |
| GET | `/health` | `{"status":"ok"}` |
| POST | `/render/image` | 1080 x 1920 PNG |
| POST | `/render/video` | 720 x 1280 MP4 at 30 fps, with no audio |

Both render endpoints accept a JSON object:

| Field | Purpose | Default |
| --- | --- | --- |
| `title` | Heading | Empty string |
| `main_text` | Main poster text | Empty string |
| `brand_handle` | Footer branding | `@YOURPAGE` |
| `category` | Category label and filename component | `CONTENT` image label / `content` filename |
| `filename_prefix` | Filename prefix | `CF` |
| `video_seconds` | Integer video duration, minimum 1 second | `8` |

Responses include `X-ContentForge-Filename` with a suggested filename such as
`CF-motivation-backup.png`. Repeated renders can have the same filename; callers
should add unique identifiers when storing batches. Videos display a static
poster for the requested duration. The layout is fixed at 9:16; keep headings,
body copy, and handles short enough to fit. Prompt-pack fields such as
`visual_style`, `quantity`, and `aspect_ratio` do not control this fallback renderer.

## Run with n8n

Before starting the full stack, edit `.env` and replace both secret placeholders
with different long random values. Retain the encryption key across restarts so
n8n can continue decrypting stored credentials.

```sh
docker compose up -d --build
```

Open [n8n](http://localhost:5678) and complete its initial account setup. The stack
includes n8n, external Python/JavaScript task runners, and the renderer. In an n8n
HTTP Request node, POST JSON to `http://contentforge-renderer:8000/render/image`
or `/render/video` and select a file response to receive the binary output.
See [workflow status](workflows/README.md) before attempting batch automation.

n8n data persists in a Compose-managed Docker volume; `local-files/` is mounted
at `/files` inside n8n. Generated files and `.env` are excluded from Git. If another
local stack uses ports 5678 or 8000, change `N8N_PORT` or `RENDERER_PORT` in `.env`.
The internal renderer URL remains unchanged.

```sh
docker compose logs -f contentforge-renderer
docker compose down
```

`docker compose down` preserves the data volume; adding `-v` deletes it.

## Run without Docker

Use Python 3.12 and install the dependencies in a virtual environment:

```sh
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements_renderer.txt
uvicorn contentforge_renderer_api_sidecar:app --host 127.0.0.1 --port 8000
```

Video rendering also requires `ffmpeg` on PATH. The Docker image installs FFmpeg
and DejaVu/Liberation fonts; native font fallback may change the appearance.
For the standalone image CLI, pass UTF-8 JSON encoded as Base64:

```sh
python contentforge_pillow_renderer.py --payload-b64 YOUR_BASE64_JSON --output output/poster.png
```

The CLI writes a PNG and prints JSON describing the resulting file.

## Files

- `contentforge_renderer_api_sidecar.py`: FastAPI image/video endpoints.
- `contentforge_pillow_renderer_sidecar.py`: in-memory PNG rendering for the API.
- `contentforge_pillow_renderer.py`: standalone PNG CLI.
- `Dockerfile.renderer`, `requirements_renderer.txt`: renderer runtime.
- `compose.yaml`, `.env.example`: local n8n and renderer setup.
- [Sample renderer payload](examples/render-payload.json).
- [ContentForge AI test prompt pack](ContentForge_AI_Test_Prompt_Pack.md).
- `workflows/`: location for future sanitized n8n exports.

## Deployment limits

The Compose ports bind to localhost. The renderer has no authentication, request
quotas, or upper bound on video duration; use it with trusted local callers.
An internet-facing deployment needs authentication, HTTPS, and resource limits.
The sample n8n cookie setting is intended for local HTTP. Keep real credentials
and private workflow data out of Git.

## Author

[Raimi Azeez](https://github.com/raimiazeez26)
