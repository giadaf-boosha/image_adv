# Criteri di Qualita per Tipologia Creativa Pubblicitaria

> Rubrica di valutazione per agente AI vision. Documento di riferimento per la valutazione qualitativa automatizzata di creative pubblicitarie digitali.
> Basato sulla mappatura: `mappatura_formati_creativi_adv.md` (128 formati, 13 macro-categorie)
> Versione: 1.0 | Data: Marzo 2026

---

## CRITERI UNIVERSALI

Questi 6 criteri si applicano a TUTTE le 128 tipologie creative, indipendentemente dalla categoria. Ogni creative riceve un punteggio su ciascun criterio universale prima di applicare i criteri specifici di categoria.

| ID | Criterio | Descrizione valutativa |
|----|----------|------------------------|
| U1 | **Risoluzione e nitidezza** | Immagine o frame video privo di pixelazione, blur non intenzionale, artifatti di compressione. Verifica: bordi netti su elementi principali. |
| U2 | **Composizione e gerarchia visiva** | Presenza di un punto focale primario chiaramente dominante. Elementi secondari non competono con il soggetto principale. Regola dei terzi o centratura intenzionale rispettata. |
| U3 | **Leggibilita del testo** | Contrasto sufficiente testo/sfondo (rapporto minimo 4.5:1 WCAG AA). Font size adeguato al formato. Nessuna sovrapposizione testo-elemento critico. |
| U4 | **Brand consistency** | Logo visibile e non distorto (se presente). Palette colori coerente con identita di brand. Tone of voice visivo allineato al posizionamento. |
| U5 | **Chiarezza del messaggio principale** | Un solo messaggio primario immediatamente identificabile entro 1-3 secondi di visione. Assenza di overcrowding informativo. |
| U6 | **Qualita tecnica generale** | Assenza di: watermark non intenzionali, metadati visibili, ritagli accidentali di elementi importanti, distorsioni geometriche non volute, banding nei gradienti. |

### Scala universale (applicata a ogni criterio U1-U6)

| Score | Livello | Descrizione |
|-------|---------|-------------|
| 1-3 | Basso | Il criterio non e soddisfatto. Difetto evidente che compromette la fruizione. |
| 4-6 | Medio | Il criterio e parzialmente soddisfatto. Margini di miglioramento significativi. |
| 7-8 | Buono | Il criterio e soddisfatto. Qualita adeguata per la pubblicazione. |
| 9-10 | Eccellente | Il criterio e soddisfatto in modo esemplare. Qualita da benchmark di settore. |

### Formula punteggio composito

```
Score_finale = (Media_criteri_universali * 0.35) + (Media_criteri_specifici_categoria * 0.65)
```

I criteri di categoria pesano di piu perche determinano l'efficacia specifica del formato scelto.

---

## MACRO-CATEGORIA 1: PRODUCT-CENTRIC (Prodotto al Centro)

> Formati: 1.1 - 1.16 (16 tipologie)
> Obiettivo primario: valorizzare il prodotto come protagonista assoluto dell'immagine.

### 1.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| PC1 | **Nitidezza e fuoco del prodotto** | 25% | Il prodotto (o la parte principale di esso) e a fuoco netto. Sfocatura selettiva (bokeh) e ammessa solo se intenzionale e il soggetto primario rimane nitido. |
| PC2 | **Illuminazione e resa materica** | 25% | La luce valorizza forma, texture e materiali del prodotto. Assenza di riflessi parassiti su superfici lucide, ombre piatte indesiderate, sottoesposizione che nasconde dettagli. |
| PC3 | **Sfondo coerente e non distraente** | 20% | Lo sfondo non compete visivamente con il prodotto. Colori, texture e pattern dello sfondo sono scelti per esaltare, non per distrarre. |
| PC4 | **Color accuracy del prodotto** | 15% | Il colore del prodotto corrisponde alla realta (verificabile rispetto a eventuali varianti di colore indicate). Nessuna dominante di colore indesiderata che altera la percezione del prodotto. |
| PC5 | **Presentazione completa del prodotto** | 15% | Il prodotto non e ritagliato in modo accidentale. Le proporzioni sono corrette. Gli elementi chiave (logo sul prodotto, etichetta, caratteristiche distintive) sono visibili. |

### 1.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Nitidezza** | Prodotto sfocato o pixelato | Focus accettabile ma non ottimale | Prodotto a fuoco, dettagli leggibili | Micro-dettagli nitidi, qualita studio |
| **Illuminazione** | Sottoesposto, riflessi disturbanti, ombre dure che nascondono forma | Illuminazione piatta o non ottimale, qualche riflesso | Illuminazione corretta, ombre morbide, materiali leggibili | Illuminazione da studio professionale, resa materica eccellente |
| **Sfondo** | Sfondo rumoroso che compete col prodotto | Sfondo accettabile ma non ideale | Sfondo pulito, prodotto chiaramente distinguibile | Sfondo perfettamente integrato, prodotto in piena evidenza |
| **Color accuracy** | Colori visibilmente alterati o dominante cromatica evidente | Leggera distorsione cromatica | Colori fedeli alla realta | Colori perfetti, rendering materiali impeccabile |
| **Presentazione** | Prodotto ritagliato o fuori quadro | Prodotto visibile ma con dettagli importanti tagliati | Prodotto completo e ben inquadrato | Proporzioni perfette, tutti gli elementi chiave visibili |

### 1.C - Red Flags (abbassano automaticamente il punteggio)

- Watermark visibile (Getty, Shutterstock, ecc.) non rimosso
- Prodotto con ombre duplicate o inconsistenti (indicano compositing mal eseguito)
- Sfondo bianco con aloni giallastri o grigi attorno al prodotto (ritaglio di bassa qualita)
- Prodotto ritagliato ai bordi dell'immagine in modo non intenzionale
- Testo del prezzo o claim sovrapposto alla parte principale del prodotto
- Riflessi che rivelano attrezzatura fotografica o ambiente di studio non desiderato
- Colori prodotto visibilmente sbiaditi o sovrasaturi rispetto alla realta

### 1.D - Best Practices (alzano automaticamente il punteggio)

- Ombra coerente con la fonte luminosa (shadow naturale o drop shadow pulito)
- Padding proporzionato attorno al prodotto (almeno 10-15% del frame)
- Consistenza di scala: il prodotto occupa il 60-80% del frame nei product-only
- Angolo di ripresa che massimizza la riconoscibilita del prodotto

---

### 1.E - Criteri per Sotto-Tipologie Critiche

#### 1.1 - Product Only / White Background

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Purezza sfondo** | Il bianco e puro (RGB 255,255,255 o vicinissimo). Nessuna dominante giallastra o grigia. |
| **Qualita del ritaglio** | I bordi del prodotto sono netti, senza aloni, frangiature o artefatti di scontorno. |
| **Ombra** | Se presente, e coerente (drop shadow morbido o ombra proiettata sul piano). Se assente, il prodotto non "galleggia" in modo innaturale. |
| **Centratura e margini** | Il prodotto e centrato (o allineato intenzionalmente). I margini sono simmetrici e proporzionati. |
| **Proporzioni** | Il prodotto non e schiacciato o stirato. Le proporzioni reali sono rispettate. |

**Score minimo accettabile per DPA/catalogo**: 7/10 su tutti i criteri sopra.

#### 1.3 - Hero Shot

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Dominanza del prodotto** | Il prodotto occupa il 50-70% del frame. Non e sovrastato da elementi contestuali. |
| **Qualita illuminazione direzionale** | Luce di qualita che conferisce tridimensionalita e volume al prodotto. |
| **Contesto suggestivo coerente** | Gli eventuali elementi di contesto (sfondo, props) comunicano il posizionamento del brand senza competere. |
| **Impatto visivo immediato** | La hero shot deve fermare lo scroll: contrasto, colore o composizione con forza visiva elevata. |

#### 1.4 - Detail Shot / Close-Up

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Area di focus corretta** | Il close-up e centrato esattamente sull'elemento che si vuole valorizzare (texture, cuciture, ingrediente). |
| **Profondita di campo** | La zona a fuoco e chiaramente identificabile. Il bokeh (se usato) esalta l'elemento principale. |
| **Informativita** | Il close-up comunica qualcosa di specifico: materiale, qualita artigianale, dettaglio unico. Non e un ingrandimento casuale. |
| **Proporzioni rispetto al formato** | Il crop non e talmente stretto da rendere non riconoscibile il contesto dell'elemento. |

#### 1.7 - Flat Lay / Knolling

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Angolo di ripresa** | Ripresa dall'alto a 90 gradi (top-down). Nessuna distorsione prospettica. |
| **Simmetria e allineamento** | Oggetti allineati a griglia o a pattern geometrico intenzionale. Spacing uguale tra gli elementi. |
| **Palette cromatica** | I colori degli oggetti nella composizione sono armonici tra loro e con lo sfondo. |
| **Densita della composizione** | Ne troppo vuoto (dispersivo) ne troppo pieno (caotico). Ogni oggetto ha il suo spazio. |
| **Pulizia dello sfondo** | Superficie di appoggio uniforme, senza segni, polvere o ombre indesiderate. |

#### 1.10 - Product Collection / Grid

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Coerenza visiva della collezione** | Tutti i prodotti sono ripresi con la stessa illuminazione, prospettiva e trattamento. |
| **Leggibilita di ogni singolo prodotto** | Nonostante la presenza multipla, ogni prodotto e distinguibile e non confuso con gli altri. |
| **Bilanciamento della griglia** | La distribuzione dei prodotti nel frame e equilibrata. Nessun raggruppamento casuale. |

#### 1.11 - Product Annotated / Point-Out

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Chiarezza delle frecce/label** | Frecce e callout puntano esattamente all'elemento descritto, senza ambiguita. |
| **Leggibilita del testo delle label** | Font size e contrasto adeguati. Le label non si sovrappongono tra loro. |
| **Non invasivita delle annotazioni** | Le annotazioni non coprono elementi chiave del prodotto. |

---

## MACRO-CATEGORIA 2: LIFESTYLE & CONTEXT (Prodotto nella Vita Reale)

> Formati: 2.1 - 2.9 (9 tipologie)
> Obiettivo primario: inserire il prodotto in un contesto di vita reale o aspirazionale che generi identificazione emotiva.

### 2.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| LS1 | **Coerenza del mood e dell'atmosfera** | 25% | Colori, luce, styling e soggetti comunicano un'atmosfera unitaria e coerente con il posizionamento del brand. |
| LS2 | **Aspirational value o identificazione** | 20% | La scena genera desiderio di emulazione (aspirazionale) o riconoscimento nella propria vita (identificazione). Deve scattare uno dei due meccanismi. |
| LS3 | **Naturalezza della presenza del prodotto** | 20% | Il prodotto appare integrato organicamente nella scena, non posizionato in modo artificioso. Non sembra "buttato" nell'immagine. |
| LS4 | **Qualita dello styling e dell'ambiente** | 20% | Abbigliamento, arredamento, props e location sono curati e coerenti tra loro. Nessun elemento fuori posto che rompe la verosimiglianza. |
| LS5 | **Visibilita e riconoscibilita del prodotto** | 15% | Pur in un contesto lifestyle, il prodotto rimane chiaramente identificabile. Non e perso nell'ambiente. |

### 2.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Mood** | Atmosfera incoerente o inesistente | Mood percepibile ma non uniforme | Atmosfera chiara e coerente | Mood immersivo, ogni elemento contribuisce |
| **Aspirational/Identificazione** | Scena generica, nessun meccanismo emotivo | Leggera connessione emotiva | Scena desiderabile o identificabile | Forte risonanza emotiva, altamente condivisibile |
| **Naturalezza prodotto** | Prodotto visibilmente "piazzato" | Presenza del prodotto accettabile | Prodotto integrato in modo credibile | Inserimento del prodotto seamless e organico |
| **Styling** | Styling trascurato o incoerente | Styling ordinario ma senza personalita | Styling curato e coerente | Styling di qualita editoriale |
| **Visibilita prodotto** | Prodotto irriconoscibile o invisibile | Prodotto visibile ma in secondo piano | Prodotto chiaramente visibile | Prodotto protagonista pur nel contesto |

### 2.C - Red Flags

- Prodotto logicamente incompatibile con il contesto rappresentato
- Modelli o persone con espressioni forzate o innaturali
- Palette di colori disomogenea (es. warm tones su sfondo con dominante fredda)
- Prodotto con dimensioni sproporzionate rispetto all'ambiente (errore di scala)
- Elementi di sfondo distraenti o brandizzati da competitor
- Abbigliamento o arredamento datati che trasmettono un'immagine di brand obsoleta

### 2.D - Best Practices

- Uso coerente di una palette cromatica limitata (3-4 colori dominanti)
- Luce naturale o luce che simula naturalezza (evoca autenticita)
- Profondita di campo selettiva che guida l'occhio verso il prodotto
- Presenza di elementi umani (mani, persone parziali) che danno scala e calore

---

### 2.E - Criteri per Sotto-Tipologie Critiche

#### 2.1 - Lifestyle / Prodotto Contestualizzato

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Coerenza location-prodotto** | La location (casa, ufficio, natura) e logicamente e stilisticamente coerente con il prodotto. |
| **Equilibrio figura-sfondo** | Il prodotto o la persona con il prodotto occupa il ruolo principale senza essere schiacciata dall'ambiente. |
| **Qualita ambientale** | Lo spazio e curato, pulito, ordinato (o volutamente casual per brand informali). |

#### 2.2 - Prodotto Indossato / In-Use

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Resa del prodotto indossato/in uso** | Il prodotto si vede chiaramente durante l'utilizzo. La resa (vestibilita, fit, funzione) e comunicata efficacemente. |
| **Naturalezza del gesto o dell'indossato** | Il modello usa il prodotto in modo naturale, non in posa statica artificiosa. |
| **Diversita e rappresentativita** | Se rilevante per il brand, la rappresentazione di corpi, etnie e stili di vita e appropriata e non stereotipata. |

#### 2.4 - GRWM (Get Ready With Me)

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Sequenzialita chiara** | Si capisce chiaramente la progressione della routine. L'ordine dei prodotti/step e logico. |
| **Integrazione naturale del prodotto** | Il prodotto non interrompe il flusso della routine: appare come parte integrante. |
| **Trasformazione percepibile** | La differenza tra inizio e fine della routine e visibile e positiva. |

---

## MACRO-CATEGORIA 3: BEHIND THE SCENES & CRAFT (Dietro le Quinte)

> Formati: 3.1 - 3.5 (5 tipologie)
> Obiettivo primario: trasmettere autenticita, trasparenza e valore del processo produttivo.

### 3.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| BTS1 | **Autenticita percepita** | 30% | La scena appare genuina e non messa in scena in modo artificioso. Il livello di "produzione" e coerente con il messaggio di trasparenza. |
| BTS2 | **Chiarezza del processo mostrato** | 25% | Si capisce cosa sta avvenendo. Le fasi del processo sono distinguibili e comprensibili anche senza testo esplicativo. |
| BTS3 | **Valorizzazione del know-how** | 25% | La scena comunica competenza, cura e qualita del processo. Giustifica il prezzo premium o differenzia dalla produzione di massa. |
| BTS4 | **Coerenza con i valori del brand** | 20% | Il BTS e allineato all'identita del brand (es. sostenibilita, artigianalita, innovazione). Nessun elemento visivo contraddice i valori dichiarati. |

### 3.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Autenticita** | Appare totalmente costruito, artificioso | Qualche elemento di autenticita ma eccessivamente curato | Genuino nella sostanza pur con buona qualita produttiva | Autenticita totale, si percepisce il vero ambiente di lavoro |
| **Chiarezza processo** | Processo incomprensibile | Processo intuibile ma non chiaro | Processo chiaramente leggibile | Processo narrato in modo coinvolgente e immediato |
| **Know-how** | Nessuna valorizzazione della competenza | Accenno di professionalita | Competenza visibilmente comunicata | Eccellenza del processo comunicata in modo memorabile |
| **Coerenza brand** | Contraddice i valori del brand | Parzialmente allineato | Allineato ai valori principali | Rinforza perfettamente il posizionamento del brand |

### 3.C - Red Flags

- Ambienti di produzione sporchi, disordinati o pericolosi visibili (rischio reputazionale)
- Persone che sembrano a disagio o non a proprio agio con la ripresa
- Processi che contraddicono claim del brand (es. brand "natural" con lavorazioni industriali pesanti mostrate)
- Qualita video/foto talmente bassa da risultare anti-professional invece che autentica
- Logo o riferimenti a fornitori terzi visibili senza accordo di brand

### 3.D - Best Practices

- Mani in movimento: il gesto artigianale ripreso in azione ha valore narrativo elevato
- Dettagli materiali che si vedono solo "da dentro" (ingredienti, componenti, materie prime)
- Presenza di persone reali del team con espressioni genuine

---

### 3.E - Criteri per Sotto-Tipologie Critiche

#### 3.2 - Process Shot / How It's Made

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Sequenzialita del processo** | Le fasi sono mostrate in ordine logico. Chiaro inizio (materia prima) e fine (prodotto). |
| **Dettaglio delle lavorazioni chiave** | I passaggi che giustificano il posizionamento premium sono in evidenza (es. cottura lenta, cucitura a mano). |
| **Pulizia e sicurezza visiva** | L'ambiente appare professionale, igienico (per food/beauty) o sicuro (per manifattura). |

#### 3.3 - Pack an Order with Me

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Qualita visiva dell'unboxing inverso** | Il packaging, il materiale di riempimento e la cura nella preparazione sono visivamente apprezzabili. |
| **Elemento satisfying** | Il processo ha un ritmo visivo appagante (movimenti fluidi, suoni se video, ordine). |
| **Comunicazione del brand attraverso il packaging** | Il packaging stesso e un veicolo di brand: colori, materiali, bigliettini personalizzati. |

#### 3.4 - Founder Story

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Credibilita del founder** | Il fondatore appare autentico, non sta "recitando". Espressioni e gestualita sono naturali. |
| **Connessione emotiva alla storia** | La narrazione (visiva o verbale) trasmette la passione e il "perche" del brand. |
| **Qualita minima accettabile** | Anche se girato in modo semplice, deve essere comprensibile e non disturbante (luce, audio se video). |

---

## MACRO-CATEGORIA 4: UGC & CREATOR CONTENT

> Formati: 4.1 - 4.12 (12 tipologie)
> Obiettivo primario: simulare o utilizzare contenuto autentico non-branded per massimizzare fiducia e identificazione.

### 4.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| UGC1 | **Autenticita percepita** | 30% | Il contenuto sembra prodotto da un utente reale, non da un brand. Assenza di elementi over-produced: lighting da studio, sfondi troppo curati, regia troppo visibile. |
| UGC2 | **Naturalezza della performance** | 25% | Il creator/utente si esprime in modo spontaneo. Nessuna recitazione forzata, script visibile nei movimenti oculari, o tono da spot televisivo. |
| UGC3 | **Engagement potential** | 20% | Il contenuto ha elementi che stimolano commenti, condivisioni o identificazione: opinione forte, momento sorpresa, trasformazione, umorismo. |
| UGC4 | **Qualita tecnica minima accettabile** | 15% | Pur nella lo-fi nature del formato, il contenuto e fruibile: soggetto visibile, audio comprensibile (se presente), illuminazione sufficiente a leggere espressioni. |
| UGC5 | **Presence e relazione con il prodotto** | 10% | Il creator interagisce realmente con il prodotto. Non e una foto del prodotto da solo con voice-over. |

### 4.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Autenticita** | Aspetto chiaramente da spot brandizzato | Tentativo di UGC ma ancora troppo prodotto | Convincente come UGC autentico | Indistinguibile da contenuto organico reale |
| **Naturalezza** | Recitazione evidente, script leggibile | Performance accettabile, qualche momento forzato | Naturale nella maggior parte | Spontaneita totale, zero percezione di script |
| **Engagement** | Nessun elemento coinvolgente | Qualche momento di interesse | Contenuto che genera interesse reale | Contenuto altamente condivisibile, hook forte |
| **Qualita tecnica** | Irriconoscibile, non fruibile | Fruibile con difficolta | Qualita adeguata alla piattaforma | Lo-fi perfetto: imperfetto nei dettagli giusti |
| **Relazione prodotto** | Prodotto quasi assente | Prodotto presente ma non interagito | Interazione credibile con il prodotto | Esperienza d'uso genuina e coinvolgente |

### 4.C - Red Flags

- Illuminazione da studio fotografico professionale in un supposto UGC organico
- Testo branded eccessivo (logo grande, claim in overlay) che rompe la natura UGC
- Creator che legge palesemente da un teleprompter (movimenti oculari rigidi)
- Prodotto presentato senza mai essere realmente usato o aperto
- Sfondo troppo curato o scenografato per essere un ambiente domestico/reale
- Espressionista visivamente forzata (sorriso plastico, entusiasmo non credibile)

### 4.D - Best Practices

- Inquadratura in formato verticale (9:16) con il telefono tenuto in mano (leggero movimento)
- Qualche imperfezione tecnica voluta (leggero shake, luce non perfetta)
- Reaction genuina al prodotto (anche se parzialmente scriptata)
- Ambiente domestico riconoscibile come reale (cucina, bagno, camera da letto)

---

### 4.E - Criteri per Sotto-Tipologie Critiche

#### 4.2 - UGC Talking Head

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Eye contact e presenza in camera** | Il creator guarda direttamente in camera per la maggior parte del tempo. Crea connessione con lo spettatore. |
| **Chiarezza espositiva** | Il messaggio e strutturato: problema/hook, esperienza, risultato/raccomandazione. |
| **Espressivita facciale** | Il viso comunica emozioni reali e appropriate al contenuto. Non e un monologo inespressivo. |
| **Inquadratura del volto** | Il viso occupa almeno il 50% del frame. Non e tagliato o eccessivamente distante. |

#### 4.3 - Unboxing

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Momento di reveal chiaro** | Il momento in cui si vede il prodotto per la prima volta e chiaramente inquadrato e visivamente soddisfacente. |
| **Qualita del packaging mostrato** | Se il packaging e di qualita, viene valorizzato. Se e minimalista, viene comunicato come scelta intenzionale. |
| **Reazione autentica** | La reazione al prodotto (sorpresa, piacere, curiosita) e genuina e non performativa. |
| **Visibilita di tutti i contenuti della box** | Tutti gli elementi inclusi (prodotto, materiali, bigliettini, accessori) sono mostrati chiaramente. |

#### 4.7 - ASMR Product

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Qualita audio** (se valutabile da frame) | L'impostazione visiva suggerisce qualita audio: microfono vicino, ambiente silenzioso. |
| **Texture e dettaglio visivo** | Le superfici, texture e movimenti sono ripresi in close-up con qualita sufficiente a trasmettere la sensazione tattile. |
| **Ritmo e fluidita dei movimenti** | I movimenti sono lenti, controllati e ripetitivi. Nessun movimento brusco. |
| **Focus sui dettagli sensoriali** | Elementi visivi che evocano sensazioni: liquidi, polveri, texture morbide, superfici lucide. |

#### 4.9 - Honest Review / "Brutally Honest"

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Credibilita della critica** | Se vengono espressi aspetti negativi, sono credibili e specifici (non generici). |
| **Struttura pro/contro** | La review ha una struttura che include sia punti positivi che aree di miglioramento. |
| **Linguaggio non promozionale** | Il tono e distinto da un testimonial classico: piu riflessivo, meno entusiasta, piu onesto. |

---

## MACRO-CATEGORIA 5: SOCIAL PROOF & TRUST

> Formati: 5.1 - 5.9 (9 tipologie)
> Obiettivo primario: trasferire credibilita attraverso prove sociali verificabili.

### 5.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| SP1 | **Credibilita della prova** | 35% | La prova sociale appare autentica e verificabile. Nome reale, foto reale, fonte reale, dati specifici (non generici). |
| SP2 | **Leggibilita e formattazione** | 25% | Il contenuto della prova (testo della review, rating, citazione) e immediatamente leggibile. Font size, contrasto e layout sono ottimali. |
| SP3 | **Specificita del beneficio comunicato** | 20% | La prova sociale menziona un beneficio specifico e misurabile, non generico ("ottimo prodotto" = basso, "perso 5kg in 30 giorni" = alto). |
| SP4 | **Coerenza visiva con il brand** | 10% | Il formato grafico della social proof e coerente con l'identita visiva del brand, pur mantenendo l'aspetto autentico. |
| SP5 | **Quantita e aggregazione** | 10% | Se rilevante, il numero di prove aggregate (5.000+ recensioni, 4.8 stelle) e chiaramente comunicato e credibile. |

### 5.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Credibilita** | Review anonima, generica, foto stock | Qualche elemento di credibilita ma non completo | Review credibile con nome e dettagli | Review con tutti gli elementi di autenticita (foto, nome, storia specifica) |
| **Leggibilita** | Testo illeggibile per dimensione o contrasto | Leggibile con sforzo | Chiaramente leggibile | Ottimizzato per lettura immediata, gerarchia visiva perfetta |
| **Specificita** | Beneficio generico ("buono", "lo consiglio") | Beneficio parzialmente specifico | Beneficio specifico e misurabile | Risultato specifico, quantificato e contestualizzato |
| **Coerenza visiva** | Stile grafico incompatibile con il brand | Parzialmente coerente | Coerente con l'identita del brand | Perfettamente integrato nell'estetica del brand |
| **Quantita** | Nessun riferimento a numeri aggregati | Numero presente ma non enfatizzato | Numeri chiari e credibili | Social proof aggregata con numeri impattanti e formattazione ottimale |

### 5.C - Red Flags

- Nomi palesemente inventati o generici ("Mario R.", "Utente verificato" senza dettagli)
- Stelle o rating con decimali non standard (es. 4.97 su 5 su un campione non dichiarato)
- Foto profilo palesemente da stock photo (riconoscibile dall'agente AI)
- Testo della review con linguaggio promozionale tipico di copy brandizzato
- Loghi media ("As Seen In") di testate non verificabili o di bassa credibilita
- Rating aggregati senza menzione della fonte o del numero di recensioni

### 5.D - Best Practices

- Foto del cliente reale (anche selfie) accanto alla review
- Data della recensione visibile (aumenta credibilita)
- Menzione specifica di come il prodotto ha risolto un problema concreto
- Badge di "acquisto verificato" o fonte della piattaforma (Amazon, Trustpilot)

---

### 5.E - Criteri per Sotto-Tipologie Critiche

#### 5.1 - Customer Review / Quote Card

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Gerarchia visiva della card** | Stelle/rating in cima, testo review al centro, nome e attributi del recensore in basso. Ordine logico di lettura. |
| **Lunghezza del testo** | La review e sufficientemente lunga da essere credibile (almeno 2-3 frasi) ma non talmente lunga da non essere letta. |
| **Presenza del prodotto nell'immagine** | Il prodotto recensito e visibile nella card o in background, collegando la review al prodotto concreto. |

#### 5.4 - Social Proof Aggregato

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Impatto visivo del numero** | Il numero chiave ("50.000+ clienti") e il visual element dominante. Dimensione e contrasto lo rendono immediatamente percepibile. |
| **Credibilita del numero** | Il numero e specifico (meglio "47.321" di "50.000+") o la fonte e dichiarata. |
| **Accompagnamento visivo** | Il numero e supportato da icone, volti di clienti, o elementi visivi che lo contestualizzano. |

#### 5.6 - Expert / Authority Endorsement

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Credenziali dell'esperto** | Il titolo/ruolo dell'esperto e visibile (es. "Dr. Rossi, Dermatologo - Ospedale X"). |
| **Professionalita del ritratto** | La foto o ripresa dell'esperto e di qualita professionale, coerente con il ruolo dichiarato. |
| **Specificita del claim** | L'endorsement menziona un meccanismo specifico del prodotto, non una generica approvazione. |

---

## MACRO-CATEGORIA 6: PROBLEM-SOLUTION & TRANSFORMATION

> Formati: 6.1 - 6.9 (9 tipologie)
> Obiettivo primario: creare connessione emotiva attraverso il riconoscimento di un problema e la presentazione convincente della soluzione.

### 6.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| PS1 | **Riconoscibilita del problema** | 25% | Il problema mostrato e immediatamente riconoscibile dal target. Genera empatia e risposta "anche io". |
| PS2 | **Logica della soluzione** | 25% | Il collegamento tra problema e prodotto come soluzione e convincente e comprensibile. Non appare arbitrario. |
| PS3 | **Chiarezza della trasformazione** | 25% | La differenza tra stato "prima" e stato "dopo" e visiva, netta e inequivocabile. |
| PS4 | **Credibilita del risultato** | 15% | La trasformazione mostrata appare raggiungibile e reale, non esagerata o irrealistica. |
| PS5 | **Struttura narrativa** | 10% | La sequenza problema-soluzione e ben ritmata: hook immediato, sviluppo chiaro, risoluzione soddisfacente. |

### 6.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Riconoscibilita** | Problema vago o poco relatable | Problema comprensibile ma non forte | Problema chiaramente riconoscibile | Problema che colpisce immediatamente, "questo sono io" |
| **Logica soluzione** | Collegamento forzato o incomprensibile | Collegamento intuibile ma non convincente | Soluzione logicamente coerente | Soluzione ovvia e necessaria data la natura del problema |
| **Chiarezza trasformazione** | Differenza prima/dopo non percepibile | Differenza percepibile ma debole | Trasformazione chiara e positiva | Trasformazione drammatica e inequivocabile |
| **Credibilita** | Risultato irrealistico o esagerato | Risultato dubbio ma non impossibile | Risultato plausibile e raggiungibile | Risultato credibile, supportato da elementi di prova |
| **Struttura narrativa** | Nessuna struttura logica | Struttura presente ma non ottimale | Flusso narrativo chiaro | Struttura narrativa ottimale, ritmo perfetto |

### 6.C - Red Flags

- Before/After con illuminazione, angolo o distanza di ripresa diversi (segnale di manipolazione)
- Trasformazione fisicamente impossibile nel tempo dichiarato (perdita di peso irrealistica)
- Problema presentato in modo offensivo o stigmatizzante per il target
- Prima parte talmente negativa da creare disagio senza catarsi nella soluzione
- Soluzione mostrata senza alcun meccanismo di collegamento al prodotto

### 6.D - Best Practices

- Il problema e mostrato nella prima metita del frame (hook immediato)
- La transizione problema-soluzione ha un elemento visivo memorabile (split screen, wipe)
- Il "dopo" include un elemento umano (persona felice, risultato tangibile)
- CTA chiara immediatamente dopo il momento di risoluzione

---

### 6.E - Criteri per Sotto-Tipologie Critiche

#### 6.3 - Before / After

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Coerenza delle condizioni di ripresa** | Stessa illuminazione, stesso angolo, stessa distanza tra "prima" e "dopo". Variabili controllate. |
| **Ampiezza della differenza** | La differenza tra prima e dopo deve essere visivamente significativa e immediatamente percepibile. |
| **Autenticita della trasformazione** | Il "prima" non sembra artificialmente peggiorato. Il "dopo" non sembra ritoccato digitalmente in modo evidente. |
| **Etichette chiare** | "Prima" e "Dopo" (o equivalenti) sono chiaramente etichettati. Nessuna ambiguita su quale sia quale. |
| **Timeline credibile** | Se indicata la durata della trasformazione, e plausibile rispetto al risultato mostrato. |

#### 6.1 - Problem-Solution (Classico)

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Hook visivo del problema** | Il problema e introdotto nei primi 2-3 secondi (video) o nella meta superiore del frame (statico). |
| **Momento di svolta** | C'e un chiaro pivot visivo che introduce il prodotto come soluzione. |
| **CTA post-soluzione** | Dopo la presentazione della soluzione, c'e un invito all'azione chiaro. |

#### 6.8 - Result Tracking / Challenge

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Progressione temporale chiara** | Le date o i giorni della challenge sono chiaramente indicati (Giorno 1, Giorno 7, Giorno 30). |
| **Coerenza delle condizioni di ripresa nel tempo** | Le riprese nei diversi giorni mantengono condizioni comparabili (luce, angolo, distanza). |
| **Progressione visibile e graduale** | Il cambiamento e progressivo e credibile, non un salto improvviso. |

---

## MACRO-CATEGORIA 7: COMPARISON & COMPETITIVE

> Formati: 7.1 - 7.5 (5 tipologie)
> Obiettivo primario: differenziare il prodotto rispetto ad alternative attraverso un confronto strutturato.

### 7.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| CMP1 | **Chiarezza e leggibilita del confronto** | 30% | Gli elementi a confronto sono immediatamente identificabili. La struttura del confronto (tabella, split, lista) e chiara e non ambigua. |
| CMP2 | **Fairness percepita del confronto** | 25% | Il confronto appare onesto nelle variabili scelte. Non sembra manipolato a sfavore del competitor in modo palese. |
| CMP3 | **Vantaggio del proprio prodotto** | 25% | Il vantaggio competitivo emerge chiaramente dalla comparazione. Non e necessario leggere tra le righe. |
| CMP4 | **Credibilita delle informazioni** | 20% | I dati usati nel confronto (prezzi, specifiche, caratteristiche) appaiono verificabili e non inventati. |

### 7.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Chiarezza confronto** | Struttura del confronto incomprensibile | Confronto intuibile ma non ottimale | Confronto chiaramente strutturato | Confronto perfettamente leggibile in 2 secondi |
| **Fairness** | Confronto palesemente di parte, alcune variabili ridicole | Parzialmente fair, qualche elemento discutibile | Confronto bilanciato e credibile | Confronto percepibilmente onesto, aumenta fiducia |
| **Vantaggio** | Vantaggio non comunicato o ambiguo | Vantaggio intuibile ma non enfatizzato | Vantaggio chiaramente visibile | Vantaggio schiacciante, immediatamente evidente |
| **Credibilita dati** | Dati non verificabili o visibilmente inventati | Dati plausibili ma senza fonte | Dati credibili con fonte indicata | Dati specifici, fonte verificabile, altamente credibili |

### 7.C - Red Flags

- Logo del competitor usato senza autorizzazione (rischio legale)
- Confronto basato su caratteristiche irrilevanti per il target
- Informazioni sul competitor palesemente errate o datate
- "Nostra offerta" con checkmark su tutto, competitor con X su tutto (troppo parziale)
- Tabella comparativa con dati non leggibili per dimensione del font

### 7.D - Best Practices

- Colore brand dominante sulla colonna "noi" per enfasi visiva
- Check/X con colori chiari (verde/rosso) e icone riconoscibili
- Almeno un criterio in cui la nostra offerta non e superiore (aumenta credibilita)
- Source dei dati visibile (anche in piccolo a fondo pagina)

---

### 7.E - Criteri per Sotto-Tipologie Critiche

#### 7.1 - Us vs. Them

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Identificazione delle parti** | "Noi" e "loro" sono chiaramente distinguibili visivamente (colori, label, posizionamento). |
| **Equilibrio visivo dello spazio** | Entrambe le parti occupano spazio simile nel frame. La superiorita emerge dal contenuto, non dallo spazio. |
| **Rispetto delle norme legali** | Il nome del competitor non e citato direttamente senza autorizzazione (o lo e in modo legalmente sicuro). |

#### 7.5 - Comparison Table

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Leggibilita della tabella** | Font size minimo 14px equivalente. Contrasto tra testo e sfondo di cella sufficiente. |
| **Numero di righe gestibile** | Massimo 8-10 criteri di confronto. Oltre, la tabella diventa illeggibile nel feed. |
| **Colonna highlight** | La colonna del proprio prodotto ha un trattamento visivo distintivo (sfondo colorato, bordo, header in evidenza). |
| **Check/X o indicatori chiari** | Gli indicatori di presenza/assenza di feature sono universalmente comprensibili senza legenda. |

---

## MACRO-CATEGORIA 8: EDUCATIONAL & INFORMATIONAL

> Formati: 8.1 - 8.10 (10 tipologie)
> Obiettivo primario: trasferire valore informativo al target, posizionando il brand come autorita.

### 8.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| ED1 | **Chiarezza e semplicita del contenuto** | 30% | Informazioni complesse sono rese accessibili. Nessun jargon non spiegato. Il target capisce al primo ascolto/lettura. |
| ED2 | **Struttura e logica sequenziale** | 25% | Il contenuto ha un inizio, uno sviluppo e una conclusione. Gli step o punti sono in ordine logico e progressivo. |
| ED3 | **Density informativa adeguata** | 20% | Ne troppo testo da risultare sovraffollato ne troppo vago da non dare valore reale. Ogni elemento porta informazione utile. |
| ED4 | **Collegamento al prodotto** | 15% | Il contenuto educativo e organicamente collegato al prodotto. Il prodotto appare come naturale protagonista o soluzione, non forzato. |
| ED5 | **Valore standalone** | 10% | L'informazione ha valore anche indipendentemente dall'acquisto del prodotto. Questo aumenta la credibilita e il save rate. |

### 8.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Chiarezza** | Contenuto incomprensibile o troppo tecnico | Comprensibile con sforzo | Chiaro e accessibile | Chiarissimo, nessuna ambiguita possibile |
| **Struttura** | Nessuna struttura logica | Struttura presente ma non ottimale | Flusso logico chiaro | Struttura perfetta, guida il lettore/spettatore naturalmente |
| **Density** | Testo muro o al contrario quasi vuoto | Densita accettabile ma non ottimale | Bilanciamento buono tra testo e visual | Perfetto equilibrio: ogni elemento e necessario e sufficiente |
| **Collegamento prodotto** | Prodotto non presente o forzato | Prodotto presente ma mal integrato | Prodotto integrato in modo coerente | Prodotto come risposta naturale e inevitabile all'informazione |
| **Valore standalone** | Nessun valore senza il prodotto | Qualche informazione utile | Informazione genuinamente utile | Contenuto che si salverebbe anche senza prodotto |

### 8.C - Red Flags

- Informazioni errate o non aggiornate (rischio credibilita)
- Step numerati che saltano numeri o sono in ordine non logico
- Testo talmente piccolo da essere illeggibile nel formato di destinazione
- Immagini educative senza connessione visiva con il testo che accompagnano
- Infografiche con dati senza fonte citata

### 8.D - Best Practices

- Numero limitato di concetti per frame/slide (max 3 punti per elemento)
- Visual che illustrano il concetto, non che lo decorano
- Progressione visiva che guida l'occhio dall'inizio alla fine
- CTA che sfrutta il momento di massima autorita ("ora che sai X, prova il prodotto Y")

---

### 8.E - Criteri per Sotto-Tipologie Critiche

#### 8.1 - How-To / Tutorial

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Completezza degli step** | Tutti i passaggi necessari sono presenti. Non ci sono salti logici. |
| **Visibilita dell'azione in ogni step** | Ogni step mostra chiaramente cosa fare (non solo dice). La componente visiva dimostra l'azione. |
| **Risultato finale mostrato** | Il tutorial culmina con la visualizzazione del risultato atteso. Chiude il ciclo. |
| **Uso del prodotto in contesto** | Il prodotto e usato nel tutorial in modo naturale e dimostrativo. |

#### 8.6 - Infographic

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Gerarchia visiva** | C'e un titolo dominante, elementi principali di media grandezza, dettagli in piccolo. Tre livelli chiari. |
| **Coerenza grafica** | Icone, colori e font sono coerenti in tutto il documento. Nessun elemento visivamente fuori sistema. |
| **Data visualization** | Grafici e diagrammi rappresentano i dati correttamente (assi etichettati, scale corrette, nessuna distorsione). |
| **Leggibilita su mobile** | L'infografica e leggibile anche a dimensione ridotta (formato feed). Testi critici non sotto i 10px equivalenti. |

#### 8.9 - Tip & Hack / Life Hack

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Utilita immediata** | Il tip e actionable immediatamente. Non richiede attrezzatura speciale o competenze avanzate. |
| **Sorpresa o non-ovvieta** | Il hack non e ovvio. Genera la reazione "non ci avevo pensato". |
| **Ruolo del prodotto** | Il prodotto e parte integrante del tip, non un'aggiunta forzata. |

---

## MACRO-CATEGORIA 9: STORYTELLING & EMOTIONAL

> Formati: 9.1 - 9.9 (9 tipologie)
> Obiettivo primario: creare un legame emotivo profondo attraverso la narrazione che trascende le caratteristiche del prodotto.

### 9.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| ST1 | **Forza emotiva** | 30% | La creative genera un'emozione identificabile e intensa: gioia, nostalgia, ispirazione, umorismo, commozione. Non lascia indifferenti. |
| ST2 | **Coerenza narrativa** | 25% | La storia ha una struttura logica con inizio, sviluppo e conclusione. Non ci sono salti narrativi incomprensibili. |
| ST3 | **Connessione al brand/prodotto** | 20% | La storia non e bella "nonostante" il prodotto: il prodotto o il brand sono parte organica della narrativa. |
| ST4 | **Qualita della produzione** | 15% | La qualita tecnica (fotografia, video, recitazione, musica) e adeguata al livello emotivo richiesto. Una storia premium richiede esecuzione premium. |
| ST5 | **Memorabilita** | 10% | C'e un elemento (scena, battuta, visual, momento) che rende la creative ricordabile a distanza di tempo. |

### 9.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Forza emotiva** | Nessuna emozione, contenuto piatto | Emozione debole o confusa | Emozione chiara e coinvolgente | Emozione intensa, possibile trigger di condivisione |
| **Coerenza narrativa** | Storia incomprensibile o frammentata | Storia seguibile ma con lacune | Narrativa chiara e ben costruita | Narrativa perfetta, ogni elemento e necessario |
| **Connessione brand** | Brand assente o completamente secondario | Brand presente ma marginale | Brand integrato nella storia | Brand inseparabile dalla storia: la storia non esisterebbe senza il brand |
| **Qualita produzione** | Qualita tecnica incompatibile con l'ambizione emotiva | Qualita sufficiente ma non ottimale | Qualita buona, supporta l'emozione | Produzione che amplifica l'emozione, scelte stilistiche deliberate |
| **Memorabilita** | Nessun elemento distintivo | Un elemento potenzialmente ricordabile | Momento o elemento chiaramente memorabile | Creative che si ricorda a settimane di distanza |

### 9.C - Red Flags

- Storia che usa emozioni manipolative in modo irresponsabile (paura eccessiva, senso di colpa)
- Rappresentazioni stereotipate di genere, eta o etnia
- Produzione di qualita bassa per un formato che richiede alta qualita (es. spot cinematografico girato male)
- Storia troppo lunga che perde il filo prima della risoluzione
- Connessione forzata e incomprensibile tra la storia e il prodotto

### 9.D - Best Practices

- Apertura con un gancio emotivo nei primi 3 secondi
- Uso di musica che amplifica l'emozione intenzionale
- Personaggi con cui il target si puo identificare
- Risoluzione soddisfacente che include il brand in modo naturale

---

### 9.E - Criteri per Sotto-Tipologie Critiche

#### 9.3 - Emotional Appeal

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Identificazione dell'emozione target** | Una sola emozione dominante (non un mix confuso). Gioia, nostalgia, appartenenza, o altra emozione specifica. |
| **Coerenza di tutti gli elementi visivi con l'emozione** | Colori, musica (se applicabile), volti, location: tutto contribuisce all'emozione scelta. |
| **Assenza di elementi che contraddicono l'emozione** | Nessun elemento fuori posto che rompe il clima emotivo. |

#### 9.7 - Humor / Comedy / Skit

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Tempismo del punchline** | Il momento comico arriva nel momento giusto, non e anticipato o ritardato. |
| **Comprensibilita dell'umorismo** | La battuta o la situazione e comprensibile dal target senza richiedere contesto culturale troppo specifico. |
| **Non offensivita** | L'umorismo non e a spese di gruppi vulnerabili, non usa stereotipi offensivi, non mette a disagio. |
| **Collegamento al prodotto** | La situazione comica e collegata logicamente al prodotto. Non e una gag casuale. |

#### 9.9 - Documentary-Style

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Qualita cinematografica** | Fotografia, color grading, montaggio hanno qualita da documentario professionale. |
| **Autenticita dei soggetti** | Le persone mostrate (fondatori, clienti, artigiani) appaiono autentiche e non recitano. |
| **Progressione narrativa** | C'e un arco narrativo completo con inizio, climax e risoluzione. |
| **Bilanciamento voiceover/immagini** | Se presente, la voce narrante complementa le immagini senza limitarsi a descrivere quello che si vede. |

---

## MACRO-CATEGORIA 10: OFFER & PROMO-DRIVEN

> Formati: 10.1 - 10.9 (9 tipologie)
> Obiettivo primario: convertire attraverso la comunicazione diretta di un'offerta economicamente vantaggiosa o urgente.

### 10.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| OF1 | **Visibilita e impatto dell'offerta** | 35% | L'offerta (sconto, prezzo, deadline, bonus) e il primo elemento che si nota. Dimensione, colore e posizionamento la rendono dominante. |
| OF2 | **Chiarezza delle condizioni** | 25% | Non ci sono ambiguita su cosa si ottiene, quando scade, quali condizioni si applicano. |
| OF3 | **Urgency e scarcity credibili** | 20% | Se presenti elementi di urgenza (countdown, "ultimi pezzi"), appaiono credibili e non artificiali. |
| OF4 | **CTA immediata e chiara** | 20% | La call-to-action e esplicita, visivamente prominente e dice esattamente cosa fare ("Acquista ora", "Usa il codice X"). |

### 10.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Visibilita offerta** | Offerta nascosta o marginale nel design | Offerta visibile ma non dominante | Offerta chiaramente in primo piano | Offerta impatta immediatamente, impossibile non notarla |
| **Chiarezza condizioni** | Condizioni ambigue o mancanti | Condizioni parzialmente chiare | Condizioni chiaramente comunicate | Zero ambiguita, tutte le info necessarie presenti |
| **Urgency/Scarcity** | Urgency assente o palesemente falsa | Urgency accennata ma debole | Urgency credibile e motivante | Urgency fortemente credibile, FOMO reale generata |
| **CTA** | CTA assente o illeggibile | CTA presente ma debole | CTA chiara e visibile | CTA ottimale: visibile, chiara, motivante, urgente |

### 10.C - Red Flags

- Prezzo scontato superiore al prezzo originale (errore numerico)
- Sconto percentuale che non corrisponde alla differenza di prezzo mostrata
- Countdown visibilmente fermo o con data nel passato
- CTA che porta a una pagina diversa dall'offerta pubblicizzata
- Testo legale ("*condizioni applicabili") talmente piccolo da essere illeggibile
- Caratteri speciali o formatting del prezzo incoerente (es. valute diverse)

### 10.D - Best Practices

- Contrasto fortissimo tra prezzo originale (barrato) e prezzo scontato
- Badge "Risparmia X%" visivamente prominente
- Countdown visibile con ore:minuti se l'offerta e a tempo
- Prodotto visibile nell'immagine anche in un creative promo-heavy

---

### 10.E - Criteri per Sotto-Tipologie Critiche

#### 10.1 - Hard Offer / Promo

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Gerarchia del messaggio** | Nell'ordine: sconto/offerta dominante, prodotto, condizioni, CTA. Gerarchia rispettata. |
| **Numero leggibile** | La percentuale di sconto o il prezzo finale e leggibile da una distanza di visione normale (testo grande). |
| **Codice sconto visibile** | Se presente un codice, e mostrato in modo chiaro, copiabile, con font monospace o evidenziato. |

#### 10.3 - Countdown / Urgency

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Visibilita del timer** | Il countdown e un elemento visivo dominante, non nascosto in basso. |
| **Credibilita della scadenza** | La data/ora di scadenza e specifica e credibile (non "offerta valida per sempre" con countdown). |
| **Contrasto visivo del countdown** | Il countdown usa colori ad alto contrasto e impatto (rosso, nero, arancione) per creare senso di urgenza. |

#### 10.8 - Price Anchor

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Chiarezza del prezzo originale barrato** | Il prezzo originale e chiaramente barrato e leggibile (non cancellato completamente). |
| **Prominenza del prezzo scontato** | Il prezzo finale e significativamente piu grande del prezzo barrato (almeno 1.5x). |
| **Calcolo visivamente coerente** | Se mostrate sia percentuale che prezzi, i numeri sono matematicamente coerenti. |

---

## MACRO-CATEGORIA 11: NATIVE & TREND-DRIVEN

> Formati: 11.1 - 11.12 (12 tipologie)
> Obiettivo primario: integrarsi nella piattaforma in modo da sembrare contenuto organico, sfruttando trend e cultura nativa.

### 11.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| NT1 | **Platform nativeness** | 30% | Il contenuto sembra nativo della piattaforma target (TikTok, Instagram, ecc.). Rispetta le convenzioni estetiche, i formati e i pattern di comunicazione tipici della piattaforma. |
| NT2 | **Tempestivita e rilevanza del trend** | 25% | Se si sfrutta un trend, questo e attuale e non scaduto. Il trend e adattato al brand in modo credibile. |
| NT3 | **Autenticita e spontaneita** | 25% | Il contenuto non appare pianificato in modo eccessivo. Ha la spontaneita tipica del contenuto organico. |
| NT4 | **Engagement bait legittimo** | 20% | Elementi che stimolano l'interazione (domande, elementi curiosi, punchline finale) sono presenti e non manipolatori. |

### 11.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Platform nativeness** | Appare chiaramente come un'ad tradizionale su una piattaforma social | Tenta di essere nativo ma si riconosce come branded | Convincente come contenuto nativo | Indistinguibile dal contenuto organico top della piattaforma |
| **Tempestivita trend** | Trend scaduto o non pertinente | Trend ancora rilevante ma in declino | Trend attuale e pertinente | Trend al picco della viralita, perfettamente adattato |
| **Autenticita** | Eccessivamente prodotto per sembrare spontaneo | Qualche elemento di spontaneita | Generalmente spontaneo e credibile | Totalmente spontaneo, nessun elemento che tradisce la pianificazione |
| **Engagement** | Nessun elemento che invita all'interazione | Un accenno di engagement bait | Elementi di engagement chiari e legittimi | Struttura ottimizzata per massimo engagement organico |

### 11.C - Red Flags

- Uso di un trend con timing sbagliato (trend scaduto da settimane)
- Qualita produzione troppo alta per una piattaforma lo-fi (tradisce la natura di ad)
- Uso di un trend di nicchia non riconoscibile dal target principale
- Meme o formato cultural reference adattato in modo forzato e incomprensibile
- Logo brand eccessivamente prominente che rompe la natura nativa

### 11.D - Best Practices

- Formato 9:16 nativo per TikTok/Reels
- Uso di font, sticker e overlay tipici della piattaforma
- Inizio in medias res (no intro brandizzata)
- Presenza di caption testuale in formato piattaforma (primo piano del testo)

---

### 11.E - Criteri per Sotto-Tipologie Critiche

#### 11.1 - Talking Head

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Inquadratura ottimale** | Busto superiore visibile, viso ben illuminato, occhi all'altezza del terzo superiore del frame (regola dei terzi verticale). |
| **Intensita della presenza** | Il creator mantiene contatto visivo con la camera. L'energia e appropriata al messaggio (non piatta). |
| **Background coerente** | Lo sfondo e rilevante o neutro. Non distrae dalla persona. |
| **Hook nei primi 2 secondi** | Le prime parole o il primo gesto catturano immediatamente l'attenzione. |

#### 11.2 - Lo-Fi / "Ugly Ads"

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Imperfezione intenzionale** | Le imperfezioni sono visibilmente scelte (shake della camera, luce non ottimale) non casuali. |
| **Messaggio chiaro nonostante il lo-fi** | Pur nell'estetica grezza, il prodotto e il messaggio sono comprensibili. |
| **Coerenza con lo spirito del brand** | Il lo-fi e coerente con i valori del brand (brand premium non dovrebbe usare lo-fi estremo). |

#### 11.5 - Meme / Internet Culture

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Riconoscibilita del template** | Il meme template usato e riconoscibile dal target. Non richiede spiegazione. |
| **Adattamento pertinente** | Il testo del meme e coerente con il template e il brand. Non e forzato. |
| **Attualita** | Il meme non e "vecchio" o gia sovraesposto. Ha ancora freschezza culturale. |
| **Qualita grafica** | Il testo del meme e leggibile, il formato e quello canonico per quel template. |

#### 11.11 - Screenshot / Native-Looking

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Verosimiglianza dello screenshot** | Lo screenshot simula fedelmente l'interfaccia della piattaforma (colori, font, layout). |
| **Contenuto credibile** | Il messaggio/notifica simulata e plausibile e non esagerata. |
| **Non ingannevolezza** | Lo screenshot non simula una notifica reale in modo da ingannare l'utente in malafede (compliance ads). |

---

## MACRO-CATEGORIA 12: VISUAL DESIGN & STILE DI PRODUZIONE

> Formati: 12.1 - 12.17 (17 tipologie)
> Obiettivo primario: comunicare principalmente attraverso scelte stilistiche, grafiche e di produzione visiva.

### 12.A - Criteri Specifici di Categoria

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| VD1 | **Coerenza del sistema visivo** | 25% | Tutti gli elementi grafici (font, colori, spaziature, icone) appartengono a un sistema coerente. Nessun elemento e fuori sistema. |
| VD2 | **Impatto visivo dello stop-the-scroll** | 25% | Il creative ha una forza visiva immediata che interrompe lo scroll: contrasto, colore, movimento, composizione inusuale. |
| VD3 | **Qualita dell'esecuzione grafica** | 20% | L'esecuzione tecnica (typesetting, allineamenti, spaziature, qualita delle immagini) e professionale. Nessun dettaglio curato male. |
| VD4 | **Gerarchia tipografica** | 15% | Se presente testo, la gerarchia tipografica e chiara: titolo, sottotitolo, corpo, dettaglio. Ogni livello e visivamente distinto. |
| VD5 | **Coerenza con il brand positioning** | 15% | Lo stile visivo e appropriato al posizionamento del brand (luxury non usa aesthetic da meme; DTC non usa aesthetic da corporate). |

### 12.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Sistema visivo** | Elementi grafici incoerenti tra loro | Qualche incoerenza ma sistema percepibile | Sistema coerente con qualche sbavatura | Sistema visivo perfettamente coerente in ogni dettaglio |
| **Stop-the-scroll** | Nessuna forza visiva, passa inosservato | Discretamente attraente | Chiaramente attraente, invita alla lettura | Impossibile non fermarsi: forza visiva eccezionale |
| **Esecuzione grafica** | Esecuzione amatoriale evidente | Esecuzione accettabile | Esecuzione professionale | Esecuzione di design award-winning |
| **Gerarchia tipografica** | Nessuna gerarchia, tutto allo stesso livello | Gerarchia accennata | Gerarchia chiara e funzionale | Gerarchia perfetta, guida lo sguardo in modo intuitivo |
| **Coerenza brand** | Stile completamente incoerente con il brand | Parzialmente coerente | Stile ben allineato al brand | Stile che rinforza e definisce il brand positioning |

### 12.C - Red Flags

- Font non leggibili (eccessivamente decorativi per testi di corpo)
- Gradiente con banding (transizione di colore a "scalini" invece di graduale)
- Allineamenti errati (elementi non allineati a griglia, spaziature irregolari)
- Troppi font diversi nello stesso layout (piu di 2-3 famiglie tipografiche)
- Colori accessibili non rispettati (testo su sfondo a basso contrasto)
- Animazioni con frame-rate basso o motion-blur eccessivo su testo

### 12.D - Best Practices

- Uso di whitespace generoso (il vuoto ha valore nel design)
- Una palette di non piu di 3-4 colori dominanti
- Font size gerarchicamente distinto (es. 48px titolo, 24px sottotitolo, 16px corpo)
- Allineamento a griglia percepibile

---

### 12.E - Criteri per Sotto-Tipologie Critiche

#### 12.1 - Bold Text / Typography-First

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Peso e dimensione del font** | Il testo occupa almeno il 50% dell'immagine. Il font e bold o black weight. |
| **Contrasto testo-sfondo** | Contrasto ratio superiore a 7:1 per il testo principale (WCAG AAA). |
| **Impatto del messaggio** | Il messaggio comunicato in poche parole e forte, diretto e memorabile. |
| **Qualita del typesetting** | Crenatura (kerning), interlinea (leading) e spaziatura delle parole sono ottimali. |

#### 12.4 - Color Blocking

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Saturazione e vivacita dei colori** | I blocchi di colore sono saturi e vivaci, non slavati o pastello (a meno che non sia intenzionale per il brand). |
| **Contrasto tra i blocchi** | I blocchi adiacenti hanno sufficiente contrasto tra loro da essere chiaramente distinguibili. |
| **Equilibrio compositivo** | La divisione dello spazio tra i blocchi di colore e visivamente equilibrata o intenzionalmente asimmetrica in modo dinamico. |
| **Leggibilita di eventuali testi sui blocchi** | Se c'e testo sui blocchi, il colore del testo contrasta con il blocco su cui poggia. |

#### 12.7 - Stop Motion

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Fluidita del movimento** | Il numero di frame e sufficiente a creare un movimento fluido (minimo 12fps equivalente). |
| **Coerenza della scena tra frame** | Gli oggetti mantengono posizione coerente tra un frame e l'altro (no jump bruschi non intenzionali). |
| **Qualita visiva dei singoli frame** | Ogni frame singolo e a fuoco e ben illuminato. |
| **Narrativa del movimento** | Il movimento racconta qualcosa: trasformazione, sequenza, azione del prodotto. |

#### 12.9 - Motion Graphics / Animated

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Qualita dell'animazione** | Le animazioni hanno easing naturale (non lineari). I movimenti sono fluidi e professionali. |
| **Sincronia audio-video** | Se presente audio, la sincronia tra elementi visivi e audio e precisa. |
| **Leggibilita degli elementi animati** | Il testo in movimento e visibile abbastanza a lungo da essere letto. |
| **Coerenza dello stile di animazione** | Tutti gli elementi usano lo stesso stile di motion (non mix di stili diversi non intenzionale). |

#### 12.11 - Kinetic Text / Text Animation

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Timing di entrata del testo** | Il testo appare nel momento esatto in cui viene detto o nel momento narrativamente corretto. |
| **Leggibilita durante il movimento** | Il testo rimane leggibile anche durante l'animazione di entrata/uscita. |
| **Stile di animazione coerente** | Un solo stile di animazione del testo (o stili intenzionalmente variati con logica). |

---

## MACRO-CATEGORIA 13: INTERACTIVE & IMMERSIVE

> Formati: 13.1 - 13.6 (6 tipologie)
> Obiettivo primario: massimizzare l'engagement attraverso interazione diretta dell'utente con il contenuto.

### 13.A - Criteri Specifici di Categoria

> Nota: questa categoria include formati che richiedono interazione. La valutazione AI si concentra sulla qualita visiva dello stato statico (screenshot, thumbnail, preview) e sulla chiarezza dell'invito all'interazione.

| ID | Criterio | Peso | Descrizione |
|----|----------|------|-------------|
| IN1 | **Chiarezza dell'invito all'interazione** | 30% | E immediatamente chiaro che il contenuto e interattivo e cosa fare (tocca, rispondi, ruota, gioca). |
| IN2 | **Qualita visiva dello stato iniziale** | 25% | La preview statica o il frame iniziale sono visivamente attraenti e invogliano l'interazione. |
| IN3 | **Pertinenza e interesse dell'interazione** | 25% | Il tipo di interazione proposta e rilevante per il prodotto e interessante per il target. Non e interazione per se. |
| IN4 | **Accessibilita dell'esperienza** | 20% | L'esperienza interattiva non richiede istruzioni complesse. Si capisce immediatamente come interagire. |

### 13.B - Scala di Valutazione Specifica

| Score | Basso (1-3) | Medio (4-6) | Buono (7-8) | Eccellente (9-10) |
|-------|-------------|-------------|-------------|-------------------|
| **Chiarezza interazione** | Non si capisce che e interattivo o come interagire | L'interativita e intuibile ma non ovvia | Chiaramente interattivo, azione chiara | Invito all'interazione irresistibile e immediato |
| **Qualita visiva preview** | Preview visivamente povera, non invoglia | Preview accettabile | Preview attraente e pertinente | Preview eccellente, massimizza il click-through |
| **Pertinenza interazione** | Interazione casuale e non pertinente al prodotto | Interazione parzialmente pertinente | Interazione pertinente e interessante | Interazione che approfondisce in modo unico il valore del prodotto |
| **Accessibilita** | Esperienza complessa o frustrante | Esperienza usabile con sforzo | Esperienza intuitiva | Esperienza immediatamente comprensibile e fluida |

### 13.C - Red Flags

- Invito all'interazione non visibile o nascosto
- Preview statica che non rappresenta correttamente l'esperienza interattiva
- Esperienza interattiva che richiede troppi step prima di arrivare al valore
- AR try-on con riconoscimento facciale/corporeo impreciso (visibile da frame di errore)
- Playable ad con meccaniche di gioco non intuitive

### 13.D - Best Practices

- CTA visiva esplicita ("Tocca per provare", "Rispondi", "Gioca ora") nella preview
- Preview che mostra un frame "in media res" dell'esperienza, non uno stato neutro
- Esperienza completabile in meno di 30 secondi
- Valore immediato all'inizio dell'interazione (non dopo un lungo caricamento)

---

### 13.E - Criteri per Sotto-Tipologie Critiche

#### 13.1 - Poll / Quiz Ad

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Chiarezza della domanda** | La domanda del poll/quiz e chiara, breve e univoca. Non richiede riflessione eccessiva. |
| **Pertinenza delle opzioni** | Le opzioni di risposta sono pertinenti, esaustive e mutuamente esclusive. |
| **Rilevanza per il prodotto** | Il poll/quiz e tematicamente collegato al prodotto in modo logico. |
| **Visual design delle opzioni** | Le opzioni sono visivamente distinte e facilmente selezionabili (target touch area adeguata). |

#### 13.2 - AR Try-On / Virtual Preview

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Realismo della sovrapposizione AR** | Il prodotto virtuale si integra visivamente con l'ambiente reale in modo credibile (colori, ombre, scala). |
| **Precisione del tracking** | Il prodotto AR si posiziona correttamente sul soggetto (viso, corpo, ambiente) senza slittamenti evidenti. |
| **Qualita del rendering del prodotto** | Il modello 3D del prodotto e fedele al prodotto reale in termini di colore, materiale e proporzioni. |
| **Chiarezza del CTA post-try-on** | Dopo la prova virtuale, e chiaro come procedere all'acquisto. |

#### 13.4 - Playable Ad

| Criterio | Descrizione specifica |
|----------|----------------------|
| **Qualita visiva del mini-gioco** | La grafica del gioco e curata e non amatoriale. |
| **Collegamento meccaniche-prodotto** | Le meccaniche di gioco sono metaforicamente o direttamente collegate al prodotto/brand. |
| **Chiarezza delle regole** | Le regole del gioco si capiscono in 5 secondi senza istruzioni testuali. |
| **CTA post-gameplay** | Dopo il gioco, il passaggio al prodotto/acquisto e naturale e motivato dall'esperienza appena vissuta. |

---

## TABELLA RIEPILOGATIVA DEI PESI PER CATEGORIA

| Macro-Categoria | Criteri Universali | Criteri Specifici | Note chiave |
|----------------|-------------------|-------------------|-------------|
| 1. Product-Centric | 35% | 65% | Nitidezza e illuminazione i piu critici |
| 2. Lifestyle & Context | 35% | 65% | Mood e naturalezza prodotto i piu critici |
| 3. Behind the Scenes | 35% | 65% | Autenticita percepita il criterio dominante |
| 4. UGC & Creator | 35% | 65% | Autenticita e naturalezza i piu critici |
| 5. Social Proof | 35% | 65% | Credibilita della prova il criterio dominante |
| 6. Problem-Solution | 35% | 65% | Chiarezza trasformazione e logica soluzione |
| 7. Comparison | 35% | 65% | Chiarezza confronto e credibilita dati |
| 8. Educational | 35% | 65% | Chiarezza e struttura sequenziale |
| 9. Storytelling | 35% | 65% | Forza emotiva e coerenza narrativa |
| 10. Offer & Promo | 35% | 65% | Visibilita offerta e CTA i piu critici |
| 11. Native & Trend | 35% | 65% | Platform nativeness il criterio dominante |
| 12. Visual Design | 35% | 65% | Sistema visivo e stop-the-scroll |
| 13. Interactive | 35% | 65% | Chiarezza interazione il criterio dominante |

---

## SCORING FINALE: GRIGLIA DI DECISIONE

| Score Composito | Classificazione | Azione raccomandata |
|----------------|-----------------|---------------------|
| 9.0 - 10.0 | **Eccellente** | Creative da benchmark. Da usare come riferimento per future produzioni. |
| 7.5 - 8.9 | **Buono** | Creative pubblicabile. Piccoli miglioramenti opzionali ma non bloccanti. |
| 6.0 - 7.4 | **Sufficiente** | Creative pubblicabile con riserva. Miglioramenti raccomandati prima del lancio. |
| 4.0 - 5.9 | **Insufficiente** | Creative da non pubblicare. Richiede revisione sostanziale su criteri chiave. |
| 1.0 - 3.9 | **Scartare** | Creative con difetti gravi. Non pubblicare. Richiedere nuova produzione. |

### Override automatici (abbassano il punteggio finale a massimo 5.0)

Qualsiasi creative che presenta UNO dei seguenti elementi viene automaticamente cappato a 5.0 indipendentemente dagli altri criteri:

1. Watermark visibile di terze parti non rimosso
2. Informazioni errate verificabili (prezzo sbagliato, sconto non corrispondente)
3. Immagini di stock riconoscibili con persone (rischio brand safety)
4. Testo principale illeggibile nel formato di destinazione
5. Prodotto non identificabile nell'immagine
6. Elementi visivi che violano le policy pubblicitarie delle piattaforme (contenuto sensibile, claim non consentiti)

---

*Fine documento — 02_criteri_qualita_per_tipologia.md*
*Documento correlato: `mappatura_formati_creativi_adv.md`*
