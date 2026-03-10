# Image ADV Analyzer — Architettura e Requisiti

> Versione 1.0 | Marzo 2026
> Riferimento tassonomia: `mappatura_formati_creativi_adv.md`

---

## Sezione 1: Requisiti Funzionali

### 1.1 RF-01 — Classificazione del Formato Creativo

**Descrizione**
L'agente riceve un'immagine pubblicitaria e la classifica in una o piu delle 128 tipologie creative definite nella tassonomia, organizzate in 13 macro-categorie. La classificazione e multi-label: un singolo annuncio puo appartenere a piu tipologie simultaneamente (es. un UGC che e anche Before/After con struttura Problem-Solution).

**Input**
- Immagine in formato JPEG, PNG, WebP, GIF (frame statico), o URL pubblico raggiungibile
- Dimensione massima accettata: 20 MB per immagine singola
- Risoluzione minima consigliata: 300x300 px (sotto soglia, avvertimento non bloccante)
- Parametri opzionali di contesto: `platform_hint` (es. "meta_feed", "tiktok", "pinterest"), `vertical_hint` (es. "beauty", "tech", "food")

**Output**
```json
{
  "classifications": [
    {
      "category_id": "4.2",
      "category_name": "UGC Talking Head",
      "macro_category_id": 4,
      "macro_category_name": "UGC & Creator Content",
      "confidence": 0.91,
      "evidence": "Persona in primo piano che parla direttamente alla camera, sfondo domestico non professionale, no lighting setup visibile"
    }
  ]
}
```

**Regole di Business**
- Vengono restituite tutte le classificazioni con confidence >= 0.45
- Se nessuna classificazione supera 0.45, si attiva RF-03 (Alert Nuova Tipologia)
- L'ordinamento e per confidence decrescente; la prima classificazione e la primaria
- Il numero massimo di classificazioni restituite e 5
- Se `platform_hint` e fornito, il modello considera la coerenza piattaforma-formato come fattore di boost
- Le categorie 13.x (Interactive & Immersive) sono classificabili solo se l'immagine contiene elementi UI visibili

**Condizioni di Errore**

| Codice | Condizione | Comportamento |
|--------|-----------|---------------|
| E-101 | Immagine illeggibile o corrotta | Errore bloccante, messaggio `"image_unreadable"` |
| E-102 | Immagine sotto 300x300 px | Warning non bloccante, analisi prosegue |
| E-103 | Nessuna classificazione >= 0.30 | Trigger automatico RF-03 |
| E-104 | Immagine non pubblicitaria | Classification vuota, `"not_advertising_content": true` |
| E-105 | URL immagine irraggiungibile | Errore bloccante `"image_url_unreachable"` |

---

### 1.2 RF-02 — Valutazione Qualitativa per Tipologia

**Descrizione**
Per ogni tipologia identificata da RF-01 con confidence >= 0.45, l'agente produce una valutazione qualitativa su criteri specifici per quella tipologia. Score 1-10, ogni dimensione motivata con evidenza visiva concreta.

**Criteri per Macro-Categoria**

| Macro-Categoria | Criteri di Valutazione Specifici |
|----------------|----------------------------------|
| 1. Product-Centric | lighting_quality, background_neutrality, product_prominence, brand_clarity, composition_quality, color_accuracy |
| 2. Lifestyle & Context | scene_authenticity, product_integration, aspirational_quality, human_presence_quality, environment_coherence |
| 3. Behind the Scenes | authenticity_perception, craft_visibility, storytelling_clarity, production_transparency |
| 4. UGC & Creator Content | authenticity_score, engagement_potential, speaker_credibility, audio_visual_sync, review_specificity |
| 5. Social Proof & Trust | credibility_elements, proof_specificity, visual_hierarchy, badge_readability, testimonial_authenticity |
| 6. Problem-Solution | problem_clarity, solution_relevance, transformation_impact, emotional_resonance, narrative_flow |
| 7. Comparison & Competitive | fairness_perception, data_clarity, visual_comparison_balance, differentiation_strength |
| 8. Educational | information_density, visual_clarity, step_logical_flow, scanability, actionability |
| 9. Storytelling & Emotional | emotional_impact, narrative_coherence, character_relatability, brand_integration, authenticity |
| 10. Offer & Promo | offer_clarity, urgency_perception, value_communication, cta_strength, visual_hierarchy |
| 11. Native & Trend-Driven | platform_nativeness, trend_relevance_score, production_quality_intentionality, hook_strength |
| 12. Visual Design & Style | typographic_quality, color_harmony, visual_impact, brand_consistency, stop_scroll_potential |
| 13. Interactive & Immersive | ui_clarity, interaction_intuitiveness, experience_depth, technical_execution |

**Calcolo Overall Score**: media pesata dei criteri attivi per quella tipologia, arrotondata a una cifra decimale.

**Scale**: 1-3 = criticita, 4-6 = media, 7-9 = buona, 10 = eccellenza

---

### 1.3 RF-03 — Alert Nuova Tipologia

**Trigger Conditions**
1. Nessuna classificazione RF-01 supera confidence 0.45
2. Classificazione primaria ha confidence 0.45-0.65 AND elementi creativi non spiegati
3. Campo `force_new_type_check: true` passato esplicitamente

**Regole di Business**
- Alert salvato con `alert_id` univoco (formato: `ALT-YYYYMMDD-NNN`)
- `confidence_in_novelty` >= 0.65 richiede revisione umana prioritaria
- `closest_known_types` mostra sempre i 3 tipi piu vicini
- Se stesso pattern segnalato >= 3 volte, flag `"repeated_pattern": true`

---

### 1.4 RF-04 — Raccomandazione Angoli e Hook

**Regole di Business**
- Minimo 3, massimo 5 angoli alternativi
- Angoli suggeriti non coincidono con tipologie gia classificate
- Ogni angolo include riferimento al formato creativo della tassonomia
- 5 hook_variations, calibrati sul prodotto specifico
- Se `funnel_stage` non specificato, angoli per tutti e tre i funnel stage

---

## Sezione 2: Requisiti Non Funzionali

### 2.1 Performance

| Modalita | Latenza P50 | Latenza P95 |
|----------|-------------|-------------|
| Single image — classificazione only | < 4s | < 8s |
| Single image — pipeline completa | < 15s | < 25s |
| Single image — con alert | < 18s | < 30s |
| Batch processing (per immagine) | < 8s media | < 20s |

### 2.2 Scalabilita

- **Single**: sincrono via API REST, timeout 60s
- **Batch**: max 50 immagini, coda con worker pool (concorrenza 10), webhook o polling
- **Worker stateless**: scalabilita orizzontale senza condivisione stato
- **Catalogo criteri**: caricato in memoria all'avvio da YAML/JSON

### 2.3 Estensibilita

Aggiornamenti tassonomia senza modifiche al codice:
1. Aggiornamento `taxonomy.json`
2. Aggiornamento `quality_criteria.json`
3. Rebuild automatico prompt template all'avvio
4. Test di regressione su ground-truth dataset

### 2.4 Output JSON Unificato

```json
{
  "analysis_id": "UUID v4",
  "timestamp": "ISO 8601",
  "input": { "image_source": "url|upload", "platform_hint": null, "vertical_hint": null, "funnel_stage": null },
  "processing_metadata": { "model_used": "string", "processing_time_ms": 0, "pipeline_steps_executed": [] },
  "classifications": [],
  "quality_evaluations": [],
  "new_type_alert": null,
  "angle_recommendations": {},
  "errors": [],
  "schema_version": "1.0"
}
```

---

## Sezione 3: Architettura del Sistema

### 3.1 Pipeline di Elaborazione

```
INPUT LAYER: HTTP POST /analyze <- immagine + parametri
       |
PREPROCESSING: validazione formato, dimensione, risoluzione, encoding base64
       |
STEP 1 - CLASSIFICAZIONE (RF-01): Vision LLM con tassonomia completa
       |
  [>= 1 classificazione sopra soglia]     [0 classificazioni sopra soglia]
       |                                          |
STEP 2 - VALUTAZIONE (RF-02)              STEP 3 - ALERT (RF-03)
  Per ogni classificazione >= 0.45           Novelty detection
       |                                          |
       +------------------------------------------+
       |
STEP 4 - RACCOMANDAZIONI (RF-04): angoli + hook
       |
RESPONSE ASSEMBLY: aggregazione JSON + metadata + validazione schema
       |
HTTP 200 JSON Response
```

### 3.2 Modelli AI

**Primario: claude-sonnet-4-6 (Anthropic)**
- Tutti e 4 gli step della pipeline
- temperature: 0.2 (classificazione/valutazione), 0.7 (raccomandazioni)
- Max tokens: 2048 (RF-01), 4096 (RF-02), 2048 (RF-03), 3072 (RF-04)

**Fallback: gpt-4o (OpenAI)**
- Automatico su errori Anthropic API (5xx, timeout)
- Structured Outputs nativi

**Batch: gemini-2.5-flash (Google)**
- Alto volume (> 100 img/ora), costo ridotto
- Context window 1M token

### 3.3 Prompt Templates

Vedere documento `03_pipeline_classificazione_ai.md` per i prompt completi.

### 3.4 Detection Nuove Tipologie

Strategia: Low-Confidence Threshold + Explicit Residual Analysis
- Threshold: nessun confidence >= 0.45
- Residual analysis nel prompt NEW_TYPE_PROMPT
- Deduplicazione: 24h stessa immagine, 72h stesso pattern
- Log persistente con coda revisione umana
- Evoluzione v2.0: embedding CLIP + clustering UMAP

---

## Sezione 4: Struttura Dati

### 4.1 Tassonomia (`taxonomy.json`)

```json
{
  "version": "1.0",
  "total_formats": 128,
  "macro_categories": [{
    "id": 1, "name": "Product-Centric", "format_count": 16,
    "formats": [{
      "id": "1.1", "name": "Product Only / White Background",
      "description": "...",
      "visual_signals": ["sfondo bianco neutro", "prodotto centrato", "assenza persone"],
      "negative_signals": ["persone", "sfondo colorato", "elementi scenografici"]
    }]
  }]
}
```

### 4.2 Criteri Qualita (`quality_criteria.json`)

```json
{
  "version": "1.0",
  "format_criteria_map": {
    "1.1": {
      "criteria": ["lighting_quality", "background_neutrality", "product_prominence", "composition_quality", "color_accuracy"],
      "weights": { "lighting_quality": 1.2, "background_neutrality": 1.3, "product_prominence": 1.2, "composition_quality": 1.0, "color_accuracy": 1.0 }
    }
  }
}
```

### 4.3 Alert Log (`new_type_alerts_log.jsonl`)

```jsonl
{"alert_id":"ALT-20260310-001","timestamp":"2026-03-10T14:32:00Z","trigger_reason":"no_classification_above_threshold","confidence_in_novelty":0.73,"review_status":"pending"}
```

---

## Sezione 5: Stack Tecnologico

| Componente | Tecnologia | Motivazione |
|-----------|-----------|-------------|
| Linguaggio | Python 3.12+ | Ecosistema AI/ML maturo, SDK ufficiali Anthropic/OpenAI/Google |
| Framework API | FastAPI 0.115+ | Async nativo, Pydantic validation, OpenAPI auto |
| LLM Validation | Pydantic V2 + Instructor | Retry automatico su output malformato |
| Immagini | Pillow 10+ / httpx | Validazione formato, download asincrono |
| Task Queue | Celery 5+ / Redis | Batch processing resiliente |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 async | Query strutturate per alert |
| Config | Pydantic Settings + .env | Type-safe configuration |
| Logging | structlog + Sentry | Structured JSON logging + error tracking |
| Testing | pytest + pytest-asyncio + VCR.py | Test deterministici senza consumo token |
| Container | Docker + Docker Compose | api + worker + redis + postgres |

### Endpoint API

- `POST /analyze` — single image (sync)
- `POST /analyze/batch` — batch (async, restituisce batch_id)
- `GET /batch/{batch_id}` — polling stato
- `GET /alerts` — lista alert nuove tipologie
- `PATCH /alerts/{alert_id}` — aggiornamento review_status
- `GET /taxonomy` — tassonomia corrente
- `GET /health` — health check

---

## Appendice A: Mapping Tipologie -> Criteri

Vedere file dedicato `02_criteri_qualita_per_tipologia.md` per il mapping completo di tutte le 128 tipologie con i rispettivi criteri di valutazione e pesi.

---

*Image ADV Analyzer — Specifica Tecnica v1.0 — Marzo 2026*
