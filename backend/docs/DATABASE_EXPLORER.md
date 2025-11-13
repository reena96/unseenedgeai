# Database Explorer - See Your Data

**Current Database**: Enhanced seed data (seed_data_enhanced.py)
**Total Records**: 12 students, 30 transcripts, 39 game sessions, 686 events

This document shows you exactly what's in your database right now.

---

## 📊 Overview

```
Students:        12 (grades 2-8)
Audio Files:     30
Transcripts:     30 (100% transcribed)
Game Sessions:   39
Telemetry:       686 events
Skill Tests:     48 assessments
```

---

## 👤 Sample Student Records

### Emma Wilson (Grade 2)
**Student ID**: STU00001

#### 🎤 Audio Files (2):

**Recording 1** (Nov 10, 2025):
- Duration: 11.4 seconds
- Size: 218,352 bytes
- Context: Presentation
- Storage: `gs://mass-audio-dev/31036060-258f-4fb9-9039-44f6a1...`

**Transcript**:
```
"I got a spelling word wrong, but I practiced it five more times
until I could spell it correctly every time."

Word Count: 21 words
Confidence: 94.6%
Language: en-US
```

**Recording 2** (Nov 10, 2025):
- Duration: 5.0 seconds
- Size: 96,000 bytes
- Context: Classroom
- Storage: `gs://mass-audio-dev/31036060-258f-4fb9-9039-44f6a1...`

**Transcript**:
```
"I tried to learn from my mistakes."

Word Count: 7 words
Confidence: 93.6%
Language: en-US
```

---

### Liam Anderson (Grade 3)
**Student ID**: STU00002

#### 🎤 Audio Files (3):

**Recording 1**:
```
"I didn't give up on the assignment."
7 words, 95.4% confidence
```

**Recording 2**:
```
"I finished my work even though it was hard."
9 words, 92.1% confidence
```

**Recording 3**:
```
"When I got a critique on my work, I took time to process it
before responding."
16 words, 94.6% confidence
```

---

### Noah Garcia (Grade 4)
**Student ID**: STU00004

#### 🎤 Audio Files (3):

**Recording 1** - Essay feedback response:
```
"I was disappointed with my essay grade, but I used the feedback
to improve my writing on the next assignment."
20 words, 88.8% confidence
```

**Recording 2** - Problem-solving:
```
"Our group project wasn't working because everyone had different ideas.
I suggested we write down all the ideas, then vote on the best parts
of each one to combine them."
30 words, 95.8% confidence
```

**Recording 3** - Empathy:
```
"I noticed that Maya was sitting alone at lunch, so I invited her to
sit with our group. She seemed really happy about it."
24 words, 91.8% confidence
```

---

## 🎮 Game Session Examples

### Emma Wilson (Grade 2) - Session 1

**Mission**: vocabulary_builder_3
**Duration**: 41 minutes
**Version**: 2.1.4
**Started**: Nov 12, 2025, 9:58 PM

#### Telemetry Events (sample):
```
[0.0s]    level_complete
          → Level 1, Score: 76, Time: 60.4s

[180.4s]  level_complete
          → Level 3, Score: 60, Time: 176.6s

[205.2s]  navigation
          → Player moved around

[323.1s]  hint_requested
          → Asked for hint level 1 after 25s

[626.3s]  item_collected
          → Picked up in-game item
```

---

### Emma Wilson (Grade 2) - Session 2

**Mission**: vocabulary_builder_3
**Duration**: 32 minutes
**Started**: Oct 27, 2025, 8:58 PM

#### Telemetry Events (sample):
```
[0.0s]    hint_requested
          → Hint level 2 after 6.5s (quick help-seeking)

[2.1s]    level_complete
          → Level 5, Score: 95, Time: 93.2s (excellent!)

[119.3s]  incorrect_answer
          → Question q_554, took 24.2s, 1 attempt

[281.1s]  correct_answer
          → Question q_707, took 4.5s, 1 attempt (fast!)

[477.5s]  navigation
          → Exploring game environment
```

---

### Liam Anderson (Grade 3) - Session 1

**Mission**: science_exploration_1
**Duration**: 13 minutes
**Started**: Nov 9, 2025, 9:58 PM

#### Telemetry Events (sample):
```
[60.2s]   level_complete
          → Level 7, Score: 64, Time: 250.7s (struggled)

[79.5s]   incorrect_answer
          → Question q_201, took 21.8s, 3 attempts (difficult)

[82.3s]   hint_requested
          → Asked for hint after struggling

[172.6s]  incorrect_answer
          → Question q_481, took 15.1s, 3 attempts

[225.6s]  hint_requested
          → Hint level 2 after 18.9s (persistence!)
```

**Pattern**: This student struggled but kept trying and used hints appropriately! Shows resilience.

---

### Sophia Martinez (Grade 3) - Session

**Mission**: reading_comprehension_1
**Duration**: 32 minutes

#### Telemetry Events (sample):
```
[23.0s]   correct_answer
          → Question q_937, 3.9s, 1 attempt (quick & right!)

[293.0s]  correct_answer
          → Question q_762, 4.1s, 1 attempt

[303.6s]  item_collected
          → Game progression

[523.4s]  incorrect_answer
          → Question q_394, 15.6s, 3 attempts (harder question)

[582.1s]  incorrect_answer
          → Question q_329, 23.3s, 2 attempts
```

**Pattern**: Started strong, then hit harder questions. Realistic learning curve!

---

## 📈 Data Variety Showcase

### Word Count Distribution:
```
5 words:   "I followed the class rules."
7 words:   "I didn't quit when it got hard."
9 words:   "I finished my work even though it was hard."
16 words:  "When I got a critique on my work..."
20 words:  "I was disappointed with my essay grade..."
24 words:  "I noticed that Maya was sitting alone..."
26 words:  "I was frustrated with my essay draft..."
30 words:  "Our group project wasn't working because..."
```

**Range**: 5-30 words (realistic variation!)

---

### Confidence Scores:
```
88.8% - Lower confidence (complex speech)
91.8% - Good confidence
93.6% - High confidence
94.6% - Very high confidence
95.4% - Excellent confidence
97.5% - Nearly perfect
```

**Range**: 88-98% (realistic for good audio quality)

---

### Recording Contexts:
```
• classroom     - Regular classroom discussion
• presentation  - Student presenting
• one_on_one    - Individual interview
• group_work    - Collaborative project
```

---

### Game Event Types (686 total):
```
item_collected:     107 events (15.6%)
incorrect_answer:   105 events (15.3%)
question_attempt:   103 events (15.0%)
correct_answer:      94 events (13.7%)
hint_requested:      94 events (13.7%)
navigation:          93 events (13.6%)
level_complete:      90 events (13.1%)
```

**Even distribution** = realistic gameplay!

---

## 🔍 How to Query Your Data

### See All Students:
```bash
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.student import Student

async def list_students():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        result = await session.execute(select(Student))
        for student in result.scalars():
            print(f'{student.first_name} {student.last_name} (Grade {student.grade_level})')
        await engine.dispose()

asyncio.run(list_students())
"
```

---

### See All Transcripts for a Student:
```bash
python -c "
# (Include student_id)
# Query Transcript table filtering by student_id
# Show text, word_count, confidence_score
"
```

---

### See Game Performance:
```bash
python -c "
# Query GameSession + GameTelemetry
# Calculate: correct/incorrect ratio, hint usage, completion rate
"
```

---

## 💾 Database Schema Overview

```
┌─────────────┐
│  Students   │
│  (12)       │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
┌──────▼─────┐    ┌─────▼──────┐
│ Audio      │    │  Game      │
│ Files      │    │  Sessions  │
│ (30)       │    │  (39)      │
└──────┬─────┘    └─────┬──────┘
       │                │
┌──────▼─────┐    ┌─────▼──────┐
│ Transcripts│    │ Telemetry  │
│ (30)       │    │ (686)      │
└────────────┘    └────────────┘
       │                │
       └────────┬───────┘
                │
       ┌────────▼────────┐
       │   Linguistic    │
       │   Features      │
       │   (extracted)   │
       └─────────────────┘
                │
       ┌────────▼────────┐
       │   Behavioral    │
       │   Features      │
       │   (extracted)   │
       └─────────────────┘
                │
       ┌────────▼────────┐
       │      Skill      │
       │   Assessments   │
       │      (48)       │
       └─────────────────┘
```

---

## 🎯 Key Observations

### Realistic Patterns:

1. **Varied Performance**: Some students get questions right quickly, others struggle
2. **Help-Seeking Behavior**: Hint requests happen naturally when stuck
3. **Persistence**: Multiple attempts on hard questions
4. **Time Variation**: Response times range from 3s to 25s
5. **Skill Progression**: Level completions show learning curves

### Grade-Appropriate Language:

- **Grade 2**: Simple, short sentences (7-21 words)
- **Grade 3**: More complex thoughts (9-26 words)
- **Grade 4**: Sophisticated reasoning (20-30 words)

### Authentic Contexts:

- **Empathy**: "I noticed Maya was sitting alone..."
- **Problem-solving**: "Our group project wasn't working..."
- **Resilience**: "I didn't quit when it got hard."
- **Self-regulation**: "I took time to process it before responding."

---

## 📊 Summary Statistics

```
Total Records:
├── 12 Students (grades 2-8)
├── 30 Audio Files (5-14s duration each)
├── 30 Transcripts (5-30 words each)
├── 39 Game Sessions (10-45 min each)
├── 686 Telemetry Events (7 types)
└── 48 Skill Assessments (4 skills × 12 students)

Data Quality:
├── Transcription: 88-98% confidence (realistic)
├── Word Count: 5-30 words (age-appropriate)
├── Event Types: 7 types evenly distributed
└── Behaviors: Help-seeking, persistence, success/failure

Skill Coverage:
├── Empathy: 12 assessments (avg 0.62)
├── Problem-solving: 12 assessments (avg 0.58)
├── Self-regulation: 12 assessments (avg 0.57)
└── Resilience: 12 assessments (avg 0.58)
```

---

## 🚀 Next Steps

### Explore Your Data:
```bash
# See everything
python -c "..." # (use query examples above)

# Test feature extraction
bash test_features.sh

# Run API and browse
uvicorn app.main:app --reload
# Visit: http://localhost:8000/api/v1/docs
```

### Analyze Patterns:
- Compare Grade 2 vs Grade 4 language complexity
- Look for correlation between hint usage and resilience scores
- Identify struggling vs. thriving students from game data

### Validate AI Models:
- Extract features from all 30 transcripts
- Compare linguistic features across grade levels
- Test if behavioral patterns correlate with skill assessments

---

**Bottom Line**: You have **real, diverse, production-quality synthetic data** ready for meaningful AI development and testing! 🎉
