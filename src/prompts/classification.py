"""
Prompt builder per la classificazione multi-label di creativi pubblicitari.

Il prompt segue le specifiche di 03_pipeline_classificazione_ai.md, Sezione 2.
Confidence score nel dominio 0.0-1.0 (il doc usa 0-100, normalizziamo qui).
"""


def build_classification_prompt(
    taxonomy_text: str,
    platform_hint: str | None,
    vertical_hint: str | None,
) -> str:
    """Costruisce il prompt di sistema per la classificazione del formato creativo.

    Args:
        taxonomy_text: Testo della tassonomia completa (128 formati, 13 macro-categorie).
                       Viene iniettato direttamente nel prompt per aggiornamenti
                       senza modifiche al codice.
        platform_hint: Piattaforma di destinazione dell'annuncio (es. "meta", "tiktok").
                       Se fornito, il modello considera la coerenza piattaforma-formato.
        vertical_hint: Verticale di prodotto (es. "beauty", "tech", "food").
                       Aiuta il modello a disambiguare formati simili.

    Returns:
        Stringa del prompt di sistema completa, pronta per essere passata all'LLM.
    """
    platform_context = ""
    if platform_hint:
        platform_context = f"\nPlatform context: This ad is intended for **{platform_hint.upper()}**. "
        platform_context += (
            "Apply a coherence check: formats that are native to this platform "
            "(e.g., Talking Head, Lo-Fi, Trend-Jacking for TikTok; "
            "Flat Lay, Lifestyle, Mood Board for Pinterest; "
            "Hero Shot, Product-Centric, Social Proof for Meta feed) "
            "receive a small confidence boost (+5 points on a 100-point scale). "
            "Formats that are structurally incompatible with this platform "
            "(e.g., Interactive/Immersive 13.x on static platforms) "
            "receive a confidence penalty (-10 points)."
        )

    vertical_context = ""
    if vertical_hint:
        vertical_context = f"\nVertical context: The product belongs to the **{vertical_hint}** vertical. "
        vertical_context += (
            "Use this to disambiguate formats with high visual overlap "
            "(e.g., a beauty 'Before/After' vs. a fitness 'Result Tracking'). "
            "Do not over-filter based on vertical alone; the visual evidence takes priority."
        )

    taxonomy_block = taxonomy_text if taxonomy_text else _DEFAULT_TAXONOMY_BLOCK

    prompt = f"""You are an expert advertising creative analyst with deep knowledge of digital advertising formats across all major platforms (Meta, TikTok, Pinterest, YouTube, Google Display).

Your task is to classify an advertising image according to a precise taxonomy of 128 creative formats organized in 13 macro-categories.{platform_context}{vertical_context}

---

CLASSIFICATION RULES:

1. **Multi-label classification**: Assign ALL applicable format types. A single ad can simultaneously belong to multiple formats (e.g., a UGC video that is also a Before/After with Problem-Solution structure).
2. **Confidence scores**: Use a 0.0–1.0 scale (0.0 = no match, 1.0 = perfect match). Only include formats with confidence >= 0.45.
3. **Evidence requirement**: Every classification MUST be grounded in specific visual or narrative elements visible in the image. Do not classify based on assumptions about off-screen content.
4. **Maximum 5 formats**: Return at most 5 classifications, ordered by confidence descending.
5. **Taxonomy fidelity**: Do not invent format IDs or names outside the taxonomy below. If the image does not match any format with confidence >= 0.45, return an empty `detected_formats` array.
6. **Interactive formats (13.x)**: Only classify as Interactive & Immersive if the image contains visible UI elements (buttons, polls, AR overlays, playable elements). Do not infer interactivity.
7. **Non-advertising content**: If the image is clearly not advertising content, set `not_advertising_content: true` and return empty `detected_formats`.
8. **Conservative approach**: When uncertain between two formats, assign both with appropriately lower confidence rather than forcing one.

---

CONFIDENCE CALIBRATION GUIDE:

| Confidence | Meaning |
|---|---|
| 0.90–1.00 | Format is unambiguously present; multiple distinctive elements confirm it |
| 0.70–0.89 | Format is clearly present; one or two distinctive elements present |
| 0.45–0.69 | Format is plausibly present; some elements match but ambiguity exists |
| < 0.45 | Do NOT include — insufficient evidence |

---

COMPLETE TAXONOMY OF 128 ADVERTISING CREATIVE FORMATS:

{taxonomy_block}

---

OUTPUT FORMAT:

Return ONLY a valid JSON object with this exact structure. Do not include any text, explanation, or markdown outside the JSON object.

{{
  "image_description": "<Detailed description in English of what you see in the image: subjects, setting, composition, visual style, text visible, colors, mood. 3-5 sentences. Be specific and objective.>",
  "product_sector": "<Identified product or sector (e.g.: 'skincare - face serum', 'SaaS - project management tool', 'fashion - women sportswear'). Write 'unknown' if not identifiable.>",
  "not_advertising_content": <true or false>,
  "detected_formats": [
    {{
      "format_id": "<e.g.: 6.3>",
      "format_name": "<e.g.: Before / After>",
      "macro_category_id": <integer, e.g.: 6>,
      "macro_category_name": "<e.g.: PROBLEM-SOLUTION & TRANSFORMATION>",
      "confidence": <float 0.0–1.0, e.g.: 0.92>,
      "evidence": "<One to two sentences explaining which specific visual or narrative elements in the image support this classification. Be concrete: name colors, layout, people, text, structure.>"
    }}
  ],
  "primary_format": {{
    "format_id": "<format_id of the single most confident classification>",
    "format_name": "<name>",
    "confidence": <float 0.0–1.0>
  }},
  "classification_notes": "<Optional: any ambiguity, overlapping formats, or elements that made classification difficult. Empty string if none.>"
}}

Rules for the JSON output:
- Sort `detected_formats` by `confidence` descending
- `primary_format` MUST be the entry with highest confidence in `detected_formats`
- If `detected_formats` is empty, set `primary_format` to null
- All confidence values are floats in [0.0, 1.0] — never integers like 92 or 45"""

    return prompt


_DEFAULT_TAXONOMY_BLOCK = """\
## MACRO-CATEGORY 1: PRODUCT-CENTRIC (Product at the Center)
1.1  Product Only / White Background — Product isolated on white or neutral background. Clean, minimal, distraction-free.
1.2  Product on Colored Background — Product on vivid colored background to stand out in feed.
1.3  Hero Shot — High-quality product image with curated lighting, slight suggestive context.
1.4  Detail Shot / Close-Up — Zoom on texture, materials, finishes, stitching, ingredients.
1.5  Scale Shot — Product next to common objects (hands, people) to communicate real dimensions.
1.6  Product in Context / In-Situ — Product in its natural use environment (sofa in living room, laptop on desk).
1.7  Flat Lay / Knolling — Products arranged from above in orderly geometric composition. Instagram-native aesthetic.
1.8  Still Life — Artistic composition of product with scenic elements (flowers, fabrics, materials).
1.9  Still Life + Text Overlay — Still life with overlaid text: claim, benefit, price, offer.
1.10 Product Collection / Grid — Multiple products in grid or unique composition. Line, collection, catalog in one frame.
1.11 Product Annotated / Point-Out — Image with arrows, labels, callouts highlighting specific features.
1.12 Ingredient / Component Spotlight — Focus on a single key ingredient or component.
1.13 360 / Multi-Angle — Product shot from multiple angles for complete view. Often in carousel.
1.14 Packaging Shot — Product in its packaging. Enhances brand experience.
1.15 Bundle / Kit Shot — Package of complementary products presented together.
1.16 Animated Product Showcase — 3D animation or motion graphics: rotation, component explosion, effects.

## MACRO-CATEGORY 2: LIFESTYLE & CONTEXT (Product in Real Life)
2.1  Lifestyle / Product in Context — Product inserted in aspirational or real environment (home, nature, office).
2.2  Product Worn / In-Use — Real people wearing or using the product.
2.3  Day in the Life / Mini Vlog — Daily routine of a person with the product naturally integrated.
2.4  GRWM (Get Ready With Me) — Person gets ready (makeup, outfit, skincare) using the product.
2.5  Morning/Night Routine — Sequence of products used in morning or evening routine.
2.6  OOTD (Outfit of the Day) — Complete outfit, often with transitions or zoom.
2.7  What I Eat in a Day — All meals of the day with food products or kitchen tools.
2.8  Study/Work with Me — Companion format: viewer accompanies creator during an activity.
2.9  "That Girl" / Clean Aesthetic — Tidy, healthy, curated lifestyle. Neutral palette, clean spaces, minimal products.

## MACRO-CATEGORY 3: BEHIND THE SCENES & CRAFT
3.1  Behind the Scenes (BTS) — Look behind the scenes: production, team, laboratory. Transparency and authenticity.
3.2  Process Shot / How It's Made — Process of creation or working of the product. Justifies premium price.
3.3  Pack an Order with Me — Preparation of an order, often in ASMR/satisfying style.
3.4  Founder Story — Founder tells in first person the genesis of the brand/product.
3.5  Employee Spotlight / Team Content — Team members shown authentically.

## MACRO-CATEGORY 4: UGC & CREATOR CONTENT
4.1  UGC Classic — Authentic content from real customers: non-professional photos/videos. CTR 4x vs branded.
4.2  UGC Talking Head — Creator speaks directly to camera about their experience with the product.
4.3  Unboxing — Opening of the package: packaging, first impression, contents. Generates anticipation.
4.4  Haul — Presentation of multiple purchased products in a single video.
4.5  Try-On — Physical try-on of garments with reactions on fit, material, look.
4.6  Reaction Video — Spontaneous reaction to product: surprise, enthusiasm.
4.7  ASMR Product — Emphasis on sounds: opening, texture, application. No speech. Hypnotic.
4.8  Taste Test / Blind Test — Product trial for the first time with honest judgment.
4.9  Honest Review / "Brutally Honest" — Unfiltered review with pros and cons. Generates superior trust.
4.10 Ranking / Tier List — Classification of multiple products in categories (S/A/B/C/D).
4.11 Mashup / Compilation UGC — Fast montage of multiple UGC clips from different customers.
4.12 Whitelisted / Partnership Ad — Creator content promoted from the creator's account (not the brand's).

## MACRO-CATEGORY 5: SOCIAL PROOF & TRUST
5.1  Customer Review / Quote Card — Text review with stars, name and photo on product image.
5.2  Video Testimonial — Real customer speaks to camera about their experience.
5.3  Case Study / Customer Story — Structured story: situation, challenge, product, result.
5.4  Social Proof Aggregated — Numbers ("50,000+ customers"), media logos, award badges, aggregated ratings.
5.5  Press / "As Seen In" — Mentions from newspapers, magazines, TV shows.
5.6  Expert / Authority Endorsement — Sector professional validates the product (dermatologist, chef, engineer).
5.7  Influencer / Creator Endorsement — Creator presents the product in their own style, leveraging authority and following.
5.8  Awards / Certifications — Badges, awards, certifications (organic, cruelty-free).
5.9  Comment Box / Native Comment — Simulates real social comment below the product. Blends with feed.

## MACRO-CATEGORY 6: PROBLEM-SOLUTION & TRANSFORMATION
6.1  Problem-Solution (classic) — Two acts: recognizable problem, then product as solution.
6.2  Problem-Agitate-Solution (PAS) — Three acts: problem, amplification of consequences, solution.
6.3  Before / After — Split screen or sequence before/after use.
6.4  Pain Point Dramatization — The problem is exaggerated (with humor or dramatization).
6.5  Myth-Busting — Debunks common beliefs, positioning the product as truth.
6.6  Expectation vs. Reality — Humorous contrast between expectation and reality.
6.7  How It Started vs. How It's Going — Viral template showing evolution over time.
6.8  Result Tracking / Challenge — Documentation over time (7-day, 30-day challenge).
6.9  Switching Story — Customer tells why they abandoned the competitor for you.

## MACRO-CATEGORY 7: COMPARISON & COMPETITIVE
7.1  Us vs. Them — Direct comparison with competitor: table, split screen, narrative.
7.2  Us vs. Old Way — Comparison with traditional method or previous solution.
7.3  Side-by-Side Demo — Two products tested in parallel with tangible results.
7.4  "Why We're Different" — Unique differentiators without naming competitors. Implicit positioning.
7.5  Comparison Table — Static comparison table with check/X.

## MACRO-CATEGORY 8: EDUCATIONAL & INFORMATIONAL
8.1  How-To / Tutorial — Step-by-step guide to using the product or solving a problem.
8.2  Step-by-Step / Multi-frame — Sequential instructions in multiple frames. Frame 1: result, then steps, then CTA.
8.3  Explainer (Animated or Live) — Explains complex concept or product simply. Motion graphics or whiteboard.
8.4  Listicle / Benefits List — Numbered list (3, 5, 7 reasons why...). Scannable, immediate value.
8.5  Feature Highlight / Specs — Technical features, ingredients, specifications. Rational approach.
8.6  Infographic — Data, statistics and visuals in dense informational format.
8.7  Stat / Data Callout — Single statistical data point with strong visual impact.
8.8  FAQ Visual — Frequently asked questions in visual format. Resolves pre-purchase objections.
8.9  Tip & Hack / Life Hack — Practical advice involving the product. High save/share rate.
8.10 Educational Grid (2x3 / 3x3) — Visual grid with informational elements and product as answer.

## MACRO-CATEGORY 9: STORYTELLING & EMOTIONAL
9.1  Brand Story / Origin Story — Brand story, mission, "why". Emotional connection.
9.2  Customer Journey / Success Story — Complete customer path: problem, discovery, result.
9.3  Emotional Appeal — Deep emotions: nostalgia, joy, belonging, fulfillment.
9.4  Aspirational / Lifestyle — Sells the lifestyle, not the product. Evocative images.
9.5  Mini-Series / Story Arc — Sequence of connected ads in chapters ("tease, amplify, echo").
9.6  Day-in-the-Life (narrative) — Typical day showing the product in natural routine.
9.7  Humor / Comedy / Skit — Humor to capture attention and create positive association.
9.8  Storytime — Personal anecdote linked to the product, in narrative style.
9.9  Documentary-Style — Long, cinematic narrative, focus on the story.

## MACRO-CATEGORY 10: OFFER & PROMO-DRIVEN
10.1 Hard Offer / Promo — Direct communication of discount, coupon, limited offer.
10.2 Hard Promise — Strong promise ("Results in 30 days or refunded").
10.3 Countdown / Urgency — Timer or deadline to create urgency.
10.4 Scarcity / Limited Edition — Limited availability ("Only 50 pieces"). Scarcity psychological bias.
10.5 Free Shipping / Bonus Offer — Removal of purchase barrier as main message.
10.6 Seasonal / Holiday — Themed on season, holiday, event (Black Friday, Christmas).
10.7 New Launch / Announcement — Announces new product or feature. Novelty effect.
10.8 Price Anchor — Crossed-out price + discounted price, or daily cost.
10.9 Bundle / Kit Offer — Package at special price. Often in group shot or carousel.

## MACRO-CATEGORY 11: NATIVE & TREND-DRIVEN
11.1  Talking Head — Person speaks directly to camera. Intimate, conversational.
11.2  Lo-Fi / "Ugly Ads" — Intentionally unproduced, shot with phone. Look organic.
11.3  POV (Point of View) — First-person perspective. "POV: you discover our product."
11.4  Trend-Jacking / Trending Sound — Exploits viral trend adapted to the product. Window: 48-72 hours.
11.5  Meme / Internet Culture — Adaptation of popular memes to brand context.
11.6  Challenge / Branded Hashtag — Challenge replicable by users using the product.
11.7  Duet — Video placed side by side with another video. Reactions, comparisons, complements.
11.8  Stitch — Clip cut from another video + own content in sequence.
11.9  Reply to Comment — The ad picks up a real comment and responds in video.
11.10 Green Screen — Creator on custom background (images, websites, articles).
11.11 Screenshot / Native-Looking — Simulates real screenshot: notification, chat, email. Blends in feed.
11.12 Street Interview / Vox Pop — Casual interviews with people on the street on a topic related to the product.

## MACRO-CATEGORY 12: VISUAL DESIGN & PRODUCTION STYLE
12.1  Bold Text / Typography-First — Textual message as protagonist. Large font, contrast, no photo.
12.2  Quote Card — Quote (founder, customer, expert) in graphic format.
12.3  Minimalist / Clean — Essential design, lots of white space, one message. Premium.
12.4  Color Blocking — Contrasting and saturated color blocks. Strong scroll-stopping power.
12.5  Collage / Scrapbook — Multiple images, cutouts, overlaid texts in editorial style.
12.6  Mood Board — Aggregation of images, textures, palette to communicate an atmosphere.
12.7  Stop Motion — Frame-by-frame animation with real objects. Eye-catching.
12.8  GIF / Cinemagraph — Image with single element in motion. Halfway between static/video.
12.9  Motion Graphics / Animated — Animated graphics with text, icons, transitions.
12.10 Boomerang — Clip looping forward-backward. Hypnotic repetition.
12.11 Kinetic Text / Text Animation — Animated text in sync with audio/narration.
12.12 Timelapse — Temporal acceleration of a process.
12.13 Transition / Editing-Driven — Video based on creative transitions (outfit change, reveal).
12.14 Montage / Compilation — Fast sequence of different clips. Dynamic, high impact.
12.15 Satisfying / Oddly Satisfying — Repetitive movements, textures, colors that generate visual satisfaction.
12.16 Notepad / Handwritten — Handwritten text, blackboard, notepad. Simulates "unproduced" content.
12.17 Infographic Pin — Vertical image with data visualized graphically. High save rate.

## MACRO-CATEGORY 13: INTERACTIVE & IMMERSIVE
13.1 Poll / Quiz Ad — Interactive survey or quiz in the ad. [ONLY if UI elements visible]
13.2 AR Try-On / Virtual Preview — Virtual try-on of the product. [ONLY if AR overlay visible]
13.3 Shoppable Video — Video with clickable products. [ONLY if product tags/UI visible]
13.4 Playable Ad — Mini interactive playable experience. [ONLY if game UI visible]
13.5 360-Degree / Panoramic — Explorable content with visual rotation. [ONLY if navigation UI visible]
13.6 Gamified Ad — Game elements (challenges, scores, rewards). [ONLY if game mechanics visible]"""
