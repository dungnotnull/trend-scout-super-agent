# CLAUDE.md — Agent Operating Manual for trend-scout-agent

> This file is the **primary instruction set** for any AI agent (Claude Code, Cursor, or equivalent) working on this project. Read this file fully before taking any action in this repository.

---

## Project Identity

**Project Name:** TrendScout  
**Tagline:** An autonomous alpha-signal intelligence agent that separates genuine tech breakthroughs from noise, hype, and astroturfed repos  
**Language:** Python (primary), TypeScript (optional dashboard)  
**License:** MIT  
**Data Sources:** GitHub API, X/Twitter API, Hacker News (Algolia API), Product Hunt, Discord (webhooks/bot), HuggingFace Hub  
**Architecture:** Multi-source collector → Signal scorer (ML/NLP) → Fake signal filter → Topic clustering (BERTrend) → LLM digest synthesizer → Push delivery

---

## What This Project Is

TrendScout runs on a schedule (default: every 6 hours, digest: every morning 07:00 local) and performs five things:

1. **Multi-source crawling** — GitHub Trending, HN front page + comments, X tech KOL timelines, Product Hunt launches, Discord tech servers (via webhook listener), HuggingFace new models/papers.
2. **Deep signal scoring** — Not raw star count. Commit velocity, contributor growth rate, fork/star ratio, code churn quality, Hacker News comment sentiment, X KOL engagement weight. Backed by ML models.
3. **Fake signal filtering** — CMU StarScout-inspired detection of lockstep starring behavior, ghost account patterns, astroturfed Product Hunt launches. Repos that fail the authenticity filter are quarantined.
4. **Topic clustering** — BERTrend (BERTopic in online learning mode) clusters signals into emerging narratives. Each cluster gets a "signal strength" label: NOISE / WEAK SIGNAL / STRONG SIGNAL.
5. **LLM digest synthesis** — A concise, opinionated morning digest written by an LLM in the voice of a senior engineer, explaining *why* each trend matters and what problem it solves — not just that it exists.

---

## Core Principles for the Agent

### 1. Signal Quality Over Volume
The output is deliberately small. The morning digest covers **5–10 items maximum**. More items = noise. Never pad the digest to seem comprehensive. If the scoring engine finds no genuine signals in a 24h period, the digest says so ("Quiet day — no new breakthroughs detected.").

### 2. Authenticity Is Non-Negotiable
Any signal that cannot pass the fake-star / astroturfing filter goes to a separate `quarantine/` log with a reason. It must **never** appear in the main digest. The rule: if in doubt, quarantine.

### 3. Explain the "Why" — Always
Every digest item must answer three questions in 2–4 sentences:
- What is this? (one technical sentence)
- Why is growth accelerating NOW? (the trigger — a new paper, a viral HN thread, a pain-point solved)
- Who should care? (engineers, investors, or both?)

A digest item that only says "X grew 200% stars" without explaining the trigger is a failed output. Rewrite until the "why" is explicit.

### 4. KOL Weighting Is Not Follower-Count
KOL (Key Opinion Leader) influence in TrendScout is not Twitter follower count. It is a learned weight based on historical signal-to-noise accuracy: KOLs who have discussed projects that later achieved mainstream adoption get higher weights. KOLs known for hype (NFT promoters, VC tweet-storms) get downweighted. The `kol_registry.json` is the source of truth.

### 5. No Raw LLM Hallucination in Signal Data
The LLM is used only for two tasks: (a) writing the final digest text, and (b) generating short project summaries from README content. It does **never** infer metrics (star counts, commit frequency, contributor counts). All numeric claims in the digest come from the raw data pipeline, not the LLM. The LLM receives pre-computed metrics as structured input.

### 6. Append-Only Signal History
`data/signal_history.db` is append-only. Never delete or update historical signal records. The ML scoring model is trained on this history — corrupted history = corrupted model.

---

## Directory Structure

```
trend-scout-agent/
├── CLAUDE.md
├── PROJECT-detail.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── SECOND-KNOWLEDGE-BRAIN.md
│
├── src/
│   ├── main.py                       # CLI entry point (Click) + scheduler
│   ├── collectors/
│   │   ├── base.py                   # Abstract Collector interface
│   │   ├── github.py                 # GitHub REST + GraphQL API
│   │   ├── hackernews.py             # Algolia HN Search API + scraper
│   │   ├── twitter.py                # X API v2 (KOL timeline + search)
│   │   ├── producthunt.py            # Product Hunt GraphQL API
│   │   ├── huggingface.py            # HuggingFace Hub API (models + papers)
│   │   └── discord.py                # Discord webhook listener + bot
│   │
│   ├── scoring/
│   │   ├── github_scorer.py          # Commit velocity, contributor growth, fork ratio
│   │   ├── social_scorer.py          # KOL weight × engagement, HN comment sentiment
│   │   ├── momentum_scorer.py        # Cross-source momentum (stars + HN + X co-spike)
│   │   ├── authenticity_filter.py    # Fake star / astroturfing detection
│   │   ├── composite_scorer.py       # Weighted ensemble of all scorers
│   │   └── kol_registry.py           # KOL list + learned influence weights
│   │
│   ├── nlp/
│   │   ├── topic_modeler.py          # BERTrend online topic modeling
│   │   ├── sentiment.py              # HN/X comment sentiment (distilBERT fine-tuned)
│   │   ├── entity_extractor.py       # Extract project names, technologies, frameworks
│   │   └── clone_detector.py         # Detect fork-spam / template-clones
│   │
│   ├── digest/
│   │   ├── synthesizer.py            # LLM digest writer (structured input → narrative)
│   │   ├── ranker.py                 # Final ranking of signals for digest
│   │   ├── formatter.py              # Telegram Markdown / Slack Block Kit formatting
│   │   └── templates/
│   │       ├── telegram.md.jinja
│   │       └── slack.json.jinja
│   │
│   ├── delivery/
│   │   ├── dispatcher.py
│   │   ├── telegram.py
│   │   ├── slack.py
│   │   ├── email.py
│   │   └── webhook.py
│   │
│   ├── storage/
│   │   ├── db.py                     # SQLite append-only signal store
│   │   ├── cache.py                  # Redis-compatible in-memory cache (fakeredis in tests)
│   │   └── kol_registry.json         # Curated KOL list with learned weights
│   │
│   └── knowledge/
│       ├── crawler.py
│       ├── parser.py
│       ├── embedder.py
│       └── updater.py
│
├── models/
│   ├── authenticity_classifier/      # Trained fake-star detector model
│   ├── kol_weight_model/             # KOL influence weight model
│   └── bertopic_state/               # Persisted BERTrend model state
│
├── data/
│   ├── signal_history.db             # Append-only SQLite
│   ├── quarantine.db                 # Signals that failed authenticity check
│   └── digest_archive/               # Past digests (JSON + rendered text)
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── scripts/
    ├── seed-kol-registry.py          # Bootstrap KOL list from tech Twitter lists
    ├── train-authenticity-model.py   # (Re)train the fake-star classifier
    ├── backfill-history.py           # Seed signal history from GitHub Archive
    └── crawl-knowledge.py            # Manual knowledge brain update
```

---

## Key Commands

```bash
# Setup
pip install -e ".[dev]"
cp .env.example .env

# Core operations
python -m src.main run              # One-time full pipeline run
python -m src.main watch            # Continuous mode (every 6h)
python -m src.main digest --send    # Generate and send morning digest now
python -m src.main digest --dry-run # Preview digest without sending

# Analysis
python -m src.main score --repo owner/repo    # Score a specific repo
python -m src.main signal-history --topic MCP # Historical signal chart for a topic
python -m src.main quarantine --list          # Show quarantined signals

# Model operations
python scripts/train-authenticity-model.py    # Retrain fake-star classifier
python scripts/seed-kol-registry.py          # Refresh KOL list

# Knowledge brain
python scripts/crawl-knowledge.py
```

---

## Collector Interface Contract

```python
class BaseCollector(ABC):
    source: str  # "github", "hackernews", "twitter", etc.
    
    async def collect(self, since: datetime) -> list[RawSignal]:
        """Collect raw signals since the given timestamp. Returns deduplicated list."""
    
    async def health_check(self) -> bool:
        """Returns True if source API is reachable and not rate-limited."""
    
    @property
    def rate_limit_remaining(self) -> int:
        """Current API rate limit remaining for this source."""
```

**RawSignal** is the universal schema — all collectors produce this:

```python
@dataclass
class RawSignal:
    signal_id: str          # Deterministic hash of source+entity_id+timestamp
    source: str             # "github", "hackernews", "twitter", "producthunt", "huggingface"
    entity_type: str        # "repository", "post", "tweet", "product", "model"
    entity_id: str          # Platform-native ID
    entity_url: str
    title: str
    description: str | None
    raw_metrics: dict       # Source-specific: {"stars": 1200, "forks": 89, ...}
    collected_at: datetime  # UTC
    author_id: str | None
    author_followers: int | None
```

---

## Scoring Model Rules

The composite score for each signal is a weighted sum:

```
CompositeScore = (
    0.30 × GithubScore       # Commit velocity, contributor growth, fork ratio
  + 0.25 × MomentumScore     # Cross-source co-spike (HN + GitHub + X within 48h)
  + 0.20 × KOLScore          # Weighted KOL mentions (by historical accuracy weight)
  + 0.15 × SentimentScore    # HN + X comment sentiment (NLP)
  + 0.10 × NoveltyScore      # How different is this from the last 30-day signal pool?
) × AuthenticityMultiplier   # 0.0 if quarantined, 0.5-1.0 based on authenticity score
```

Weights stored in `src/scoring/composite_scorer.py::SCORE_WEIGHTS`. Re-tune quarterly using backtesting.

---

## Digest Format Contract

Each digest item must contain exactly:

```python
@dataclass
class DigestItem:
    rank: int                    # 1 = most important
    signal_id: str               # Links back to signal_history.db
    title: str                   # "Library X: [one-line description]"
    composite_score: float       # For transparency
    what: str                    # ≤ 1 sentence technical description
    why_now: str                 # ≤ 2 sentences explaining the trigger
    who_cares: str               # "Engineers using Y" or "VCs tracking Z space"
    key_metrics: dict            # {"stars_48h": 2400, "contributors_7d": +12, ...}
    source_urls: list[str]       # Primary sources (HN thread, X posts, repo)
    kol_quotes: list[str]        # ≤ 2 actual quotes from high-weight KOLs
    authenticity: str            # "VERIFIED" | "UNVERIFIED" | "SUSPICIOUS"
```

---

## Forbidden Actions

- **Never** include a signal in the digest that has `AuthenticityMultiplier < 0.7`
- **Never** allow the LLM to generate or modify metric values (stars, commits, growth rates)
- **Never** delete from `signal_history.db` or `quarantine.db`
- **Never** send a digest with > 10 items (enforce via `ranker.py`)
- **Never** include a KOL quote without linking to the original post URL
- **Never** hardcode API tokens — use `.env` / OS keychain
- **Never** make more than 5,000 GitHub API calls per hour (enforced by `rate_limiter.py`)

---

## When in Doubt

1. Check `PROJECT-detail.md` for design decisions
2. Check `SECOND-KNOWLEDGE-BRAIN.md` for research on signal detection methods
3. If a signal looks impressive but the authenticity score is borderline: **quarantine it**
4. If the digest is empty today: that is a valid, correct output — send "No breakthrough signals detected today."
