"""
Service to generate a demo directory corpus with sample text files grouped by topic.
"""
from __future__ import annotations

import os
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.schemas.demo import DemoGenerateRequest, DemoGenerateResponse, DEFAULT_TOPICS


_PARAGRAPHS: List[str] = [
    "In a surprising turn of events, sources confirmed late Tuesday that the committee reached a bipartisan agreement after weeks of negotiation.",
    "Analysts say the market reaction was driven by stronger-than-expected earnings and a renewed appetite for risk among institutional investors.",
    "The coaching staff emphasized fundamentals during practice, focusing on ball control, defensive positioning, and situational awareness.",
    "Researchers highlighted the importance of clear disclosure and rigor in methodology to maintain public trust in emerging AI systems.",
    "Health officials reiterated their guidance, encouraging regular checkups and balanced nutrition as key preventive measures.",
    "Industry leaders described the announcement as a milestone, citing new partnerships and an expanding developer ecosystem.",
]


def _gen_title(topic: str, idx: int) -> str:
    return f"{topic.capitalize()} Update #{idx}"


def _gen_body(topic: str, paragraphs_per_file: int, rng: random.Random) -> str:
    parts = []
    for _ in range(paragraphs_per_file):
        parts.append(rng.choice(_PARAGRAPHS))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    header = f"Topic: {topic}\nGenerated: {ts}\n\n"
    return header + "\n\n".join(parts) + "\n"


def generate_demo_corpus(payload: DemoGenerateRequest) -> DemoGenerateResponse:
    rng = random.Random(payload.seed)

    base = Path(payload.base_path).expanduser().resolve()
    topics = payload.topics or DEFAULT_TOPICS

    if base.exists():
        if not payload.overwrite:
            # Keep existing content; compute counts from requested files_per_topic
            return DemoGenerateResponse(
                base_path=str(base),
                topics_created=topics,
                total_files=len(topics) * payload.files_per_topic,
                files_per_topic=payload.files_per_topic,
                paragraphs_per_file=payload.paragraphs_per_file,
            )
        # Overwrite requested
        shutil.rmtree(base)
    os.makedirs(base, exist_ok=True)

    total_files = 0
    for topic in topics:
        topic_dir = base / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, payload.files_per_topic + 1):
            title = _gen_title(topic, i)
            body = _gen_body(topic, payload.paragraphs_per_file, rng)
            # Use .txt extension by default, can be filtered by UI include_extensions
            file_path = topic_dir / f"{title.replace(' ', '_').lower()}.txt"
            file_path.write_text(body, encoding="utf-8")
            total_files += 1

    return DemoGenerateResponse(
        base_path=str(base),
        topics_created=topics,
        total_files=total_files,
        files_per_topic=payload.files_per_topic,
        paragraphs_per_file=payload.paragraphs_per_file,
    )
