# SECOND-KNOWLEDGE-BRAIN.md — TrendScout Living Knowledge Corpus

> **APPEND-ONLY FILE.** New entries go at the TOP of each section with a dated header.  
> Updated nightly by `src/knowledge/updater.py`.  
> Top-5 semantically relevant entries injected into the agent's system prompt at startup.  
> **Never delete or modify existing entries.**

---

## How This File Works

At agent startup, `src/knowledge/updater.py` queries the local HNSW vector index at `~/.trendscout/knowledge-index/` and retrieves the entries most semantically relevant to the current pipeline task (e.g., "detect fake GitHub stars", "score KOL influence", "cluster emerging topics"). Those entries are prepended to the scoring/synthesis context — making every model decision progressively better as the corpus grows.

**Entry Format:**
```
## [CATEGORY] — Updated: YYYY-MM-DD

### [Title] (Source: URL)
**Key Insight:** One-sentence distillation
**Relevance to TrendScout:** Direct application to a module or design decision
**Applied In:** src/module/file.py (once implemented; leave blank otherwise)
**Tags:** comma-separated

---
```

**Categories:**
- `SIGNAL-DETECTION` — methods for finding genuine signals in noisy data streams
- `FAKE-STAR-AUTHENTICITY` — fake engagement detection, astroturfing, bot networks
- `TOPIC-MODELING` — BERTopic, LDA, online topic evolution, emerging trend classification
- `KOL-INFLUENCE` — key opinion leader identification, influence weighting, network analysis
- `GITHUB-ANALYTICS` — repository health metrics, star velocity, contributor dynamics
- `SOCIAL-MEDIA-NLP` — sentiment analysis, entity extraction, tech discourse analysis
- `MOMENTUM-DIFFUSION` — cross-platform viral spread, HN→GitHub diffusion, adoption curves
- `DIGEST-SYNTHESIS` — LLM-based narrative generation, structured-to-text pipelines
- `INVESTMENT-SIGNALS` — GitHub as alternative data for tech equity research

---

## [FAKE-STAR-AUTHENTICITY] — Updated: 2026-05-31

### Six Million (Suspected) Fake Stars on GitHub: A Growing Spiral (Source: https://arxiv.org/html/2412.13459v2)
**Key Insight:** CMU's StarScout tool identified ~6 million suspected fake stars across GitHub by detecting lockstep behavioral patterns (multiple accounts starring the same repo within narrow time windows) and low-activity account signatures, validated by comparing deletion rates of flagged repos/accounts against GitHub's own takedowns.
**Relevance to TrendScout:** Direct blueprint for our `authenticity_filter.py`. The lockstep burst detector (burst in 5-min windows), ghost account detection (account age + activity check on sampled stargazers), and cross-platform coherence check together form a three-signal ensemble that is harder to game than any single signal. Use StarScout's deletion-rate validation methodology to evaluate our own filter accuracy.
**Applied In:** src/scoring/authenticity_filter.py
**Tags:** fake-stars, StarScout, CMU, lockstep, ghost-accounts, authenticity

---

### Inside GitHub's Fake Star Economy (Source: https://peerlist.io/saxenashikhil/articles/inside-githubs-fake-star-economy)
**Key Insight:** Services like SocialPlug claim 3.1M stars delivered to 53K+ clients; star campaigns now mimic organic growth curves (delivered slowly over weeks with coordinated fake Product Hunt launches and HN posts to explain the spike); the only reliable counter-signals are cross-platform coherence and stargazer account quality — not velocity alone.
**Relevance to TrendScout:** Updates our threat model: naive lockstep detection catches old-generation fakes, but sophisticated campaigns now distribute stars over weeks. Our `cross_platform_coherence_scorer` is therefore the most robust signal — fake campaigns can manufacture GitHub stars cheaply but generating authentic HN threads or real KOL engagement is expensive. Weight coherence at 0.25 in authenticity composite.
**Applied In:** src/scoring/authenticity_filter.py (cross_platform_coherence, weight tuning)
**Tags:** fake-stars, astroturfing, star-economy, Fiverr, SocialPlug, platform-coherence

---

### Your GitHub Stars Might Be Fake — Replacing Stars with Verifiable Signals (Source: https://medium.com/@joefreccejunior50/your-github-stars-might-be-fake-and-its-a-bigger-problem-than-you-think-0580d35f07d0)
**Key Insight:** OpenSSF Scorecard v5 (19+ automated security/health criteria, scored 0–10) and CHAOSS metrics (contributor diversity, commit frequency, issue resolution time) are the most reliable star-replacement signals in 2026; "Trusted Open Source Index" (TOSI) composites Scorecard + CHAOSS + SLSA + GitHub data.
**Relevance to TrendScout:** Add OpenSSF Scorecard API calls as an optional enrichment step in `GitHubScorer` — repos with Scorecard > 7 get a quality bonus. CHAOSS-aligned metrics (contributor diversity, issue response time) should be in our `github_scorer.py` from Phase 3. TOSI is a future integration target for Phase 9.
**Applied In:** src/scoring/github_scorer.py (CHAOSS-aligned metrics), Phase 9 (TOSI integration)
**Tags:** OpenSSF, CHAOSS, TOSI, verifiable-signals, repo-health, scorecard

---

### GitHub Stars History: Tracking, Analyzing, and Growing Open Source Repositories (Source: https://earezki.com/ai-news/2026-04-03-github-stars-history-how-to-track-analyze-grow-your-repository/)
**Key Insight:** Star velocity (stars gained per week) is the primary metric rewarded by GitHub's own trending algorithm; the `starred_at` ISO timestamp field in the GitHub API enables granular velocity analysis; the critical distinction for signal quality is between a "bot-driven vertical cliff" pattern and a "multiple spike" pattern from genuine community re-activation.
**Relevance to TrendScout:** Confirms that `starred_at` timestamp extraction is the foundation of our velocity and lockstep analysis. The "vertical cliff vs. multiple spike" visual heuristic maps directly to our lockstep detector threshold tuning: a single tight burst = suspicious, multiple spikes correlated with external events (HN posts, blog mentions) = authentic. Use this as training signal for the authenticity classifier.
**Applied In:** src/scoring/authenticity_filter.py (burst pattern shapes), src/scoring/github_scorer.py (velocity)
**Tags:** star-velocity, starred_at, trending-algorithm, burst-patterns, GitHub-API

---

## [TOPIC-MODELING] — Updated: 2026-05-31

### BERTrend: Neural Topic Modeling for Emerging Trends Detection (Source: https://arxiv.org/pdf/2411.05930)
**Key Insight:** BERTrend extends BERTopic with online learning (consecutive time-slice model merging via cosine similarity between topic centroids) and a decay-weighted popularity metric `popularity(topic,t) = Σ docs × update_recency × exp(-λ × days_since_update)` that automatically classifies topics as NOISE / WEAK SIGNAL / STRONG SIGNAL — emphasizing temporal growth of nascent topics over static topic sizes.
**Relevance to TrendScout:** This is the direct implementation blueprint for `src/nlp/topic_modeler.py`. Key implementation details: (1) segment long documents into paragraphs before embedding to avoid truncation; (2) use consecutive-day model merging rather than full retraining; (3) the decay factor λ should be tuned so that topics with no new documents for 7+ days fade to NOISE. The WEAK→STRONG transition is our "include in digest" trigger.
**Applied In:** src/nlp/topic_modeler.py
**Tags:** BERTrend, BERTopic, online-learning, emerging-signals, topic-evolution, NOISE-WEAK-STRONG

---

### Fine-Tune Your Topic Modeling Workflow with BERTopic (Source: https://towardsdatascience.com/finetune-your-topic-modeling-workflow-with-bertopic/)
**Key Insight:** BERTopic's four-step pipeline (embedding → UMAP dimensionality reduction → HDBSCAN clustering → c-TF-IDF topic representation) benefits significantly from tuning: `min_topic_size=5` for small daily corpora, `nr_topics="auto"` for dynamic signal counts, and custom stopword lists for domain-specific noise (e.g., generic tech words like "github", "open", "source" that appear in every document).
**Relevance to TrendScout:** Practical tuning guide for our BERTopic instantiation. For TrendScout's daily signal corpus (estimated 200–500 documents/day), `min_topic_size=5` prevents over-fragmentation. Add a custom stopword list of generic open-source vocabulary to `src/nlp/topic_modeler.py::TECH_STOPWORDS`. GPU accelerates embedding but CPU is sufficient for our volume.
**Applied In:** src/nlp/topic_modeler.py (configuration constants)
**Tags:** BERTopic, tuning, HDBSCAN, UMAP, stopwords, min_topic_size

---

### Topic Modelling Using BERTopic for Robust Spam Detection (Source: https://www.researchgate.net/publication/380615870)
**Key Insight:** BERTopic applied to spam detection achieves high accuracy by identifying structurally similar topic clusters corresponding to spam templates — the same mechanism works in reverse: repositories whose README embeddings cluster tightly with known marketing-template topics are likely clone/spam repos.
**Relevance to TrendScout:** Directly applicable to `src/nlp/clone_detector.py`. Build a "spam template corpus" by manually labeling 50 known template/boilerplate repos, extract their README embeddings, store as cluster centroids. Any new repo whose README embedding falls within threshold distance of a spam cluster centroid gets flagged. Reuse the BERTopic model already loaded for trend detection — shared embedding model = no extra compute.
**Applied In:** src/nlp/clone_detector.py (reuse BERTopic embedding model)
**Tags:** BERTopic, spam-detection, clone-detection, README-embedding, template-repos

---

## [KOL-INFLUENCE] — Updated: 2026-05-31

### Mapping the Technological Future: KOL Analysis on X (Source: https://arxiv.org/pdf/2407.17522)
**Key Insight:** BERTopic modeling of 1.5M tweets from 400 identified tech KOLs (2021–2023) reveals that KOL anticipatory discourse clusters around specific technology themes 6–18 months before those themes reach mainstream coverage; KOL sentiment ('Hope' score 10.33% above median 'Anxiety') is itself a leading indicator of technology adoption velocity.
**Relevance to TrendScout:** Validates the 6-18 month lead time of KOL signals over mainstream adoption — this is the core value proposition of our KOL scoring layer. Also validates using BERTopic (already in our NLP stack) for KOL discourse analysis, meaning we can identify not just *what* KOLs mention but *which emerging tech cluster* they're signaling with their language. Feed KOL post embeddings into the same BERTopic model used for general signal clustering.
**Applied In:** src/scoring/kol_registry.py (lead-time hypothesis), src/nlp/topic_modeler.py (KOL posts as input documents)
**Tags:** KOL, key-opinion-leaders, tech-forecasting, BERTopic, anticipatory-discourse, lead-time

---

### Mapping Technological Futures: Anticipatory Discourse Through Text Mining (Source: https://arxiv.org/pdf/2504.02853)
**Key Insight:** Three research questions that should guide KOL influence modeling: (RQ1) What are the characteristics of KOL influence on social platforms? (RQ2) What are the dominant themes in their anticipatory discourse? (RQ3) How does discourse evolve over time in response to external events? External events (model releases, acquisitions, papers) act as "discourse accelerators" for KOL networks.
**Relevance to TrendScout:** Formalizes the framework for our KOL registry. RQ1 → KOL weight model. RQ2 → topic domain tags in `kol_registry.json`. RQ3 → the "trigger event" field in `DigestItem.why_now`. When a KOL network shows sudden coordinated discourse acceleration around a topic (all independently mentioning the same thing within 48h), that is a STRONG SIGNAL regardless of the GitHub metrics.
**Applied In:** src/scoring/kol_registry.py, src/digest/synthesizer.py (trigger_event field)
**Tags:** KOL, anticipatory-discourse, trigger-events, discourse-acceleration, social-network

---

### Social Sentiment Sensor: KOL Network Analysis and Influence Identification (Source: https://link.springer.com/chapter/10.1007/978-981-96-5238-9_3)
**Key Insight:** Network analysis of Twitter interactions identifies "bridge nodes" — KOLs who connect otherwise separate technology communities — as having disproportionate influence on information diffusion; bridge KOLs who span e.g. "systems programming" and "ML infrastructure" communities are particularly high-value for cross-domain emerging technology signals.
**Relevance to TrendScout:** Add a `bridge_score` field to `kol_registry.json`: KOLs who span multiple domain_tags (e.g., ["databases", "ml-infra", "distributed-systems"]) should have a higher base weight multiplier (×1.2) because they surface cross-domain convergence signals — often the most important technology shifts happen at the intersection of two domains.
**Applied In:** src/scoring/kol_registry.py (bridge_score multiplier)
**Tags:** network-analysis, bridge-nodes, cross-domain, influence-diffusion, KOL-weighting

---

## [MOMENTUM-DIFFUSION] — Updated: 2026-05-31

### Launch-Day Diffusion: Tracking Hacker News Impact on GitHub Stars for AI Tools (Source: https://arxiv.org/pdf/2511.04453)
**Key Insight:** Analysis of 138 HN-to-GitHub repository pairs (2024–2025) reveals: repos gain avg 121 stars in 24h, 189 in 48h, and 289 in 7 days after HN front-page exposure; Gradient Boosting on post metadata (score at 2h, comment count, title length) predicts viral growth better than Elastic Net; the 2-hour HN score is the single best predictor of ultimate star growth.
**Relevance to TrendScout:** Quantifies the HN→GitHub diffusion model precisely. Our MomentumScorer should weight HN signals by the 2-hour point score (not final score, since we need to fire signals early). The research confirms our 48-hour co-spike window is the right choice. Also: a repo appearing on HN that has NOT yet spiked on GitHub is a *predictive* signal — we should catch these early and alert before the GitHub spike fully materializes.
**Applied In:** src/scoring/momentum_scorer.py (2h HN score feature), src/collectors/hackernews.py (2h score tracking)
**Tags:** HN-diffusion, launch-day, star-velocity, momentum, Gradient-Boosting, predictive-signal

---

### GitHub and Software Adoption Data for Investment Research 2026 (Source: https://www.paradoxintelligence.com/blog/github-software-adoption-data-investment-research)
**Key Insight:** Star velocity and fork rates across major AI libraries gave early signals of developer mindshare 6-18 months before commercial contract traction appeared; thematic investors tracking aggregate activity trends across a target technology category get a real-time view of theme momentum before it shows in revenue or analyst estimates.
**Relevance to TrendScout:** Validates the investment-grade use case for TrendScout. The "aggregate category tracking" pattern (not just individual repos but the total activity across all repos in a theme cluster) is implemented by our BERTrend layer: the STRONG SIGNAL classification on a topic cluster is essentially a thematic momentum indicator. Add a "category momentum score" computed from the sum of constituent signal scores within each BERTrend cluster.
**Applied In:** src/nlp/topic_modeler.py (category momentum aggregation), investment use case documentation
**Tags:** investment-signals, developer-mindshare, thematic-momentum, alternative-data, leading-indicator

---

### LLM-Powered Trend Analysis: From Scraped Signals to Narratives (Source: https://scrapingant.com/blog/llm-powered-trend-analysis-from-scraped-signals-to)
**Key Insight:** End-to-end LLM trend analysis pipelines are most impactful at two specific layers: (1) turning heterogeneous raw data into structured views via NLP, and (2) turning structured data into stakeholder-specific narratives — LLMs should not infer or generate raw metrics but should contextualize and explain pre-computed signals.
**Relevance to TrendScout:** Validates our strict LLM contract: LLM receives structured metrics and writes narrative only. Also validates the pipeline architecture (collector → NLP structuring → LLM synthesis) rather than feeding raw scraped text directly to an LLM. The "use time-series analysis to detect acceleration phases before LLM interpretation" instruction directly maps to our flow: scorer → ranker → synthesizer.
**Applied In:** src/digest/synthesizer.py (strict input contract), src/main.py (pipeline order)
**Tags:** LLM-pipeline, narrative-synthesis, structured-input, trend-analysis, ScrapingAnt

---

## [GITHUB-ANALYTICS] — Updated: 2026-05-31

### GitHub Statistics 2026: 180M Developers, 630M Repositories (Source: https://coinlaw.io/github-statistics/)
**Key Insight:** GitHub reached 180M developers and 630M repositories in 2026 with 230 new repos/minute; Asia-Pacific saw 38% user growth led by Vietnam, Indonesia, and Bangladesh; TypeScript became the most-used language in August 2025 overtaking Python and JavaScript, driven by AI-assisted coding adoption.
**Relevance to TrendScout:** Scale context for our signal-to-noise problem: 230 repos/minute = 331,200 repos/day. Our pipeline must filter this to 5-10 digest items. Also: the high Asia-Pacific growth (including Vietnam, our primary user base) means our collector should not be biased toward English-language repos only — include Vietnamese and Chinese language tech discussions in the collector scope (Zalo Tech Blog, WeChat tech accounts as future Discord-equivalent sources).
**Applied In:** src/collectors/github.py (language/region diversity), docs/contributing.md
**Tags:** GitHub-2026, scale, Asia-Pacific, Vietnam, TypeScript, repository-growth

---

### GitHub Trending Analysis: January 2026 — The Great Coding Agent Race (Source: https://medium.com/@lssmj2014/github-trending-january-6-2026-the-great-coding-agent-race-49c42471ac5f)
**Key Insight:** OpenCode overtook Claude Code in GitHub stars on Jan 6, 2026 (+1,852 stars in one day); Microsoft's VibeVoice (open-source voice AI) reached 19,803 stars immediately; Manim (83K stars) demonstrates that educational/visualization tools sustain long-term community momentum differently from "launch-and-forget" AI wrappers.
**Relevance to TrendScout:** Provides qualitative ground truth for calibrating our digest. A legitimate STRONG SIGNAL event (OpenCode surge) should receive a composite score > 0.8. The VibeVoice launch shows how "major company open-sources frontier model" is a distinct signal type — add a `signal_type` field to `DigestItem`: "organic-community", "institutional-release", "viral-launch", "sustained-momentum". Each type has a different "why_now" narrative pattern for the LLM synthesizer.
**Applied In:** src/scoring/composite_scorer.py (signal_type classification), src/digest/synthesizer.py (narrative templates per signal_type)
**Tags:** GitHub-trending, signal-calibration, OpenCode, signal-types, institutional-release

---

## [SOCIAL-MEDIA-NLP] — Updated: 2026-05-31

### BERTopic for Spam Detection: Topic Similarity as Authenticity Signal (Source: https://www.researchgate.net/publication/380615870_Topic_Modelling_Using_BERTopic_for_Robust_Spam_Detection)
**Key Insight:** BERTopic identifies spam not by keywords but by structural topic similarity — spam documents cluster tightly in embedding space because they follow narrow template patterns; legitimate diverse content produces more spread-out topic distributions.
**Relevance to TrendScout:** Dual use: (1) detect spam/marketing-clone repos via README embedding clustering (already noted in TOPIC-MODELING section), and (2) detect coordinated X/HN astroturfing campaigns by checking if a batch of "organic" social posts cluster suspiciously tightly in BERTopic space. Legitimate organic discussion about a project is topically diverse; coordinated campaigns use similar phrasing and cluster tightly.
**Applied In:** src/nlp/clone_detector.py, src/scoring/authenticity_filter.py (social astroturfing detection)
**Tags:** BERTopic, spam, astroturfing, embedding-clustering, social-manipulation

---

### New Trends and Applications in Social Media Analytics (Source: https://www.sciencedirect.com/science/article/abs/pii/S0167739X20324924)
**Key Insight:** Social media analytics combines clustering, community detection, sentiment analysis, and network analysis for applications including financial forecasting — the multi-method approach consistently outperforms any single technique, especially for detecting emerging signals in noisy real-time streams.
**Relevance to TrendScout:** Validates our ensemble approach across the entire scoring layer. No single signal (stars, HN points, KOL mentions, sentiment, novelty) is reliable alone; the composite ensemble is the correct design. The financial forecasting connection also validates our investment-grade signal framing — tech sentiment on social media precedes market signals, just as it precedes mainstream adoption.
**Applied In:** src/scoring/composite_scorer.py (ensemble philosophy)
**Tags:** social-media-analytics, ensemble-methods, community-detection, financial-forecasting, sentiment

---

## Knowledge Brain Statistics

| Metric | Value |
|---|---|
| Total entries | 16 |
| Categories covered | 7 of 9 |
| Last manual crawl | 2026-05-31 |
| Last auto-crawl | Never (system not yet implemented) |
| Embedding index status | Not yet initialized |
| Oldest entry | 2026-05-31 |

*Statistics updated automatically by `src/knowledge/updater.py` after each crawl.*

---

## Crawler Configuration Reference

```yaml
# ~/.trendscout/knowledge-crawler.yml
sources:
  arxiv:
    queries:
      - "cs.SI social network trend detection emerging signals"
      - "cs.IR information retrieval topic modeling BERTopic"
      - "cs.LG GitHub repository quality prediction"
      - "cs.CY fake engagement detection social media bot"
      - "cs.HC key opinion leader influence technology adoption"
    max_results_per_query: 5
    cadence: weekly

  semantic_scholar:
    topics:
      - "fake star detection GitHub"
      - "emerging technology trend prediction"
      - "KOL influence social media tech"
      - "online topic modeling evolving corpus"
    cadence: weekly

  github_releases:
    repos:
      - MaartenGr/BERTopic            # BERTopic updates
      - explosion/spaCy                # NLP pipeline updates
      - huggingface/transformers       # Embedding model updates
    cadence: weekly

  papers_with_code:
    leaderboards:
      - topic-models
      - social-media-analysis
    cadence: monthly

  blogs:
    sources:
      - "https://paradoxintelligence.com/blog"   # GitHub as investment signal
      - "https://scrapingant.com/blog"           # Web scraping + trend analysis
    cadence: monthly

summarizer:
  provider: deepseek
  model: deepseek-chat
  max_tokens: 300
  prompt: |
    Extract from this paper/article:
    1. Key Insight (1 sentence — specific, technical, actionable)
    2. Direct relevance to ONE of: fake signal detection, topic modeling,
       KOL influence scoring, GitHub analytics, social media NLP, 
       momentum diffusion, or digest synthesis
    3. Tags (comma-separated, lowercase, hyphenated)
    Format as JSON only. If not relevant to tech trend intelligence,
    return {"skip": true}.
```
