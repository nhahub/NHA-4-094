from __future__ import annotations

import re
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

from app.ai_system.memory.memory_store import MemoryStore
from app.ai_system.memory.memory_types import (
    ChatMessage, SessionMemory, FrustrationLog, RepetitionSchedule
)
from app.schemas.memory_schema import MemoryItem, WeakTopic, MistakePattern, TopicMastery
from app.ai_system.memory import memory_config

def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[:max_chars - 3] + "..."

def _messages_to_transcript(messages: List[ChatMessage]) -> str:
    lines = []
    for m in messages:
        speaker = "Student" if m.role == "user" else "Tutor"
        lines.append(f"{speaker}: {m.content}")
    return "\n".join(lines)

def _extract_topics(messages: List[ChatMessage]) -> List[str]:
    seen, topics = set(), []
    for m in messages:
        if m.topic and m.topic not in seen:
            seen.add(m.topic)
            topics.append(m.topic)
    return topics

def _extract_questions(messages: List[ChatMessage]) -> List[str]:
    q_pattern = re.compile(
        r"^(?:what|how|why|when|where|who|which|can|could|is|are|does|do|"
        r"explain|tell me|describe|define|clarify|show me).+[?]?$",
        re.IGNORECASE | re.MULTILINE
    )
    questions = []
    seen = set()
    for m in messages:
        if m.role != "user":
            continue
        stripped = m.content.strip()
        if q_pattern.match(stripped) or stripped.endswith("?"):
            if stripped not in seen and len(stripped) > 10:
                seen.add(stripped)
                questions.append(stripped[:200])
        for sentence in re.split(r"[.!]", stripped):
            s = sentence.strip()
            if s.endswith("?") and len(s) > 10 and s not in seen:
                seen.add(s)
                questions.append(s[:200])
    return questions[:15]

def _extract_concepts_learned(messages: List[ChatMessage]) -> List[str]:
    concepts = []
    seen = set()
    understand_signals = [
        "i understand", "that makes sense", "got it", "i see", "now i know",
        "okay so", "so basically", "ah i see", "makes sense", "thanks that helped",
        "فهمت", "واضح", "شكرا", "تمام"
    ]
    for i, m in enumerate(messages):
        if m.role == "user" and any(sig in m.content.lower() for sig in understand_signals):
            for j in range(i - 1, max(i - 4, -1), -1):
                if messages[j].role == "assistant" and messages[j].topic:
                    t = messages[j].topic
                    if t not in seen:
                        seen.add(t)
                        concepts.append(t)
                    break
    for m in messages:
        if m.role == "assistant" and m.topic and m.topic not in seen:
            seen.add(m.topic)
            concepts.append(m.topic)
    return concepts[:10]

def _extract_confusions(messages: List[ChatMessage]) -> List[str]:
    confusion_signals = [
        "don't understand", "confused", "i'm lost", "unclear", "doesn't make sense",
        "still don't get", "can you explain again", "what do you mean", "i don't get",
        "not sure", "huh?", "what?", "i thought", "why is it not",
        "مش فاهم", "لم أفهم", "غير واضح", "صعب"
    ]
    confusions = []
    seen = set()
    for m in messages:
        if m.role != "user":
            continue
        cl = m.content.lower()
        if any(sig in cl for sig in confusion_signals):
            snippet = m.content.strip()[:150]
            if snippet not in seen:
                seen.add(snippet)
                confusions.append(snippet)
    return confusions[:8]

def build_planner_summary(
    session: SessionMemory,
    planner_ctx: Optional[Dict[str, Any]] = None,
) -> str:
    lines = [
        "=== PLANNER SESSION CONTEXT ===",
        f"Session ID: {session.session_id}",
        f"Messages:   {session.message_count}",
        "",
    ]
    if session.topics_covered:
        lines.append(f"TOPICS COVERED: {', '.join(session.topics_covered)}")
    if session.questions_asked:
        lines.append("QUESTIONS ASKED:")
        for q in session.questions_asked[:5]:
            lines.append(f"  * {q}")
    if session.concepts_learned:
        lines.append(f"CONCEPTS LEARNED: {', '.join(session.concepts_learned)}")
    if session.confusions:
        lines.append("UNRESOLVED CONFUSIONS (needs follow-up):")
        for c in session.confusions[:4]:
            lines.append(f"  [!] {c}")
    if planner_ctx:
        lines.append("")
        lines.append(f"LAST INTENT:    {planner_ctx.get('last_intent', '')}")
        lines.append(f"LAST TASK:      {planner_ctx.get('last_task', '')}")
        lines.append(f"LAST TOPIC:     {planner_ctx.get('last_topic', '')}")
        lines.append(f"RESPONSE TYPE:  {planner_ctx.get('last_response_type', '')}")
        if planner_ctx.get("unfinished_goals"):
            lines.append("UNFINISHED GOALS:")
            for g in planner_ctx["unfinished_goals"]:
                lines.append(f"  -> {g}")
    lines.append("=== END PLANNER CONTEXT ===")
    return "\n".join(lines)


class ExtractiveSummarizer:
    """Rule-based summarizer fallback."""
    HIGH_VALUE = re.compile(
        r"\b(explain|understand|learn|study|mistake|wrong|correct|answer|"
        r"result|score|question|concept|definition|because|therefore|"
        r"however|important|key|main|summary|conclusion|confusion|clarify)\b",
        re.IGNORECASE
    )

    def _score_sentence(self, s: str) -> float:
        score = len(self.HIGH_VALUE.findall(s)) * 0.12
        n = len(s.split())
        if 8 <= n <= 35:
            score += 0.2
        return score

    def summarize_text(
        self, text: str,
        max_sentences: int = memory_config.SUMMARY_MAX_OUTPUT_SENTENCES
    ) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip())
                     if len(s.strip()) > 20]
        if not sentences:
            return text[:300]
        scored = sorted(enumerate(sentences), key=lambda x: self._score_sentence(x[1]), reverse=True)
        top_idx = sorted(i for i, _ in scored[:max_sentences])
        return " ".join(sentences[i] for i in top_idx)


class Summarizer:
    def __init__(self) -> None:
        self.store = MemoryStore()
        self._engine = ExtractiveSummarizer()

    async def should_summarize(self, user_id: str, session_id: str) -> bool:
        count = await self.store.count_session_messages(user_id, session_id)
        return count >= memory_config.SUMMARIZE_AFTER_N_MESSAGES

    async def summarize_session(
        self,
        user_id: str,
        session_id: str,
        force: bool = False,
        planner_ctx: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Compress session into conversation summary."""
        if not force and not await self.should_summarize(user_id, session_id):
            return None

        messages = await self.store.get_all_session_messages(user_id, session_id)
        if not messages:
            return None

        topics = _extract_topics(messages)
        questions = _extract_questions(messages)
        concepts = _extract_concepts_learned(messages)
        confusions = _extract_confusions(messages)

        transcript = _messages_to_transcript(messages)
        transcript = _truncate(transcript, memory_config.SUMMARY_MAX_INPUT_CHARS)
        narrative = self._engine.summarize_text(transcript)
        header = f"[Session | {len(messages)} messages | Topics: {', '.join(topics) or 'general'}]"
        full_narrative = f"{header}\n{narrative}"

        # Build SessionMemory
        session = SessionMemory(
            session_id=session_id,
            user_id=user_id,
            summary_text=full_narrative,
            topics_covered=topics,
            questions_asked=questions,
            concepts_learned=concepts,
            confusions=confusions,
            message_count=len(messages),
            is_summarized=True,
            ended_at=datetime.utcnow()
        )
        session.planner_summary = build_planner_summary(session, planner_ctx)
        
        # Save to database
        await self.store.upsert_session(session)
        await self.store.advance_session_in_planner(user_id, session)

        # Save long-term memory items for concepts learned and confusions
        import uuid
        for concept in concepts:
            try:
                mem_item = MemoryItem(
                    user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                    memory_type="fact",
                    content=f"Student mastered/learned concept: {concept}",
                    is_active=True,
                    source_id=uuid.UUID(session_id) if isinstance(session_id, str) else session_id,
                    source_type="session"
                )
                await self.store.save_memory_item(mem_item)
            except Exception as e:
                logger.error(f"Failed to auto-save concept memory item: {e}")

        for confusion in confusions:
            try:
                mem_item = MemoryItem(
                    user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                    memory_type="fact",
                    content=f"Student struggled with or was confused about: {confusion}",
                    is_active=True,
                    source_id=uuid.UUID(session_id) if isinstance(session_id, str) else session_id,
                    source_type="session"
                )
                await self.store.save_memory_item(mem_item)
            except Exception as e:
                logger.error(f"Failed to auto-save confusion memory item: {e}")

        return full_narrative

    async def build_continuation_context(
        self, user_id: str, current_query: str
    ) -> str:
        ctx = await self.store.get_planner_context(user_id)
        if not ctx:
            return "[No prior context found — treating as new topic]"

        lines = [
            "=== CONTINUATION CONTEXT ===",
            "The student is continuing from a previous interaction.",
            f"Last topic:         {ctx.get('last_topic') or 'unknown'}",
            f"Last task done:     {ctx.get('last_task') or 'unknown'}",
            f"Last response type: {ctx.get('last_response_type') or 'unknown'}",
            f"Last question:      {ctx.get('last_question') or 'unknown'}",
        ]

        if ctx.get("previous_session_summary"):
            lines.append("")
            lines.append("Previous session context:")
            lines.append(ctx["previous_session_summary"][:500])

        if ctx.get("unfinished_goals"):
            lines.append("")
            lines.append("Unfinished goals to address:")
            for g in ctx["unfinished_goals"]:
                lines.append(f"  -> {g}")

        lines.append("=== END CONTINUATION CONTEXT ===")
        return "\n".join(lines)

    def summarize_mistakes(self, mistakes: List[MistakePattern]) -> str:
        if not mistakes:
            return "No recorded mistakes."
        high = [m for m in mistakes if getattr(m, "severity", "medium") == "high"]
        medium = [m for m in mistakes if getattr(m, "severity", "medium") == "medium"]
        low = [m for m in mistakes if getattr(m, "severity", "medium") == "low"]

        lines = ["Mistake Analysis:"]

        def _fmt_group(label: str, group: List[MistakePattern]) -> None:
            if not group:
                return
            lines.append(f"\n  [{label} priority]")
            for m in group[:4]:
                freq = f"(x{m.frequency})" if m.frequency > 1 else ""
                lines.append(f"  * [{m.topic}] {freq} {m.mistake_text[:70]}")
                if m.correct_answer:
                    lines.append(f"    [correct]: {m.correct_answer[:70]}")

        _fmt_group("HIGH", high)
        _fmt_group("MEDIUM", medium)
        _fmt_group("LOW", low)
        return "\n".join(lines)

    def summarize_topic_memories(self, topics: List[TopicMastery]) -> str:
        if not topics:
            return "No topic mastery data yet."
        lines = ["Topic Mastery Scores:"]
        for t in sorted(topics, key=lambda x: x.mastery_score or 0.0, reverse=True):
            score = float(t.mastery_score or 0.0)
            bar_n = int(score * 10)
            bar = "#" * bar_n + "." * (10 - bar_n)
            lines.append(
                f"  {t.topic:<22} {bar} {score:.0%}"
                f"  (studied x{t.times_studied})"
            )
        return "\n".join(lines)

    def summarize_weak_topics(self, weak_topics: List[WeakTopic]) -> str:
        if not weak_topics:
            return "No identified weak topics."
        sorted_wt = sorted(weak_topics, key=lambda w: w.weakness_score or 0.0, reverse=True)
        lines = ["Areas needing extra attention (ranked by weakness):"]
        for wt in sorted_wt[:6]:
            w_score = float(wt.weakness_score or 0.0)
            ws_bar = "#" * int(w_score * 8) + "." * (8 - int(w_score * 8))
            lines.append(
                f"  * {wt.topic:<22} weakness: {ws_bar} {w_score:.0%}"
                f"  fails: {wt.failed_count}"
            )
        return "\n".join(lines)

    def summarize_frustration(self, frustration_logs: List[FrustrationLog]) -> str:
        if not frustration_logs:
            return "No frustration detected."
        lines = ["Frustration Analysis:"]
        high = [f for f in frustration_logs if f.frustration_level == "high"]
        medium = [f for f in frustration_logs if f.frustration_level == "medium"]
        if high:
            lines.append(f"  !!! HIGH FRUSTRATION ({len(high)} topics):")
            for f in high:
                lines.append(f"    * {f.topic} (score={f.frustration_score:.2f})")
        if medium:
            lines.append(f"  !! MEDIUM FRUSTRATION ({len(medium)} topics):")
            for f in medium:
                lines.append(f"    * {f.topic} (score={f.frustration_score:.2f})")
        if not high and not medium:
            lines.append("  [OK] No significant frustration detected.")
        return "\n".join(lines)

    def summarize_repetition_schedule(self, schedules: List[RepetitionSchedule]) -> str:
        if not schedules:
            return "No repetition schedule data."
        lines = ["Spaced Repetition Schedule:"]
        due = [s for s in schedules if s.is_due_today or s.is_overdue]
        if due:
            lines.append(f"  ⏰ DUE NOW ({len(due)} topics):")
            for s in sorted(due, key=lambda x: x.review_priority or 0.0, reverse=True)[:5]:
                lines.append(
                    f"    * {s.topic:<20} priority={s.review_priority:.2f}"
                    f" retention={s.retention_score:.0%}"
                )
        return "\n".join(lines)
