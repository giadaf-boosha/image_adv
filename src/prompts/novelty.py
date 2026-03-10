"""
Prompt builder per la novelty detection di creativi pubblicitari non classificabili.

Si attiva quando nessun formato nella tassonomia raggiunge confidence >= 0.45,
seguendo le specifiche di 03_pipeline_classificazione_ai.md, Sezione 3,
e 01_architettura_e_requisiti.md, Sezione 1.3 (RF-03).

Soglie operative:
  - confidence_in_novelty >= 0.65 → richiede revisione umana prioritaria
  - confidence_in_novelty < 0.65 → edge case, probabilmente formato esistente mal classificato
"""

_TAXONOMY_SUMMARY_BLOCK = """\
KNOWN TAXONOMY SUMMARY (13 macro-categories, 128 formats):

1. PRODUCT-CENTRIC (16 formats): product isolated on white/colored background, hero shot, detail/close-up,
   scale shot, in-context, flat lay/knolling, still life, still life + text, product grid, annotated/point-out,
   ingredient spotlight, 360/multi-angle, packaging, bundle/kit, animated showcase.

2. LIFESTYLE & CONTEXT (9 formats): product in aspirational environment, product worn/in-use, day-in-the-life
   mini vlog, GRWM, morning/night routine, OOTD, what I eat in a day, study/work with me, "That Girl" aesthetic.

3. BEHIND THE SCENES & CRAFT (5 formats): BTS production, how it's made/process shot, pack an order,
   founder story, employee spotlight.

4. UGC & CREATOR CONTENT (12 formats): classic UGC, talking head, unboxing, haul, try-on, reaction video,
   ASMR product, taste/blind test, honest/"brutally honest" review, ranking/tier list, UGC mashup/compilation,
   whitelisted/partnership ad.

5. SOCIAL PROOF & TRUST (9 formats): customer review/quote card, video testimonial, case study/customer story,
   aggregated social proof, press/"as seen in", expert/authority endorsement, influencer/creator endorsement,
   awards/certifications, native comment box.

6. PROBLEM-SOLUTION & TRANSFORMATION (9 formats): classic problem-solution, PAS (problem-agitate-solution),
   before/after, pain point dramatization, myth-busting, expectation vs. reality, "how it started vs. how it's going",
   result tracking/challenge, switching story.

7. COMPARISON & COMPETITIVE (5 formats): us vs. them, us vs. old way, side-by-side demo, "why we're different",
   comparison table.

8. EDUCATIONAL & INFORMATIONAL (10 formats): how-to/tutorial, step-by-step/multi-frame, explainer (animated or live),
   listicle/benefits list, feature highlight/specs, infographic, stat/data callout, FAQ visual, tip & hack/life hack,
   educational grid (2x3 / 3x3).

9. STORYTELLING & EMOTIONAL (9 formats): brand story/origin story, customer journey/success story, emotional appeal,
   aspirational/lifestyle, mini-series/story arc, day-in-the-life (narrative), humor/comedy/skit, storytime,
   documentary-style.

10. OFFER & PROMO-DRIVEN (9 formats): hard offer/promo, hard promise, countdown/urgency, scarcity/limited edition,
    free shipping/bonus offer, seasonal/holiday, new launch/announcement, price anchor, bundle/kit offer.

11. NATIVE & TREND-DRIVEN (12 formats): talking head, lo-fi/"ugly ads", POV, trend-jacking/trending sound, meme/
    internet culture, challenge/branded hashtag, duet, stitch, reply to comment, green screen, screenshot/native-looking,
    street interview/vox pop.

12. VISUAL DESIGN & PRODUCTION STYLE (17 formats): bold text/typography-first, quote card, minimalist/clean,
    color blocking, collage/scrapbook, mood board, stop motion, GIF/cinemagraph, motion graphics/animated, boomerang,
    kinetic text/text animation, timelapse, transition/editing-driven, montage/compilation, satisfying/oddly satisfying,
    notepad/handwritten, infographic pin.

13. INTERACTIVE & IMMERSIVE (6 formats): poll/quiz ad, AR try-on/virtual preview, shoppable video, playable ad,
    360-degree/panoramic, gamified ad."""


def build_novelty_prompt(closest_types: list[dict]) -> str:
    """Costruisce il prompt per la novelty detection.

    Args:
        closest_types: Lista (max 3) dei formati più vicini trovati dalla classificazione
                       che non hanno superato la soglia di confidence 0.45.
                       Ogni dict ha: {"category_id": str, "category_name": str, "confidence": float}.

    Returns:
        Stringa del prompt di sistema completa.
    """
    closest_block = _format_closest_types(closest_types)

    prompt = f"""You are an expert advertising creative analyst specializing in identifying new, emerging, or uncategorized advertising creative formats.

You have been provided an advertising image that did NOT match any of the 128 known creative formats in our taxonomy with sufficient confidence (no format reached confidence >= 0.45 on a 0.0–1.0 scale).

Your task is to:
1. Describe the image in precise detail
2. Explain WHY it does not fit the known taxonomy — be specific about which elements are novel
3. Propose a working name and structured description for a potential new format
4. Assess with calibrated confidence whether this is TRULY a new format or a known format presented in an unusual/edge-case way

---

CONSERVATISM PRINCIPLE:

Be conservative. Most images that fail classification are edge cases of existing formats, not genuinely new ones.
Only assign `confidence_in_novelty >= 0.65` if you can clearly articulate:
  (a) what specific structural or narrative element is absent from ALL 128 existing formats, AND
  (b) why this element constitutes a distinct communicative intent, not just a stylistic variation.

If the image seems like an unusual execution of an existing format, set `is_truly_novel: false`
and explain which existing format it most closely resembles and why it was borderline.

---

{_TAXONOMY_SUMMARY_BLOCK}

---

CLOSEST MATCHING FORMATS FROM PREVIOUS CLASSIFICATION ATTEMPT:

{closest_block}

These formats were the best candidates but did not reach the minimum confidence threshold of 0.45.
Use them as reference points when explaining why the image is novel (or not).

---

OUTPUT FORMAT:

Return ONLY a valid JSON object. Do not include any text, explanation, or markdown outside the JSON.

{{
  "image_description": "<Detailed description in English of what you see: subjects, setting, composition, visual style, text visible, colors, mood. 4-6 sentences. Be specific and objective.>",
  "product_sector": "<Identified product or sector, or 'unknown'>",
  "novelty_assessment": {{
    "is_truly_novel": <true or false>,
    "confidence_in_novelty": <float 0.0–1.0. Use >= 0.65 ONLY if genuinely novel by the conservatism principle above.>,
    "explanation": "<2-4 sentences. If truly novel: explain what specific element is absent from all 128 formats and why it constitutes a new format. If not truly novel: explain which existing format it actually resembles and what made it borderline.>"
  }},
  "proposed_new_type": {{
    "working_name": "<A concise name for the potential new format, in English, following naming conventions of the existing taxonomy (e.g., 'Interactive Poll Overlay', 'AI-Generated Product Demo')>",
    "description": "<2-3 sentences describing this format: what it shows, how it is structured, what communicative intent it serves, how it differs from all 128 existing formats.>",
    "visual_elements": ["<distinctive visual element 1>", "<distinctive visual element 2>", "<distinctive narrative element>"],
    "suggested_macro_category": "<Name of the most appropriate existing macro-category (e.g., 'VISUAL DESIGN & PRODUCTION STYLE'), or 'NEW MACRO-CATEGORY' only if no existing category fits at all>",
    "differentiation_from_closest": "<Specific explanation of how this proposed format differs from the closest known types listed above. Name the closest types explicitly.>",
    "use_cases": ["<advertising context 1>", "<advertising context 2>"],
    "confidence_in_novelty": <float 0.0–1.0, same value as novelty_assessment.confidence_in_novelty>
  }},
  "recommendation": "<Exactly one of: 'ADD_TO_TAXONOMY', 'REVIEW_NEEDED', 'EDGE_CASE_EXISTING_FORMAT'. Follow with a brief justification (1 sentence).>"
}}

Rules:
- `confidence_in_novelty` in `proposed_new_type` must equal `novelty_assessment.confidence_in_novelty`
- If `is_truly_novel` is false, still populate `proposed_new_type` with the best description of what was observed, but use low `confidence_in_novelty` (< 0.40)
- `recommendation` must be 'EDGE_CASE_EXISTING_FORMAT' if `is_truly_novel` is false
- `recommendation` must be 'ADD_TO_TAXONOMY' only if `confidence_in_novelty >= 0.80`
- `recommendation` must be 'REVIEW_NEEDED' if `confidence_in_novelty` is between 0.65 and 0.79"""

    return prompt


def _format_closest_types(closest_types: list[dict]) -> str:
    """Formatta la lista dei tipi più vicini in testo leggibile per il prompt."""
    if not closest_types:
        return "No close matches found — all formats were below 0.30 confidence."

    lines = []
    for i, ct in enumerate(closest_types[:3], start=1):
        category_id = ct.get("category_id", "unknown")
        category_name = ct.get("category_name", "unknown")
        confidence = ct.get("confidence", 0.0)
        lines.append(
            f"{i}. Format {category_id} — {category_name} "
            f"(confidence: {confidence:.2f}/1.00)"
        )

    return "\n".join(lines)
