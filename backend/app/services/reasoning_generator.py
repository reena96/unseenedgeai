"""GPT-4 reasoning generation service for skill assessments."""

import logging
import os
from typing import List, Optional, Tuple
import openai
from dataclasses import dataclass
import tiktoken

from app.models.assessment import SkillType
from app.services.evidence_fusion import EvidenceItem
from app.core.rate_limiter import (
    get_rate_limiter_registry,
    RateLimitConfig,
    rate_limit,
)
from app.core.secrets import get_openai_api_key

logger = logging.getLogger(__name__)

# Token limits for GPT models
MODEL_TOKEN_LIMITS = {
    "gpt-4o-mini": 128000,
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 16385,
}

# Safe token limits (leaving buffer for response)
SAFE_TOKEN_LIMITS = {
    "gpt-4o-mini": 120000,  # Leave 8k for response
    "gpt-4o": 120000,
    "gpt-4-turbo": 120000,
    "gpt-4": 6000,  # Leave 2k for response
    "gpt-3.5-turbo": 14000,  # Leave 2k for response
}


@dataclass
class SkillReasoning:
    """Generated reasoning for a skill assessment."""

    skill_type: SkillType
    score: float
    reasoning: str
    growth_suggestions: List[str]
    strengths: List[str]


class ReasoningGeneratorService:
    """Service for generating growth-oriented reasoning using GPT-4."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        calls_per_minute: int = 50,
        calls_per_hour: int = 500,
    ):
        """
        Initialize reasoning generator.

        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: GPT model to use
            calls_per_minute: Rate limit for API calls per minute
            calls_per_hour: Rate limit for API calls per hour
        """
        # Get API key from secret manager or environment variable
        if api_key:
            self.api_key = api_key
        else:
            # Try secret manager first, fall back to env var
            self.api_key = get_openai_api_key()

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required for reasoning generation. "
                "Configure in GCP Secret Manager (openai-api-key) or "
                "set OPENAI_API_KEY environment variable."
            )

        self.model = model

        self.client = openai.AsyncOpenAI(api_key=self.api_key)

        # Initialize tokenizer for counting tokens
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to cl100k_base for newer models
            logger.warning(f"No tokenizer found for {self.model}, using cl100k_base")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Register rate limiter for OpenAI API calls
        registry = get_rate_limiter_registry()
        rate_limit_config = RateLimitConfig(
            calls_per_minute=calls_per_minute,
            calls_per_hour=calls_per_hour,
            burst_size=10,
        )
        registry.register("openai_reasoning", rate_limit_config)

        logger.info(
            f"Initialized ReasoningGenerator with model: {self.model}, "
            f"rate limits: {calls_per_minute}/min, {calls_per_hour}/hour"
        )

        # Skill definitions for context
        self.skill_definitions = {
            SkillType.EMPATHY: {
                "name": "Empathy",
                "description": "Understanding and sharing the feelings of others",
                "key_aspects": [
                    "perspective-taking",
                    "emotional awareness",
                    "caring responses",
                ],
            },
            SkillType.PROBLEM_SOLVING: {
                "name": "Problem-Solving",
                "description": "Analyzing challenges and developing effective solutions",
                "key_aspects": [
                    "analytical thinking",
                    "strategy development",
                    "persistence",
                ],
            },
            SkillType.SELF_REGULATION: {
                "name": "Self-Regulation",
                "description": "Managing emotions, thoughts, and behaviors effectively",
                "key_aspects": ["impulse control", "focus", "emotional management"],
            },
            SkillType.RESILIENCE: {
                "name": "Resilience",
                "description": "Recovering from setbacks and persisting through challenges",
                "key_aspects": [
                    "persistence",
                    "learning from failure",
                    "positive coping",
                ],
            },
        }

        logger.info(f"Initialized ReasoningGeneratorService with model: {self.model}")

    def _format_evidence_for_prompt(self, evidence: List[EvidenceItem]) -> str:
        """
        Format evidence items for GPT-4 prompt.

        Args:
            evidence: List of evidence items

        Returns:
            Formatted evidence string
        """
        if not evidence:
            return "No specific evidence available."

        formatted = []
        for i, item in enumerate(evidence[:5], 1):  # Top 5 evidence items
            formatted.append(f"{i}. {item.content} (confidence: {item.confidence:.2f})")

        return "\n".join(formatted)

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))

    def _count_message_tokens(self, messages: List[dict]) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Total token count
        """
        # Count tokens for each message
        total_tokens = 0
        for message in messages:
            # Add tokens for role and content
            total_tokens += self._count_tokens(message.get("role", ""))
            total_tokens += self._count_tokens(message.get("content", ""))
            # Add 4 tokens per message for formatting
            total_tokens += 4

        # Add 2 tokens for assistant response priming
        total_tokens += 2

        return total_tokens

    def _truncate_evidence(
        self, evidence: List[EvidenceItem], max_items: int = 5
    ) -> Tuple[List[EvidenceItem], bool]:
        """
        Truncate evidence list if needed to stay within token limits.

        Args:
            evidence: List of evidence items
            max_items: Maximum number of items to keep

        Returns:
            Tuple of (truncated_evidence, was_truncated)
        """
        if len(evidence) <= max_items:
            return evidence, False

        # Keep top evidence items by strength
        sorted_evidence = sorted(evidence, key=lambda x: x.strength, reverse=True)
        truncated = sorted_evidence[:max_items]

        logger.warning(
            f"Truncated evidence from {len(evidence)} to {max_items} items "
            "to stay within token limits"
        )

        return truncated, True

    def _build_prompt(
        self,
        skill_type: SkillType,
        score: float,
        confidence: float,
        evidence: List[EvidenceItem],
        student_grade: Optional[int] = None,
    ) -> str:
        """
        Build GPT-4 prompt for reasoning generation.

        Args:
            skill_type: Skill type
            score: Assessment score (0-1)
            confidence: Confidence in assessment
            evidence: List of evidence items
            student_grade: Student's grade level

        Returns:
            Formatted prompt
        """
        skill_info = self.skill_definitions[skill_type]
        grade_context = f"Grade {student_grade} student" if student_grade else "Student"

        prompt = f"""You are an educational psychologist providing feedback on a student's {skill_info['name'].lower()} skill.

SKILL: {skill_info['name']}
DEFINITION: {skill_info['description']}
KEY ASPECTS: {', '.join(skill_info['key_aspects'])}

ASSESSMENT SCORE: {score:.2f}/1.00 (on a 0-1 scale)
CONFIDENCE: {confidence:.2f}
STUDENT CONTEXT: {grade_context}

EVIDENCE:
{self._format_evidence_for_prompt(evidence)}

Please provide:
1. A 2-3 sentence explanation of the assessment that is:
   - Growth-oriented and encouraging
   - Specific to the evidence
   - Appropriate for educators and parents
   - Free of jargon
   - Focuses on observable behaviors

2. Two specific strengths the student demonstrated

3. Two actionable growth suggestions that are:
   - Concrete and specific
   - Achievable in the near term
   - Tied to the evidence
   - Encouraging and positive

Format your response as JSON:
{{
  "reasoning": "2-3 sentence explanation here",
  "strengths": ["strength 1", "strength 2"],
  "growth_suggestions": ["suggestion 1", "suggestion 2"]
}}"""

        return prompt

    @rate_limit("openai_reasoning")
    async def generate_reasoning(
        self,
        skill_type: SkillType,
        score: float,
        confidence: float,
        evidence: List[EvidenceItem],
        student_grade: Optional[int] = None,
    ) -> SkillReasoning:
        """
        Generate reasoning for a skill assessment using GPT-4.

        Args:
            skill_type: Skill type
            score: Assessment score (0-1)
            confidence: Confidence score
            evidence: List of evidence items
            student_grade: Student's grade level

        Returns:
            SkillReasoning object with generated content

        Raises:
            Exception: If GPT-4 API call fails
        """
        logger.info(f"Generating reasoning for {skill_type.value} (score: {score:.2f})")

        # Check and potentially truncate evidence to stay within token limits
        safe_limit = SAFE_TOKEN_LIMITS.get(self.model, 100000)
        evidence_to_use = evidence
        was_truncated = False

        # Start with all evidence, then truncate if needed
        for max_items in [len(evidence), 10, 5, 3]:
            truncated_evidence, _ = self._truncate_evidence(evidence, max_items)
            prompt = self._build_prompt(
                skill_type, score, confidence, truncated_evidence, student_grade
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an educational psychologist specializing in "
                        "providing growth-oriented feedback on student skills. "
                        "Always respond with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ]

            token_count = self._count_message_tokens(messages)

            if token_count <= safe_limit:
                evidence_to_use = truncated_evidence
                was_truncated = len(truncated_evidence) < len(evidence)
                logger.info(
                    f"Token count: {token_count} (limit: {safe_limit}), "
                    f"using {len(evidence_to_use)} evidence items"
                )
                break
        else:
            # Even with 3 items we're over limit - use fallback
            logger.warning(
                f"Prompt too large even with 3 evidence items ({token_count} tokens), "
                "using fallback reasoning"
            )
            return self._generate_fallback_reasoning(skill_type, score, evidence)

        if was_truncated:
            logger.warning(
                f"Truncated evidence from {len(evidence)} to {len(evidence_to_use)} items "
                f"to stay within {safe_limit} token limit"
            )

        # Build final prompt with appropriate evidence
        prompt = self._build_prompt(
            skill_type, score, confidence, evidence_to_use, student_grade
        )

        try:
            # Call GPT-4 with token-validated prompt
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an educational psychologist specializing in "
                            "providing growth-oriented feedback on student skills. "
                            "Always respond with valid JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            # Parse response
            import json

            content = response.choices[0].message.content
            parsed = json.loads(content)

            reasoning = parsed.get("reasoning", "")
            strengths = parsed.get("strengths", [])
            growth_suggestions = parsed.get("growth_suggestions", [])

            logger.info(f"Generated reasoning for {skill_type.value}")

            return SkillReasoning(
                skill_type=skill_type,
                score=score,
                reasoning=reasoning,
                growth_suggestions=growth_suggestions,
                strengths=strengths,
            )

        except Exception as e:
            logger.error(f"Failed to generate reasoning: {e}")

            # Fallback to template-based reasoning
            return self._generate_fallback_reasoning(skill_type, score, evidence)

    def _generate_fallback_reasoning(
        self,
        skill_type: SkillType,
        score: float,
        evidence: List[EvidenceItem],
    ) -> SkillReasoning:
        """
        Generate fallback reasoning when GPT-4 is unavailable.

        Args:
            skill_type: Skill type
            score: Assessment score
            evidence: Evidence items

        Returns:
            SkillReasoning with template-based content
        """
        skill_info = self.skill_definitions[skill_type]

        # Determine level
        if score >= 0.75:
            level = "strong"
            reasoning_template = f"The student demonstrates strong {skill_info['name'].lower()} skills. Evidence shows consistent application of {skill_info['key_aspects'][0]} and {skill_info['key_aspects'][1]}."
        elif score >= 0.5:
            level = "developing"
            reasoning_template = f"The student is developing {skill_info['name'].lower()} skills. They show emerging abilities in {skill_info['key_aspects'][0]}, with room for growth in {skill_info['key_aspects'][1]}."
        else:
            level = "emerging"
            reasoning_template = f"The student is beginning to develop {skill_info['name'].lower()} skills. With support and practice, they can strengthen their {skill_info['key_aspects'][0]} and {skill_info['key_aspects'][1]}."

        # Extract evidence-based context
        if evidence:
            reasoning_template += f" {evidence[0].content}."

        return SkillReasoning(
            skill_type=skill_type,
            score=score,
            reasoning=reasoning_template,
            strengths=[
                f"Shows awareness of {skill_info['key_aspects'][0]}",
                "Demonstrates engagement with learning activities",
            ],
            growth_suggestions=[
                f"Practice {skill_info['key_aspects'][1]} in daily activities",
                f"Set small goals to improve {skill_info['key_aspects'][2]}",
            ],
        )

    async def generate_all_reasoning(
        self,
        skill_scores: dict,  # {SkillType: (score, confidence, evidence)}
        student_grade: Optional[int] = None,
    ) -> dict:  # {SkillType: SkillReasoning}
        """
        Generate reasoning for all skills.

        Args:
            skill_scores: Dictionary mapping skills to (score, confidence, evidence)
            student_grade: Student's grade level

        Returns:
            Dictionary mapping skills to SkillReasoning objects
        """
        results = {}

        for skill_type, (score, confidence, evidence) in skill_scores.items():
            try:
                reasoning = await self.generate_reasoning(
                    skill_type, score, confidence, evidence, student_grade
                )
                results[skill_type] = reasoning
            except Exception as e:
                logger.error(
                    f"Failed to generate reasoning for {skill_type.value}: {e}"
                )
                continue

        return results
