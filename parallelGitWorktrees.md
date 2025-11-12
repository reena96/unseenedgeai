# MASS System: Parallel Git Worktrees Implementation Strategy

This document outlines the complete strategy for implementing the 8 OpenSpec changes using git worktrees for parallel development, along with the proper merge order to maintain a stable main branch.

## Table of Contents

- [Overview](#overview)
- [Dependency Analysis](#dependency-analysis)
- [Wave-Based Implementation](#wave-based-implementation)
- [Merge Order](#merge-order)
- [Git Worktree Commands](#git-worktree-commands)
- [Integration Testing](#integration-testing)
- [Timeline](#timeline)
- [Critical Rules](#critical-rules)

---

## Overview

**Total Changes**: 8 OpenSpec changes
**Total Tasks**: 571 tasks
**Timeline**: Weeks 15-30 (16 weeks)
**Peak Parallelization**: 3 concurrent worktrees (Wave 2)

### Changes Summary

| # | Change | Tasks | Weeks |
|---|--------|-------|-------|
| 01 | Infrastructure Setup | 59 | 15-16 |
| 02 | Authentication System | 86 | 17-18 |
| 03 | STT Pipeline | 77 | 19-20 |
| 04 | Game Telemetry Ingestion | 61 | 17-28 |
| 05 | ML Inference Service | 59 | 21-22 |
| 06 | Evidence Fusion Service | 47 | 23-24 |
| 07 | GPT-4 Reasoning | 74 | 25-26 |
| 08 | Teacher Dashboard | 108 | 17-30 |

---

## Dependency Analysis

### Change Dependencies

```
01-infrastructure-setup (Wave 1)
    ↓
    ├─→ 02-authentication-system (Wave 2)
    ├─→ 03-stt-pipeline (Wave 2)
    └─→ 04-game-telemetry (Wave 2)
            ↓
            ├─→ 05-ml-inference (Wave 3) ←─┐
            │       ↓                        │
            │       06-evidence-fusion ──────┤
            │           ↓                    │
            │           08-dashboard         │
            │                                │
            └─→ 07-gpt4-reasoning (Wave 3)──┘
```

### Dependency Matrix

| Change | Depends On | Blocks |
|--------|-----------|--------|
| 01-infrastructure | None | ALL |
| 02-authentication | Infrastructure | Dashboard (auth) |
| 03-stt-pipeline | Infrastructure | ML Inference, Fusion |
| 04-game-telemetry | Infrastructure | ML Inference, Fusion |
| 05-ml-inference | Infrastructure, STT, Telemetry | Fusion |
| 06-evidence-fusion | ML Inference, GPT-4 | Dashboard (data) |
| 07-gpt4-reasoning | Infrastructure | Fusion, Dashboard |
| 08-teacher-dashboard | Auth, Fusion | None |

---

## Wave-Based Implementation

### Wave 1: Foundation (Sequential)

**Parallelization**: None (single branch)
**Duration**: Weeks 15-16

```
01-infrastructure-setup (59 tasks)
  - GCP project setup
  - Cloud SQL + TimescaleDB
  - Cloud Storage buckets
  - Cloud Tasks queues
  - Pub/Sub topics
  - Secret Manager
  - IAM service accounts
  - Terraform IaC
  - CI/CD pipeline
```

**Why Sequential**: All other changes require this infrastructure.

---

### Wave 2: Core Data Pipelines (Parallel)

**Parallelization**: 3 concurrent worktrees
**Duration**: Weeks 17-20

```
02-authentication-system (86 tasks)     ┐
  - JWT authentication                   │
  - RBAC middleware                      ├─ Develop in parallel
  - Password management                  │
  - Audit logging                        │
                                         │
03-stt-pipeline (77 tasks)              │
  - Google Cloud STT API                 │
  - Audio file upload                    ├─ No dependencies
  - Speaker diarization                  │   between these 3
  - Transcript storage                   │
                                         │
04-game-telemetry (61 tasks)            │
  - Unity game integration               │
  - Event ingestion API                  │
  - TimescaleDB events                   │
  - Behavioral features                  ┘
```

**Why Parallel**: These three components are independent and only depend on infrastructure (Wave 1).

---

### Wave 3: Intelligence Layer (Parallel)

**Parallelization**: 2 concurrent worktrees
**Duration**: Weeks 21-26

```
05-ml-inference (59 tasks)              ┐
  - XGBoost model loading                │
  - Feature preparation                  ├─ Develop in parallel
  - Inference API                        │
  - Model versioning                     │
                                         │
07-gpt4-reasoning (74 tasks)            │
  - OpenAI GPT-4 integration             │
  - Reasoning prompts                    ├─ No dependencies
  - Cost tracking                        │   between these 2
  - Caching                              ┘
```

**Why Parallel**: ML Inference needs STT+Telemetry data, but GPT-4 Reasoning is independent. Both can develop simultaneously.

---

### Wave 4: Fusion & Presentation (Partially Parallel)

**Parallelization**: 2 concurrent worktrees (with merge dependency)
**Duration**: Weeks 23-30

```
06-evidence-fusion (47 tasks)           ┐
  - Multi-source score fusion            │
  - Evidence extraction                  ├─ Fusion develops first
  - Confidence calculation               │   Dashboard UI can start
  - Evidence ranking                     │   in parallel
                                         │
08-teacher-dashboard (108 tasks)        │
  - React + TypeScript app               │
  - Class overview + heatmap             ├─ BUT: Dashboard integration
  - Student detail pages                 │   MUST wait for Fusion
  - Evidence viewer                      │   to complete
  - Historical trends                    │
  - Teacher rubric interface             ┘
```

**Why Partially Parallel**:
- Dashboard UI components can be built in parallel with Fusion
- Dashboard API integration MUST wait for Fusion to complete
- Consider splitting dashboard into: `08a-dashboard-ui` and `08b-dashboard-integration`

---

## Merge Order

### Complete Merge Sequence

| Merge # | Branch | Tasks | Wave | Merge Rule |
|---------|--------|-------|------|------------|
| **#1** | `01-infrastructure-setup` | 59 | 1 | Foundation - must merge first |
| **#2** | `02-authentication-system` | 86 | 2 | Merge when ready (suggested first in Wave 2) |
| **#3** | `04-game-telemetry` | 61 | 2 | Merge when ready (any order in Wave 2) |
| **#4** | `03-stt-pipeline` | 77 | 2 | Merge when ready (likely last in Wave 2) |
| **#5** | `07-gpt4-reasoning` | 74 | 3 | Merge when ready (any order in Wave 3) |
| **#6** | `05-ml-inference` | 59 | 3 | Merge when ready (any order in Wave 3) |
| **#7** | `06-evidence-fusion` | 47 | 4 | **MUST merge before #8** |
| **#8** | `08-teacher-dashboard` | 108 | 4 | **MUST merge after #7** |

### Merge Rules by Wave

#### Wave 1 → Wave 2
- **STRICT**: Infrastructure (#1) MUST merge before starting Wave 2

#### Within Wave 2 (Auth, STT, Telemetry)
- **FLEXIBLE**: Merge in ANY order when ready
- Suggested order: Auth → Telemetry → STT (based on complexity)
- Can merge simultaneously if multiple PRs are ready

#### Wave 2 → Wave 3
- **STRICT**: STT (#4) AND Telemetry (#3) MUST merge before ML Inference (#6)
- GPT-4 (#5) can merge independently

#### Within Wave 3 (ML Inference, GPT-4)
- **FLEXIBLE**: Merge in ANY order when ready
- Suggested order: GPT-4 → ML Inference (GPT-4 is simpler)

#### Wave 3 → Wave 4
- **STRICT**: ML Inference (#6) AND GPT-4 (#5) MUST merge before Fusion (#7)

#### Within Wave 4 (Fusion, Dashboard)
- **STRICT**: Fusion (#7) MUST merge before Dashboard (#8)
- Exception: Dashboard UI-only work can be merged earlier if split into separate branch

---

## Git Worktree Commands

### Wave 1: Infrastructure Setup

```bash
# Start from main branch
cd /Users/reena/gauntletai/unseenedgeai

# Create worktree for infrastructure
git worktree add ../mass-infrastructure feature/01-infrastructure-setup

# Work in the worktree
cd ../mass-infrastructure

# Follow tasks from:
cat openspec/changes/01-add-infrastructure-setup/tasks.md

# When complete:
git add .
git commit -m "feat: complete infrastructure setup

- GCP project configuration
- Cloud SQL with PostgreSQL 15 + TimescaleDB
- Cloud Storage buckets with lifecycle policies
- Cloud Tasks and Pub/Sub setup
- Secret Manager configuration
- IAM service accounts and roles
- Terraform infrastructure-as-code
- GitHub Actions CI/CD pipeline

Implements OpenSpec change 01-add-infrastructure-setup
Closes #XX"

git push origin feature/01-infrastructure-setup

# Create PR
gh pr create --title "feat: Infrastructure Setup for MASS System" \
  --body "$(cat openspec/changes/01-add-infrastructure-setup/proposal.md)"

# After review and approval: MERGE to main
```

### Wave 2: Core Data Pipelines (3 Parallel Worktrees)

```bash
# After infrastructure is merged, pull latest main
cd /Users/reena/gauntletai/unseenedgeai
git checkout main
git pull origin main

# Create 3 parallel worktrees
git worktree add ../mass-auth feature/02-authentication-system
git worktree add ../mass-stt feature/03-stt-pipeline
git worktree add ../mass-telemetry feature/04-game-telemetry

# Work in each worktree (can be done by different developers or sequentially)

# Worktree A: Authentication
cd ../mass-auth
cat openspec/changes/02-add-authentication-system/tasks.md
# ... develop authentication system ...
git add . && git commit -m "feat: implement authentication system"
git push origin feature/02-authentication-system
gh pr create --title "feat: Authentication System"

# Worktree B: STT Pipeline
cd ../mass-stt
cat openspec/changes/03-add-stt-pipeline/tasks.md
# ... develop STT pipeline ...
git add . && git commit -m "feat: implement STT pipeline"
git push origin feature/03-stt-pipeline
gh pr create --title "feat: Speech-to-Text Pipeline"

# Worktree C: Game Telemetry
cd ../mass-telemetry
cat openspec/changes/04-add-game-telemetry-ingestion/tasks.md
# ... develop game telemetry ...
git add . && git commit -m "feat: implement game telemetry ingestion"
git push origin feature/04-game-telemetry
gh pr create --title "feat: Game Telemetry Ingestion"

# Merge PRs in order of completion (flexible order)
```

### Wave 3: Intelligence Layer (2 Parallel Worktrees)

```bash
# After Wave 2 merges complete (especially STT + Telemetry), pull latest main
cd /Users/reena/gauntletai/unseenedgeai
git checkout main
git pull origin main

# Create 2 parallel worktrees
git worktree add ../mass-ml-inference feature/05-ml-inference
git worktree add ../mass-gpt4 feature/07-gpt4-reasoning

# Worktree A: ML Inference
cd ../mass-ml-inference
cat openspec/changes/05-add-ml-inference-service/tasks.md
# ... develop ML inference service ...
git add . && git commit -m "feat: implement ML inference service"
git push origin feature/05-ml-inference
gh pr create --title "feat: ML Inference Service"

# Worktree B: GPT-4 Reasoning
cd ../mass-gpt4
cat openspec/changes/07-add-gpt4-reasoning/tasks.md
# ... develop GPT-4 reasoning ...
git add . && git commit -m "feat: implement GPT-4 reasoning generation"
git push origin feature/07-gpt4-reasoning
gh pr create --title "feat: GPT-4 Reasoning Generation"

# Merge PRs in any order when ready
```

### Wave 4: Fusion & Presentation (2 Worktrees, Strict Merge Order)

```bash
# After Wave 3 merges complete, pull latest main
cd /Users/reena/gauntletai/unseenedgeai
git checkout main
git pull origin main

# Create 2 worktrees
git worktree add ../mass-fusion feature/06-evidence-fusion
git worktree add ../mass-dashboard feature/08-teacher-dashboard

# Worktree A: Evidence Fusion
cd ../mass-fusion
cat openspec/changes/06-add-evidence-fusion-service/tasks.md
# ... develop evidence fusion ...
git add . && git commit -m "feat: implement evidence fusion service"
git push origin feature/06-evidence-fusion
gh pr create --title "feat: Evidence Fusion Service"
# MERGE THIS FIRST

# Worktree B: Teacher Dashboard
cd ../mass-dashboard
cat openspec/changes/08-add-teacher-dashboard/tasks.md
# ... develop dashboard (can start UI early, but integration waits for fusion) ...
git add . && git commit -m "feat: implement teacher dashboard"
git push origin feature/08-teacher-dashboard
gh pr create --title "feat: Teacher Dashboard"
# MERGE THIS AFTER FUSION
```

### Cleaning Up Worktrees

```bash
# After a branch is merged, remove its worktree
cd /Users/reena/gauntletai/unseenedgeai

# Remove specific worktree
git worktree remove ../mass-infrastructure

# List all worktrees
git worktree list

# Remove all completed worktrees
git worktree prune
```

---

## Integration Testing

### Before Each PR/Merge

Run comprehensive tests to ensure the feature integrates properly:

```bash
# In the feature worktree, before creating PR

# 1. Run unit tests
pytest tests/unit/

# 2. Run integration tests
pytest tests/integration/

# 3. Run E2E tests (for frontend changes)
npm run test:e2e

# 4. Validate against OpenSpec
./scripts/validate-openspec.sh

# 5. Check code quality
black . --check
flake8 .
mypy .

# 6. Test with production-like data
./scripts/test-with-sample-data.sh
```

### Cross-Branch Integration Testing

When multiple PRs from the same wave are ready:

```bash
# Create a temporary integration branch
git checkout -b integration/wave-2-test main

# Merge all Wave 2 branches locally
git merge feature/02-authentication-system
git merge feature/03-stt-pipeline
git merge feature/04-game-telemetry

# Run full integration test suite
pytest tests/integration/wave2/

# If tests pass, merge PRs to main individually
# If tests fail, identify conflicts and fix in feature branches
```

---

## Timeline

### Gantt Chart View

```
Week 15 ████ Infrastructure Setup
Week 16 ████ Infrastructure Setup → MERGE #1
         ↓
Week 17 ████ Auth ████████████ STT ████████████ Telemetry
Week 18 ████ Auth → MERGE #2    ████ STT       ████ Telemetry → MERGE #3
Week 19                         ████ STT
Week 20                         ████ STT → MERGE #4
         ↓
Week 21                              ████ ML Inference ████ GPT-4
Week 22                              ████ ML Inference ████ GPT-4 → MERGE #5
Week 23                              ████ ML Inference → MERGE #6
         ↓                                ↓
Week 24                                   ████ Evidence Fusion
Week 25                                   ████ Evidence Fusion → MERGE #7
         ↓
Week 26                                        ████ Dashboard
Week 27                                        ████ Dashboard
Week 28                                        ████ Dashboard
Week 29                                        ████ Dashboard
Week 30                                        ████ Dashboard → MERGE #8 ✅
```

### Milestone Summary

| Week | Milestone | Merges |
|------|-----------|--------|
| 16 | Infrastructure complete | #1 |
| 18-20 | Wave 2 complete | #2, #3, #4 |
| 22-23 | Wave 3 complete | #5, #6 |
| 25 | Fusion complete | #7 |
| 30 | Dashboard complete, System ready | #8 |

---

## Critical Rules

### ✅ DO

1. **Always branch from latest main** when starting a new wave
   ```bash
   git checkout main && git pull origin main
   ```

2. **Rebase long-running branches** if other branches merge first
   ```bash
   git fetch origin
   git rebase origin/main
   ```

3. **Run full test suite** before creating PR
   ```bash
   pytest tests/ && npm run test:e2e
   ```

4. **Keep PRs focused** - one OpenSpec change per PR

5. **Document infrastructure changes** in Terraform and README

6. **Update OpenSpec specs** as you implement features

7. **Merge frequently** within waves to avoid long-lived branches

### ⛔ DON'T

1. **Don't merge out of order** across waves
   - Infrastructure MUST merge before Wave 2
   - Fusion MUST merge before Dashboard

2. **Don't skip integration testing** before merging

3. **Don't merge with failing tests**

4. **Don't create circular dependencies** between branches

5. **Don't work directly on main** - always use feature branches/worktrees

6. **Don't forget to clean up worktrees** after merging
   ```bash
   git worktree remove ../mass-old-branch
   ```

7. **Don't rebase after pushing to shared PR** - use merge commits for collaboration

---

## Handling Conflicts

### Scenario: Branch A merged while you're working on Branch B

```bash
# You're in ../mass-stt (Branch B)
# Meanwhile, feature/02-authentication-system (Branch A) merged to main

# Fetch latest changes
git fetch origin

# Rebase onto main
git rebase origin/main

# If conflicts occur:
git status  # See conflicting files
# Resolve conflicts in editor
git add <resolved-files>
git rebase --continue

# Force push (since rebase rewrites history)
git push origin feature/03-stt-pipeline --force-with-lease
```

### Scenario: Multiple branches in same wave have conflicts

```bash
# Test integration before merging by creating temp branch
git checkout main
git checkout -b test/wave-2-integration

# Merge all Wave 2 branches
git merge feature/02-authentication-system
git merge feature/03-stt-pipeline  # Conflict here!
git merge feature/04-game-telemetry

# Resolve conflicts to understand impact
# Then coordinate with other developers to fix in feature branches
```

---

## Quick Reference Commands

### Common Operations

```bash
# List all worktrees
git worktree list

# Create new worktree
git worktree add <path> <branch-name>

# Remove worktree
git worktree remove <path>

# Switch between worktrees (just use cd)
cd ../mass-infrastructure
cd ../mass-auth

# Update worktree from main
git fetch origin
git rebase origin/main

# Create PR from worktree
gh pr create --title "feat: Title" --body "Description"

# Check which branch you're on
git branch --show-current
```

### Automation Script

Create `scripts/create-worktree.sh`:

```bash
#!/bin/bash
# Usage: ./scripts/create-worktree.sh <change-number>

CHANGE_NUM=$1
CHANGE_DIR="openspec/changes/$(printf "%02d" $CHANGE_NUM)-*"
CHANGE_NAME=$(basename $CHANGE_DIR)

# Get change title from proposal
TITLE=$(head -1 $CHANGE_DIR/proposal.md | sed 's/# Change: //')

# Create worktree
WORKTREE_PATH="../mass-${CHANGE_NAME#*-}"
BRANCH_NAME="feature/${CHANGE_NAME}"

git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

echo "Created worktree at: $WORKTREE_PATH"
echo "Branch: $BRANCH_NAME"
echo "Tasks: cat $CHANGE_DIR/tasks.md"
```

---

## Summary

This parallel git worktree strategy enables:

- **Maximum parallelization**: Up to 3 concurrent branches
- **Minimal blocking**: Only 2 strict merge dependencies (Wave 1→2, Fusion→Dashboard)
- **Flexible workflow**: Merge within waves in any order
- **Clean history**: Each feature is independently reviewable
- **Efficient development**: Multiple developers can work simultaneously

**Total Duration**: 16 weeks (vs ~30 weeks if sequential)
**Efficiency Gain**: ~47% time savings through parallelization

---

## Next Steps

1. **Start Wave 1**: Create infrastructure worktree
   ```bash
   git worktree add ../mass-infrastructure feature/01-infrastructure-setup
   cd ../mass-infrastructure
   cat openspec/changes/01-add-infrastructure-setup/tasks.md
   ```

2. **Review tasks**: Each change has detailed tasks in `tasks.md`

3. **Set up CI/CD**: Configure GitHub Actions to test each PR

4. **Create PR templates**: Use OpenSpec proposals as PR description templates

Ready to begin implementation!
