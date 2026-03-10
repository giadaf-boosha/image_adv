<div align="center">

# Image ADV Analyzer

**AI-powered advertising image analysis: classify creative formats, evaluate quality, detect new trends, and generate strategic recommendations.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)]()
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)]()

---

[**Get Started**](#-quick-start) · [**API Docs**](#-usage) · [**Architecture**](#-architecture) · [**Contributing**](#-contributing)

</div>

---

## Overview

Advertising teams analyze hundreds of creatives weekly, but lack a structured framework to classify formats, benchmark quality, and explore new angles. Manual analysis is slow, inconsistent, and misses cross-format patterns.

**Image ADV Analyzer** is a REST API that receives an advertising image and runs a 4-step AI pipeline:

1. **Classifies** the creative into a taxonomy of 128 ad formats across 13 macro-categories
2. **Evaluates quality** using weighted criteria specific to each format type
3. **Detects novel formats** not covered by the existing taxonomy
4. **Recommends angles and hooks** to improve or diversify the creative strategy

Use it when you need to:
- Audit ad creative libraries at scale
- Benchmark creative quality across campaigns
- Discover untapped advertising angles for a product
- Track emerging ad format trends

---

## ✨ Key Features

- **128 ad format taxonomy** — Product-Centric, Lifestyle, UGC, Social Proof, Problem-Solution, Educational, Storytelling, Offer-Driven, Native/Trend, Visual Design, Interactive, and more
- **Multi-label classification** — A single image can match multiple formats with calibrated confidence scores (0.0–1.0)
- **Weighted quality scoring** — 6 universal criteria + category-specific criteria with customizable weights, scored 1–10
- **Novelty detection** — Flags images that don't fit the taxonomy, proposes new format definitions for human review
- **24 advertising angles + 20 creative hooks** — Strategic recommendations mapped to funnel stages (TOFU/MOFU/BOFU)
- **Dual LLM with auto-failover** — Gemini 3.1 Flash (primary) → GPT-4o (fallback), transparent retry with exponential backoff
- **Extensible without code changes** — Update `taxonomy.json` and `quality_criteria.json` to add formats or criteria
- **OpenAPI auto-docs** — Interactive Swagger UI at `/docs`

---

## 🚀 Quick Start

The fastest way to get running with Docker:

```bash
git clone https://github.com/giadaf-boosha/image_adv.git
cd image_adv

cp .env.example .env
# Edit .env and add your API keys:
#   GOOGLE_API_KEY=your_key_here
#   OPENAI_API_KEY=your_key_here

docker compose up --build
```

Then analyze an image:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "image_url=https://example.com/your-ad-image.jpg" \
  -F "platform_hint=meta" \
  -F "vertical_hint=beauty"
```

> **Note**: You need at least one API key (Google or OpenAI) for the pipeline to work. Both are recommended for failover support.

---

## 📦 Installation

### Requirements

- Python 3.12+
- A Google AI API key (`GOOGLE_API_KEY`) and/or an OpenAI API key (`OPENAI_API_KEY`)

### Option A: Docker (recommended)

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Option B: Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys

uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 🧑‍💻 Usage

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/analyze` | Analyze image via multipart form (URL or file upload) |
| `POST` | `/analyze/json` | Analyze image via JSON body (URL only) |
| `GET` | `/health` | Health check with LLM connection status |
| `GET` | `/taxonomy` | Return the full 128-format taxonomy as JSON |
| `GET` | `/docs` | Interactive Swagger UI (auto-generated) |

### Example: Analyze via file upload

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@my-ad-creative.jpg" \
  -F "platform_hint=tiktok" \
  -F "funnel_stage=tofu"
```

### Example: Analyze via JSON

```bash
curl -X POST http://localhost:8000/analyze/json \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/ad.jpg",
    "platform_hint": "meta",
    "vertical_hint": "skincare",
    "funnel_stage": "mofu"
  }'
```

### Response structure

```json
{
  "analysis_id": "uuid-v4",
  "timestamp": "2026-03-10T14:30:00Z",
  "classifications": [
    {
      "category_id": "6.3",
      "category_name": "Before / After",
      "macro_category_id": 6,
      "macro_category_name": "Problem-Solution & Transformation",
      "confidence": 0.91,
      "evidence": "Split screen layout showing product transformation..."
    }
  ],
  "quality_evaluations": [
    {
      "category_id": "6.3",
      "overall_score": 7.4,
      "criteria": [
        { "criterion": "U1", "score": 8, "rationale": "..." },
        { "criterion": "transformation_impact", "score": 9, "rationale": "..." }
      ]
    }
  ],
  "new_type_alert": null,
  "angle_recommendations": {
    "product_context": { "identified_product": "...", "identified_brand": "..." },
    "angle_recommendations": [
      {
        "angle_name": "SOCIAL PROOF (QUANTITATIVE)",
        "creative_format_reference": "5.4 — Social Proof Aggregated",
        "hook_example": "..."
      }
    ],
    "hook_variations": ["[CURIOSITY GAP] ...", "[BOLD CLAIM] ...", "..."]
  },
  "errors": [],
  "schema_version": "1.0"
}
```

### Request parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | one of `image_url` or `file` | Public URL of the ad image |
| `file` | binary | one of `image_url` or `file` | Image file upload (JPEG, PNG, WebP, GIF) |
| `platform_hint` | enum | no | Target platform: `meta`, `tiktok`, `pinterest`, `youtube`, `google_display` |
| `vertical_hint` | string | no | Product vertical (e.g., `beauty`, `tech`, `food`) |
| `funnel_stage` | enum | no | Funnel stage: `tofu`, `mofu`, `bofu` |
| `audience_hint` | string | no | Target audience description |
| `force_new_type_check` | bool | no | Force novelty detection even if classifications are found |

---

## ⚙️ Configuration

All settings are configured via environment variables or a `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | Google AI API key (required for primary model) |
| `OPENAI_API_KEY` | — | OpenAI API key (required for fallback model) |
| `PRIMARY_MODEL` | `gemini-3.1-flash-image-preview` | Primary vision LLM model name |
| `FALLBACK_MODEL` | `gpt-4o` | Fallback vision LLM model name |
| `TAXONOMY_PATH` | `data/taxonomy.json` | Path to the ad format taxonomy file |
| `QUALITY_CRITERIA_PATH` | `data/quality_criteria.json` | Path to the quality criteria file |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | `0.45` | Minimum confidence to include a classification |
| `NOVELTY_TRIGGER_THRESHOLD` | `0.45` | Threshold below which novelty detection triggers |
| `LLM_TIMEOUT_SECONDS` | `45` | Timeout per LLM API call (seconds) |

### Extending the taxonomy

You can add new ad formats or modify criteria **without code changes**:

1. Edit `data/taxonomy.json` — add formats with `id`, `name`, `description`, `visual_signals`, `negative_signals`
2. Edit `data/quality_criteria.json` — add matching criteria entries with `criteria` and `weights`
3. Restart the application — taxonomy is loaded at startup

---

## 🏗 Architecture

```
POST /analyze
     │
     ▼
┌─────────────────┐
│  Preprocessing   │  Validate format, size, resolution. Encode to base64.
└────────┬────────┘
         ▼
┌─────────────────┐
│ RF-01 Classify   │  Vision LLM + 128-format taxonomy → multi-label classification
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│ RF-02  │ │   RF-03    │  Quality evaluation (if classifications found)
│Quality │ │  Novelty   │  Novelty detection (if no classifications found)
└────┬───┘ └─────┬──────┘
     └─────┬─────┘
           ▼
   ┌───────────────┐
   │ RF-04 Angles  │  Strategic angle + hook recommendations
   └───────┬───────┘
           ▼
     JSON Response
```

### Tech stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| API Framework | FastAPI + Pydantic V2 |
| Primary LLM | Google Gemini 3.1 Flash (vision) |
| Fallback LLM | OpenAI GPT-4o (vision) |
| Image Processing | Pillow + httpx |
| Logging | structlog (structured JSON) |
| Container | Docker + Docker Compose |

### Project structure

```
image_adv/
├── src/
│   ├── main.py                 # FastAPI app, pipeline orchestrator
│   ├── config.py               # Pydantic Settings
│   ├── models/
│   │   ├── schemas.py          # Request/response Pydantic models
│   │   └── taxonomy.py         # TaxonomyManager (load, index, query)
│   ├── llm/
│   │   ├── base.py             # Abstract LLM client interface
│   │   ├── gemini_client.py    # Google Gemini client with retry
│   │   └── openai_client.py    # OpenAI GPT-4o client with retry
│   ├── pipeline/
│   │   ├── preprocessor.py     # Image validation, resize, base64
│   │   ├── classifier.py       # RF-01: multi-label classification
│   │   ├── quality_evaluator.py# RF-02: weighted quality scoring
│   │   ├── novelty_detector.py # RF-03: new format detection
│   │   └── recommender.py      # RF-04: angles + hooks
│   └── prompts/
│       ├── classification.py   # Classification prompt builder
│       ├── quality.py          # Quality evaluation prompt builder
│       ├── novelty.py          # Novelty detection prompt builder
│       └── recommendation.py   # Angle/hook recommendation prompt builder
├── data/
│   ├── taxonomy.json           # 128 ad formats (75 KB)
│   └── quality_criteria.json   # Quality criteria per format (60 KB)
├── docs/                       # Technical specification documents
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🛣 Roadmap

This project is in **experimental** status. The core pipeline is functional but has not been battle-tested in production.

- [x] 128-format taxonomy with visual/negative signals
- [x] 4-step AI pipeline (classify → evaluate → detect → recommend)
- [x] Dual LLM with automatic failover
- [x] Docker deployment
- [ ] Batch processing endpoint (`POST /analyze/batch`)
- [ ] PostgreSQL persistence for alerts and analysis history
- [ ] Celery + Redis worker queue for async batch jobs
- [ ] Ground-truth dataset and regression test suite
- [ ] CLIP embedding + UMAP clustering for v2.0 novelty detection
- [ ] Rate limiting and API key authentication

---

## 🤝 Contributing

Contributions are welcome. Before starting:

1. Open an issue describing the change you'd like to make
2. Fork the repository and create a feature branch
3. Follow existing code patterns (see `src/pipeline/` for reference)
4. Ensure all new formats are added to both `taxonomy.json` and `quality_criteria.json`
5. Submit a pull request with a clear description

### Development setup

```bash
git clone https://github.com/giadaf-boosha/image_adv.git
cd image_adv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn src.main:app --reload
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built with [FastAPI](https://fastapi.tiangolo.com/) · Powered by [Gemini](https://ai.google.dev/) and [GPT-4o](https://openai.com/)

</div>
