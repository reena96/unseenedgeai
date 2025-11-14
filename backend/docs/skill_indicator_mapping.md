# Skill Indicator Mapping

## Overview

This document maps specific game behaviors and choices to the 7 social-emotional skills we assess. Each skill has multiple behavioral indicators across the 3 game missions.

---

## The 7 Skills

1. **Empathy** - Understanding and sharing others' feelings
2. **Adaptability** - Adjusting to new situations and changes
3. **Problem-Solving** - Finding effective solutions to challenges
4. **Self-Regulation** - Managing emotions and impulses
5. **Resilience** - Recovering from setbacks and persisting
6. **Communication** - Expressing ideas clearly and listening
7. **Collaboration** - Working effectively with others

---

## Mission 1: Understanding Perspectives

### Primary Skills: Empathy, Communication

#### Empathy Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Empathetic dialogue choices | High empathy | 0.35 | `empathy_choices / total_choices` |
| Re-reading emotional dialogue | Attention to emotions | 0.20 | `min(reread_count / 3, 1.0)` |
| Deliberation time on emotional choices | Thoughtfulness | 0.15 | Sigmoid(`time`, optimal=8s) |
| Help requests for understanding emotions | Self-awareness | 0.15 | `help_requests / choice_points` |
| Avoidance of dismissive responses | Sensitivity | 0.15 | `1 - (dismissive_choices / total_choices)` |

**Empathy Score Calculation:**
```python
empathy_score = (
    0.35 * (empathy_choices / total_choices) +
    0.20 * min(reread_count / 3, 1.0) +
    0.15 * sigmoid(avg_deliberation_time, optimal=8) +
    0.15 * (help_requests / choice_points) +
    0.15 * (1 - dismissive_choices / total_choices)
)
```

#### Communication Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Clear expression in choices | Clarity | 0.30 | Manual rating of choices (1-4 scale) |
| Listening (not skipping dialogue) | Active listening | 0.25 | `1 - (skipped_dialogues / total_dialogues)` |
| Asking clarifying questions | Engagement | 0.25 | `clarifying_questions / opportunities` |
| Appropriate response timing | Pacing | 0.20 | Sigmoid(`response_time`, optimal=6s) |

---

## Mission 2: The Group Project Challenge

### Primary Skills: Collaboration, Problem-Solving

#### Collaboration Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Fair task delegation | Equity | 0.30 | `1 - stddev(tasks_per_person) / mean` |
| Voluntary turn-taking | Generosity | 0.20 | `voluntary_turns / total_turns` |
| Collaborative conflict resolution | Win-win approach | 0.25 | `win_win_resolutions / total_conflicts` |
| Inclusive resource allocation | Fairness | 0.15 | Gini coefficient (inverted) |
| Seeking others' input | Openness | 0.10 | `input_requests / decisions` |

**Collaboration Score Calculation:**
```python
collaboration_score = (
    0.30 * (1 - std_dev(tasks) / mean(tasks)) +
    0.20 * (voluntary_turns / total_turns) +
    0.25 * (win_win_resolutions / total_conflicts) +
    0.15 * (1 - gini_coefficient(resources)) +
    0.10 * (input_requests / decisions)
)
```

#### Problem-Solving Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Systematic planning approach | Organization | 0.30 | Binary (systematic=1, random=0) |
| Resource allocation efficiency | Optimization | 0.25 | `actual_outcome / optimal_outcome` |
| Strategy adaptation when stuck | Flexibility | 0.25 | `strategy_changes / obstacles` |
| Mini-game score | Applied skills | 0.20 | `game_score / max_score` |

---

## Mission 3: The Unexpected Change

### Primary Skills: Adaptability, Resilience

#### Adaptability Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Positive initial reaction to setbacks | Acceptance | 0.25 | Binary (acceptance=1, panic=0) |
| Speed of strategy switching | Agility | 0.30 | `1 / (switch_time_seconds / 30)` |
| Willingness to try new approaches | Openness | 0.25 | `unique_strategies / attempts` |
| Recovery time after setbacks | Speed | 0.20 | `1 / (recovery_seconds / 60)` |

**Adaptability Score Calculation:**
```python
adaptability_score = (
    0.25 * (positive_reactions / total_setbacks) +
    0.30 * (1 / (avg_switch_time / 30)) +
    0.25 * (unique_strategies / attempts) +
    0.20 * (1 / (avg_recovery_time / 60))
)
```

#### Resilience Indicators

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Retry attempts after failure | Persistence | 0.35 | `min(retries / 3, 1.0)` |
| Emotional regulation speed | Self-control | 0.25 | `1 / (regulation_seconds / 10)` |
| Help-seeking when stuck | Resourcefulness | 0.20 | Binary (sought_help=1, didn't=0) |
| Task completion after setbacks | Determination | 0.20 | `completed_tasks / attempted_tasks` |

**Resilience Score Calculation:**
```python
resilience_score = (
    0.35 * min(avg_retries / 3, 1.0) +
    0.25 * (1 / (avg_regulation_time / 10)) +
    0.20 * (help_sought_when_stuck / times_stuck) +
    0.20 * (tasks_completed / tasks_attempted)
)
```

---

## Cross-Mission Indicators

### Self-Regulation (All Missions)

| Game Behavior | Indicator | Weight | Score Formula |
|---------------|-----------|--------|---------------|
| Thoughtful deliberation (not impulsive) | Impulse control | 0.30 | Sigmoid(`avg_choice_time`, optimal=7s) |
| Managing frustration after failure | Emotional control | 0.30 | `positive_reactions / failures` |
| Completing missions without abandoning | Follow-through | 0.20 | `completed_missions / started_missions` |
| Low distraction rate | Focus | 0.20 | `1 - (distractions / total_time_minutes)` |

---

## Behavioral Feature Extraction

### From Mission 1 Events → Empathy Features

```python
def extract_empathy_features(events):
    """Extract empathy-related features from Mission 1 telemetry."""

    empathy_choices = count_choices_by_alignment(events, "empathy")
    total_choices = count_events(events, "choice_made")
    reread_count = sum_event_field(events, "dialogue_viewed", "reread_count")
    avg_deliberation = mean_event_field(events, "choice_made", "deliberation_time_ms")
    help_requests = count_events(events, "help_requested", context="emotion")

    return {
        "empathy_choice_ratio": empathy_choices / total_choices,
        "emotional_attention": min(reread_count / 3, 1.0),
        "empathetic_deliberation": sigmoid(avg_deliberation / 1000, optimal=8),
        "help_seeking_empathy": help_requests / total_choices,
        "dismissive_avoidance": 1 - (count_dismissive_choices(events) / total_choices)
    }
```

### From Mission 2 Events → Collaboration Features

```python
def extract_collaboration_features(events):
    """Extract collaboration-related features from Mission 2 telemetry."""

    delegation_events = filter_events(events, "task_delegated")
    tasks_per_person = group_by_assignee(delegation_events)
    voluntary_turns = count_events(events, "turn_taken", turn_type="voluntary")
    total_turns = count_events(events, "turn_taken")

    return {
        "delegation_fairness": 1 - (np.std(tasks_per_person) / np.mean(tasks_per_person)),
        "voluntary_turn_ratio": voluntary_turns / total_turns,
        "win_win_resolution_rate": count_win_win_resolutions(events) / count_conflicts(events),
        "resource_fairness": 1 - calculate_gini(get_resource_allocations(events)),
        "input_seeking_rate": count_input_requests(events) / count_decisions(events)
    }
```

### From Mission 3 Events → Resilience Features

```python
def extract_resilience_features(events):
    """Extract resilience-related features from Mission 3 telemetry."""

    failures = filter_events(events, "failure_occurred")
    retries = filter_events(events, "retry_attempted")
    setbacks = filter_events(events, "setback_encountered")
    recoveries = filter_events(events, "recovery_achieved")

    return {
        "persistence_score": min(len(retries) / (len(failures) * 0.75), 1.0),
        "recovery_speed": 1 / (mean_recovery_time_seconds(recoveries) / 60),
        "emotional_regulation": 1 / (mean_regulation_time_seconds(events) / 10),
        "help_seeking_resilience": count_help_when_stuck(events) / len(setbacks),
        "completion_after_setback": count_completions_after_setback(events) / len(setbacks)
    }
```

---

## Skill-Specific Choice Mappings

### Empathy Choices (Mission 1)

| Choice Point | Empathetic Option | Self-Focused Option | Neutral Option |
|--------------|-------------------|---------------------|----------------|
| CP 1.1 | "I notice you seem worried. Want to talk?" | "Everyone gets stressed. It's fine." | "What's up?" |
| CP 1.2 | "That sounds really hard for you." | "Just don't think about it." | "Okay." |
| CP 1.3 | "How can I help you feel better?" | "You'll get over it." | "Let me know if you need anything." |
| CP 1.4 | "I understand why you'd feel that way." | "You're overreacting a bit." | "I see." |
| CP 1.5 | "Your feelings are valid." | "There are worse problems." | "Thanks for sharing." |

### Collaboration Choices (Mission 2)

| Choice Point | Collaborative Option | Autocratic Option | Avoidant Option |
|--------------|---------------------|-------------------|----------------|
| CP 2.1 | "Let's decide together who does what." | "I'll assign everyone their tasks." | "Someone else can decide." |
| CP 2.2 | "Sam, what do you think we should do?" | "I already know what we should do." | "Whatever works." |
| CP 2.3 | "Let's compromise and combine our ideas." | "My way is better, trust me." | "I don't really care." |
| CP 2.4 | "Jordan, I value your input on this." | "Jordan, just do what I say." | "Jordan can do whatever." |
| CP 2.5 | "We all contributed equally to this." | "I did most of the work honestly." | "I guess we did okay." |

### Adaptability Choices (Mission 3)

| Choice Point | Adaptive Option | Rigid Option | Avoidant Option |
|--------------|-----------------|--------------|----------------|
| CP 3.1 | "Okay, let's adjust our plan for this." | "No! We're sticking to the original plan." | "I give up." |
| CP 3.2 | "Let's try a completely different approach." | "We'll keep doing it the same way." | "Maybe it'll just work out." |
| CP 3.3 | "This is a chance to make it even better!" | "This is ruining everything!" | "Whatever happens, happens." |
| CP 3.4 | "I'll ask Maya for advice on how to adapt." | "I don't need help, I'll force this to work." | "I'll just wait and see." |

---

## Validation Criteria

### Indicator Quality Checks

For each indicator, we validate:

1. **Range:** All scores must be [0.0, 1.0]
2. **Distribution:** Scores should approximate normal distribution (mean ~0.5, sd ~0.2)
3. **Correlation:** Indicators for same skill should correlate (r > 0.3)
4. **Discrimination:** High vs Low skill students should differ significantly (Cohen's d > 0.5)
5. **Reliability:** Test-retest reliability (r > 0.70) for repeated plays

### Example Validation Results

```python
{
    "empathy_choice_ratio": {
        "range": [0.0, 1.0],  # ✓
        "mean": 0.52,  # ✓
        "std_dev": 0.22,  # ✓
        "internal_consistency": 0.78,  # ✓ (Cronbach's alpha)
        "test_retest": 0.74  # ✓
    },
    "collaboration_fairness": {
        "range": [0.12, 0.98],  # ✓
        "mean": 0.58,  # ✓
        "std_dev": 0.19,  # ✓
        "internal_consistency": 0.82,  # ✓
        "test_retest": 0.71  # ✓
    }
}
```

---

## Feature Engineering Pipeline

### Step 1: Raw Event Extraction
```
Telemetry Events (JSON)
   → Parse by mission
   → Filter by event_type
   → Extract event_data fields
```

### Step 2: Behavioral Aggregation
```
Raw Fields
   → Count occurrences
   → Calculate ratios
   → Compute averages
   → Derive composites
```

### Step 3: Feature Normalization
```
Raw Scores
   → Min-max normalization [0, 1]
   → Z-score standardization
   → Sigmoid transformation
   → Percentile ranking
```

### Step 4: Skill Score Calculation
```
Normalized Features
   → Apply weights
   → Sum weighted features
   → Clip to [0, 1]
   → Generate confidence intervals
```

---

## Implementation Notes

- **Real-time Processing:** Features extracted on mission completion
- **Batch Processing:** Aggregates recalculated daily for all students
- **Storage:** Features stored in `extracted_features` table
- **Privacy:** Behavioral patterns anonymized, no video/audio stored

---

## Versioning

- **Version:** 1.0
- **Last Updated:** 2025-01-14
- **Dependencies:** game_telemetry_specification.md v1.0
