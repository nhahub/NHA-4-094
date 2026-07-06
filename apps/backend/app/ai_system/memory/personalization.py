from __future__ import annotations

from typing import List, Optional, Dict, Any, Tuple

from app.ai_system.memory.memory_types import (
    ChatMessage, SessionMemory, FrustrationLog, RepetitionSchedule, MemoryContext
)
from app.schemas.memory_schema import MemoryItem, WeakTopic, MistakePattern, TopicMastery
from app.schemas.personalization_schema import UserProfile
from app.ai_system.memory import memory_config
from app.ai_system.memory.summarizer import Summarizer, _messages_to_transcript
from app.ai_system.memory.memory_retriever import detect_continuation


class PersonalizationEngine:
    """
    Adapts all AI outputs to the individual learner's full profile.
    Main integration point for generating personalized system instructions.
    """
    def __init__(self) -> None:
        self._summarizer = Summarizer()

    def get_accessibility_instruction(self, profile: Optional[UserProfile]) -> str:
        if not profile or not profile.accessibility:
            return ""

        acc = profile.accessibility
        instructions = []

        if acc.dyslexia_friendly:
            instructions.append(
                "DYSLEXIA SUPPORT: Use very short sentences (max 15 words). "
                "One idea per sentence. Use bullet points over paragraphs. "
                "Avoid italics. Use simple, common words."
            )
        if acc.screen_reader:
            instructions.append(
                "SCREEN READER: Use plain text only. No tables, no ASCII art, "
                "no markdown formatting. Spell out all abbreviations. "
                "Describe any process as numbered steps."
            )
        if acc.simplified_language:
            instructions.append(
                "SIMPLIFIED LANGUAGE: Override the student's level. "
                "Always use the simplest possible vocabulary regardless of topic. "
                "Explain every technical term immediately after using it."
            )
        if acc.extended_time:
            instructions.append(
                "EXTENDED TIME: This student has extended time accommodation. "
                "Do not create time pressure. Avoid phrases like 'quickly' or 'briefly'."
            )
        if acc.custom_notes:
            instructions.append(f"CUSTOM NOTE: {acc.custom_notes}")

        if not instructions:
            return ""

        return "ACCESSIBILITY REQUIREMENTS (apply to all responses):\n" + \
               "\n".join(f"  • {i}" for i in instructions)

    def get_difficulty_instruction(
        self,
        profile: Optional[UserProfile],
        topic: Optional[str] = None,
        weak_topics: Optional[List[WeakTopic]] = None,
    ) -> str:
        if profile and profile.accessibility and profile.accessibility.simplified_language:
            return memory_config.DIFFICULTY_INSTRUCTIONS["beginner"]

        level = profile.learning_level if profile else "beginner"

        if topic and weak_topics:
            is_weak = any(
                wt.topic.lower() == topic.lower()
                for wt in weak_topics if not wt.resolved
            )
            if is_weak:
                downgrade = {"advanced": "intermediate", "intermediate": "beginner"}.get(level, level)
                if downgrade != level:
                    return (
                        memory_config.DIFFICULTY_INSTRUCTIONS[downgrade] +
                        f"\n[Difficulty reduced: '{topic}' is a known weak area — "
                        f"build confidence before increasing challenge.]"
                    )

        return memory_config.DIFFICULTY_INSTRUCTIONS.get(level, memory_config.DIFFICULTY_INSTRUCTIONS["beginner"])

    def get_style_instruction(self, profile: Optional[UserProfile]) -> str:
        if profile and profile.accessibility and profile.accessibility.dyslexia_friendly:
            return memory_config.STYLE_INSTRUCTIONS["simple"]
        style = profile.explanation_style if profile else "simple"
        return memory_config.STYLE_INSTRUCTIONS.get(style, memory_config.STYLE_INSTRUCTIONS["simple"])

    def get_language_instruction(self, profile: Optional[UserProfile]) -> str:
        lang = profile.preferred_language if profile else "english"
        if lang.lower() in ("english", "en"):
            return ""
        return (
            f"Always respond in {lang}. "
            f"Translate all technical terms and provide definitions in {lang}."
        )

    def get_quiz_params(
        self,
        profile: Optional[UserProfile],
        topic: Optional[str] = None,
        weak_topics: Optional[List[WeakTopic]] = None,
    ) -> dict:
        level = profile.learning_level if profile else "beginner"

        if profile and profile.accessibility and profile.accessibility.simplified_language:
            level = "beginner"

        is_weak = False
        if topic and weak_topics:
            is_weak = any(wt.topic.lower() == topic.lower()
                          for wt in weak_topics if not wt.resolved)

        effective = {"advanced": "intermediate", "intermediate": "beginner"}.get(level, level) \
            if is_weak else level

        params = dict(memory_config.QUIZ_PARAMS[effective])
        params["difficulty"]        = effective
        params["focus_weak_areas"]  = is_weak
        params["extra_explanation"] = (effective == "beginner") or is_weak
        params["hints"]             = params.get("hints", False) or \
            (profile.accessibility.extended_time if profile and profile.accessibility else False)

        return params

    def get_summary_params(self, profile: Optional[UserProfile]) -> dict:
        level = profile.learning_level if profile else "beginner"
        style = profile.explanation_style if profile else "simple"
        acc   = profile.accessibility if profile else None

        use_bullets = style in ("simple", "visual")
        if acc and acc.dyslexia_friendly:
            use_bullets = True
        if acc and acc.screen_reader:
            use_bullets = False

        return {
            "length":            {"beginner": "short", "intermediate": "medium", "advanced": "long"}[level],
            "use_bullet_points": use_bullets,
            "include_analogies": style in ("simple", "example-based"),
            "technical_depth":   {"beginner": "low", "intermediate": "medium", "advanced": "high"}[level],
            "language":          profile.preferred_language if profile else "english",
            "plain_text_only":   bool(acc and acc.screen_reader),
        }

    def generate_study_plan_prompt(
        self,
        profile: Optional[UserProfile],
        weak_topics: List[WeakTopic],
        progress: List[TopicMastery],
    ) -> str:
        level   = profile.learning_level if profile else "beginner"
        goals   = profile.study_goals if profile else []
        lang    = profile.preferred_language if profile else "english"

        mastered   = [p.topic for p in progress if p.mastery_level == "mastered"]
        struggling = [wt.topic for wt in weak_topics if not wt.resolved]

        session_len = {"beginner": 30, "intermediate": 45, "advanced": 60}[level]
        review_freq = {"beginner": 2,  "intermediate": 3,  "advanced": 4 }[level]

        return f"""
Generate a personalized 2-week study plan.

Student: Level={level}, Language={lang}
Goals: {', '.join(goals) or 'general understanding'}

Topic Status:
  Mastered:       {', '.join(mastered) or 'none yet'}
  Struggling:     {', '.join(struggling) or 'none'}

Requirements:
  - Session length: {session_len} minutes
  - Review weak topics every {review_freq} days
  - Interleave new topics with weak-area review
  - Schedule spaced repetition for review-due topics
  - End each week with a full mixed review
  - Language: {lang}
""".strip()

    def get_frustration_instruction(
        self, frustration_logs: Optional[List[FrustrationLog]]
    ) -> str:
        if not frustration_logs:
            return ""

        high = [f for f in frustration_logs if f.frustration_level == "high"]
        medium = [f for f in frustration_logs if f.frustration_level == "medium"]

        if not high and not medium:
            return ""

        instructions = []
        if high:
            topics = ", ".join(f.topic for f in high[:3])
            instructions.append(
                "FRUSTRATION ALERT: The student is showing HIGH frustration "
                f"on topics: {topics}.\n"
                "• Use extremely simple explanations.\n"
                "• Provide more examples than usual.\n"
                "• Slow down — one step at a time.\n"
                "• Frequently check understanding.\n"
                "• Be encouraging and patient.\n"
                "• Offer to switch to a different topic if needed."
            )

        if medium and not high:
            topics = ", ".join(f.topic for f in medium[:3])
            instructions.append(
                "FRUSTRATION WARNING: The student is showing moderate frustration "
                f"on topics: {topics}.\n"
                "• Simplify explanations slightly.\n"
                "• Add one extra example per concept.\n"
                "• Check if they want to continue or need a break."
            )

        return "\n\n".join(instructions)

    def build_prompt_context_block(
        self,
        context: MemoryContext,
        current_topic: Optional[str] = None,
        current_query: Optional[str] = None,
    ) -> str:
        """
        Assemble the full memory + personalization block for LLM injection.
        """
        profile     = context.user_profile
        recent      = context.recent_messages
        past        = context.relevant_past
        weak        = context.weak_topics
        mistakes    = context.recent_mistakes
        topic_mems  = context.topic_memories
        summary     = context.session_summary

        sections: List[str] = []
        used = 0
        char_cap = memory_config.TOKEN_BUDGET_TOTAL * 4

        def _add(header: str, body: str, budget_tokens: int) -> None:
            nonlocal used
            if used >= char_cap or not body.strip():
                return
            avail = min(budget_tokens * 4, char_cap - used)
            body  = body[:avail - 3] + "..." if len(body) > avail else body
            block = f"{'─'*48}\n{header}\n{'─'*48}\n{body}"
            sections.append(block)
            used += len(block)

        # ── 1. Student Profile ─────────────────────────────────────
        if profile:
            p_text = (
                f"Name:    Student\n"
                f"Level:   {profile.learning_level}\n"
                f"Style:   {profile.explanation_style}\n"
                f"Language:{profile.preferred_language}\n"
                f"Goals:   {', '.join(profile.study_goals) or 'not set'}\n"
                f"Avg Score:{profile.avg_quiz_score:.0%}"
            )
            _add("STUDENT PROFILE", p_text, memory_config.TOKEN_BUDGET_PROFILE // 2)

        # ── 2. Personalization + Accessibility ─────────────────────
        diff  = self.get_difficulty_instruction(profile, current_topic, weak)
        style = self.get_style_instruction(profile)
        lang  = self.get_language_instruction(profile)
        acc   = self.get_accessibility_instruction(profile)

        instr = f"Difficulty: {diff}\nStyle: {style}"
        if lang:  
            instr += f"\nLanguage: {lang}"
        if acc:   
            instr  = acc + "\n\n" + instr

        _add("PERSONALIZATION INSTRUCTIONS", instr, memory_config.TOKEN_BUDGET_PROFILE // 2)

        # ── 3. Frustration Detection ──────────────────────────
        frustration_logs = context.frustration_logs
        frust_instr = self.get_frustration_instruction(frustration_logs)
        if frust_instr:
            _add("FRUSTRATION ADAPTATION", frust_instr, 400)

        # ── 4. Weak Areas ──────────────────────────────────────────
        if weak:
            _add("WEAK AREAS (give extra attention)",
                 self._summarizer.summarize_weak_topics(weak),
                 memory_config.TOKEN_BUDGET_WEAK_TOPICS)

        # ── 5. Recent Conversation ─────────────────────────────────
        if recent:
            transcript = _messages_to_transcript(recent[-8:])
            _add("RECENT CONVERSATION", transcript, memory_config.TOKEN_BUDGET_RECENT_CHAT)
        elif summary:
            _add("SESSION SUMMARY (compressed)", summary, memory_config.TOKEN_BUDGET_RECENT_CHAT)

        # ── 6. Relevant Past Learning ──────────────────────────────
        if past:
            lines = []
            for m in past[:4]:
                lines.append(f"[ episiodic ] {m.content[:100]}")
            _add("RELEVANT PAST LEARNING", "\n".join(lines), memory_config.TOKEN_BUDGET_PAST_CONTEXT)

        # ── 7. Mistake History ─────────────────────────────────────
        if mistakes:
            _add("MISTAKE HISTORY (clustered by severity)",
                 self._summarizer.summarize_mistakes(mistakes),
                 memory_config.TOKEN_BUDGET_MISTAKES)

        # ── 8. Topic Mastery ───────────────────────────────────────
        if topic_mems:
            _add("TOPIC MASTERY SCORES",
                 self._summarizer.summarize_topic_memories(topic_mems), 400)

        if not sections:
            return "[No memory context — treating as first session]"

        header = (
            f"\n{'#'*58}\n"
            f"# MEMORY & PERSONALIZATION CONTEXT  (Engineer 5)\n"
            f"# Sections: {len(sections)}  |  Est. tokens: ~{used//4}\n"
            f"{'#'*58}\n"
        )
        return header + "\n\n".join(sections) + f"\n{'#'*58}\n"

    def get_system_prompt(
        self,
        context: MemoryContext,
        base_prompt: str = "You are an expert AI tutor for the AI Study Platform.",
        current_topic: Optional[str] = None,
        current_query: Optional[str] = None,
    ) -> str:
        block = self.build_prompt_context_block(context, current_topic, current_query)
        return f"{base_prompt}\n\n{block}"

    def adapt_explanation(
        self,
        explanation: str,
        profile: Optional[UserProfile],
        weak_topics: Optional[List[WeakTopic]] = None,
        topic: Optional[str] = None,
    ) -> str:
        level = profile.learning_level if profile else "beginner"
        style = profile.explanation_style if profile else "simple"
        note  = f"\n\n[Personalized: level={level}, style={style}"
        if topic and weak_topics:
            if any(wt.topic.lower() == topic.lower() for wt in (weak_topics or [])):
                note += f", '{topic}' is a weak area — extra care applied"
        note += "]"
        return explanation + note
