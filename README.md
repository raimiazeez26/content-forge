# Content Forge — Social Media Content Rendering System

A social media content rendering system built with Python, Pillow, FastAPI, FFmpeg and a local n8n environment.

The renderer transforms prepared text into branded vertical images and short, silent videos, providing a reusable rendering step for content automation workflows.

For API details, configuration and runtime commands, see the [Technical README](TECHNICAL_README.md).

## Demo

**Open Form Here:**

[![Test Workflow](https://img.shields.io/badge/TEST%20WORKFLOW-Open%20Demo-brightgreen?style=for-the-badge)](https://n8n-rai-ff11f30e81fc.herokuapp.com/form/334b03da-92b2-4cc6-bc96-5c0da6c9eec7)
> This is a demonstration environment. Submit fictional information only. Do not enter confidential, financial, identity or personal data.

Run the renderer locally using the installation steps below, then try the [sample content payload](examples/render-payload.json) through the [interactive API documentation](http://localhost:8000/docs).

## Project Overview

Preparing social media content often involves repetitive work:

* Applying a consistent visual layout
* Adding headings, content and branding
* Exporting images in a vertical format
* Converting posters into short videos
* Connecting rendering tools to automation workflows

Content Forge packages those rendering steps into a local HTTP service and a standalone image-rendering script.

The repository also includes a ContentForge AI test prompt pack for a broader batch content workflow. **The n8n workflow JSON exports are not yet included.** AI content generation, Drive uploads and batch tracking require those additional workflows and credentials.

## Business Objective

The objective is to reduce repeated design and export work while maintaining a consistent format for social media content.

One prepared content payload can produce a branded image or a video version of the same poster.

## Main Features

* Branded vertical poster rendering
* Category, title, main text and handle placement
* Automatic wrapping and font sizing for the main text
* 1080 × 1920 PNG output
* 720 × 1280 MP4 output at 30 frames per second
* Configurable video duration
* HTTP endpoints for image and video rendering
* Suggested output filenames in response headers
* Standalone Python image-rendering CLI
* Docker-based renderer setup
* Local n8n and external task-runner environment
* Sample renderer payload
* Fifteen batch-workflow test prompts

## Workflow Summary

The included rendering service follows this flow:

```text
Prepared content payload
          ↓
Submit an HTTP request
          ↓
Render a branded vertical poster
          ↓
     Requested output
       ┌──┴───┐
       │      │
     Image   Video
       │      │
       │   Convert poster with FFmpeg
       │      │
       ↓      ↓
   PNG file  Silent MP4 file
```

An n8n HTTP Request node can call the renderer and receive the output as a file. Batch orchestration and subsequent storage depend on workflows supplied separately.

## Technology Stack

| Component | Technology |
| --- | --- |
| Workflow environment | n8n |
| Rendering logic | Python |
| Image creation | Pillow |
| HTTP API | FastAPI and Uvicorn |
| Video creation | FFmpeg |
| Containerisation | Docker and Docker Compose |
| External workflow execution | n8n task runners |
| Version control | Git and GitHub |

## Workflow Components

### Image Renderer

The image renderer:

1. Reads the supplied category, title, main text and brand handle.
2. Creates a vertical gradient background.
3. Positions the title and category label.
4. Wraps and sizes the main text.
5. Adds the branding footer.
6. Returns a PNG image.

### Video Renderer

The video renderer:

1. Creates a poster using the image renderer.
2. Uses FFmpeg to display the poster for the requested duration.
3. Scales the output to 720 × 1280.
4. Returns a silent MP4 video.

### Standalone Image CLI

The Python CLI accepts a Base64-encoded JSON payload, saves a PNG and returns file metadata as JSON. It can run independently of n8n and the HTTP API.

### Batch Controller Integration

The [test prompt pack](ContentForge_AI_Test_Prompt_Pack.md) describes requests for Workflow 07 — Batch Controller, including content categories, quantities and destination folder placeholders.

That workflow is not included in this repository. See [workflow availability](workflows/README.md) before using the batch prompts.

## Content Input Structure

A renderer request contains prepared text:

```json
{
  "title": "Keep Going",
  "main_text": "Small steps every day build lasting progress.",
  "brand_handle": "@YOURPAGE",
  "category": "motivation",
  "filename_prefix": "CF",
  "video_seconds": 8
}
```

The renderer uses this text directly. Batch prompt fields such as audience, tone, visual style and quantity belong to the broader content workflow and do not generate content through this API.

## Output Filename Format

Suggested filenames follow this structure:

```text
PREFIX-category-backup.png
PREFIX-category-backup.mp4
```

Example:

```text
CF-motivation-backup.png
```

The API returns the suggested name in the `X-ContentForge-Filename` header. Callers should add a unique identifier when saving batches because repeated requests can produce the same suggested filename.

## Repository Structure

```text
.
├── README.md
├── TECHNICAL_README.md
├── .gitignore
├── .dockerignore
├── .gitattributes
├── .env.example
├── compose.yaml
├── Dockerfile.renderer
├── requirements_renderer.txt
├── contentforge_renderer_api_sidecar.py
├── contentforge_pillow_renderer_sidecar.py
├── contentforge_pillow_renderer.py
├── ContentForge_AI_Test_Prompt_Pack.md
├── examples/
│   └── render-payload.json
├── local-files/
│   └── .gitkeep
└── workflows/
    └── README.md
```

## Prerequisites

You need:

* Docker Desktop, or Docker Engine with Docker Compose
* Available local ports for the renderer and optional n8n service
* Prepared text for your content

Running the renderer without Docker requires Python dependencies and, for video output, FFmpeg. See the [Technical README](TECHNICAL_README.md#run-without-docker).

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/raimiazeez26/content-forge.git
cd content-forge
```

### 2. Create the environment file

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`. Before starting n8n, replace the encryption-key and runner-token placeholders with different long random values.

### 3. Start the renderer

```bash
docker compose up -d --build contentforge-renderer
```

### 4. Open the local API

Visit the [interactive API documentation](http://localhost:8000/docs). Select `/render/image`, click **Try it out**, and submit the [sample payload](examples/render-payload.json).

### 5. Start n8n if required

```bash
docker compose up -d --build
```

Open [n8n](http://localhost:5678) and complete its initial account setup. Within this Compose network, use `http://contentforge-renderer:8000` for renderer requests.

See the [Technical README](TECHNICAL_README.md) for endpoint examples, file responses, persistence and operating commands.

## Testing

Checks completed when the repository was prepared:

* Python source syntax validation
* In-memory PNG rendering at 1080 × 1920
* Standalone CLI PNG rendering
* JSON validation for all fifteen test prompt examples
* Docker Compose configuration validation

HTTP endpoint execution and video rendering were not verified in that environment because FastAPI was unavailable locally and Docker was stopped.

For a local smoke test, submit the sample payload to both render endpoints and confirm that the image, branding and video duration match the request. The batch prompt pack provides additional scenarios for use once the missing workflows are supplied.

## Security

* Keep `.env`, credentials and private content outside Git.
* Replace the sample n8n secret placeholders before starting the full stack.
* Keep the n8n encryption key stable so stored credentials remain readable.
* Use the renderer with trusted local callers; it has no built-in authentication.
* Add authentication, HTTPS and resource limits before exposing the renderer publicly.
* Review n8n exports for credentials and private execution data before publishing them.

## Limitations

* n8n workflow exports are not included.
* The renderer does not generate AI text or imagery, upload files to Drive or maintain a content registry.
* Output uses a fixed 9:16 layout.
* Videos show a static poster and contain no audio.
* Long headings, handles or unbroken text can exceed the layout.
* Suggested output filenames are not unique.
* Video duration has a minimum of one second but no configured upper limit.
* Native font availability can change the rendered appearance.

## Future Improvements

Potential enhancements include:

* Sanitized n8n workflow exports
* AI content generation integration
* Batch orchestration and unique output identifiers
* Google Drive delivery and content tracking
* Additional layouts and aspect ratios
* Animated video templates and audio support
* Stronger payload validation and resource limits
* Automated HTTP and video integration tests

## Business Value

Content Forge demonstrates how a reusable rendering service can reduce repeated formatting and export work. Content teams can prepare text once and connect image or video rendering to their automation tools.

Potential applications include:

* Social media content operations
* Marketing agencies
* Creator content libraries
* Branded quote and announcement posts
* Educational content workflows
* Automated content prototypes

## Author

**Raimi Azeez Babatunde**

Data Scientist, Python Developer and AI Automation Engineer.

Specialising in:

* n8n automation
* Python development
* Data analysis
* AI-assisted workflows
* API integration
* Business reporting
* Financial and operational automation

## Contact

* Upwork: [Raimi Azeez](https://www.upwork.com/freelancers/raimiazeez?mp_source=share)
* GitHub: [raimiazeez26](https://github.com/raimiazeez26)
* LinkedIn: [Raimi Azeez](https://www.linkedin.com/in/raimi-azeez/)
* Email: [raimiazeez26@gmail.com](mailto:raimiazeez26@gmail.com)
