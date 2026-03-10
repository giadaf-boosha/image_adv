# Pipeline di Classificazione AI per Formati Creativi Advertising

> Documento tecnico per sviluppatori. Versione: 1.0 | Marzo 2026
> Prerequisito: `mappatura_formati_creativi_adv.md` (128 formati, 13 macro-categorie)

---

## Sezione 1: Approccio alla Classificazione

### Perché un approccio multimodale (vision + language)

La classificazione dei formati creativi pubblicitari non è una task di riconoscimento di oggetti o scene generiche. È una task di **comprensione semantica composita**: un'immagine va classificata non solo per cosa mostra, ma per come è strutturata narrativamente, quale intenzione comunicativa esprime, e come si posiziona rispetto a schemi retorici consolidati (Problem-Solution, Before/After, UGC, ecc.).

Un classificatore tradizionale basato solo su feature visive (CNN, ResNet) fallisce su questa task per tre motivi fondamentali:

1. **Sovrapposizione semantica alta**: un "UGC Talking Head" (4.2) e un "Video Testimonial" (5.2) sono quasi identici visivamente. La distinzione sta nel contesto narrativo e nel tono, non nei pixel.
2. **Tassonomia non visivamente discriminante**: molte categorie della sezione 12 (Visual Design) sono stili che coesistono con categorie di contenuto di altre sezioni. Un classificatore single-label non può gestire questa geometria.
3. **Generalizzazione a zero-shot**: 128 tipologie rendono impraticabile raccogliere abbastanza esempi labeled per ogni classe, specialmente per le sotto-tipologie più rare (es. 11.7 Duet, 13.4 Playable Ad).

Un approccio multimodale che combina embedding visivi con ragionamento linguistico permette di:
- Descrivere il contenuto dell'immagine in linguaggio naturale
- Ragionare sulla struttura narrativa e sulle intenzioni comunicative
- Fare zero-shot classification su tutte le 128 tipologie senza training dedicato

---

### Confronto degli approcci

#### a) Classificatore fine-tuned (CLIP ViT-L/14, SigLIP)

**Come funziona:** Si effettua fine-tuning di CLIP (OpenAI) o SigLIP (Google) su un dataset labeled di creativi pubblicitari. L'encoder visivo produce embedding; un classification head finale produce logit per ogni classe.

**Pro:**
- Latenza molto bassa in inference (<50ms su GPU A10)
- Costo per predizione molto contenuto dopo il training
- Deterministico e riproducibile
- Non dipende da API esterne in produzione

**Contro:**
- Richiede dataset labeled: minimo 50-100 esempi per classe per fare fine-tuning decente, quindi 6.400-12.800 immagini annotate
- Gestione multi-label richiede binary cross-entropy + soglie per ogni classe, difficile da calibrare
- Le classi con scarsi esempi (long tail della tassonomia) avranno performance scadenti
- Non produce spiegazioni: nessuna descrizione di cosa ha visto il modello
- Ogni aggiornamento della tassonomia richiede re-training

**Modelli di riferimento reali:**
- `openai/clip-vit-large-patch14` (Hugging Face)
- `google/siglip-so400m-patch14-384` (Hugging Face)

**Quando usarlo:** Solo se si dispone di >10.000 immagini annotate e si ha un vincolo stringente di latenza (<100ms) e di costo per query.

---

#### b) LLM multimodale con prompt engineering (GPT-4o, Claude, Gemini)

**Come funziona:** L'immagine viene inviata direttamente a un LLM multimodale insieme a un prompt che descrive la tassonomia completa. Il modello restituisce le tipologie identificate con confidence score in formato JSON.

**Pro:**
- Zero esempi di training richiesti: funziona subito sulla tassonomia completa
- Produce output ricchi: descrizione, classificazione, reasoning
- Aggiornamento della tassonomia = modifica del prompt (nessun re-training)
- Gestione nativa del multi-label
- Spiega le scelte, abilitando audit e debug

**Contro:**
- Latenza più alta (1-5 secondi per immagine via API)
- Costo per query significativo ($0.01-0.05 per immagine con GPT-4o)
- Output non deterministico (variabilità con temperature > 0)
- Dipendenza da API esterne (SLA, rate limits)
- Hallucination risk: il modello può inventare reasoning non ancorato all'immagine

**Modelli di riferimento reali:**
- `gpt-4o` (OpenAI API, vision nativa)
- `claude-sonnet-4-6` (Anthropic API, vision nativa)
- `gemini-2.0-flash` (Google AI API, vision nativa, più economico)

**Quando usarlo:** Fase di avvio del progetto, dataset di labeling, casi d'uso con volumi bassi (<10.000 immagini/giorno).

---

#### c) Approccio ibrido (embedding + LLM)

**Come funziona:** La pipeline è in due stadi.
- **Stadio 1 (veloce):** Un encoder visivo leggero (CLIP) produce un embedding dell'immagine. Tramite nearest-neighbor search su un index di esempi labeled, si identifica la macro-categoria più probabile e si restringono le sotto-tipologie candidate.
- **Stadio 2 (preciso):** Solo per le sotto-tipologie candidate (non per tutte le 128), si invoca l'LLM multimodale con un prompt ridotto, limitando la ricerca al sottoinsieme rilevante.

**Pro:**
- Riduce il costo dell'LLM del 60-80% limitando il prompt alle classi candidate
- Riduce la latenza totale rispetto al puro LLM
- Combina la velocità dell'embedding con il ragionamento dell'LLM
- Più robusto all'hallucination: l'LLM opera su un insieme ristretto di opzioni

**Contro:**
- Architettura più complessa da sviluppare e mantenere
- Richiede un index vettoriale (Chroma, Weaviate, Pinecone) e un dataset minimo di esempi per il retrieval
- Bug in Stadio 1 si propagano a Stadio 2 (errori di macro-categoria non recuperabili)

---

### Raccomandazione

**Per il lancio iniziale: approccio (b) LLM multimodale puro con GPT-4o o Gemini 2.0 Flash.**

Motivazione: la tassonomia è nuova, non esiste ancora un dataset labeled. La priorità è validare la tassonomia stessa (alcune tipologie potrebbero risultare difficilmente distinguibili) prima di investire in infrastruttura di embedding. Il costo API è accettabile a volumi iniziali.

**Roadmap verso approccio (c) ibrido** quando si raggiungono >500 immagini classificate manualmente: usare quel dataset per costruire un CLIP index e ridurre il costo LLM per le query ad alto volume.

| Criterio | Fine-tuned | LLM Puro | Ibrido |
|---|---|---|---|
| Tempo al primo deploy | Alto (mesi) | Basso (giorni) | Medio (settimane) |
| Costo per query | Molto basso | Alto | Medio |
| Qualità su classi rare | Bassa | Alta | Alta |
| Latenza | <100ms | 2-5s | 500ms-2s |
| Necessità di dataset | Alta | Nulla | Minima |
| Aggiornamento tassonomia | Re-training | Solo prompt | Partial re-index |
| Output spiegabile | No | Sì | Sì |

---

## Sezione 2: Prompt Engineering per la Classificazione

### Prompt principale di classificazione

Il prompt seguente è pronto per essere usato con GPT-4o o Claude Sonnet via API. La variabile `{image}` rappresenta l'immagine inviata nel campo `image_url` o `base64` della richiesta multimodale.

```
SYSTEM:
You are an expert advertising creative analyst. Your task is to classify advertising images according to a precise taxonomy of 128 creative formats organized in 13 macro-categories.

You must:
1. Analyze the image carefully before classifying
2. Assign ALL applicable format types (multi-label classification)
3. Provide a confidence score (0-100) for each identified format
4. Only include formats with confidence >= 15
5. Return a structured JSON response strictly following the schema provided

Be precise and conservative: only assign a format if you can clearly identify its characteristics in the image. Do not assign formats based on assumptions about what is not visible.

---

TAXONOMY OF 128 ADVERTISING CREATIVE FORMATS:

## MACRO-CATEGORY 1: PRODUCT-CENTRIC (Product at the Center)
1.1  Product Only / White Background - Product isolated on white or neutral background. Clean, minimal, distraction-free.
1.2  Product on Colored Background - Product on vivid colored background to stand out in feed.
1.3  Hero Shot - High-quality product image with curated lighting, slight suggestive context.
1.4  Detail Shot / Close-Up - Zoom on texture, materials, finishes, stitching, ingredients.
1.5  Scale Shot - Product next to common objects (hands, people) to communicate real dimensions.
1.6  Product in Context / In-Situ - Product in its natural use environment (sofa in living room, laptop on desk).
1.7  Flat Lay / Knolling - Products arranged from above in orderly geometric composition. Instagram-native aesthetic.
1.8  Still Life - Artistic composition of product with scenic elements (flowers, fabrics, materials).
1.9  Still Life + Text Overlay - Still life with overlaid text: claim, benefit, price, offer.
1.10 Product Collection / Grid - Multiple products in grid or unique composition. Line, collection, catalog in one frame.
1.11 Product Annotated / Point-Out - Image with arrows, labels, callouts highlighting specific features.
1.12 Ingredient / Component Spotlight - Focus on a single key ingredient or component.
1.13 360 / Multi-Angle - Product shot from multiple angles for complete view. Often in carousel.
1.14 Packaging Shot - Product in its packaging. Enhances brand experience.
1.15 Bundle / Kit Shot - Package of complementary products presented together.
1.16 Animated Product Showcase - 3D animation or motion graphics: rotation, component explosion, effects.

## MACRO-CATEGORY 2: LIFESTYLE & CONTEXT (Product in Real Life)
2.1  Lifestyle / Product in Context - Product inserted in aspirational or real environment (home, nature, office).
2.2  Product Worn / In-Use - Real people wearing or using the product.
2.3  Day in the Life / Mini Vlog - Daily routine of a person with the product naturally integrated.
2.4  GRWM (Get Ready With Me) - Person gets ready (makeup, outfit, skincare) using the product.
2.5  Morning/Night Routine - Sequence of products used in morning or evening routine.
2.6  OOTD (Outfit of the Day) - Complete outfit, often with transitions or zoom.
2.7  What I Eat in a Day - All meals of the day with food products or kitchen tools.
2.8  Study/Work with Me - Companion format: viewer accompanies creator during an activity.
2.9  "That Girl" / Clean Aesthetic - Tidy, healthy, curated lifestyle. Neutral palette, clean spaces, minimal products.

## MACRO-CATEGORY 3: BEHIND THE SCENES & CRAFT
3.1  Behind the Scenes (BTS) - Look behind the scenes: production, team, laboratory. Transparency and authenticity.
3.2  Process Shot / How It's Made - Process of creation or working of the product. Justifies premium price.
3.3  Pack an Order with Me - Preparation of an order, often in ASMR/satisfying style.
3.4  Founder Story - Founder tells in first person the genesis of the brand/product.
3.5  Employee Spotlight / Team Content - Team members shown authentically.

## MACRO-CATEGORY 4: UGC & CREATOR CONTENT
4.1  UGC Classic - Authentic content from real customers: non-professional photos/videos. CTR 4x vs branded.
4.2  UGC Talking Head - Creator speaks directly to camera about their experience with the product.
4.3  Unboxing - Opening of the package: packaging, first impression, contents. Generates anticipation.
4.4  Haul - Presentation of multiple purchased products in a single video.
4.5  Try-On - Physical try-on of garments with reactions on fit, material, look.
4.6  Reaction Video - Spontaneous reaction to product: surprise, enthusiasm.
4.7  ASMR Product - Emphasis on sounds: opening, texture, application. No speech. Hypnotic.
4.8  Taste Test / Blind Test - Product trial for the first time with honest judgment.
4.9  Honest Review / "Brutally Honest" - Unfiltered review with pros and cons. Generates superior trust.
4.10 Ranking / Tier List - Classification of multiple products in categories (S/A/B/C/D).
4.11 Mashup / Compilation UGC - Fast montage of multiple UGC clips from different customers.
4.12 Whitelisted / Partnership Ad - Creator content promoted from the creator's account (not the brand's).

## MACRO-CATEGORY 5: SOCIAL PROOF & TRUST
5.1  Customer Review / Quote Card - Text review with stars, name and photo on product image.
5.2  Video Testimonial - Real customer speaks to camera about their experience.
5.3  Case Study / Customer Story - Structured story: situation, challenge, product, result.
5.4  Social Proof Aggregated - Numbers ("50,000+ customers"), media logos, award badges, aggregated ratings.
5.5  Press / "As Seen In" - Mentions from newspapers, magazines, TV shows.
5.6  Expert / Authority Endorsement - Sector professional validates the product (dermatologist, chef, engineer).
5.7  Influencer / Creator Endorsement - Creator presents the product in their own style, leveraging authority and following.
5.8  Awards / Certifications - Badges, awards, certifications (organic, cruelty-free).
5.9  Comment Box / Native Comment - Simulates real social comment below the product. Blends with feed.

## MACRO-CATEGORY 6: PROBLEM-SOLUTION & TRANSFORMATION
6.1  Problem-Solution (classic) - Two acts: recognizable problem, then product as solution.
6.2  Problem-Agitate-Solution (PAS) - Three acts: problem, amplification of consequences, solution.
6.3  Before / After - Split screen or sequence before/after use.
6.4  Pain Point Dramatization - The problem is exaggerated (with humor or dramatization).
6.5  Myth-Busting - Debunks common beliefs, positioning the product as truth.
6.6  Expectation vs. Reality - Humorous contrast between expectation and reality.
6.7  How It Started vs. How It's Going - Viral template showing evolution over time.
6.8  Result Tracking / Challenge - Documentation over time (7-day, 30-day challenge).
6.9  Switching Story - Customer tells why they abandoned the competitor for you.

## MACRO-CATEGORY 7: COMPARISON & COMPETITIVE
7.1  Us vs. Them - Direct comparison with competitor: table, split screen, narrative.
7.2  Us vs. Old Way - Comparison with traditional method or previous solution.
7.3  Side-by-Side Demo - Two products tested in parallel with tangible results.
7.4  "Why We're Different" - Unique differentiators without naming competitors. Implicit positioning.
7.5  Comparison Table - Static comparison table with check/X.

## MACRO-CATEGORY 8: EDUCATIONAL & INFORMATIONAL
8.1  How-To / Tutorial - Step-by-step guide to using the product or solving a problem.
8.2  Step-by-Step / Multi-frame - Sequential instructions in multiple frames. Frame 1: result, then steps, then CTA.
8.3  Explainer (Animated or Live) - Explains complex concept or product simply. Motion graphics or whiteboard.
8.4  Listicle / Benefits List - Numbered list (3, 5, 7 reasons why...). Scannable, immediate value.
8.5  Feature Highlight / Specs - Technical features, ingredients, specifications. Rational approach.
8.6  Infographic - Data, statistics and visuals in dense informational format.
8.7  Stat / Data Callout - Single statistical data point with strong visual impact.
8.8  FAQ Visual - Frequently asked questions in visual format. Resolves pre-purchase objections.
8.9  Tip & Hack / Life Hack - Practical advice involving the product. High save/share rate.
8.10 Educational Grid (2x3 / 3x3) - Visual grid with informational elements and product as answer.

## MACRO-CATEGORY 9: STORYTELLING & EMOTIONAL
9.1  Brand Story / Origin Story - Brand story, mission, "why". Emotional connection.
9.2  Customer Journey / Success Story - Complete customer path: problem, discovery, result.
9.3  Emotional Appeal - Deep emotions: nostalgia, joy, belonging, fulfillment.
9.4  Aspirational / Lifestyle - Sells the lifestyle, not the product. Evocative images.
9.5  Mini-Series / Story Arc - Sequence of connected ads in chapters ("tease, amplify, echo").
9.6  Day-in-the-Life (narrative) - Typical day showing the product in natural routine.
9.7  Humor / Comedy / Skit - Humor to capture attention and create positive association.
9.8  Storytime - Personal anecdote linked to the product, in narrative style.
9.9  Documentary-Style - Long, cinematic narrative, focus on the story.

## MACRO-CATEGORY 10: OFFER & PROMO-DRIVEN
10.1 Hard Offer / Promo - Direct communication of discount, coupon, limited offer.
10.2 Hard Promise - Strong promise ("Results in 30 days or refunded").
10.3 Countdown / Urgency - Timer or deadline to create urgency.
10.4 Scarcity / Limited Edition - Limited availability ("Only 50 pieces"). Scarcity psychological bias.
10.5 Free Shipping / Bonus Offer - Removal of purchase barrier as main message.
10.6 Seasonal / Holiday - Themed on season, holiday, event (Black Friday, Christmas).
10.7 New Launch / Announcement - Announces new product or feature. Novelty effect.
10.8 Price Anchor - Crossed-out price + discounted price, or daily cost.
10.9 Bundle / Kit Offer - Package at special price. Often in group shot or carousel.

## MACRO-CATEGORY 11: NATIVE & TREND-DRIVEN
11.1  Talking Head - Person speaks directly to camera. Intimate, conversational.
11.2  Lo-Fi / "Ugly Ads" - Intentionally unproduced, shot with phone. Look organic.
11.3  POV (Point of View) - First-person perspective. "POV: you discover our product."
11.4  Trend-Jacking / Trending Sound - Exploits viral trend adapted to the product. Window: 48-72 hours.
11.5  Meme / Internet Culture - Adaptation of popular memes to brand context.
11.6  Challenge / Branded Hashtag - Challenge replicable by users using the product. Generates organic UGC.
11.7  Duet - Video placed side by side with another video. Reactions, comparisons, complements.
11.8  Stitch - Clip cut from another video + own content in sequence.
11.9  Reply to Comment - The ad picks up a real comment and responds in video.
11.10 Green Screen - Creator on custom background (images, websites, articles).
11.11 Screenshot / Native-Looking - Simulates real screenshot: notification, chat, email. Blends in feed.
11.12 Street Interview / Vox Pop - Casual interviews with people on the street on a topic related to the product.

## MACRO-CATEGORY 12: VISUAL DESIGN & PRODUCTION STYLE
12.1  Bold Text / Typography-First - Textual message as protagonist. Large font, contrast, no photo.
12.2  Quote Card - Quote (founder, customer, expert) in graphic format.
12.3  Minimalist / Clean - Essential design, lots of white space, one message. Premium.
12.4  Color Blocking - Contrasting and saturated color blocks. Strong scroll-stopping power.
12.5  Collage / Scrapbook - Multiple images, cutouts, overlaid texts in editorial style.
12.6  Mood Board - Aggregation of images, textures, palette to communicate an atmosphere.
12.7  Stop Motion - Frame-by-frame animation with real objects. Eye-catching.
12.8  GIF / Cinemagraph - Image with single element in motion. Halfway between static/video.
12.9  Motion Graphics / Animated - Animated graphics with text, icons, transitions.
12.10 Boomerang - Clip looping forward-backward. Hypnotic repetition.
12.11 Kinetic Text / Text Animation - Animated text in sync with audio/narration.
12.12 Timelapse - Temporal acceleration of a process.
12.13 Transition / Editing-Driven - Video based on creative transitions (outfit change, reveal).
12.14 Montage / Compilation - Fast sequence of different clips. Dynamic, high impact.
12.15 Satisfying / Oddly Satisfying - Repetitive movements, textures, colors that generate visual satisfaction.
12.16 Notepad / Handwritten - Handwritten text, blackboard, notepad. Simulates "unproduced" content.
12.17 Infographic Pin - Vertical image with data visualized graphically. High save rate.

## MACRO-CATEGORY 13: INTERACTIVE & IMMERSIVE
13.1 Poll / Quiz Ad - Interactive survey or quiz in the ad.
13.2 AR Try-On / Virtual Preview - Virtual try-on of the product (glasses, makeup, furniture).
13.3 Shoppable Video - Video with clickable products. Purchase without leaving.
13.4 Playable Ad - Mini interactive playable experience.
13.5 360-Degree / Panoramic - Explorable content with visual rotation.
13.6 Gamified Ad - Game elements (challenges, scores, rewards).

---

USER:
Analyze the advertising image provided and classify it according to the taxonomy above.

Return ONLY a valid JSON object with this exact structure:

{
  "image_description": "<Detailed description in English of what you see in the image: subjects, setting, composition, visual style, text visible, colors, mood. 3-5 sentences.>",
  "product_sector": "<Identified product or sector (e.g.: 'skincare - face serum', 'SaaS - project management tool', 'fashion - women sportswear'). Write 'unknown' if not identifiable.>",
  "detected_formats": [
    {
      "format_id": "<e.g.: 6.3>",
      "format_name": "<e.g.: Before / After>",
      "macro_category_id": <integer, e.g.: 6>,
      "macro_category_name": "<e.g.: PROBLEM-SOLUTION & TRANSFORMATION>",
      "confidence": <integer 0-100>,
      "reasoning": "<One sentence explaining which specific visual or narrative elements in the image support this classification.>"
    }
  ],
  "primary_format": {
    "format_id": "<format_id of the single most confident classification>",
    "format_name": "<name>",
    "confidence": <integer>
  },
  "classification_notes": "<Optional: any ambiguity, overlapping formats, or elements that made classification difficult. Leave empty string if none.>"
}

Rules:
- Include ONLY formats with confidence >= 15
- Sort detected_formats by confidence descending
- The primary_format must be the format with the highest confidence in detected_formats
- Do not include formats not present in the taxonomy
- Do not return any text outside the JSON object
```

### Schema JSON atteso (esempio di output)

```json
{
  "image_description": "Split-screen static image. Left side shows a woman with dull, uneven skin tone. Right side shows the same woman with visibly clearer, brighter skin. A serum bottle is placed at the center bottom with the brand logo. Text overlay reads 'Week 1 vs Week 4'. Warm neutral background, professional lighting.",
  "product_sector": "skincare - brightening face serum",
  "detected_formats": [
    {
      "format_id": "6.3",
      "format_name": "Before / After",
      "macro_category_id": 6,
      "macro_category_name": "PROBLEM-SOLUTION & TRANSFORMATION",
      "confidence": 95,
      "reasoning": "The image is explicitly structured as a split-screen before/after comparison with visible skin transformation and week labels."
    },
    {
      "format_id": "1.3",
      "format_name": "Hero Shot",
      "macro_category_id": 1,
      "macro_category_name": "PRODUCT-CENTRIC",
      "confidence": 42,
      "reasoning": "The serum bottle is prominently featured in the center with professional lighting, functioning as a secondary hero product shot."
    },
    {
      "format_id": "6.8",
      "format_name": "Result Tracking / Challenge",
      "macro_category_id": 6,
      "macro_category_name": "PROBLEM-SOLUTION & TRANSFORMATION",
      "confidence": 38,
      "reasoning": "The 'Week 1 vs Week 4' labeling implies a time-tracked challenge documentation structure."
    }
  ],
  "primary_format": {
    "format_id": "6.3",
    "format_name": "Before / After",
    "confidence": 95
  },
  "classification_notes": "Formats 6.3 and 6.8 overlap significantly in this image. 6.3 is dominant due to the explicit split-screen visual structure."
}
```

---

## Sezione 3: Sistema di Detection Nuove Tipologie

### Logica per determinare "fuori tassonomia"

Un'immagine è considerata potenzialmente fuori tassonomia quando si verificano una o più delle seguenti condizioni:

**Condizione A — Bassa confidence su tutti i formati rilevati:**
Nessun formato nella risposta del classificatore supera confidence 40. Questo indica che il modello non trova ancoraggi solidi nella tassonomia esistente.

**Condizione B — Assenza di classificazioni:**
Il campo `detected_formats` è vuoto o contiene solo formati con confidence < 15 (che vengono già filtrati dal prompt principale).

**Condizione C — Bassa confidence aggregata:**
La somma delle confidence di tutti i formati rilevati è inferiore a 60. Formula:
```
aggregated_score = sum(f.confidence for f in detected_formats)
is_candidate_novel = aggregated_score < 60 OR max_confidence < 40
```

**Soglie operative:**

| Soglia | Significato | Azione |
|---|---|---|
| max_confidence >= 70 | Classificazione affidabile | Accetta come classificazione definitiva |
| max_confidence 40-69 | Classificazione plausibile | Accetta con flag `low_confidence` per review umana |
| max_confidence < 40 | Classificazione incerta | Attiva novelty detection pipeline |
| detected_formats vuoto | Nessuna corrispondenza | Attiva novelty detection pipeline (priorità alta) |

---

### Prompt per Novelty Detection

Il prompt seguente si invoca solo quando si entra nella novelty detection pipeline (max_confidence < 40 o detected_formats vuoto). L'immagine viene inviata di nuovo insieme al contesto della classificazione fallita.

```
SYSTEM:
You are an expert advertising creative analyst specializing in identifying new, emerging, or uncategorized advertising creative formats.

You have been provided an advertising image that did NOT match any of the 128 known creative formats in our taxonomy with sufficient confidence (no format exceeded confidence 40/100).

Your task is to:
1. Describe the image in detail
2. Explain precisely WHY it does not fit the known taxonomy
3. Propose a name and description for a potential new format category
4. Assess whether this is truly a new format or a known format presented in an unusual way

---

KNOWN TAXONOMY SUMMARY (13 macro-categories, 128 formats):
- 1. PRODUCT-CENTRIC (16 formats): product isolated, hero shot, detail shot, flat lay, still life, packaging, bundle, animated showcase, etc.
- 2. LIFESTYLE & CONTEXT (9 formats): product in real-life settings, GRWM, OOTD, daily routines, "That Girl" aesthetic, etc.
- 3. BEHIND THE SCENES & CRAFT (5 formats): BTS, how it's made, pack an order, founder story, employee spotlight.
- 4. UGC & CREATOR CONTENT (12 formats): UGC classic, talking head, unboxing, haul, try-on, ASMR, honest review, tier list, compilation.
- 5. SOCIAL PROOF & TRUST (9 formats): review quote card, video testimonial, case study, aggregated social proof, press mentions, expert endorsement, awards.
- 6. PROBLEM-SOLUTION & TRANSFORMATION (9 formats): problem-solution, PAS, before/after, pain point dramatization, myth-busting, expectation vs reality, challenge tracking, switching story.
- 7. COMPARISON & COMPETITIVE (5 formats): us vs them, us vs old way, side-by-side demo, why we're different, comparison table.
- 8. EDUCATIONAL & INFORMATIONAL (10 formats): how-to, step-by-step, explainer, listicle, feature highlight, infographic, stat callout, FAQ visual, life hack, educational grid.
- 9. STORYTELLING & EMOTIONAL (9 formats): brand story, customer journey, emotional appeal, aspirational, mini-series, humor/skit, storytime, documentary-style.
- 10. OFFER & PROMO-DRIVEN (9 formats): hard offer, countdown/urgency, scarcity, free shipping, seasonal, new launch, price anchor, bundle offer.
- 11. NATIVE & TREND-DRIVEN (12 formats): talking head, lo-fi/ugly ads, POV, trend-jacking, meme, challenge, duet, stitch, reply to comment, green screen, screenshot native, street interview.
- 12. VISUAL DESIGN & PRODUCTION STYLE (17 formats): bold text/typography, quote card, minimalist, color blocking, collage, mood board, stop motion, cinemagraph, motion graphics, boomerang, kinetic text, timelapse, transition-driven, montage, satisfying, handwritten, infographic pin.
- 13. INTERACTIVE & IMMERSIVE (6 formats): poll/quiz, AR try-on, shoppable video, playable ad, 360-degree, gamified.

---

USER:
Analyze this advertising image that did not match our taxonomy.

Previous classification attempt result:
- Best matching format: {previous_best_format_id} - {previous_best_format_name} (confidence: {previous_max_confidence}/100)
- All detected formats: {previous_detected_formats_summary}

Return ONLY a valid JSON object with this exact structure:

{
  "image_description": "<Detailed description in English of what you see: subjects, setting, composition, visual style, text, colors, mood. 4-6 sentences.>",
  "product_sector": "<Identified product or sector, or 'unknown'>",
  "novelty_assessment": {
    "is_truly_novel": <true or false>,
    "novelty_confidence": <integer 0-100, how confident you are this is a genuinely new format>,
    "explanation": "<2-3 sentences explaining why this image does not fit the existing taxonomy OR explaining which existing format it actually resembles if not truly novel.>"
  },
  "proposed_new_format": {
    "suggested_name": "<A concise name for the potential new format, in English, following naming conventions of the existing taxonomy>",
    "suggested_macro_category": "<Name of the most appropriate existing macro-category, or 'NEW MACRO-CATEGORY' if none applies>",
    "description": "<2-3 sentences describing this format: what it shows, how it is structured, what communicative intent it serves.>",
    "use_cases": "<Typical advertising contexts where this format would be used.>",
    "distinguishing_elements": ["<visual element 1>", "<visual element 2>", "<narrative element 1>"]
  },
  "recommendation": "<One of: 'ADD_TO_TAXONOMY', 'REVIEW_NEEDED', 'EDGE_CASE_EXISTING_FORMAT'. Add a brief justification.>"
}
```

### Template dell'alert generato dal sistema

Quando la novelty detection pipeline identifica un potenziale nuovo formato (`is_truly_novel: true` con `novelty_confidence >= 60`), il sistema genera il seguente alert strutturato:

```json
{
  "alert_type": "NOVELTY_DETECTED",
  "alert_id": "<uuid-v4>",
  "timestamp": "<ISO 8601>",
  "image_reference": {
    "image_id": "<internal image id>",
    "source": "<campaign/upload source>",
    "url": "<internal storage url>"
  },
  "classification_attempt": {
    "max_confidence_achieved": <integer>,
    "best_matching_format": "<format_id - format_name>",
    "all_detected_formats": []
  },
  "novelty_detection": {
    "is_truly_novel": true,
    "novelty_confidence": <integer>,
    "proposed_format_name": "<suggested_name>",
    "proposed_macro_category": "<suggested_macro_category>",
    "proposed_description": "<description>",
    "distinguishing_elements": []
  },
  "recommended_action": "<ADD_TO_TAXONOMY | REVIEW_NEEDED | EDGE_CASE_EXISTING_FORMAT>",
  "review_assignee": null,
  "review_status": "PENDING"
}
```

---

## Sezione 4: Pipeline Tecnica Step-by-Step

### Pre-processing dell'immagine

Prima di inviare l'immagine all'LLM, applicare i seguenti step di normalizzazione:

1. **Validazione formato:** Accettare solo JPEG, PNG, WebP, GIF (primo frame). Rifiutare con errore esplicito altri formati.
2. **Ridimensionamento:** Se la risoluzione supera 2048x2048 pixel, ridimensionare mantenendo aspect ratio con interpolazione Lanczos. Risoluzione minima richiesta: 256x256 px (sotto questa soglia, segnalare `low_resolution_warning`).
3. **Dimensione file:** Comprimere a JPEG quality 85 se il file supera 4MB. GPT-4o e Claude accettano immagini fino a 20MB ma costi e latenza aumentano con immagini grandi senza benefici classificativi.
4. **Encoding:** Convertire in base64 per invio via API, oppure usare URL diretto se l'immagine è accessibile pubblicamente.
5. **Metadata extraction:** Estrarre e loggare: dimensioni originali, formato, dimensione file, aspect ratio. Utile per correlazioni successive tra tipo di immagine e qualità della classificazione.

```python
from PIL import Image
import base64, io

def preprocess_image(image_path: str, max_size: int = 2048, max_bytes: int = 4_000_000) -> dict:
    img = Image.open(image_path).convert("RGB")
    original_size = img.size

    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    buffer = io.BytesIO()
    quality = 85
    img.save(buffer, format="JPEG", quality=quality)

    if buffer.tell() > max_bytes:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)

    image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "base64": image_b64,
        "original_size": original_size,
        "processed_size": img.size,
        "format": "JPEG",
        "low_resolution_warning": min(img.size) < 256,
    }
```

---

### Step 1: Prima classificazione (macro-categoria)

**Obiettivo:** Identificare rapidamente le macro-categorie plausibili prima di procedere con la classificazione fine-grained. Questo step è opzionale ma consigliato nell'approccio ibrido; nel puro LLM, viene folded nello Step 2.

**Modello:** Gemini 2.0 Flash (più economico) o GPT-4o-mini per tenere basso il costo dello step veloce.

**Input:** Immagine pre-processata.

**Output:** Lista di macro-category_id con confidence, usata per restringere il prompt dello Step 2.

**Nota:** Nello stack iniziale (LLM puro), Step 1 e Step 2 sono un'unica chiamata con il prompt completo della Sezione 2.

---

### Step 2: Classificazione fine-grained (sotto-tipologia)

**Obiettivo:** Classificare l'immagine nelle specifiche sotto-tipologie (128 formati) con confidence score per ciascuna.

**Modello consigliato:** `gpt-4o` o `claude-sonnet-4-6`. Non usare modelli più piccoli per questo step: la qualità della classificazione su 128 classi dipende dalla capacità di ragionamento del modello.

**Input:** Immagine pre-processata + prompt completo della Sezione 2.

**Output:** JSON strutturato con `detected_formats`, `primary_format`, `image_description`, `product_sector`.

**Parametri di chiamata consigliati:**
- `temperature: 0.1` (quasi deterministico, riduce variabilità)
- `max_tokens: 1500` (sufficiente per JSON completo con 5-10 formati rilevati)
- `response_format: { "type": "json_object" }` (se supportato dall'API)

---

### Step 3: Confidence validation

**Obiettivo:** Validare e categorizzare il risultato della classificazione.

```python
from dataclasses import dataclass
from enum import Enum

class ClassificationStatus(Enum):
    CONFIDENT = "confident"
    LOW_CONFIDENCE = "low_confidence"
    NOVELTY_CANDIDATE = "novelty_candidate"

@dataclass
class ValidationResult:
    status: ClassificationStatus
    max_confidence: int
    aggregated_score: int
    flags: list[str]

def validate_classification(detected_formats: list[dict]) -> ValidationResult:
    if not detected_formats:
        return ValidationResult(
            status=ClassificationStatus.NOVELTY_CANDIDATE,
            max_confidence=0,
            aggregated_score=0,
            flags=["NO_FORMATS_DETECTED"]
        )

    max_confidence = max(f["confidence"] for f in detected_formats)
    aggregated_score = sum(f["confidence"] for f in detected_formats)
    flags = []

    if max_confidence < 40:
        flags.append("MAX_CONFIDENCE_BELOW_THRESHOLD")
    if aggregated_score < 60:
        flags.append("LOW_AGGREGATED_SCORE")
    if len(detected_formats) > 8:
        flags.append("EXCESSIVE_FORMATS_COUNT")  # possibile hallucination

    if "MAX_CONFIDENCE_BELOW_THRESHOLD" in flags or "NO_FORMATS_DETECTED" in flags:
        status = ClassificationStatus.NOVELTY_CANDIDATE
    elif max_confidence < 70:
        status = ClassificationStatus.LOW_CONFIDENCE
    else:
        status = ClassificationStatus.CONFIDENT

    return ValidationResult(
        status=status,
        max_confidence=max_confidence,
        aggregated_score=aggregated_score,
        flags=flags
    )
```

---

### Step 4: Novelty detection check

**Obiettivo:** Se Step 3 restituisce `NOVELTY_CANDIDATE`, invocare il prompt di novelty detection della Sezione 3.

**Input:** Immagine pre-processata + prompt novelty + risultati parziali dello Step 2 (iniettati come `previous_classification`).

**Output:** JSON novelty con `is_truly_novel`, `novelty_confidence`, `proposed_new_format`.

**Azione in base all'output:**
- `is_truly_novel: true` AND `novelty_confidence >= 60`: genera alert (template Sezione 3) e invia a coda di review umana
- `is_truly_novel: true` AND `novelty_confidence < 60`: logga come `EDGE_CASE`, non genera alert
- `is_truly_novel: false`: il modello ha identificato un formato esistente con ragionamento migliore; usare il formato proposto nella sezione `explanation` come classificazione finale con flag `RECOVERED_FROM_NOVELTY`

---

### Diagramma del flusso

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IMMAGINE IN INPUT                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PRE-PROCESSING                                                      │
│  • Validazione formato (JPEG/PNG/WebP/GIF)                          │
│  • Resize se > 2048px                                               │
│  • Compressione se > 4MB                                            │
│  • Encoding base64                                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: CLASSIFICAZIONE FINE-GRAINED                               │
│  Modello: GPT-4o / claude-sonnet-4-6                                │
│  Prompt: tassonomia completa 128 formati                            │
│  Output: detected_formats[] con confidence, primary_format          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: CONFIDENCE VALIDATION                                      │
│  max_confidence = max(detected_formats[].confidence)                │
│  aggregated_score = sum(detected_formats[].confidence)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────────┐
              │                                     │
    max_confidence >= 40                   max_confidence < 40
    OR detected_formats non vuoto          OR detected_formats vuoto
              │                                     │
              ▼                                     ▼
┌─────────────────────────┐           ┌─────────────────────────────┐
│  STEP 3A: STATUS OK     │           │  STEP 4: NOVELTY DETECTION  │
│                         │           │  Prompt novelty + contesto  │
│  >= 70 → CONFIDENT      │           │  classificazione fallita    │
│  40-69 → LOW_CONFIDENCE │           └──────────────┬──────────────┘
│  (flag per review)      │                          │
└──────────┬──────────────┘          ┌───────────────┴──────────────┐
           │                         │                              │
           │                 is_truly_novel                 is_truly_novel
           │                 AND conf >= 60                 = false
           │                         │                              │
           │                         ▼                              ▼
           │              ┌─────────────────────┐    ┌─────────────────────┐
           │              │  GENERA ALERT        │    │  RECOVERED FORMAT   │
           │              │  Novelty template    │    │  Usa formato dal    │
           │              │  → coda review umana │    │  novelty reasoning  │
           │              └─────────────────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OUTPUT FINALE                                                       │
│  {                                                                  │
│    classification_status: "confident|low_confidence|novelty",       │
│    primary_format: { format_id, format_name, confidence },         │
│    detected_formats: [...],                                         │
│    image_description: "...",                                        │
│    product_sector: "...",                                           │
│    flags: [...],                                                    │
│    novelty_alert: null | { ... }                                    │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Sezione 5: Gestione Multi-Label

### Problema

La tassonomia è esplicitamente non mutuamente esclusiva. Un'immagine può essere simultaneamente:
- Un **UGC Talking Head** (4.2) che è anche una **Honest Review** (4.9) con struttura **Problem-Solution** (6.1) e stile **Lo-Fi** (11.2)

Questo non è un caso limite: è il comportamento normale per i creativi pubblicitari migliori, che combinano più registri retorici.

### Regole di assegnazione multi-label

**Regola 1 — Soglia minima di inclusione:** Un formato viene incluso nella classificazione se il modello gli assegna confidence >= 15. Sotto questa soglia, la presenza del formato è troppo ambigua per essere utile.

**Regola 2 — Limite massimo di formati:** Massimo 8 formati per immagine. Se il modello restituisce più di 8 formati con confidence >= 15, tenere solo i primi 8 per confidence decrescente. Più di 8 formati indicano tipicamente over-labeling o immagini composte (carousel, multi-frame), da gestire separatamente.

**Regola 3 — Gerarchia primario/secondario:**

```
primary_format   → confidence >= 65 (formato dominante)
secondary_formats → confidence 35-64 (formati chiaramente presenti)
tertiary_formats  → confidence 15-34 (formati suggeriti, peso ridotto)
```

Se nessun formato raggiunge confidence 65, il primary_format è quello con confidence massima, ma il campo `classification_status` sarà `low_confidence`.

**Regola 4 — Compatibilità tra macro-categorie:** Alcune combinazioni sono strutturalmente compatibili, altre sono quasi sempre mutuamente esclusive. Usare questa matrice come sanity check:

| | Prod-Centric | Lifestyle | BTS | UGC | Social Proof | Prob-Sol | Comparison | Educational | Storytelling | Offer | Native | Visual Design | Interactive |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Prod-Centric** | - | Bassa | Bassa | Media | Alta | Alta | Alta | Alta | Bassa | Alta | Bassa | Alta | Media |
| **UGC** | Bassa | Alta | Alta | - | Alta | Alta | Bassa | Media | Alta | Media | Alta | Alta | Bassa |
| **Offer** | Alta | Media | Bassa | Media | Media | Media | Alta | Bassa | Bassa | - | Media | Alta | Media |

*Alta = combinazione frequente e valida. Bassa = combinazione rara, potenziale segnale di over-labeling.*

**Regola 5 — Formati Visual Design (categoria 12) sono trasversali:** I formati della categoria 12 descrivono lo stile produttivo, non il contenuto narrativo. Possono sempre coesistere con formati di altre categorie. Esempio valido: `6.3 Before/After` (contenuto) + `12.9 Motion Graphics` (stile produttivo).

### Come riportare le tipologie

Nell'output finale, la struttura raccomandata è:

```json
{
  "primary_format": { "format_id": "6.3", "format_name": "Before / After", "confidence": 95 },
  "secondary_formats": [
    { "format_id": "4.2", "format_name": "UGC Talking Head", "confidence": 58 },
    { "format_id": "12.11", "format_name": "Kinetic Text / Text Animation", "confidence": 45 }
  ],
  "tertiary_formats": [
    { "format_id": "11.2", "format_name": "Lo-Fi / Ugly Ads", "confidence": 22 }
  ]
}
```

---

## Sezione 6: Benchmark e Metriche

### Dataset di test e validazione

**Costruzione del dataset:** Il dataset di benchmark deve essere costruito con annotazione umana da esperti di creative strategy (non da annotatori generici). Ogni immagine deve essere annotata da almeno 2 revisori indipendenti, con risoluzione del conflitto da un terzo revisore in caso di disaccordo.

**Dimensione minima raccomandata:**
- 5 esempi per ogni formato raro (con meno di 3 esempi reali disponibili) → generare con ricerca mirata
- 15-20 esempi per ogni formato comune
- Target totale: 500-800 immagini per il dataset iniziale di validazione

**Stratificazione:** Il dataset deve contenere:
- 60% immagini con classificazione "pulita" (1-2 formati dominanti)
- 30% immagini multi-label genuine (3-5 formati)
- 10% immagini fuori tassonomia (per testare la novelty detection)

**Dove reperire immagini:** Swipe file esistenti dell'azienda, Facebook Ad Library (pubblico), TikTok Creative Center (pubblico). Non usare immagini generate sinteticamente per il benchmark: potrebbero non rappresentare la distribuzione reale.

---

### Metriche per classificazione multi-label

Per la classificazione multi-label, le metriche standard di accuracy per singola classe non sono sufficienti. Usare:

**1. Per ogni singolo formato (micro-level):**

```
Precision_k = TP_k / (TP_k + FP_k)
Recall_k = TP_k / (TP_k + FN_k)
F1_k = 2 * (Precision_k * Recall_k) / (Precision_k + Recall_k)
```

**2. Metriche aggregate (macro-level):**

- **Macro-F1:** Media semplice di F1_k su tutti i 128 formati. Penalizza le performance scadenti sui formati rari.
- **Micro-F1:** F1 calcolato su tutti i TP/FP/FN aggregati. Favorisce le classi più frequenti.
- **Samples-F1:** F1 calcolato per ogni immagine individualmente, poi mediato. La metrica più rilevante per la use case reale.

**3. Metriche specifiche per il sistema:**

- **Primary Format Accuracy:** Percentuale di immagini dove il `primary_format` del sistema coincide con il formato primario dell'annotatore umano. Target: >= 80%.
- **Jaccard Similarity (per immagine):** `|predicted_formats ∩ true_formats| / |predicted_formats ∪ true_formats|`. Target medio: >= 0.60.
- **Novelty Detection Rate:** Percentuale di immagini fuori tassonomia correttamente flaggiate come `NOVELTY_CANDIDATE`. Target: >= 75% con false positive rate < 15%.
- **Confidence Calibration (ECE):** Expected Calibration Error. Misura quanto i confidence score del modello rispecchiano la probabilità reale di correttezza. Target ECE < 0.15.

---

### Soglie minime di performance accettabili

| Metrica | Minimo Accettabile | Target Ottimale |
|---|---|---|
| Primary Format Accuracy | 75% | >= 85% |
| Samples-F1 | 0.55 | >= 0.70 |
| Macro-F1 | 0.45 | >= 0.60 |
| Jaccard Similarity (media) | 0.55 | >= 0.70 |
| Novelty Detection Rate | 70% | >= 80% |
| Novelty False Positive Rate | < 20% | < 10% |
| Confidence Calibration ECE | < 0.20 | < 0.12 |
| Latenza end-to-end (p95) | < 8s | < 4s |
| API Success Rate | > 99% | > 99.9% |

**Nota sul Macro-F1:** Un Macro-F1 di 0.45 su 128 classi sbilanciate è già un risultato solido per un sistema zero-shot. Formati molto rari (es. 13.4 Playable Ad, 11.7 Duet) avranno inevitabilmente recall basso se il dataset di test è piccolo: isolarli in una categoria "formati rari" per il reporting.

---

### Come misurare in produzione (online evaluation)

Il benchmark offline (su dataset annotato) misura la qualità in isolamento. Per monitorare la qualità in produzione:

1. **Human-in-the-loop sampling:** Campionare il 5% delle classificazioni in produzione per review umana periodica. Usare i risultati per aggiornare le soglie di confidence.

2. **Confidence drift monitoring:** Monitorare la distribuzione dei `max_confidence` nel tempo. Un abbassamento sistematico della confidence media indica che i creativi in input si stanno allontanando dalla distribuzione di training del modello LLM (un segnale che la tassonomia potrebbe necessitare di aggiornamento).

3. **Novelty alert rate:** Monitorare la percentuale di immagini che finiscono in novelty detection. Un aumento sostenuto nel tempo (>5% delle immagini) indica l'emergere di nuovi format creativi nel mercato e deve attivare una revisione della tassonomia.

4. **Inter-rater agreement (IRA):** Quando due revisori umani annotano la stessa immagine, misurare l'accordo con Cohen's kappa. Se IRA scende sotto 0.60 per certi formati, significa che quei formati sono ambiguamente definiti nella tassonomia e devono essere chiariti.

---

*Fine documento. Versione 1.0 — Marzo 2026.*
*File correlato: `../mappatura_formati_creativi_adv.md`*
