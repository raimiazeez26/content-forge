import os
import re
import subprocess
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from contentforge_pillow_renderer_sidecar import render_image

app = FastAPI(title="ContentForge Renderer API")

def safe_slug(value: str, default: str = "content") -> str:
    value = str(value or default).strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or default

def make_filename(prefix: str, category: str, ext: str) -> str:
    prefix = safe_slug(prefix, "cf").upper()
    category = safe_slug(category, "content")
    return f"{prefix}-{category}-backup.{ext}"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/render/image")
def render_image_endpoint(payload: dict):
    try:
        png_bytes = render_image(payload)
        filename = make_filename(payload.get("filename_prefix", "CF"), payload.get("category", "content"), "png")
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"X-ContentForge-Filename": filename},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image render failed: {e}")

@app.post("/render/video")
def render_video_endpoint(payload: dict):
    try:
        video_seconds = int(payload.get("video_seconds", 8))
        if video_seconds < 1:
            video_seconds = 1

        filename = make_filename(payload.get("filename_prefix", "CF"), payload.get("category", "content"), "mp4")

        with tempfile.TemporaryDirectory(prefix="contentforge_") as tmpdir:
            poster_path = os.path.join(tmpdir, "poster.png")
            video_path = os.path.join(tmpdir, "video.mp4")

            with open(poster_path, "wb") as f:
                f.write(render_image(payload))

            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", poster_path,
                "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-r", "30",
                "-t", str(video_seconds),
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                video_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "ffmpeg failed")

            with open(video_path, "rb") as f:
                video_bytes = f.read()

        return Response(
            content=video_bytes,
            media_type="video/mp4",
            headers={"X-ContentForge-Filename": filename},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video render failed: {e}")
