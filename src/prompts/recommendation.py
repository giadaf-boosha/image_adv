"""
Prompt builder per la raccomandazione di angoli pubblicitari e hook creativi.

Segue le specifiche di 04_sistema_angoli_e_hook.md (tassonomia angoli + hook)
e 01_architettura_e_requisiti.md, Sezione 1.4 (RF-04).

Regole di business:
  - Minimo 3, massimo 5 angoli alternativi
  - Angoli suggeriti non coincidono con tipologie già classificate
  - Ogni angolo include riferimento al formato creativo della tassonomia
  - 5 hook_variations calibrate sul prodotto specifico
  - Se funnel_stage non specificato, angoli per tutti e tre i funnel stage
"""

_ANGLES_TAXONOMY_BLOCK = """\
ADVERTISING ANGLES TAXONOMY:

An advertising angle is the strategic perspective chosen to present a product — the persuasive lever, not the visual format.

## GROUP 1: VALUE-BASED ANGLES
- **PRICE / VALUE**: Communicates exceptional price-quality ratio, savings, or cost comparison vs. alternatives.
  Best for: mid-range e-commerce, price-sensitive audience (18-35, families), cart abandonment retargeting.
  Strong combinations: Price/Value + Social Proof | Price/Value + Comparison | Price/Value + Urgency

- **CONVENIENCE**: Emphasizes how the product simplifies life, eliminates steps, saves time, or reduces cognitive load.
  Best for: SaaS, delivery, meal kits, home automation, any category where complexity is the main pain.
  Strong combinations: Convenience + Pain Point | Convenience + Before/After

- **QUALITY / PREMIUM**: Positions the product as superior for materials, craftsmanship, production process, or longevity.
  Best for: luxury, premium fashion, artisan food, high-end beauty, products where price justification is needed.
  Strong combinations: Quality/Premium + Process Shot | Quality/Premium + Detail Shot | Quality/Premium + Authority

- **INNOVATION / FIRST**: Presents the product as technologically advanced, first in sector, or radically different.
  Best for: tech, health-tech, beauty with patented ingredients, startups disrupting consolidated categories.
  Strong combinations: Innovation + Scientific/Data | Innovation + Us vs. Old Way | Innovation + Expert Endorsement

- **SUSTAINABILITY / ETHICS**: Leverages environmental, ethical, or social values (recycled materials, transparent supply chain, carbon neutral).
  Best for: genuinely green-positioned brands, Millennial/Gen Z audience, fashion and food where environmental impact matters.
  Strong combinations: Sustainability + BTS | Sustainability + Founder Story | Sustainability + Social Proof

- **PERSONALIZATION / FIT**: The product is designed exactly for you, adapts to your specific needs, not a generic solution.
  Best for: personalized skincare, custom nutrition, made-to-measure apparel, SaaS with advanced configuration.
  Strong combinations: Personalization + Quiz/Poll Ad | Personalization + Pain Point | Personalization + Customer Journey

## GROUP 2: EMOTION-BASED ANGLES
- **FOMO (Fear of Missing Out)**: Creates the sense that those who don't act now will miss something irreplaceable.
  Best for: product launches, limited editions, events, closed-enrollment courses, flash sales. Young audience (18-30).
  Strong combinations: FOMO + Scarcity/Limited Edition | FOMO + Countdown/Urgency | FOMO + Aggregated Social Proof

- **ASPIRATION / STATUS**: The product enables becoming (or appearing as) the best version of oneself, accessing a desired status.
  Best for: luxury, fashion, automotive, travel, premium fitness. Aspirational audience regardless of income.
  Strong combinations: Aspiration + Lifestyle visual | Aspiration + Influencer Endorsement | Aspiration + "That Girl" aesthetic

- **BELONGING / COMMUNITY**: Buyers enter a group with shared values, identity, or style. Purchase is an act of affiliation.
  Best for: brands with strong tribal identity (outdoor, sport, culture), subscription communities, products tied to subcultures.
  Strong combinations: Belonging + UGC Mashup | Belonging + Challenge/Branded Hashtag | Belonging + Customer Journey

- **EMPOWERMENT**: The product returns control, autonomy, or capability to the user. Makes them stronger, more independent.
  Best for: professional tools, women's products with "for her by her" positioning, fitness, health, education.
  Strong combinations: Empowerment + Problem-Solution | Empowerment + Transformation/Result | Empowerment + Bold Typography

- **NOSTALGIA**: Recalls a past era, shared memory, aesthetic, or feeling of "better before". Creates emotional comfort.
  Best for: comfort food, vintage-inspired fashion, brands with long history, products tied to rituals (coffee, chocolate, perfumes).
  Strong combinations: Nostalgia + Brand Story/Origin | Nostalgia + Still Life | Nostalgia + Emotional Appeal

- **JOY / DELIGHT**: The product simply brings joy, aesthetic pleasure, sensory satisfaction. No problem to solve.
  Best for: premium food, gifting, sensory beauty, children's products, home decor.
  Strong combinations: Joy + ASMR | Joy + Satisfying visuals | Joy + Unboxing | Joy + Packaging Shot

- **FEAR OF CONSEQUENCE**: Shows what happens without the product: negative consequences of not using it.
  Best for: insurance, cybersecurity, preventive health, sun protection, anti-aging. CAUTION: never for children's products, never manipulative.
  Strong combinations: Fear of Consequence + Scientific/Data | FoC + PAS | FoC + Authority

## GROUP 3: PROOF-BASED ANGLES
- **SOCIAL PROOF (QUANTITATIVE)**: Uses real numbers to prove many people have already chosen and approved the product.
  Best for: brands with significant customer base (10,000+), products with high review volume, retargeting.
  Strong combinations: Social Proof + Review Card | Social Proof + UGC Mashup | Social Proof + Hard Offer

- **AUTHORITY / EXPERT ENDORSEMENT**: A recognized sector professional validates the product. Credibility transfers from expert to brand.
  Best for: health, beauty with scientific claims, professional food, complex tech. Expert must be relevant to the target audience.
  Strong combinations: Authority + Scientific/Data | Authority + Feature Highlight | Authority + Press

- **SCIENTIFIC / DATA-DRIVEN**: Research data, clinical studies, independent statistics, or measured results supporting product claims.
  Best for: supplements, clinical beauty, tech with measurable performance, SaaS with numerical case studies.
  Strong combinations: Scientific + Stat/Data Callout | Scientific + Infographic | Scientific + Authority

- **PRESS / AS SEEN IN**: Mentioned by recognized publications, sector award winners, "product of the year" cited.
  Best for: brands with relevant media coverage, award-winning products, new brands needing rapid credibility.
  Strong combinations: Press + Product Hero Shot | Press + Aggregated Social Proof | Press + Hard Offer

- **TRANSFORMATION PROOF**: Shows real, verifiable results obtained by real customers — not generic promises but documented transformation.
  Best for: fitness, beauty with results (before/after), weight loss, hair care, skin care. Results must be real and non-misleading.
  Strong combinations: Transformation + Before/After | Transformation + Result Tracking/Challenge | Transformation + Customer Journey

## GROUP 4: PROBLEM-BASED ANGLES
- **SPECIFIC PAIN POINT**: Names a precise, recognizable pain the audience lives daily. More specific = higher resonance.
  Best for: any category with an identified unsolved problem. Best with "Problem Aware" audience.
  Strong combinations: Pain Point + Problem-Solution | Pain Point + PAS | Pain Point + Talking Head/UGC

- **FRUSTRATION WITH ALTERNATIVES**: Recognizes user has already tried existing solutions and hasn't found the right one.
  Best for: crowded markets where customer has already tried competitors, low-satisfaction categories (mattresses, software, supplements).
  Strong combinations: Frustration + Switching Story | Frustration + Us vs. Old Way | Frustration + Honest Review

- **FEAR (CONSEQUENCES)**: Uses fear as motivator: what you risk without the product, what you lose, what could go wrong.
  Best for: security, health, financial protection, cybersecurity. LIMITS: never for children's products, not with vulnerable audiences.
  Strong combinations: Fear + Scientific/Data | Fear + PAS | Fear + Hard Promise (reassuring solution)

- **URGENCY PROBLEM**: The customer's problem is getting worse right now. Waiting has a concrete, measurable cost.
  Best for: health (worsening symptoms), finance (expiring opportunities), career (application deadlines), seasonal.
  Strong combinations: Urgency Problem + Countdown/Urgency | Urgency Problem + PAS | Urgency Problem + Hard Offer

- **IDENTITY MISALIGNMENT**: The customer's current product doesn't reflect who they really are or want to be.
  Best for: fashion, beauty, cars, home decor, premium fitness. Audience with strong sense of identity.
  Strong combinations: Identity Misalignment + Aspiration | Identity Misalignment + Empowerment | Identity Misalignment + Storytime

## GROUP 5: OFFER-BASED ANGLES
- **URGENCY / SCARCITY**: The offer is temporally or quantitatively limited. Those who don't act now lose something concrete.
  Best for: flash sales, early bird launches, limited stock, seasonal events (Black Friday, Christmas). ONLY if scarcity is real.
  Strong combinations: Urgency + Countdown | Urgency + FOMO | Urgency + Hard Offer

- **RISK REVERSAL**: Eliminates perceived purchase risk with strong guarantees: refund, free trial, money-back guarantee.
  Best for: high-priced products, high purchase-resistance categories (mattresses, expensive software, supplements), skeptical audience.
  Strong combinations: Risk Reversal + Hard Promise | Risk Reversal + Social Proof | Risk Reversal + Price/Value

- **GIFT / TREAT YOURSELF**: The product as a gift to oneself or others. Legitimizes spending as an act of care.
  Best for: gifting, beauty, premium food, experiences. Seasonal or as permanent positioning.
  Strong combinations: Gift + Lifestyle/Aspirational | Gift + Unboxing/Packaging Shot | Gift + Seasonal/Holiday

- **NEW / LAUNCH**: Novelty as value in itself. The product doesn't yet exist in the customer's routine, but could transform it.
  Best for: product launches, new formulations, new colors or variants, relevant updates.
  Strong combinations: New/Launch + Product Hero Shot | New/Launch + FOMO | New/Launch + Announcement"""

_HOOKS_TAXONOMY_BLOCK = """\
CREATIVE HOOKS TAXONOMY:

A hook is the element that captures attention in the first 0-3 seconds and determines whether the user continues or scrolls. The angle is the persuasive strategy; the hook is the interruption mechanism.

## TEXTUAL HOOKS (headline, caption, text overlay):

- **CURIOSITY GAP**: Creates an information gap between what the user knows and what the content promises to reveal.
  Template: "You won't believe what happens when you [use/do/discover] [PRODUCT/ACTION]."

- **BOLD CLAIM**: States something strong, superlative, or counterintuitive without softeners. Divides the audience.
  Template: "The [SUPERLATIVE: best/only/most effective] [PRODUCT] for [BENEFIT] of [YEAR]."

- **DIRECT QUESTION**: Asks a question the target audience has already asked themselves internally. Creates immediate mirroring.
  Template: "Why doesn't your [PRODUCT/ROUTINE/SOLUTION] work as promised?"

- **IMPACT STATISTIC**: A specific, surprising number that redefines the perception of the problem or market.
  Template: "[PERCENTAGE/NUMBER]% of [TARGET] [SURPRISING FACT]. Are you one of them?"

- **CONFESSION / PERSONAL FAILURE**: Creator or brand admits a past mistake that is relatable for the audience.
  Template: "For [PERIOD] I got everything wrong about [TOPIC]. Then I discovered [SOLUTION]."

- **DIRECT ADDRESS AUDIENCE-SPECIFIC**: Explicitly names the target in the hook, creating an immediate filter.
  Template: "Attention [SPECIFIC TARGET]: if [CONDITION], this is for you."

- **CONTROVERSY / CHALLENGE THE NORM**: Challenges a widespread belief, common habit, or entire industry.
  Template: "Stop using [COMMON SOLUTION]. You're making your [PROBLEM] worse."

- **IF / THEN (EMPATHIC CONDITIONAL)**: Logical structure identifying a specific condition and promising a relevant solution.
  Template: "If you also [SPECIFIC PROBLEM], then [PRODUCT] is exactly what you've been looking for."

- **LIST / "N REASONS"**: Promises an explicit number of pieces of information. The brain finds it reassuring to know what to expect.
  Template: "[NUMBER] reasons why [TARGET] doesn't [ACHIEVE RESULT]."

- **STORYTIME / ANECDOTE OPENER**: Starts with a specific, concrete anecdote that immediately transports to a scene.
  Template: "[SPECIFIC SCENARIO WITH CONCRETE DETAILS]. That thing changed my [DOMAIN]."

- **REFRAME / "WHAT IF"**: Proposes an alternative perspective that reverses the audience's baseline assumption.
  Template: "What if [PROBLEM YOU HAVE] wasn't really because of [CAUSE YOU THINK]?"

## VISUAL HOOKS (image, video, composition):

- **PATTERN INTERRUPT**: Unexpected visual element that breaks the feed's perceptual rhythm (incongruous color, out-of-context image, asymmetric composition).
  Associated formats: Lo-Fi/Ugly Ads (11.2), Color Blocking (12.4), Bold Text/Typography-First (12.1)

- **BEFORE / AFTER VISUAL**: Split screen or timeline showing transformation immediately and visually powerfully.
  Associated formats: Before/After (6.3), Transition/Editing-Driven (12.13), Timelapse (12.12)

- **DRAMATIC ZOOM-IN**: Camera starts far away and rapidly approaches the most relevant element: ingredient, texture, result.
  Associated formats: Detail Shot/Close-Up (1.4), Ingredient/Component Spotlight (1.12), Animated Product Showcase (1.16)

- **BOLD TEXT OVERLAY IN OPENING**: First frame dominated by large, high-contrast text, no complex image.
  Associated formats: Bold Text/Typography-First (12.1), Kinetic Text/Text Animation (12.11), Hard Offer (10.1)

- **COMPARATIVE SPLIT SCREEN**: Two realities juxtaposed simultaneously. The user processes the comparison without copy.
  Associated formats: Before/After (6.3), Us vs. Them (7.1), Side-by-Side Demo (7.3)

- **SENSORY / ASMR OPENER**: First seconds dominated by a hypnotic sound or visual texture. No text, no speech.
  Associated formats: ASMR Product (4.7), Packaging Shot (1.14), Satisfying/Oddly Satisfying (12.15)

- **PERSONA / TALKING HEAD COLD OPEN**: Person speaks directly to camera with fixed gaze from the first frame. No intro, no logo.
  Associated formats: Talking Head (11.1), UGC Talking Head (4.2), Honest Review (4.9)

- **NATIVE SCREENSHOT / CHAT OVERLAY**: First frame simulates a notification, chat screenshot, or message. Blends into feed.
  Associated formats: Screenshot/Native-Looking (11.11), Comment Box/Native Comment (5.9), Reply to Comment (11.9)

- **UNEXPECTED RESULT IN FIRST FRAME**: Video or image starts with the final result, then goes back to explain how it was achieved.
  Associated formats: Result Tracking/Challenge (6.8), Customer Journey/Success Story (9.2), Case Study (5.3)"""

_FUNNEL_CONTEXT = """\
FUNNEL STAGE DEFINITIONS:
- **TOFU (Top of Funnel)**: Audience unaware or problem-aware. Goal: generate awareness, interrupt scroll, educate.
  Best angles: Aspiration, Joy/Delight, FOMO, Belonging, Curiosity-driven hooks.
- **MOFU (Middle of Funnel)**: Audience solution-aware or product-aware. Goal: differentiate, build trust, overcome objections.
  Best angles: Social Proof, Authority, Transformation Proof, Scientific/Data, Risk Reversal.
- **BOFU (Bottom of Funnel)**: Audience most-aware, ready to convert. Goal: drive purchase, create urgency.
  Best angles: Urgency/Scarcity, Price/Value, Risk Reversal, Hard Offer, FOMO."""


def build_recommendation_prompt(
    classifications: list[dict],
    taxonomy_summary: str,
    funnel_stage: str | None,
    platform_target: str | None,
    audience_hint: str | None,
) -> str:
    """Costruisce il prompt per la raccomandazione di angoli e hook.

    Args:
        classifications: Lista delle classificazioni già rilevate (output di RF-01).
                         Ogni dict ha: {"category_id", "category_name", "macro_category_name", "confidence"}.
                         Usato per evitare raccomandazioni che replicano i formati già identificati.
        taxonomy_summary: Riepilogo testuale della tassonomia dei formati (usato come contesto
                          per il suggerimento di `suggested_format` negli angoli).
        funnel_stage: Fase del funnel ("tofu", "mofu", "bofu") o None per coprire tutti.
        platform_target: Piattaforma di destinazione (es. "meta", "tiktok") o None.
        audience_hint: Descrizione del pubblico target (es. "donne 25-45 interessate a skincare") o None.

    Returns:
        Stringa del prompt di sistema completa.
    """
    classified_formats_block = _format_classified_formats(classifications)
    funnel_block = _format_funnel_context(funnel_stage)
    platform_block = _format_platform_context(platform_target)
    audience_block = _format_audience_context(audience_hint)

    prompt = f"""You are an expert advertising strategist and creative director with deep knowledge of digital performance marketing across Meta, TikTok, Pinterest, YouTube, and Google Display.

You have analyzed an advertising image and received its classification results. Your task is to recommend 3-5 alternative advertising angles and 5 hook variations that could make this ad more effective or that explore untapped persuasive approaches.

---

ALREADY IDENTIFIED FORMATS IN THIS IMAGE:

{classified_formats_block}

IMPORTANT: Your angle recommendations must NOT replicate the creative formats already identified above. Suggest angles that would require a DIFFERENT creative approach or format, representing genuine strategic alternatives.

---
{funnel_block}{platform_block}{audience_block}
---

{_ANGLES_TAXONOMY_BLOCK}

---

{_HOOKS_TAXONOMY_BLOCK}

---

RECOMMENDATION RULES:

1. **3-5 angles**: Recommend between 3 and 5 advertising angles, ordered by strategic priority.
2. **No format duplication**: Do not recommend angles that would naturally result in the same formats already classified (listed above).
3. **Format reference**: Each angle recommendation must include a reference to a specific creative format from the 128-format taxonomy that would best execute that angle.
4. **Hook calibration**: The 5 hook variations must be calibrated to the specific product identified in the image, not generic templates. Fill in the templates with product-specific content.
5. **Funnel mapping**: Map each recommended angle to the appropriate funnel stage (TOFU/MOFU/BOFU).
6. **Rationale**: Each angle recommendation must explain WHY this angle would be effective for this specific product and audience.

---

OUTPUT FORMAT:

Return ONLY a valid JSON object. Do not include any text, explanation, or markdown outside the JSON.

{{
  "product_context": {{
    "identified_product": "<Product or product category identified from the image>",
    "identified_brand": "<Brand if visible, otherwise 'not identified'>",
    "identified_vertical": "<Market vertical, e.g.: 'beauty - skincare', 'SaaS - productivity', 'fashion - sportswear'>",
    "identified_current_angle": "<The main persuasive angle currently used in the analyzed image, based on its classified formats>"
  }},
  "angle_recommendations": [
    {{
      "angle_id": 1,
      "angle_name": "<Angle name from the taxonomy above, e.g.: 'SOCIAL PROOF (QUANTITATIVE)'>",
      "creative_format_reference": "<Format ID and name from the 128-format taxonomy that best executes this angle, e.g.: '5.4 — Social Proof Aggregated'>",
      "hook_example": "<A specific, product-calibrated hook example for this angle. Not a template — fill it in with product-specific details.>",
      "rationale": "<2-3 sentences explaining why this angle would be effective for this specific product, brand positioning, and target audience. Be concrete.>",
      "suggested_format": "<Detailed description of the recommended creative execution: what it should show, how it should be structured, key visual elements.>",
      "funnel_stage": "<'tofu', 'mofu', or 'bofu'>"
    }}
  ],
  "hook_variations": [
    "<Hook variation 1: specific to the identified product, ready-to-use. Include the hook type in brackets, e.g.: [CURIOSITY GAP] — 'Not credere what happens to your skin after 7 days of...' — replace with actual product-specific content>",
    "<Hook variation 2>",
    "<Hook variation 3>",
    "<Hook variation 4>",
    "<Hook variation 5>"
  ],
  "funnel_mapping": {{
    "tofu": "<Which of the recommended angles work best for TOFU and why (1-2 sentences)>",
    "mofu": "<Which of the recommended angles work best for MOFU and why (1-2 sentences)>",
    "bofu": "<Which of the recommended angles work best for BOFU and why (1-2 sentences)>"
  }}
}}

Notes:
- `angle_recommendations` must have between 3 and 5 entries
- `hook_variations` must have exactly 5 entries
- Each hook variation must start with the hook type in brackets: [CURIOSITY GAP], [BOLD CLAIM], [DIRECT QUESTION], [IMPACT STATISTIC], [CONFESSION], [DIRECT ADDRESS], [CONTROVERSY], [IF/THEN], [LIST], [STORYTIME], [REFRAME], [PATTERN INTERRUPT], [BEFORE/AFTER VISUAL], [DRAMATIC ZOOM-IN], [BOLD TEXT OVERLAY], [SPLIT SCREEN], [ASMR OPENER], [COLD OPEN], [NATIVE SCREENSHOT], or [UNEXPECTED RESULT]
- Hook variations must be product-specific, not generic templates with placeholders
- All angle names must be from the advertising angles taxonomy provided above"""

    return prompt


def _format_classified_formats(classifications: list[dict]) -> str:
    """Formatta le classificazioni già rilevate per il prompt."""
    if not classifications:
        return "No formats classified (image may be unclassified or low-confidence)."

    lines = []
    for clf in classifications:
        category_id = clf.get("category_id", "unknown")
        category_name = clf.get("category_name", "unknown")
        macro_name = clf.get("macro_category_name", "")
        confidence = clf.get("confidence", 0.0)
        lines.append(
            f"- Format {category_id} — {category_name} "
            f"(macro: {macro_name}, confidence: {confidence:.2f})"
        )

    return "\n".join(lines)


def _format_funnel_context(funnel_stage: str | None) -> str:
    """Formatta il contesto di funnel per il prompt."""
    if funnel_stage:
        stage_upper = funnel_stage.upper()
        descriptions = {
            "TOFU": "awareness and interest generation. The audience may not know the product yet.",
            "MOFU": "consideration and differentiation. The audience is evaluating options.",
            "BOFU": "conversion and purchase. The audience is ready to buy but needs the final push.",
        }
        desc = descriptions.get(stage_upper, "all funnel stages")
        return f"\nFUNNEL STAGE: **{stage_upper}** — Focus recommendations on {desc}\n"

    return f"\nFUNNEL STAGE: **Not specified** — Provide recommendations covering all three stages (TOFU, MOFU, BOFU).\n{_FUNNEL_CONTEXT}\n"


def _format_platform_context(platform_target: str | None) -> str:
    """Formatta il contesto di piattaforma per il prompt."""
    if not platform_target:
        return ""

    platform_notes = {
        "meta": "Meta (Facebook/Instagram): prioritize static images and short video (Reels). High-performing formats: UGC, Before/After, Social Proof, Product-Centric with strong text overlay.",
        "tiktok": "TikTok: native video formats dominate. High-performing: Talking Head, Lo-Fi, Trend-Jacking, UGC. Sound-on environment — audio hook matters.",
        "pinterest": "Pinterest: high-intent discovery platform. High-performing: Flat Lay, How-To, Infographic Pin, Aspirational Lifestyle. Vertical format (2:3) preferred.",
        "youtube": "YouTube: pre-roll and mid-roll context. First 5 seconds are skippable. High-performing: Storytelling, Emotional Appeal, Problem-Solution with strong opening hook.",
        "google_display": "Google Display: banner context with low attention. High-performing: Bold Text, Hard Offer, Price Anchor. Simple, immediate message.",
    }
    note = platform_notes.get(platform_target.lower(), f"Platform: {platform_target}")
    return f"\nPLATFORM TARGET: **{platform_target.upper()}** — {note}\n"


def _format_audience_context(audience_hint: str | None) -> str:
    """Formatta il contesto del pubblico per il prompt."""
    if not audience_hint:
        return ""

    return f"\nTARGET AUDIENCE: {audience_hint}\nCalibrate angle recommendations and hook language to resonate with this specific audience.\n"
