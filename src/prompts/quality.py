"""
Prompt builder per la valutazione qualitativa di un creativo pubblicitario
rispetto a una specifica tipologia classificata.

Segue le specifiche di 02_criteri_qualita_per_tipologia.md e 01_architettura_e_requisiti.md,
Sezione 1.2 (RF-02).

I criteri di categoria provengono da TaxonomyManager.get_criteria_for_format(),
che restituisce list[dict] con chiavi: {"criterion": str, "weight": float}.

Formula punteggio composito (da 02_criteri_qualita_per_tipologia.md):
  Score_finale = (Media_criteri_universali * 0.35) + (Media_pesata_criteri_categoria * 0.65)
"""

_UNIVERSAL_CRITERIA_BLOCK = """\
UNIVERSAL CRITERIA (apply to ALL 128 format types, weight: 35% of final score):

| ID | Criterion | Description |
|----|-----------|-------------|
| U1 | Resolution & Sharpness | Image free of pixelation, unintentional blur, compression artifacts. Sharp edges on main elements. |
| U2 | Composition & Visual Hierarchy | A clearly dominant primary focal point. Secondary elements do not compete with the main subject. Rule of thirds or intentional centering respected. |
| U3 | Text Legibility | Sufficient text/background contrast (min 4.5:1 WCAG AA). Font size appropriate to format. No text overlapping critical elements. |
| U4 | Brand Consistency | Logo visible and undistorted (if present). Color palette coherent with brand identity. Visual tone aligned with brand positioning. |
| U5 | Clarity of Main Message | A single primary message immediately identifiable within 1-3 seconds. No informational overcrowding. |
| U6 | General Technical Quality | Absence of: unintentional watermarks, visible metadata, accidental cropping of important elements, unintended geometric distortions, gradient banding. |"""

_SCORING_SCALE = """\
SCORING SCALE (apply to every criterion):

| Score | Level | Description |
|-------|-------|-------------|
| 1–3   | Critical  | Criterion not met. Evident defect that compromises the ad's usability or effectiveness. |
| 4–6   | Average   | Criterion partially met. Significant room for improvement. |
| 7–8   | Good      | Criterion met. Quality adequate for publication. |
| 9–10  | Excellent | Criterion met in an exemplary way. Benchmark-level quality for the sector. |"""


def build_quality_prompt(
    category_id: str,
    category_name: str,
    criteria_list: list[dict],
) -> str:
    """Costruisce il prompt per la valutazione qualitativa di una tipologia specifica.

    Args:
        category_id: ID della tipologia (es. "6.3").
        category_name: Nome della tipologia (es. "Before / After").
        criteria_list: Lista di dizionari con i criteri specifici per questa tipologia.
                       Ogni dict ha almeno: {"criterion": str, "weight": float}.
                       Questo è il formato restituito da TaxonomyManager.get_criteria_for_format().

    Returns:
        Stringa del prompt di sistema completa.
    """
    criteria_table_rows = []
    for i, criterion in enumerate(criteria_list):
        criterion_id = criterion.get("criterion", f"C{i + 1}")
        weight = criterion.get("weight", 1.0)
        weight_str = f" (weight: {weight:.1f}x)" if weight != 1.0 else ""
        # Il nome del criterio è l'ID stesso (es. "lighting_quality") — lo umanizziamo
        human_label = criterion_id.replace("_", " ").title()
        criteria_table_rows.append(
            f"| {criterion_id} | **{human_label}**{weight_str} | "
            f"Evaluate the quality of {human_label.lower()} in this ad. |"
        )

    criteria_table = "\n".join(criteria_table_rows)
    criteria_ids = [c.get("criterion", f"C{i}") for i, c in enumerate(criteria_list)]

    example_id = criteria_ids[0] if criteria_ids else "C1"
    example_label = example_id.replace("_", " ").title()

    prompt = f"""You are an expert advertising creative quality analyst. Your task is to evaluate the quality of an advertising image that has been classified as **{category_name}** (format ID: {category_id}).

You will assess the image on two sets of criteria:
1. Six universal criteria that apply to all advertising formats (weight: 35% of final score)
2. Category-specific criteria for the "{category_name}" format (weight: 65% of final score)

Provide a score from 1 to 10 for each criterion, with a concrete rationale grounded in specific visual elements you can observe in the image.

---

{_SCORING_SCALE}

---

{_UNIVERSAL_CRITERIA_BLOCK}

---

CATEGORY-SPECIFIC CRITERIA FOR "{category_name.upper()}" (format {category_id}) — weight: 65% of final score:

| Criterion ID | Criterion | Note |
|---|---|---|
{criteria_table}

---

SCORING FORMULA:

Final score = (Average of U1–U6 scores × 0.35) + (Weighted average of category-specific criteria × 0.65)

Round the final score to one decimal place.

---

RED FLAGS (automatically lower individual criterion scores):
- Visible unintentional watermarks (Getty, Shutterstock, etc.)
- Inconsistent shadows suggesting low-quality compositing
- White background with yellowish/grey halos around the product (poor cutout)
- Text claim overlaid on the most critical part of the visual
- Reflections revealing camera equipment or unintended studio environment

---

OUTPUT FORMAT:

Return ONLY a valid JSON object. Do not include any text, explanation, or markdown outside the JSON.

{{
  "category_id": "{category_id}",
  "category_name": "{category_name}",
  "universal_criteria": [
    {{
      "criterion": "U1",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation about this specific image. Minimum 20 characters.>"
    }},
    {{
      "criterion": "U2",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation.>"
    }},
    {{
      "criterion": "U3",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation. If no text is present, score 7 and note 'No text elements present'.>"
    }},
    {{
      "criterion": "U4",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation. If brand identity is not assessable, score 5 and explain.>"
    }},
    {{
      "criterion": "U5",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation.>"
    }},
    {{
      "criterion": "U6",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation.>"
    }}
  ],
  "category_criteria": [
    {{
      "criterion": "{example_id}",
      "label": "Good",
      "score": <integer 1-10>,
      "rationale": "<Concrete observation about this specific image, anchored to what is visually present. Minimum 20 characters.>"
    }}
  ],
  "overall_score": <float, e.g.: 7.4>,
  "overall_assessment": "<2-3 sentences summarizing the main strengths and the most impactful areas for improvement for this specific '{category_name}' execution.>",
  "top_improvement": "<The single most impactful change that would raise the score of this creative. Be specific and actionable.>"
}}

Notes on the output:
- `universal_criteria` must contain exactly 6 entries (U1 through U6)
- `category_criteria` must contain one entry for EACH of the {len(criteria_list)} category-specific criteria ({', '.join(criteria_ids)})
- For label: use "Critical" for scores 1-3, "Average" for 4-6, "Good" for 7-8, "Excellent" for 9-10
- `overall_score` must be calculated as (avg(U1..U6) × 0.35) + (weighted_avg(category_criteria) × 0.65), rounded to 1 decimal
- All scores are integers in [1, 10]; `overall_score` is a float in [1.0, 10.0]
- Criterion IDs in `category_criteria` must match exactly: {', '.join(criteria_ids)}"""

    return prompt
