"""Tests for GPT-4 reasoning generation service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from app.services.reasoning_generator import ReasoningGeneratorService, SkillReasoning
from app.models.assessment import SkillType, EvidenceType
from app.services.evidence_fusion import EvidenceItem, EvidenceSource


class TestReasoningGeneratorService:
    """Test ReasoningGeneratorService."""

    @pytest.fixture
    def service(self):
        """Create reasoning generator service."""
        return ReasoningGeneratorService(api_key="test_key")

    @pytest.fixture
    def sample_evidence(self):
        """Create sample evidence items."""
        return [
            EvidenceItem(
                source=EvidenceSource.ML_INFERENCE,
                evidence_type=EvidenceType.BEHAVIORAL,
                content="ML model prediction: 0.75",
                score=0.75,
                confidence=0.85,
                relevance=1.0,
            ),
            EvidenceItem(
                source=EvidenceSource.LINGUISTIC_FEATURES,
                evidence_type=EvidenceType.LINGUISTIC,
                content="Used 8 empathy markers in speech",
                score=0.80,
                confidence=0.70,
                relevance=0.9,
            ),
        ]

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.model == "gpt-4o-mini"
        assert service.skill_definitions is not None
        assert SkillType.EMPATHY in service.skill_definitions

    def test_skill_definitions(self, service):
        """Test skill definitions are complete."""
        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            assert skill_type in service.skill_definitions
            definition = service.skill_definitions[skill_type]
            assert "name" in definition
            assert "description" in definition
            assert "key_aspects" in definition

    def test_format_evidence_for_prompt(self, service, sample_evidence):
        """Test evidence formatting for prompt."""
        formatted = service._format_evidence_for_prompt(sample_evidence)

        assert "1. ML model prediction" in formatted
        assert "2. Used 8 empathy markers" in formatted
        assert "confidence:" in formatted

    def test_format_evidence_empty(self, service):
        """Test formatting with no evidence."""
        formatted = service._format_evidence_for_prompt([])
        assert formatted == "No specific evidence available."

    def test_build_prompt(self, service, sample_evidence):
        """Test prompt building."""
        prompt = service._build_prompt(
            SkillType.EMPATHY, 0.75, 0.85, sample_evidence, student_grade=3
        )

        # Check prompt includes key elements
        assert "Empathy" in prompt
        assert "0.75" in prompt
        assert "Grade 3 student" in prompt
        assert "ML model prediction" in prompt
        assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_generate_reasoning_success(self, service, sample_evidence):
        """Test successful reasoning generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "reasoning": "The student demonstrates strong empathy skills through consistent use of empathy markers and social awareness.",
                "strengths": [
                    "Shows genuine concern for others",
                    "Uses empathy language naturally",
                ],
                "growth_suggestions": [
                    "Practice perspective-taking in group activities",
                    "Reflect on others' feelings during discussions",
                ],
            }
        )

        with patch.object(
            service.client.chat.completions, "create", return_value=mock_response
        ) as mock_create:
            reasoning = await service.generate_reasoning(
                SkillType.EMPATHY, 0.75, 0.85, sample_evidence, student_grade=3
            )

            # Verify result
            assert isinstance(reasoning, SkillReasoning)
            assert reasoning.skill_type == SkillType.EMPATHY
            assert reasoning.score == 0.75
            assert len(reasoning.reasoning) > 0
            assert len(reasoning.strengths) == 2
            assert len(reasoning.growth_suggestions) == 2

    @pytest.mark.asyncio
    async def test_generate_reasoning_fallback(self, service, sample_evidence):
        """Test fallback reasoning when GPT-4 fails."""
        # Mock API failure
        with patch.object(
            service.client.chat.completions,
            "create",
            side_effect=Exception("API Error"),
        ):
            reasoning = await service.generate_reasoning(
                SkillType.EMPATHY, 0.75, 0.85, sample_evidence
            )

            # Should return fallback reasoning
            assert isinstance(reasoning, SkillReasoning)
            assert reasoning.skill_type == SkillType.EMPATHY
            assert reasoning.score == 0.75
            assert len(reasoning.reasoning) > 0
            assert "strong" in reasoning.reasoning.lower()

    def test_fallback_reasoning_levels(self, service, sample_evidence):
        """Test fallback reasoning for different score levels."""
        # High score (>= 0.75)
        high_reasoning = service._generate_fallback_reasoning(
            SkillType.EMPATHY, 0.80, sample_evidence
        )
        assert "strong" in high_reasoning.reasoning.lower()

        # Medium score (0.5-0.75)
        mid_reasoning = service._generate_fallback_reasoning(
            SkillType.EMPATHY, 0.60, sample_evidence
        )
        assert "developing" in mid_reasoning.reasoning.lower()

        # Low score (< 0.5)
        low_reasoning = service._generate_fallback_reasoning(
            SkillType.EMPATHY, 0.35, sample_evidence
        )
        assert (
            "emerging" in low_reasoning.reasoning.lower()
            or "beginning" in low_reasoning.reasoning.lower()
        )

    @pytest.mark.asyncio
    async def test_generate_all_reasoning(self, service):
        """Test generating reasoning for all skills."""
        skill_scores = {
            SkillType.EMPATHY: (
                0.75,
                0.85,
                [
                    EvidenceItem(
                        source=EvidenceSource.ML_INFERENCE,
                        evidence_type=EvidenceType.BEHAVIORAL,
                        content="High empathy",
                        score=0.75,
                        confidence=0.85,
                        relevance=1.0,
                    )
                ],
            ),
            SkillType.PROBLEM_SOLVING: (
                0.65,
                0.75,
                [
                    EvidenceItem(
                        source=EvidenceSource.ML_INFERENCE,
                        evidence_type=EvidenceType.BEHAVIORAL,
                        content="Good problem solving",
                        score=0.65,
                        confidence=0.75,
                        relevance=1.0,
                    )
                ],
            ),
        }

        # Mock successful generation
        with patch.object(
            service,
            "generate_reasoning",
            side_effect=lambda skill_type, score, conf, evidence, grade: SkillReasoning(
                skill_type=skill_type,
                score=score,
                reasoning="Test reasoning",
                strengths=["Strength 1", "Strength 2"],
                growth_suggestions=["Suggestion 1", "Suggestion 2"],
            ),
        ):
            results = await service.generate_all_reasoning(
                skill_scores, student_grade=3
            )

            assert len(results) == 2
            assert SkillType.EMPATHY in results
            assert SkillType.PROBLEM_SOLVING in results
            assert all(isinstance(r, SkillReasoning) for r in results.values())

    def test_growth_oriented_language(self, service, sample_evidence):
        """Test that fallback reasoning uses growth-oriented language."""
        reasoning = service._generate_fallback_reasoning(
            SkillType.EMPATHY, 0.60, sample_evidence
        )

        # Should not use deficit language
        forbidden_words = ["poor", "weak", "failing", "inadequate", "lacking"]
        reasoning_lower = reasoning.reasoning.lower()

        for word in forbidden_words:
            assert word not in reasoning_lower, f"Reasoning should not contain '{word}'"

        # Should include growth suggestions
        assert len(reasoning.growth_suggestions) >= 2
        for suggestion in reasoning.growth_suggestions:
            assert len(suggestion) > 10  # Meaningful suggestions
