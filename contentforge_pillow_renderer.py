#!/usr/bin/env python3
import argparse
import base64
import io
import json
import os
import sys
import textwrap
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920

def load_font(size, bold=False):
    candidates = []
    if os.name == "nt":
        candidates += [
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

def fit_text(draw, text, max_width, start_size, min_size=28, bold=True):
    size = start_size
    while size >= min_size:
        font = load_font(size, bold=bold)
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            box = draw.textbbox((0, 0), test, font=font)
            if (box[2] - box[0]) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        line_height = int(size * 1.25)
        total_h = len(lines) * line_height
        if len(lines) <= 6 and total_h <= 760:
            return font, lines, line_height
        size -= 4
    font = load_font(min_size, bold=bold)
    return font, textwrap.wrap(text, width=28), int(min_size * 1.25)

def make_gradient():
    img = Image.new("RGB", (W, H), (15, 18, 28))
    px = img.load()
    for y in range(H):
        t = y / max(1, H - 1)
        r = int(14 + 34 * t)
        g = int(17 + 21 * t)
        b = int(28 + 38 * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return img

def draw_soft_shapes(img):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.ellipse((-220, 1080, 540, 1840), fill=(255, 255, 255, 18))
    d.ellipse((680, -160, 1320, 520), fill=(255, 255, 255, 14))
    d.rounded_rectangle((120, 250, 960, 300), radius=25, fill=(255,255,255,12))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def render(payload, out_path):
    title = str(payload.get("title", "")).strip()
    main_text = str(payload.get("main_text", "")).strip()
    handle = str(payload.get("brand_handle", "@YOURPAGE")).strip()
    category = str(payload.get("category", "content")).strip().upper()

    img = draw_soft_shapes(make_gradient())
    draw = ImageDraw.Draw(img)

    margin_x = 100
    safe_width = W - margin_x * 2

    # Category kicker
    kicker_font = load_font(32, bold=True)
    draw.text((margin_x, 170), category, font=kicker_font, fill=(205, 210, 220))

    # Title
    title_font = load_font(68, bold=True)
    draw.text((margin_x, 310), title.upper(), font=title_font, fill=(255,255,255))

    # Accent line
    draw.rounded_rectangle((margin_x, 430, margin_x + 150, 442), radius=6, fill=(235,235,235))

    # Main text
    quote_font, lines, line_h = fit_text(draw, main_text, safe_width, 92, 44, True)
    block_h = len(lines) * line_h
    start_y = max(610, int((H - block_h) / 2) - 30)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=quote_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = start_y + i * line_h
        # subtle shadow
        draw.text((x+3, y+4), line, font=quote_font, fill=(0,0,0,120))
        draw.text((x, y), line, font=quote_font, fill=(255,255,255))

    # Footer safely above bottom
    footer_y = H - 230
    draw.rounded_rectangle((margin_x, footer_y-45, W-margin_x, footer_y+70), radius=28, fill=(255,255,255,18))
    footer_font = load_font(34, bold=True)
    draw.text((margin_x+35, footer_y-5), handle, font=footer_font, fill=(235,235,240))

    # Small label
    small_font = load_font(26, bold=False)
    label = "CONTENTFORGE • FALLBACK RENDER"
    bbox = draw.textbbox((0,0), label, font=small_font)
    draw.text((W-margin_x-(bbox[2]-bbox[0]), footer_y+5), label, font=small_font, fill=(170,175,185))

    img.save(out_path, "PNG", optimize=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--payload-b64", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    payload = json.loads(base64.b64decode(args.payload_b64).decode("utf-8"))
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    render(payload, args.output)

    result = {
        "success": True,
        "output_path": os.path.abspath(args.output),
        "filename": os.path.basename(args.output),
        "mime_type": "image/png"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
