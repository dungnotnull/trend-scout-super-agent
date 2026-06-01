# PROJECT-detail.md — TrendScout Full Architecture & Design Specification

> Version: 0.1.0-draft  
> Last Updated: 2026-05-31  
> Status: Pre-development, specification phase

---

## 1. Executive Summary

### Problem Statement

In 2026, GitHub hosts 630 million repositories. 230 new repositories are created every minute. HuggingFace adds dozens of models daily. Product Hunt, Hacker News, and X collectively produce tens of thousands of tech-adjacent signals per day. No human — even a full-time tech researcher — can process this volume and extract genuine breakthroughs before the crowd does.

The current proxies for "important" are broken:
- **GitHub stars** are purchasable at scale. CMU's StarScout identified 6 million fake stars. Services like SocialPlug claim 3.1 million stars delivered to 53,000+ clients. A repo can reach 10K stars in 48 hours through coordinated bot networks.
- **Hacker News front page** is crowded but is one of the few remaining authentic organic signals — if you know how to weight it.
- **X/Twitter trending** is dominated by engagement-bait, VC announcements, and coordinated amplification.
- **Product Hunt** is systematically gamed through mutual-upvoting networks.

**TrendScout** builds a multi-source signal intelligence system that replaces naive metric counting with a composite authenticity-weighted score, powered by ML classifiers trained on historical signals and their eventual adoption outcomes.

### Core Value Proposition

| User Type | Pain Point Solved |
|---|---|
| Senior Engineers | "Which of the 50 libraries that launched this week are worth 2 hours of evaluation?" |
| Engineering Managers | "What should my team learn this quarter to stay ahead?" |
| VC Analysts / Tech Investors | "Which open-source projects are gaining developer mindshare before commercial traction?" |
| Technical Founders | "Where is the ecosystem moving so I can build in front of it?" |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COLLECTOR LAYER                             │
│  GitHub API · HN Algolia · X API v2 · Product Hunt · HuggingFace  │
│  Discord Webhook · RSS (tech blogs) · GitHub Archive (backfill)    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │  RawSignal stream
          ┌────────────▼──────────────┐
          │     Signal Deduplicator    │  (hash-based, cross-source)
          └────────────┬──────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │               SCORING LAYER                  │
    │                                              │
    │  GitHubScorer  (commit velocity, contrib    │
    │                 growth, fork/star ratio)     │
    │  MomentumScorer (cross-source co-spike      │
    │                  within 48h window)          │
    │  KOLScorer     (weighted KOL mentions,      │
    │                 historical accuracy)         │
    │  SentimentScorer (HN comments + X replies)  │
    │  NoveltyScorer  (embedding distance from    │
    │                  recent signal pool)        │
    │                                              │
    │  AuthenticityFilter ← ML classifier        │
    │   (StarScout-inspired fake-star detection)  │
    │                                              │
    │  CompositeScorer → final signal score       │
    └──────────────────┬──────────────────────────┘
                       │
    ┌──────────────────▼──────────────────────────┐
    │              NLP / CLUSTERING LAYER          │
    │                                              │
    │  BERTrend (BERTopic online) → topic clusters│
    │  Signal Classification: NOISE / WEAK / STRONG│
    │  EntityExtractor → project + tech tags       │
    │  CloneDetector → spam/fork-spam filter       │
    └──────────────────┬──────────────────────────┘
                       │
    ┌──────────────────▼──────────────────────────┐
    │             DIGEST SYNTHESIS LAYER           │
    │                                              │
    │  Ranker: top-N signals by composite score   │
    │  LLM Synthesizer: narrative generation      │
    │   (LLM reads structured metrics + writes)   │
    │  Formatter: Telegram MD / Slack Block Kit   │
    └──────────────────┬──────────────────────────┘
                       │
    ┌──────────────────▼──────────────────────────┐
    │            DELIVERY LAYER                    │
    │  Telegram · Slack · Email · Webhook         │
    │  Web archive (digest_archive/)              │
    └─────────────────────────────────────────────┘
```

---

## 3. Collector Layer — Detailed Design

### 3.1 GitHub Collector (`src/collectors/github.py`)

**What we collect (per repository):**
- Current stars, forks, watchers, open issues, contributors count
- Star history: `starred_at` timestamps (last 1,000 stargazers) — for velocity and pattern analysis
- Commit frequency: commits per day over last 30 days (GitHub GraphQL: `defaultBranchRef.target.history`)
- Contributor growth: unique contributor count at 7d / 14d / 30d intervals
- Language breakdown
- README content (for LLM summarization and clone detection)
- Release frequency (major signal of active maintenance)

**Sources within GitHub:**
1. `GET /trending` — scrape daily/weekly trending (HTML; no official API)
2. `GET /search/repositories?sort=stars&q=created:>2026-05-24` — new repos with rapid growth
3. GitHub GraphQL API — detailed per-repo metrics
4. GitHub Archive (`gharchive.org`) — historical event stream for backfill

**Rate limit strategy:**
- GitHub REST: 5,000 req/hour authenticated → never exceed 4,500 (90% buffer)
- GitHub GraphQL: 5,000 points/hour → use for deep dives on shortlisted repos only
- GH Archive: batch S3 downloads — no rate limit (hourly JSON files)

### 3.2 Hacker News Collector (`src/collectors/hackernews.py`)

HN is the most reliable organic signal in the dataset. Research confirms: repositories gain avg 121 stars within 24h and 289 stars within a week of HN front-page exposure (Kraishan 2025).

**What we collect:**
- Front page stories (top 30 + new 100) every 2 hours
- Stories linking to GitHub repos or tech announcements
- Comment threads for front-page tech stories (sentiment signal)
- "Ask HN" threads as weak signals for pain points (useful for "why" context)

**Key HN signals:**
- Points accumulated within 2h of posting (virality proxy)
- Comment velocity (rapid discussion = high interest)
- Comment sentiment — not just volume. A thread with 200 comments criticizing a project is noise. 200 comments asking "how do I use this?" is a strong signal.
- "Second-order HN": when a repo appears on HN, then shows a GitHub star spike within 24h — this co-spike is the MomentumScorer's primary input

**API:** Algolia HN Search API (`hn.algolia.com/api/v1/`) — no auth required, generous rate limits.

### 3.3 X/Twitter Collector (`src/collectors/twitter.py`)

X data is high-signal but high-noise. The key is **not** to process the full public timeline — only targeted KOL feeds and tech search terms.

**Collection modes:**
1. **KOL Timeline Monitoring** — fetch recent posts from accounts in `kol_registry.json` (e.g., @antirez, @gdb, @dan_abramov, @karpathy level of engineers). Limit to verified KOLs (weight > 0.5 in registry).
2. **Keyword Search** — tech-relevant query: `("GitHub" OR "just shipped" OR "open sourced") (from:verified OR min_faves:500) lang:en`
3. **Link extraction** — for every post, extract GitHub/HuggingFace/PH URLs. These become the cross-reference signal.

**API:** X API v2 (Basic tier: 10,000 posts/month read) — very limited. Strategy: batch collection every 3 hours targeting only KOL accounts (~150 accounts × 10 posts = 1,500 requests/day). For search: use only with remaining quota.

**Alternative:** Nitter instances or third-party data providers (Apify X actor) as fallback when API quota exhausted.

### 3.4 Product Hunt Collector (`src/collectors/producthunt.py`)

Product Hunt is heavily gamed but still surfaces genuine launches from known teams. The key is cross-referencing with GitHub activity.

**What we collect:** Daily new products with GitHub repo links. Filter: only include if the linked GitHub repo shows organic activity (not just a launch-day spike).

**API:** Product Hunt GraphQL API (official, requires OAuth token).

### 3.5 HuggingFace Collector (`src/collectors/huggingface.py`)

HuggingFace Hub is the ground truth for new model and paper releases. Less gamed than GitHub. High signal-to-noise.

**What we collect:**
- New models with >50 downloads in first 48h
- New papers (`paperswithcode.com` + HF Papers endpoint)
- Trending model downloads (weekly delta)
- Model card content for LLM summarization

**API:** HuggingFace Hub API (no auth for public data; high rate limits).

---

## 4. Scoring Layer — Detailed Design

### 4.1 GitHub Scorer (`src/scoring/github_scorer.py`)

#### Commit Velocity Score
Not raw commit count — **commit consistency and acceleration:**

```python
def commit_velocity_score(commits_per_day: list[float], window: int = 30) -> float:
    # Exponentially weighted moving average (recent commits count more)
    ewma = pd.Series(commits_per_day).ewm(span=7).mean()
    
    # Acceleration: is commit rate increasing?
    recent = ewma.iloc[-7:].mean()
    baseline = ewma.iloc[-30:-7].mean()
    acceleration = (recent - baseline) / (baseline + 0.01)
    
    # Score: 0-1, higher = healthier commit trajectory
    return sigmoid(acceleration * 2)
```

#### Contributor Growth Score
Single-contributor repos with thousands of stars are a red flag (bot network or solo viral project with no community):

```python
def contributor_growth_score(
    contributors_7d: int,
    contributors_30d: int,
    contributors_total: int,
) -> float:
    # New contributors in last 7d as fraction of total (ecosystem growth)
    new_contrib_rate = contributors_7d / (contributors_total + 1)
    
    # Multi-contributor signal: prefer repos with > 5 contributors
    diversity_bonus = min(contributors_total / 10, 1.0)
    
    return (new_contrib_rate * 0.6 + diversity_bonus * 0.4)
```

#### Fork/Star Ratio
High fork/star ratio = people are actively using and building on the project (not just bookmarking):

```python
HEALTHY_FORK_RATIO_RANGE = (0.05, 0.30)  # 5-30% of stars are forks

def fork_ratio_score(stars: int, forks: int) -> float:
    ratio = forks / (stars + 1)
    # Peak score at ~15% fork ratio; penalize extremes
    return 1.0 - abs(ratio - 0.15) * 2
```

### 4.2 Authenticity Filter (`src/scoring/authenticity_filter.py`)

This is TrendScout's most critical differentiator. Inspired by CMU's StarScout algorithm (identified 6M fake stars with high accuracy via lockstep behavior and low-activity signatures).

#### Detection Signal 1: Lockstep Starring Pattern
Fake star campaigns deliver stars in coordinated bursts. Real organic growth is stochastic.

```python
def detect_lockstep_burst(star_timestamps: list[datetime]) -> float:
    """
    Returns suspicion score 0-1.
    Lockstep pattern: many stars within the same 5-minute window from different accounts.
    """
    # Group stars by 5-minute buckets
    buckets = group_by_time_window(star_timestamps, minutes=5)
    
    # Legitimate viral spikes: max ~50 stars/5min (HN front page effect)
    # Fake campaigns: 200-500 stars/5min in multiple waves
    max_bucket = max(len(b) for b in buckets.values())
    suspicion = sigmoid((max_bucket - 50) / 50)
    return suspicion
```

#### Detection Signal 2: Stargazer Account Quality
```python
def stargazer_quality_score(stargazers: list[GithubUser]) -> float:
    """
    Check median account age, bio presence, other starred repos.
    Ghost accounts (created same day, no bio, only starred this repo) = red flag.
    """
    ghost_ratio = sum(1 for u in stargazers if is_ghost_account(u)) / len(stargazers)
    return 1.0 - ghost_ratio  # Higher = more legitimate
```

#### Detection Signal 3: Cross-Platform Coherence
A repo with 10K stars but zero HN posts, zero X mentions, zero Reddit threads = suspicious.

```python
def cross_platform_coherence(
    github_stars: int,
    hn_mentions: int,
    twitter_mentions: int,
    reddit_mentions: int,
) -> float:
    """
    Real viral repos leave traces across platforms.
    Stars without external traces = likely synthetic.
    """
    external_signal = hn_mentions * 100 + twitter_mentions * 10 + reddit_mentions * 20
    expected_external = github_stars * 0.05  # Rule of thumb: 5% of stars = external mentions
    coherence = min(external_signal / (expected_external + 1), 1.0)
    return coherence
```

**Authenticity Multiplier** (composite):
```
AuthenticityMultiplier = (
    0.40 × (1 - lockstep_suspicion)
  + 0.35 × stargazer_quality
  + 0.25 × cross_platform_coherence
)
```
- ≥ 0.80 → VERIFIED (include in digest)
- 0.60–0.79 → UNVERIFIED (include with caveat)
- < 0.60 → QUARANTINE (excluded from digest, logged with reason)

### 4.3 KOL Scorer (`src/scoring/kol_registry.py`)

KOL influence weights are not static follower counts. They are trained weights based on **historical predictive accuracy**:

- Every time a KOL mentions a project that achieves >1K real stars in the next 90 days, their weight increases
- Every time a KOL promotes a project that later gets exposed as fake/abandoned, their weight decreases
- New KOLs start with weight 0.5 (neutral) and converge over time

The `kol_registry.json` format:

```json
{
  "github_id": "antirez",
  "twitter_handle": "antirez",
  "weight": 0.92,
  "signal_accuracy_90d": 0.78,
  "total_signals": 45,
  "domain_tags": ["databases", "systems", "c"],
  "last_updated": "2026-05-31"
}
```

Initial KOL seed list (~150 accounts) from:
- GitHub "Most Influential" annual reports
- `scripts/seed-kol-registry.py` pulls from curated Twitter/X lists ("Tech Twitter All-Stars", etc.)
- Manual curation by project maintainers

### 4.4 Momentum Scorer (`src/scoring/momentum_scorer.py`)

The strongest signal in the entire system: **cross-source co-spike within 48 hours**. Research (Kraishan 2025) confirms that HN exposure causes immediate GitHub star surges (avg +121 stars in 24h, +289 in 7d).

```python
def momentum_score(
    signal: RawSignal,
    window_hours: int = 48,
) -> float:
    """
    Score how many independent sources co-mentioned this entity in the time window.
    Multiple independent sources = organic viral spread, not manufactured hype.
    """
    sources_in_window = count_independent_sources(signal.entity_url, window_hours)
    # 1 source = 0.0, 2 sources = 0.5, 3+ sources = 0.8+
    return min((sources_in_window - 1) / 2, 1.0)
```

### 4.5 Topic Modeler — BERTrend (`src/nlp/topic_modeler.py`)

BERTrend (arXiv 2411.05930) extends BERTopic with online learning to track **emerging topics over time**, classifying each as:
- **NOISE** — low frequency, no growth, likely spam
- **WEAK SIGNAL** — small but growing topic cluster; monitor
- **STRONG SIGNAL** — rapidly growing topic cluster; include in digest

The popularity metric from BERTrend:
```
popularity(topic, t) = Σ docs_in_topic × update_recency_weight × decay_factor
```

Where `decay_factor = exp(-λ × days_since_last_update)` — topics that stop growing fade out.

**Implementation:**
```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# Online learning via model merging (consecutive time-slice models)
model = BERTopic(
    embedding_model=SentenceTransformer("all-MiniLM-L6-v2"),
    min_topic_size=5,
    calculate_probabilities=True,
)
# Merge daily models to build evolving topic landscape
merged = BERTopic.merge_models([model_day1, model_day2, model_day3])
```

---

## 5. Clone & Spam Detection (`src/nlp/clone_detector.py`)

Two distinct problems:

### 5.1 Fork-Spam Detection
Dozens of repos that are direct forks of a popular project, renamed with marketing language, submitted to trending. Detection:

```python
def is_fork_spam(repo: RepoMetrics) -> bool:
    # Hard rules
    if repo.is_fork and repo.commits_since_fork < 3:
        return True
    if repo.readme_similarity_to_parent > 0.95:  # Near-identical README
        return True
    if repo.stars > repo.parent_stars * 0.3 and repo.age_days < 7:
        return True  # Suspiciously fast catch-up
    return False
```

### 5.2 Template/Marketing Clone Detection
Projects that are essentially boilerplate templates marketed as innovations. Use embedding similarity:

```python
def clone_similarity_score(readme_embedding: np.ndarray) -> float:
    """
    Compare README embedding against a corpus of known boilerplate templates.
    Returns similarity to the most similar known template (0 = unique, 1 = clone).
    """
    return max(cosine_similarity(readme_embedding, template) for template in TEMPLATE_CORPUS)
```

---

## 6. Digest Synthesis — LLM Layer

### 6.1 Strict Input/Output Contract

The LLM receives **structured data** (never raw text to summarize freely):

```python
DIGEST_PROMPT = """
You are a senior staff engineer at a top tech company writing the morning tech intelligence brief.
Write in plain, opinionated prose — not bullet points. Be specific, not vague.

Here is the structured data for one signal. Write the digest entry:

Project: {title}
URL: {url}
Category: {topic_cluster}
Signal Strength: {signal_label}  # WEAK / STRONG

Metrics (DO NOT change any number):
- Stars gained in 48h: {stars_48h}
- Contributor growth (7d): +{contributors_7d_new}
- Commit velocity (7d): {commits_7d} commits
- HN points: {hn_points} (in {hn_comment_count} comments)
- KOL mentions: {kol_count} from accounts with combined weight {kol_total_weight:.2f}

KOL quotes (use at most 1, verbatim, with attribution):
{kol_quotes}

README summary:
{readme_summary_200_words}

Trigger event (if known — e.g., specific HN thread title):
{trigger_event}

Write a digest entry with:
1. what: one crisp technical sentence describing what this is
2. why_now: 1-2 sentences explaining the specific trigger for this growth spike
3. who_cares: one sentence identifying the exact audience

Do not add any markdown headers. Do not add metrics not listed above. Max 80 words total.
"""
```

### 6.2 Morning Digest Format (Telegram)

```
🌅 TrendScout Morning Brief — {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 STRONG SIGNALS ({n} today)

1. ⚡ {title} [{signal_emoji}VERIFIED]
{what}

{why_now}

{who_cares}

📊 +{stars_48h} stars · {contributors_7d_new} new contributors · {hn_points} HN pts
🔗 {github_url} · {hn_thread_url}
💬 "{kol_quote}" — @{kol_handle}

────────────────────────────

2. ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ WEAK SIGNALS (worth watching)

• {weak_signal_1_title}: {one_sentence_summary}
• {weak_signal_2_title}: ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 {quarantine_count} signals quarantined today (fake star patterns detected)
📊 Signals scored: {total_scored} | Passed: {passed} | Digest rate: {digest_rate:.1f}%
```

---

## 7. Technical Stack

| Component | Technology | Rationale |
|---|---|---|
| Language | Python 3.12 | NLP/ML ecosystem; async support |
| Async | asyncio + aiohttp | Concurrent multi-source collection |
| CLI + scheduler | Click + APScheduler | Clean CLI; cron-style scheduling |
| Topic modeling | BERTopic + sentence-transformers | BERTrend pattern for online emerging signal detection |
| ML scoring | scikit-learn (IsolationForest, GradientBoosting) | Fake-star detection, KOL weight model |
| Sentiment | distilBERT (Hugging Face transformers) | Fast, GPU-optional; fine-tuned on tech discourse |
| Storage | SQLite (append-only signals) | Simple, portable, queryable |
| Cache | Redis (optional) / fakeredis (tests) | Deduplication buffer, rate limit tracking |
| GitHub API | PyGithub + httpx | REST + GraphQL access |
| LLM (digest) | Claude claude-sonnet-4-20250514 via API | Best narrative synthesis quality |
| Delivery | python-telegram-bot, slack-sdk | Primary delivery channels |
| Testing | pytest + pytest-recording | Fixture-based, no live APIs in tests |
| Embedding search | hnswlib | Local ANN for clone detection + knowledge brain |

---

## 8. Investment-Grade Signal Architecture

For users who want to use TrendScout as an alternative data source for tech investing (inspired by Paradox Intelligence 2026 research showing GitHub data gives early signals of commercial traction):

### Leading Indicator Framework
1. **Developer mindshare velocity** (star velocity × contributor growth) → precedes commercial adoption by 6-18 months
2. **Ecosystem formation** (forks + downstream dependencies in package registries) → precedes enterprise contracts
3. **KOL migration** (senior engineers at major companies mentioning in professional context) → strongest leading indicator

### Signal Persistence Tracking
Every signal is tracked over 90 days post-detection:
- Did the repo reach 10K+ stars? (mainstream adoption)
- Did it appear in any tech company engineering blog? (enterprise validation)
- Did a major company acquire it or announce adoption? (commercial traction)

This persistence data trains the KOL weight model and the composite scorer — closing the feedback loop.

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| X API quota exhaustion (10K posts/month) | High | Medium | Batch-collect KOL timelines only; Apify X actor as backup |
| GitHub API rate limit (5K req/hour) | High | Medium | Exponential backoff; prioritize shortlisted repos for deep analysis |
| BERTopic cold start (not enough data) | Medium | High | Backfill with GitHub Archive data before first production run |
| KOL list stale or biased | Medium | High | Quarterly review; add accuracy feedback loop |
| Fake star detection false positives (quarantine real project) | Medium | Medium | Include quarantine log in digest footer; user can override |
| LLM generates incorrect metrics | Low | High | LLM receives structured metrics; prompt prohibits invention; output parsed and validated against input |
| Discord API changes (webhooks broken) | Low | Low | Discord is optional; Telegram + Slack are primary |
| Dataset poisoning (coordinated campaigns to game our scorer) | Low | High | Ensemble of independent signals; cross-platform coherence requirement makes gaming expensive |
