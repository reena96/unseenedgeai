# Game Telemetry Specification v1.0

## Overview

This document defines the telemetry event schema for the 3-mission social-emotional learning game. Each mission targets specific skills and generates telemetry events that capture student behavior and decision-making patterns.

## Missions Overview

1. **Mission 1: Understanding Perspectives** - Empathy + Communication
2. **Mission 2: The Group Project Challenge** - Collaboration + Problem-Solving
3. **Mission 3: The Unexpected Change** - Adaptability + Resilience

---

## Event Structure

All telemetry events follow this base schema:

```json
{
  "event_id": "uuid",
  "student_id": "string",
  "session_id": "uuid",
  "mission_id": "1|2|3",
  "timestamp": "ISO8601",
  "event_type": "string",
  "event_data": {}
}
```

---

## Mission 1: Understanding Perspectives (Empathy)

### Targeted Skills
- **Primary:** Empathy, Communication
- **Secondary:** Self-regulation

### Event Types

#### 1.1 `mission_started`
```json
{
  "event_type": "mission_started",
  "event_data": {
    "mission_id": 1,
    "mission_name": "Understanding Perspectives",
    "student_grade": 6
  }
}
```

#### 1.2 `dialogue_viewed`
```json
{
  "event_type": "dialogue_viewed",
  "event_data": {
    "dialogue_id": "string",
    "character": "alex|maya",
    "emotional_state": "happy|sad|anxious|isolated|hopeful",
    "text_content": "string",
    "view_duration_ms": 5000,
    "reread_count": 0
  }
}
```

#### 1.3 `choice_presented`
```json
{
  "event_type": "choice_presented",
  "event_data": {
    "choice_point_id": "cp_1_1",
    "prompt": "Alex seems upset. What do you say?",
    "options": [
      {
        "option_id": "opt_1_empathetic",
        "text": "I notice you seem worried. Want to talk about it?",
        "skill_alignment": "empathy"
      },
      {
        "option_id": "opt_1_dismissive",
        "text": "Everyone gets stressed sometimes. It's not a big deal.",
        "skill_alignment": "self_focused"
      }
    ],
    "time_to_present_ms": 1200
  }
}
```

#### 1.4 `choice_made`
```json
{
  "event_type": "choice_made",
  "event_data": {
    "choice_point_id": "cp_1_1",
    "selected_option_id": "opt_1_empathetic",
    "skill_alignment": "empathy",
    "deliberation_time_ms": 8500,
    "changed_mind_count": 0
  }
}
```

#### 1.5 `help_requested`
```json
{
  "event_type": "help_requested",
  "event_data": {
    "context": "choice_point_1",
    "help_type": "hint|explanation|skip",
    "timestamp_in_mission_ms": 45000
  }
}
```

#### 1.6 `dialogue_skipped`
```json
{
  "event_type": "dialogue_skipped",
  "event_data": {
    "dialogue_id": "string",
    "skip_reason": "user_initiated|timeout",
    "time_before_skip_ms": 2000
  }
}
```

#### 1.7 `mission_completed`
```json
{
  "event_type": "mission_completed",
  "event_data": {
    "mission_id": 1,
    "total_duration_ms": 720000,
    "empathy_choices": 4,
    "self_focused_choices": 1,
    "help_requests": 1,
    "completion_status": "completed|abandoned"
  }
}
```

### Skill Indicators - Mission 1

| Behavior | Indicates High Empathy | Indicates Low Empathy |
|----------|----------------------|----------------------|
| Choice alignment | >60% empathetic responses | <40% empathetic responses |
| Deliberation time | 5-15 seconds (thoughtful) | <3 seconds (impulsive) |
| Re-reading dialogue | 2+ re-reads of emotional cues | 0 re-reads |
| Help-seeking | Asks for help understanding emotions | Rarely asks for help |

---

## Mission 2: The Group Project Challenge (Collaboration + Problem-Solving)

### Targeted Skills
- **Primary:** Collaboration, Problem-Solving
- **Secondary:** Communication, Self-regulation

### Event Types

#### 2.1 `mission_started`
```json
{
  "event_type": "mission_started",
  "event_data": {
    "mission_id": 2,
    "mission_name": "Group Project Challenge",
    "team_members": ["jordan", "sam", "player"]
  }
}
```

#### 2.2 `task_delegated`
```json
{
  "event_type": "task_delegated",
  "event_data": {
    "task_id": "research_task",
    "assigned_to": "sam",
    "task_difficulty": "easy|medium|hard",
    "delegation_strategy": "fair|autocratic|collaborative",
    "consideration_time_ms": 6000
  }
}
```

#### 2.3 `resource_allocated`
```json
{
  "event_type": "resource_allocated",
  "event_data": {
    "resource_type": "time|materials|team_member",
    "amount": 30,
    "allocated_to": "research_phase",
    "rationale": "systematic|random|intuitive"
  }
}
```

#### 2.4 `conflict_encountered`
```json
{
  "event_type": "conflict_encountered",
  "event_data": {
    "conflict_type": "task_disagreement|personality_clash|resource_dispute",
    "characters_involved": ["jordan", "sam"],
    "conflict_description": "Jordan wants to do all the work alone"
  }
}
```

#### 2.5 `conflict_resolved`
```json
{
  "event_type": "conflict_resolved",
  "event_data": {
    "conflict_id": "conf_2_1",
    "resolution_approach": "compromise|avoidance|collaboration|domination",
    "time_to_resolve_ms": 45000,
    "outcome_quality": "win_win|win_lose|lose_lose"
  }
}
```

#### 2.6 `turn_taken`
```json
{
  "event_type": "turn_taken",
  "event_data": {
    "turn_giver": "player",
    "turn_receiver": "sam",
    "turn_type": "voluntary|prompted",
    "fairness_score": 0.85
  }
}
```

#### 2.7 `mini_game_started`
```json
{
  "event_type": "mini_game_started",
  "event_data": {
    "game_type": "resource_allocation",
    "difficulty": "medium",
    "available_resources": {
      "time": 100,
      "materials": 50,
      "team_members": 3
    }
  }
}
```

#### 2.8 `mini_game_completed`
```json
{
  "event_type": "mini_game_completed",
  "event_data": {
    "game_type": "resource_allocation",
    "score": 85,
    "efficiency": 0.78,
    "fairness": 0.92,
    "completion_time_ms": 120000
  }
}
```

#### 2.9 `mission_completed`
```json
{
  "event_type": "mission_completed",
  "event_data": {
    "mission_id": 2,
    "total_duration_ms": 900000,
    "collaboration_score": 0.82,
    "problem_solving_score": 0.75,
    "tasks_completed": 7,
    "conflicts_resolved": 2,
    "delegation_fairness": 0.88
  }
}
```

### Skill Indicators - Mission 2

| Behavior | Indicates High Collaboration | Indicates Low Collaboration |
|----------|----------------------------|----------------------------|
| Delegation strategy | Fair distribution of tasks | Autocratic or self-centered |
| Turn-taking | Voluntary turn-giving | Only when prompted |
| Conflict resolution | Collaborative, win-win | Avoidance or domination |
| Resource allocation | Considers team needs | Self-focused allocation |

| Behavior | Indicates High Problem-Solving | Indicates Low Problem-Solving |
|----------|------------------------------|------------------------------|
| Planning approach | Systematic, organized | Random, chaotic |
| Resource efficiency | High efficiency (>0.75) | Low efficiency (<0.50) |
| Adaptation | Adjusts plan when needed | Rigid, doesn't adapt |

---

## Mission 3: The Unexpected Change (Adaptability + Resilience)

### Targeted Skills
- **Primary:** Adaptability, Resilience
- **Secondary:** Self-regulation, Problem-Solving

### Event Types

#### 3.1 `mission_started`
```json
{
  "event_type": "mission_started",
  "event_data": {
    "mission_id": 3,
    "mission_name": "The Unexpected Change",
    "initial_plan": "Complete group presentation"
  }
}
```

#### 3.2 `setback_encountered`
```json
{
  "event_type": "setback_encountered",
  "event_data": {
    "setback_type": "requirements_changed|member_left|time_reduced|resources_lost",
    "severity": "minor|moderate|major",
    "description": "Project requirements changed - must add new section",
    "timestamp_in_mission_ms": 180000
  }
}
```

#### 3.3 `initial_reaction`
```json
{
  "event_type": "initial_reaction",
  "event_data": {
    "setback_id": "setback_3_1",
    "reaction_type": "panic|frustration|acceptance|problem_solving",
    "emotional_regulation_time_ms": 5000,
    "negative_self_talk": false
  }
}
```

#### 3.4 `strategy_switched`
```json
{
  "event_type": "strategy_switched",
  "event_data": {
    "old_strategy": "work_alone",
    "new_strategy": "seek_help",
    "switch_reason": "previous_failed|proactive|suggested",
    "switch_speed_ms": 30000
  }
}
```

#### 3.5 `failure_occurred`
```json
{
  "event_type": "failure_occurred",
  "event_data": {
    "failure_type": "task_failed|time_expired|wrong_approach",
    "attempt_number": 2,
    "task_id": "presentation_section_1"
  }
}
```

#### 3.6 `retry_attempted`
```json
{
  "event_type": "retry_attempted",
  "event_data": {
    "task_id": "presentation_section_1",
    "retry_number": 2,
    "time_before_retry_ms": 8000,
    "strategy_changed": true,
    "persistence_indicator": 0.85
  }
}
```

#### 3.7 `help_sought`
```json
{
  "event_type": "help_sought",
  "event_data": {
    "help_source": "mentor_maya|peer|hint_system",
    "help_type": "emotional|strategic|informational",
    "time_before_seeking_ms": 25000,
    "self_advocacy_quality": "clear|vague"
  }
}
```

#### 3.8 `recovery_achieved`
```json
{
  "event_type": "recovery_achieved",
  "event_data": {
    "setback_id": "setback_3_1",
    "time_to_recover_ms": 120000,
    "recovery_strategy": "problem_solving|help_seeking|persistence|adaptation",
    "success_level": "full|partial|minimal"
  }
}
```

#### 3.9 `mission_completed`
```json
{
  "event_type": "mission_completed",
  "event_data": {
    "mission_id": 3,
    "total_duration_ms": 850000,
    "setbacks_encountered": 3,
    "setbacks_overcome": 2,
    "failures": 4,
    "retries": 5,
    "adaptability_score": 0.78,
    "resilience_score": 0.82,
    "recovery_time_avg_ms": 95000
  }
}
```

### Skill Indicators - Mission 3

| Behavior | Indicates High Adaptability | Indicates Low Adaptability |
|----------|---------------------------|---------------------------|
| Initial reaction | Acceptance, problem-solving | Panic, frustration |
| Strategy switching | Quick, proactive switches | Rigid, resists change |
| Flexibility | Tries multiple approaches | Repeats failed approach |

| Behavior | Indicates High Resilience | Indicates Low Resilience |
|----------|-------------------------|-------------------------|
| Persistence after failure | Retries 3+ times | Gives up after 1 failure |
| Recovery time | <60 seconds | >180 seconds |
| Help-seeking | Seeks help appropriately | Refuses help or delays |
| Emotional regulation | Manages frustration quickly | Prolonged negative reactions |

---

## Aggregated Telemetry Metrics

### Per-Mission Metrics

These metrics are calculated from raw events:

```json
{
  "student_id": "string",
  "mission_id": 1,
  "metrics": {
    "completion_rate": 1.0,
    "total_duration_ms": 720000,
    "empathy_choice_ratio": 0.80,
    "help_request_count": 1,
    "dialogue_reread_count": 3,
    "deliberation_time_avg_ms": 7500,
    "skill_aligned_choices": 4,
    "skill_misaligned_choices": 1
  }
}
```

### Cross-Mission Aggregates

```json
{
  "student_id": "string",
  "all_missions": {
    "missions_completed": 3,
    "total_playtime_ms": 2470000,
    "avg_completion_rate": 0.95,
    "empathy_score": 0.82,
    "collaboration_score": 0.78,
    "problem_solving_score": 0.75,
    "adaptability_score": 0.80,
    "resilience_score": 0.85,
    "self_regulation_score": 0.77,
    "communication_score": 0.81
  }
}
```

---

## Implementation Notes

### Event Storage

- Events stored in TimescaleDB `game_telemetry_events` hypertable
- Indexed by `student_id`, `session_id`, `timestamp`
- Retention: 2 years

### Event Processing Pipeline

1. **Ingestion** - Events received via POST `/api/v1/telemetry/events`
2. **Validation** - JSON schema validation against event type
3. **Storage** - Write to TimescaleDB
4. **Aggregation** - Calculate metrics every 5 minutes (materialized view)
5. **Feature Extraction** - Extract behavioral features for ML models

### Privacy & Security

- Student IDs anonymized using UUID
- Events encrypted at rest
- FERPA-compliant: No PII in event data
- Access restricted to authorized teachers/admins

---

## Versioning

- **Current Version:** 1.0
- **Last Updated:** 2025-01-14
- **Breaking Changes:** None
- **Backward Compatibility:** N/A (first version)

---

## Appendix: Event Type Summary

| Mission | Event Types | Total Events |
|---------|-------------|--------------|
| Mission 1 | 7 types | ~15-25 events per playthrough |
| Mission 2 | 9 types | ~25-40 events per playthrough |
| Mission 3 | 9 types | ~30-50 events per playthrough |

**Total Expected Events per Student:** 70-115 events across all 3 missions
