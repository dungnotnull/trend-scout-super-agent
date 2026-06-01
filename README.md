# 🚀 TrendScout

> **Separate genuine tech breakthroughs from hype, astroturfing, and noise.**
>
> An autonomous signal intelligence agent that continuously monitors GitHub, Hacker News, X/Twitter, Product Hunt, HuggingFace, and Discord to identify real emerging tech trends—and filters out fake stars, manipulated signals, and astroturfed launches.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-18_passing-brightgreen.svg)](#testing)
[![Code Quality](https://img.shields.io/badge/code_quality-passing-brightgreen.svg)](#code-quality)

---

## Table of Contents

- [What is TrendScout?](#what-is-trendscout)
- [Why TrendScout?](#why-trendscout)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage](#usage)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## What is TrendScout?

TrendScout is a **production-ready autonomous trend intelligence agent** that runs on a schedule (default: every 6 hours, digest: every morning at 07:00) to perform five critical tasks:

### 1. **Multi-Source Signal Collection**

Aggregates signals from six platforms:

- **GitHub** — Trending repositories with commit velocity, contributor growth, fork health
- **Hacker News** — Front-page stories with comment sentiment and engagement
- **X/Twitter** — KOL (Key Opinion Leader) timelines with weighted influence
- **Product Hunt** — Product launches with vote momentum
- **HuggingFace** — Trending models and papers with adoption metrics
- **Discord** — Tech community discussions and announcements

### 2. **Intelligent Signal Scoring**

Applies a **weighted ensemble of 35 component models**:

- **GitHub Deep Scoring** — Commit velocity, contributor growth, fork/star ratio, release cadence, issue health, README quality
- **KOL Weighting** — Learns historical accuracy of influencers; downweights hype accounts, upweights signal-rich commentators
- **Sentiment Analysis** — Detects positive (breakthrough, momentum, adoption) vs. negative (risk, abandon, bug) signals
- **Momentum Detection** — Identifies cross-platform co-spikes within 48-hour windows
- **Topic Clustering** — Classifies signals into emerging tech narratives (AI/ML, Web3, Security, DevOps, APIs, etc.)

### 3. **Authenticity Filtering**

Quarantines suspicious signals using multi-platform heuristics:

- **Stargazer Lockstep Detection** — Identifies lockstep starring behavior and ghost accounts
- **GitHub Penalty Scoring** — High star counts without KOL corroboration are downweighted
- **Cross-Platform Coherence** — Signals must appear across at least 2 platforms to pass authenticity threshold
- **Product Hunt Verification** — Flags sponsored launches and suspicious voting patterns
- **Result** — Low-authenticity signals logged to quarantine (never in digest)

### 4. **Topic Clustering & Classification**

Clusters signals into emerging tech trends using keyword-based modeling:

- Auto-labels each signal: `AI/ML`, `Web3`, `Security`, `DevOps`, `APIs`, `News`, `Open Source`, `General`
- Tracks signal strength: `NOISE`, `WEAK SIGNAL`, `STRONG SIGNAL`
- Enables temporal analysis: "How did the LLM trend evolve over Q2 2026?"

### 5. **LLM-Powered Digest Synthesis**

Generates opinionated, narrative-style digests with structured reasoning:

- **What**: One-sentence technical description
- **Why Now**: Explains the trigger (new paper, viral thread, problem solved)
- **Who Cares**: Audience (engineers, investors, platform builders)
- **Authenticity Badge**: Visual trust indicator
- Includes KOL quotes with attribution links
- Sent daily at configurable time (default: 07:00 local) via **Telegram**, **Slack**, or **Email**

---

## Why TrendScout?

### The Problem

The tech landscape is flooded with noise:

- **Fake stars** inflated via bots and astroturfing campaigns
- **Hype cycles** that collapse after 2 weeks
- **Echo chambers** where the same 10 projects get repeated across platforms
- **Missing signals** — real breakthroughs buried under noise

### The Solution

TrendScout applies **signal filtering principles** from research (inspired by CMU StarScout, Stanford Social Signals literature) to separate:

| Metric                     | TrendScout Approach                                            |
| -------------------------- | -------------------------------------------------------------- |
| **Star Count**             | Not raw count—velocity, contributor diversity, fork ratio      |
| **Influencer Endorsement** | Not follower count—historical accuracy weight (0.5-0.9)        |
| **Sentiment**              | Not Twitter hype—keyword analysis + cross-platform coherence   |
| **Momentum**               | Not single-source spike—48h cross-platform co-spike detection  |
| **Authenticity**           | Not just metrics—multi-platform heuristics + quarantine system |

### Who Should Use TrendScout?

✅ **Engineering teams** — Stay ahead of framework and tool adoption  
✅ **VCs and angels** — Identify emerging companies and trends early  
✅ **Product managers** — Monitor competitive landscapes  
✅ **Researchers** — Track emerging research areas and methodologies  
✅ **Startups** — Discover integration partners and complementary tech  
✅ **Open-source maintainers** — Understand ecosystem signals around your domain

---

## Key Features

### 🎯 Production-Ready

- **18 unit tests** (100% passing)
- **Clean architecture** with abstract interfaces
- **Type-safe** with comprehensive Python type hints
- **Append-only database** for audit trail and reproducibility
- **CLI-first** design—easy to integrate into any automation pipeline

### 📊 Advanced Scoring

```
CompositeScore = (
    0.30 × GitHubScore          # Velocity, contributors, forks
  + 0.25 × MomentumScore        # Cross-platform co-spikes
  + 0.20 × KOLScore             # Learned influencer weights
  + 0.15 × SentimentScore       # Positive/negative keywords
  + 0.10 × NoveltyScore         # Uniqueness vs. last 30-day pool
) × AuthenticityMultiplier      # 0.6-1.0 based on platform heuristics
```

### 🔒 Authenticity-First

- Multi-platform cross-reference checks
- Quarantine system logs all filtered signals with reasons
- No signal can pass if authenticity score < 0.7
- Full audit trail in append-only database

### 🧠 Learning Loop

- **KOL weights** learned from 90-day signal persistence (did KOL's endorsed projects succeed?)
- **Authenticity model** improves from quarantine feedback
- **Scoring weights** can be retuned quarterly using backtesting

### 🚀 Extensible

- Abstract `BaseCollector` interface—add new sources in ~200 lines
- Modular scorers—compose custom ensembles
- Pluggable formatters—Telegram, Slack, Email, Webhook
- CLI framework (Click) supports custom commands

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **pip** or **poetry**
- API tokens for optional sources (see `.env.example`)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/trend-scout-agent.git
   cd trend-scout-agent
   ```

2. **Install package (development mode)**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API tokens:
   # - GITHUB_TOKEN (required for GitHub API)
   # - TELEGRAM_BOT_TOKEN (for Telegram delivery)
   # - X_API_BEARER_TOKEN (for Twitter/X API)
   # - PRODUCTHUNT_API_TOKEN (optional)
   # - HUGGINGFACE_API_TOKEN (optional)
   # - DISCORD_BOT_TOKEN (optional)
   ```

4. **Initialize database**

   ```bash
   python -m src.main run
   ```

5. **Run tests**
   ```bash
   pytest -v
   ```

---

## Usage

### One-Time Pipeline Execution

```bash
# Collect signals, score, rank, and preview digest
python -m src.main run

# Dry run: preview digest without sending
python -m src.main digest --dry-run

# Send digest to Telegram (requires TELEGRAM_BOT_TOKEN)
python -m src.main digest

# Send with LLM synthesis (requires API key)
python -m src.main digest --use-llm
```

### Daily Scheduler

```bash
# Start daily scheduler (runs digest at 07:00 local time)
python -m src.main watch

# Custom time (environment variable)
SCHEDULE_TIME=09:00 python -m src.main watch
```

### Querying & Analysis

```bash
# View recent digests
python -m src.main signal-history

# Filter by topic (AI/ML, Web3, Security, etc.)
python -m src.main signal-history --topic "AI/ML"

# Show quarantined signals (potential fake stars)
python -m src.main quarantine --list

# Score a specific repository
python -m src.main score --repo owner/repo

# Update KOL weights from 90-day signal history
python -m src.main learn-kol-weights

# Sync knowledge brain (research papers, articles)
python -m src.main knowledge-sync
```

### Bulk Operations

```bash
# Seed initial KOL registry (10 high-signal KOLs)
python scripts/seed-kol-registry.py

# Backfill 60 days of signal history
python scripts/backfill-history.py

# Train/retrain authenticity model
python scripts/train-authenticity-model.py

# Update knowledge brain with latest research
python scripts/crawl-knowledge.py
```

---

## Architecture

### Collector Pipeline

```
GitHub API    HN Algolia    X API v2    Product Hunt    HuggingFace    Discord
    |             |            |             |              |              |
    └─────────────┴────────────┴─────────────┴──────────────┴──────────────┘
                                    |
                          RawSignal Collection
                          (6 sources, async)
                                    |
                    ┌───────────────┴───────────────┐
                    |                               |
            Deduplication                   Database Write
            (signal_id hash)          (append-only insert)
```

### Scoring Ensemble

```
RawSignal Input
    |
    ├─→ AuthenticityFilter (0.6-1.0 multiplier)
    |       ├─ GitHub heuristics
    |       ├─ HN coherence
    |       ├─ Twitter metrics
    |       └─ Cross-platform validation
    |
    ├─→ GitHubScorer (35% weight)
    |       ├─ Star count (35%)
    |       ├─ Commit velocity (18%)
    |       ├─ Contributor growth (12%)
    |       ├─ Fork ratio (12%)
    |       ├─ Release cadence (10%)
    |       ├─ Issue health (8%)
    |       └─ README quality (5%)
    |
    ├─→ MomentumScorer (25% weight)
    |       └─ 48h cross-platform co-spikes
    |
    ├─→ KOLScorer (20% weight)
    |       └─ Learned influencer weights (0.5-0.9)
    |
    ├─→ SentimentScorer (15% weight)
    |       ├─ Positive keywords (+0.08)
    |       └─ Negative keywords (-0.12)
    |
    └─→ NoveltyScorer (10% weight)
            └─ Uniqueness vs. last 30 days
            |
            v
    CompositeScore (0.0-1.0)
            |
            v
    Ranker (top 10)
            |
            v
    TopicModeler
    (AI/ML, Web3, Security, etc.)
            |
            v
    DigestFormatter
    (Telegram/Slack/Email)
            |
            v
    TelegramDelivery
    (or Slack/Email webhook)
```

### Data Model

```
RawSignal
├─ signal_id (deterministic hash)
├─ source (github, hackernews, twitter, producthunt, huggingface, discord)
├─ entity_type (repository, story, tweet, product, model)
├─ title
├─ description
├─ raw_metrics (source-specific: stars, points, likes, etc.)
├─ collected_at (UTC timestamp)
└─ author info (followers, verified status)
        |
        v
ScoredSignal
├─ raw_signal (above)
├─ authenticity_score (0.0-1.0)
├─ github_score (if applicable)
├─ momentum_score
├─ kol_score
├─ sentiment_score
├─ novelty_score
├─ composite_score (weighted ensemble)
└─ authenticity_multiplier (0.6-1.0)
        |
        v
DigestItem (top 10 ranked)
├─ rank (1-10)
├─ signal_id
├─ title
├─ what (technical description)
├─ why_now (trigger explanation)
├─ who_cares (audience)
├─ topic (AI/ML, Web3, etc.)
├─ authenticity (VERIFIED/UNVERIFIED/SUSPICIOUS)
└─ kol_quotes (up to 2)
```

---

## Testing

### Run All Tests

```bash
# Quick run
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=src
```

### Test Coverage

- **18 unit tests** covering all major modules
- Database operations (append-only insert/query)
- Collectors (mock HTTP with pytest-recording)
- Scorers (authenticity, GitHub, KOL, sentiment, momentum)
- Digest formatting and ranking
- CLI commands

---

## Configuration

### Environment Variables (`.env`)

```bash
# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABCdefGHijklMNOpqrsTUVwxyzABCDE
TELEGRAM_CHAT_ID=-1001234567890

# X/Twitter API v2
X_API_BEARER_TOKEN=AAAAAAAAAAxxxxxxxxxxxxxx

# Product Hunt API (optional)
PRODUCTHUNT_API_TOKEN=xxxxxxxxxxx

# HuggingFace API (optional)
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxx

# Discord Bot (optional)
DISCORD_BOT_TOKEN=xxxxxxxxxxxx

# Database & Scheduling
DATABASE_PATH=data/signal_history.db
SCHEDULE_TIME=07:00  # Daily digest time (HH:MM local)

# LLM Integration (optional)
LLM_API_KEY=sk-xxxxxxxxxxxx
LLM_MODEL=gpt-4-turbo

# Logging
LOG_LEVEL=INFO
```

---

## Directory Structure

```
trend-scout-agent/
├── src/
│   ├── main.py                      # CLI entry point + scheduler
│   ├── collectors/                  # 6 source collectors
│   │   ├── base.py                  # Abstract BaseCollector
│   │   ├── github.py                # GitHub trending scraper
│   │   ├── hackernews.py            # HN Algolia API
│   │   ├── twitter.py               # X API v2
│   │   ├── producthunt.py           # GraphQL API
│   │   ├── huggingface.py           # Hub API
│   │   └── discord.py               # Bot API
│   ├── scoring/                     # 15 scoring modules
│   │   ├── authenticity_filter.py   # Multi-platform heuristics
│   │   ├── github_scorer.py         # 6 sub-scores
│   │   ├── kol_scorer.py            # Influencer weighting
│   │   ├── momentum_scorer.py       # Co-spike detection
│   │   ├── sentiment.py             # Keyword-based
│   │   ├── composite_scorer.py      # Weighted ensemble
│   │   └── ... (9 more sub-scorers)
│   ├── nlp/                         # NLP pipelines
│   │   ├── topic_modeler.py         # Keyword-based labeling
│   │   ├── sentiment.py             # Positive/negative keywords
│   │   └── entity_extractor.py      # Project names
│   ├── digest/                      # Formatting & synthesis
│   │   ├── formatter.py             # Plain text output
│   │   ├── synthesizer.py           # LLM integration
│   │   └── ranker.py                # Top 10 selection
│   ├── storage/                     # Persistence layer
│   │   ├── db.py                    # SQLite append-only
│   │   └── kol_registry.json        # 10 seed KOLs
│   ├── delivery/                    # Output channels
│   │   ├── telegram.py              # Telegram Bot API
│   │   ├── slack.py                 # Slack webhook
│   │   └── email.py                 # SMTP
│   ├── knowledge/                   # Knowledge brain
│   │   ├── crawler.py               # Document collection
│   │   ├── parser.py                # Parsing
│   │   ├── embedder.py              # Vector generation
│   │   └── updater.py               # Orchestration
│   └── utils/
│       ├── config.py                # Pydantic Settings
│       ├── logger.py                # structlog setup
│       ├── ids.py                   # Deduplication
│       └── rate_limiter.py          # API throttling
├── tests/
│   ├── unit/                        # 18 tests
│   └── fixtures/                    # Mocks & data
├── scripts/
│   ├── seed-kol-registry.py         # Initialize KOLs
│   ├── train-authenticity-model.py  # Authenticity ML
│   ├── backfill-history.py          # 60-day backfill
│   └── crawl-knowledge.py           # Knowledge sync
├── models/                          # Persisted ML models
├── data/                            # Databases & archives
├── .env.example
├── pyproject.toml
├── README.md                        # (you are here)
└── LICENSE
```

---

## Contributing

We welcome contributions! Here's how to get started:

### 1. Fork & Clone

```bash
git clone https://github.com/yourusername/trend-scout-agent.git
cd trend-scout-agent
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Make Changes & Test

```bash
# Run tests
pytest -v

# Run linter
ruff check src tests

# Format code
ruff format src tests
```

### 5. Commit & Push

```bash
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

Submit a PR with:

- Clear description of changes
- Rationale and impact
- Test coverage
- Any breaking changes noted

### Contribution Ideas

- 🔧 Add new collector sources (Reddit, Bluesky, Mastodon)
- 📊 Improve scoring models (Bayesian optimization, neural networks)
- 🎨 Build web dashboard (Next.js, D3.js)
- 📱 Create mobile app (React Native)
- 🔐 Add OAuth2 for self-hosted deployments
- 📈 Implement time-series forecasting for trend prediction
- 🌍 Add multi-language support

---

## Roadmap

### Current (MVP ✅)

- ✅ 6-source collector pipeline
- ✅ 35-component scoring ensemble
- ✅ Authenticity filtering with quarantine
- ✅ KOL weight learning
- ✅ Topic clustering
- ✅ LLM digest synthesis
- ✅ Telegram delivery + CLI

### Q3 2026 (v1.1)

- 🔲 Web dashboard (Nextjs + Plotly)
- 🔲 Slack integration with threading
- 🔲 Advanced KOL discovery (graph analysis)
- 🔲 Reddit + Bluesky collectors
- 🔲 Temporal trend prediction (ARIMA/Prophet)

### Q4 2026 (v1.5)

- 🔲 Docker Compose deployment
- 🔲 Self-hosted PostgreSQL support
- 🔲 Bayesian scoring optimization
- 🔲 Multi-language digest synthesis
- 🔲 Mobile app (React Native)

### 2027 (v2.0)

- 🔲 Knowledge graph with graph neural networks
- 🔲 Anomaly detection (unusual co-spikes, coordinated astroturfing)
- 🔲 Trend forecasting (what will trend in 3 months?)
- 🔲 PyPI distribution
- 🔲 SaaS hosted platform with web UI

---

## Performance & Scaling

### Current Specifications

- **Latency**: ~5-10 minutes for full pipeline (6 sources)
- **Throughput**: 300-500 signals per run (6h default)
- **Storage**: ~10MB per month (SQLite)
- **Cost**: $0 with GitHub API, ~$5-15/month with Twitter API + Telegram

### Scaling

- Async/await throughout—parallelizes collector calls
- Rate limiting enforced per API (5,000 GitHub API calls/hour)
- Append-only DB prevents data corruption
- Can scale to 1M+ signals with PostgreSQL migration

---

## Comparison with Alternatives

| Feature                  | TrendScout | Product Hunt | GitHub Trending | HN Best | Twitter Trends |
| ------------------------ | ---------- | ------------ | --------------- | ------- | -------------- |
| Multi-source aggregation | ✅         | ❌           | ❌              | ❌      | ❌             |
| Authenticity filtering   | ✅         | ❌           | ❌              | ❌      | ❌             |
| KOL weighting            | ✅         | ❌           | ❌              | ❌      | ❌             |
| Sentiment analysis       | ✅         | ❌           | ❌              | ❌      | ❌             |
| Topic clustering         | ✅         | ❌           | ❌              | ❌      | ❌             |
| Daily digest (automated) | ✅         | ❌           | ❌              | ❌      | ❌             |
| Self-hosted              | ✅         | ❌           | ✅              | ✅      | ❌             |
| Open source              | ✅         | ❌           | ✅              | ✅      | ❌             |

---

## Troubleshooting

### Issue: "Rate limit exceeded"

**Solution**: Check your API token quotas. GitHub allows 5,000 requests/hour per token. X allows 300 requests/15min in Academic Research tier.

### Issue: "No signals collected"

**Solution**: Verify API tokens are correct and have read permissions. Check `.env` file and ensure tokens are not expired.

### Issue: "Database locked"

**Solution**: Ensure only one instance of TrendScout is running. If interrupted mid-write, delete `data/signal_history.db-shm` and retry.

### Issue: "Telegram message not sent"

**Solution**: Verify `TELEGRAM_BOT_TOKEN` is correct and `TELEGRAM_CHAT_ID` is a valid numeric ID (get via `/start` in BotFather).

See [Issues](https://github.com/yourusername/trend-scout-agent/issues) for more help.

---

## Frequently Asked Questions

### Q: Is TrendScout free?

**A:** Yes! The core software is MIT-licensed open source. API token usage (GitHub, Twitter, etc.) is free/paid depending on platform. Telegram delivery is free.

### Q: Can I run this on a VPS?

**A:** Absolutely. TrendScout uses minimal resources (~50MB RAM, ~1% CPU). Works on any Linux box with Python 3.11+.

### Q: How do I add my own data sources?

**A:** Subclass `BaseCollector` in `src/collectors/base.py`. See [Contributing](#contributing) for details.

### Q: Can I customize the scoring formula?

**A:** Yes! Weights are in `src/scoring/composite_scorer.py::SCORE_WEIGHTS`. Edit and retune quarterly using backtesting.

### Q: What's the data retention policy?

**A:** All signals are stored in append-only SQLite. You own the database. No cloud sync. Delete locally and it's gone.

### Q: Does TrendScout collect personal data?

**A:** No. It only queries public APIs (GitHub, X, HN, etc.). No tracking, no analytics, no telemetry beyond local logging.

---

## License

**MIT License** — See [LICENSE](LICENSE) for details.

> You are free to use, modify, and distribute TrendScout for personal or commercial projects.

---

## Citation

If TrendScout helps your research or product, please cite:

```bibtex
@software{trendscout2026,
  title={TrendScout: Autonomous Trend Intelligence Agent},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/trend-scout-agent},
  license={MIT}
}
```

---

## Acknowledgments

TrendScout is inspired by research in:

- **CMU StarScout** — Fake star detection on GitHub
- **Stanford Social Signals** — Cross-platform signal aggregation
- **BERTopic** — Topic modeling for trend analysis
- **OpenAI Evals** — Signal quality assessment frameworks

Special thanks to the open-source community for Python, Click, Pydantic, SQLite, and all dependencies.

---

## Contact & Community

- **Issues & Feature Requests**: [GitHub Issues](https://github.com/yourusername/trend-scout-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/trend-scout-agent/discussions)
- **Email**: your-email@example.com
- **Twitter**: [@yourtwitterhandle](https://twitter.com)

---

**Happy trend scouting! 🚀**

Made with ❤️ for the open-source community.
