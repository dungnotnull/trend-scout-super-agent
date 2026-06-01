import asyncio
import time
from datetime import datetime, timedelta

import click

from src.collectors.discord import DiscordCollector
from src.collectors.github import GitHubCollector
from src.collectors.huggingface import HuggingFaceCollector
from src.collectors.hackernews import HackerNewsCollector
from src.collectors.producthunt import ProductHuntCollector
from src.collectors.twitter import TwitterCollector
from src.digest.formatter import format_digest
from src.digest.ranker import rank_signals
from src.digest.synthesizer import DigestSynthesizer
from src.delivery.telegram import send_telegram_message
from src.models import DigestItem
from src.nlp.sentiment import estimate_sentiment
from src.nlp.topic_modeler import TopicModeler
from src.knowledge.updater import KnowledgeUpdater
from src.scoring.authenticity_filter import compute_authenticity_score
from src.scoring.basic_scorer import score_raw_signal
from src.scoring.composite_scorer import compute_composite_score
from src.scoring.github_scorer import compute_github_score
from src.scoring.hn_scorer import compute_hackernews_score
from src.scoring.kol_scorer import compute_kol_score, extract_kol_quotes
from src.scoring.kol_weight_learner import learn_kol_weights
from src.scoring.momentum_scorer import compute_momentum_score
from src.storage.db import Database
from src.utils.config import Settings
from src.utils.logger import configure_logging


def summarize_why_now(raw_signal: object) -> str:
    source = getattr(raw_signal, "source", "unknown")
    return f"This signal surfaced from {source} in the last 24 hours."


def summarize_who_cares(raw_signal: object) -> str:
    if getattr(raw_signal, "source", "") == "hackernews":
        return "Engineers watching early launch momentum."
    return "Engineers and investors monitoring emerging GitHub projects."


async def collect_signals(since: datetime) -> list:
    collectors = [
        GitHubCollector(),
        HackerNewsCollector(),
        TwitterCollector(),
        ProductHuntCollector(),
        HuggingFaceCollector(),
        DiscordCollector(),
    ]
    signals = []

    for collector in collectors:
        try:
            collected = await collector.collect(since)
            signals.extend(collected)
        except Exception as exc:
            click.echo(f"Warning: collector {collector.source} failed: {exc}")

    return signals


def build_digest_items(scored_signals: list, generated_at: datetime) -> list[DigestItem]:
    items: list[DigestItem] = []
    for rank, scored in enumerate(scored_signals, start=1):
        raw = scored.raw_signal
        key_metrics = getattr(raw, "raw_metrics", {})
        urls = [getattr(raw, "entity_url", "")]
        if raw.source == "hackernews" and raw.raw_metrics.get("hn_url"):
            urls.append(raw.raw_metrics["hn_url"])

        items.append(
            DigestItem(
                rank=rank,
                signal_id=scored.signal_id,
                title=getattr(raw, "title", "Untitled"),
                composite_score=scored.composite_score,
                what=getattr(raw, "description", "No description available.") or getattr(raw, "title", "Untitled"),
                why_now=summarize_why_now(raw),
                who_cares=summarize_who_cares(raw),
                key_metrics=key_metrics,
                source_urls=[url for url in urls if url],
                kol_quotes=scored.kol_quotes or [],
                authenticity="VERIFIED" if scored.authenticity_multiplier >= 0.7 else "UNVERIFIED",
                topic=getattr(scored, "topic", None),
                generated_at=generated_at,
            )
        )
    return items


@click.group()
def cli() -> None:
    """TrendScout command line interface."""
    configure_logging()


@cli.command()
def run() -> None:
    """Run the full TrendScout pipeline once."""
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()

    since = datetime.utcnow() - timedelta(hours=24)
    raw_signals = asyncio.run(collect_signals(since))
    inserted_count = 0
    for raw_signal in raw_signals:
        if db.insert_raw_signal(raw_signal):
            inserted_count += 1

    click.echo(f"TrendScout run: {len(raw_signals)} signals collected, {inserted_count} inserted.")


@cli.command()
@click.option("--dry-run", is_flag=True, default=False, help="Build digest without sending.")
@click.option("--use-llm", is_flag=True, default=False, help="Use the LLM-style digest synthesizer.")
def digest(dry_run: bool, use_llm: bool) -> None:
    """Generate the morning digest."""
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()

    since = datetime.utcnow() - timedelta(hours=24)
    raw_signals = asyncio.run(collect_signals(since))
    scored_signals = []
    topic_modeler = TopicModeler()

    quarantined_count = 0
    for raw_signal in raw_signals:
        authenticity_score, authenticity_reason = compute_authenticity_score(raw_signal)
        if authenticity_score < 0.7:
            db.insert_quarantine(raw_signal.signal_id, raw_signal.source, authenticity_reason, authenticity_score)
            quarantined_count += 1
            continue

        base_score = score_raw_signal(raw_signal, authenticity_score)
        topic_label = topic_modeler.label_topic(raw_signal)
        base_score.topic = topic_label
        base_score.kol_quotes = extract_kol_quotes(raw_signal)

        github_score = compute_github_score(raw_signal) if raw_signal.source == "github" else 0.0
        hn_score = compute_hackernews_score(raw_signal) if raw_signal.source == "hackernews" else 0.0
        kol_score = compute_kol_score(raw_signal)
        sentiment_score = estimate_sentiment(raw_signal)
        momentum_score = compute_momentum_score(raw_signal)
        combined_score = compute_composite_score(github_score or hn_score, kol_score, sentiment_score, momentum_score)
        base_score.composite_score = combined_score * authenticity_score

        scored_signals.append(base_score)

    ranked = rank_signals(scored_signals, top_n=10)
    digest_items = build_digest_items(ranked, generated_at=datetime.utcnow())
    synthesizer = DigestSynthesizer()
    formatted = synthesizer.synthesize(digest_items) if use_llm else format_digest(digest_items, quarantined_count=quarantined_count)
    click.echo(formatted)

    if not dry_run:
        click.echo("Sending digest via Telegram...")
        sent = asyncio.run(send_telegram_message(settings.telegram_bot_token, settings.telegram_chat_id, formatted))
        if sent:
            digest_id = db.archive_digest(formatted)
            click.echo(f"Digest sent and archived as {digest_id}.")
        else:
            click.echo("Failed to send digest.")


@cli.command(name="signal-history")
@click.option("--topic", default=None, help="Filter digest history by topic label.")
def signal_history(topic: str | None) -> None:
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()
    rows = db.query("SELECT digest_id, generated_at, payload FROM digest_archive ORDER BY generated_at DESC LIMIT 20")
    if not rows:
        click.echo("No digest history found.")
        return

    for digest_id, generated_at, payload in rows:
        if topic and topic.lower() not in payload.lower():
            continue
        click.echo(f"{generated_at} | {digest_id}")
        click.echo(payload)
        click.echo("---")


@cli.command(name="learn-kol-weights")
def learn_kol_weights_command() -> None:
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()
    weights = learn_kol_weights(db)
    if not weights:
        click.echo("No KOL registry found or no historical signals available to learn from.")
        return

    click.echo("Updated KOL weights:")
    for kol_id, weight in sorted(weights.items(), key=lambda item: item[0]):
        click.echo(f" - {kol_id}: {weight:.2f}")


@cli.command(name="knowledge-sync")
def knowledge_sync() -> None:
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()
    summary = KnowledgeUpdater().update()
    click.echo("Knowledge brain sync completed:")
    click.echo(f" - documents collected: {summary['documents_collected']}")
    click.echo(f" - documents parsed: {summary['parsed']}")
    click.echo(f" - embeddings generated: {summary['embeddings']}")


@cli.command()
def watch() -> None:
    """Run a daily digest scheduler at the configured local time."""
    settings = Settings()
    try:
        schedule_time = datetime.strptime(settings.schedule_daily, "%H:%M").time()
    except ValueError as exc:
        raise click.BadParameter("schedule_daily must be formatted as HH:MM") from exc

    click.echo(f"Starting TrendScout daily digest scheduler at {settings.schedule_daily} local time.")
    while True:
        now = datetime.now()
        next_run = datetime.combine(now.date(), schedule_time)
        if next_run <= now:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        click.echo(f"Next digest at {next_run.isoformat(timespec='minutes')}. Sleeping {int(wait_seconds)} seconds.")
        time.sleep(wait_seconds)

        try:
            digest.callback(dry_run=False)
        except Exception as exc:
            click.echo(f"Scheduled digest failed: {exc}")


@cli.command(name="quarantine")
def quarantine_list() -> None:
    """List quarantined signals."""
    settings = Settings()
    db = Database(settings.database_path)
    db.initialize()
    quarantined = db.list_quarantined(limit=25)
    if not quarantined:
        click.echo("No quarantined signals found.")
        return
    for signal_id, source, reason, score, quarantined_at in quarantined:
        click.echo(f"{quarantined_at} | {source} | {signal_id} | {score:.2f} | {reason}")
