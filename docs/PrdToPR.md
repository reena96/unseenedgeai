# From PRD to PR Task Lists: Complete Workflow

**Document Version:** 1.0
**Date:** January 2025
**Project:** MASS (Middle School Non-Academic Skills Measurement System)

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Preparation](#phase-1-preparation-already-done-)
3. [Phase 2: Create OpenSpec Changes](#phase-2-create-openspec-changes-not-yet-done-)
4. [Phase 3: Implementation](#phase-3-implementation-code-development)
5. [Phase 4: Multiple PRs per Change](#phase-4-multiple-prs-per-change-optional)
6. [Summary Flow](#summary-the-complete-flow)
7. [Quick Reference Commands](#quick-reference-commands)

---

## Overview

This document describes the complete workflow from Product Requirements Documents (PRDs) to Pull Request (PR) task lists using the OpenSpec framework.

### The Flow Diagram

```
PRD/Tech Arch/Roadmap (planning docs)
         ↓
OpenSpec specs (requirements - WHAT to build)
         ↓
OpenSpec changes (implementation plans - HOW to implement)
         ↓
tasks.md files (PR task lists - CHECKLIST for implementation)
         ↓
Pull Requests (actual code)
```

### Key Insight

**OpenSpec's `tasks.md` files ARE your PR task lists.** They serve as implementation checklists that you mark off as you complete work, then paste directly into your PR description.

---

## Phase 1: Preparation (Already Done ✅)

### Step 1.1: Write PRD
**File:** `docs/MASS_Implementation_PRD_v3.md`
**Purpose:** Define WHAT to build
- Functional requirements
- Success metrics
- Budget and timeline overview
- Phase 0 decision gates

### Step 1.2: Write Technical Architecture
**File:** `docs/MASS_Technical_Architecture_v1.md`
**Purpose:** Define HOW to build it
- Technology stack
- System architecture diagrams
- API specifications
- Database schemas
- Infrastructure setup

### Step 1.3: Write Implementation Roadmap
**File:** `docs/MASS_Implementation_Roadmap.md`
**Purpose:** Define WHEN to build it
- 38-week week-by-week plan
- Team allocation
- Milestone dates
- Budget breakdown

### Step 1.4: Create OpenSpec Specs
**Location:** `openspec/specs/[capability]/spec.md`
**Purpose:** Define requirements for each capability

**Created specs:**
1. `audio-processing` - STT pipeline, transcription
2. `authentication` - User auth, RBAC, session management
3. `evidence-fusion` - Multi-source score fusion, GPT-4 reasoning
4. `game-telemetry` - Unity game telemetry ingestion
5. `skill-inference` - ML models, feature extraction
6. `teacher-dashboard` - Teacher UI, visualizations

**Command to list specs:**
```bash
openspec list --specs
```

---

## Phase 2: Create OpenSpec Changes (NOT YET DONE ❌)

This phase creates the implementation plans and PR task lists.

### Step 2.1: Identify Components from Roadmap

Break down your 38-week roadmap into logical implementation units:

| Weeks | Component | Change ID |
|-------|-----------|-----------|
| 15-16 | Infrastructure | `add-infrastructure-setup` |
| 17-18 | Core API + Auth | `add-authentication-system` |
| 19-20 | STT Pipeline | `add-stt-pipeline` |
| 17-20 | Game Mission 1 | `add-game-mission-1` |
| 21-24 | Game Mission 2 | `add-game-mission-2` |
| 25-28 | Game Mission 3 | `add-game-mission-3` |
| 21-22 | ML Inference | `add-ml-inference-service` |
| 23-24 | Evidence Fusion | `add-evidence-fusion-service` |
| 25-26 | GPT-4 Reasoning | `add-gpt4-reasoning` |
| 17-30 | Dashboard Foundation | `add-teacher-dashboard-foundation` |
| 29-30 | Dashboard Features | `add-teacher-dashboard-features` |
| 31-32 | Security & Compliance | `add-security-compliance` |

**Total:** 10-15 changes

### Step 2.2: For Each Change, Create Directory Structure

**Example:** For `add-stt-pipeline`

```bash
mkdir -p openspec/changes/add-stt-pipeline/specs/audio-processing
cd openspec/changes/add-stt-pipeline
```

### Step 2.3: Write `proposal.md`

**File:** `openspec/changes/add-stt-pipeline/proposal.md`

```markdown
# Change: Add Speech-to-Text Pipeline

## Why
Enable classroom audio transcription using Google Cloud STT with speaker diarization,
which is the foundation for linguistic feature extraction and skill inference.

## What Changes
- Google Cloud STT integration with async processing
- Audio file upload API with Cloud Storage backend
- Speaker diarization and student-speaker mapping
- Transcript storage and segmentation
- Cloud Tasks queue for async transcription jobs

## Impact
- Affected specs: audio-processing
- Affected code: New files in src/services/, src/api/v1/
- Database: 3 new tables (audio_files, transcripts, transcript_segments)
- Infrastructure: GCS bucket, Cloud Tasks queue
- **BREAKING:** None (new functionality)
```

### Step 2.4: Write `tasks.md` (THIS IS YOUR PR TASK LIST!)

**File:** `openspec/changes/add-stt-pipeline/tasks.md`

```markdown
## 1. Infrastructure Setup
- [ ] 1.1 Enable Google Cloud Speech-to-Text API in GCP project
- [ ] 1.2 Create service account with STT permissions
- [ ] 1.3 Store API credentials in Secret Manager
- [ ] 1.4 Create GCS bucket: mass-production-audio-files
- [ ] 1.5 Set 30-day lifecycle policy on bucket
- [ ] 1.6 Create Cloud Tasks queue: transcription-jobs

## 2. Database Schema
- [ ] 2.1 Create migration: audio_files table
- [ ] 2.2 Create migration: transcripts table
- [ ] 2.3 Create migration: transcript_segments table
- [ ] 2.4 Run migrations on dev database
- [ ] 2.5 Verify schema with openspec validate

## 3. Backend Services
- [ ] 3.1 Implement STTService class (src/services/stt_service.py)
  - [ ] 3.1.1 transcribe_audio() method
  - [ ] 3.1.2 speaker diarization logic
  - [ ] 3.1.3 error handling and retries
- [ ] 3.2 Implement TranscriptionWorker (src/workers/transcription_worker.py)
  - [ ] 3.2.1 Cloud Tasks handler
  - [ ] 3.2.2 Progress tracking
  - [ ] 3.2.3 Status updates
- [ ] 3.3 Implement student-speaker mapping algorithm

## 4. API Endpoints
- [ ] 4.1 POST /api/v1/audio/upload
  - [ ] 4.1.1 Multipart file upload handling
  - [ ] 4.1.2 Upload to GCS
  - [ ] 4.1.3 Queue transcription job
  - [ ] 4.1.4 Return job ID and status
- [ ] 4.2 GET /api/v1/audio/status/{job_id}
- [ ] 4.3 GET /api/v1/transcripts/{transcript_id}

## 5. Testing
- [ ] 5.1 Unit tests for STTService
- [ ] 5.2 Mock STT API responses
- [ ] 5.3 Integration test: upload → GCS → queue → transcribe
- [ ] 5.4 Test with sample 5-minute classroom audio
- [ ] 5.5 Test with 6-hour classroom audio
- [ ] 5.6 Verify STT accuracy >75% (manual spot check)
- [ ] 5.7 Verify diarization with known speakers

## 6. Documentation
- [ ] 6.1 Update API docs (Swagger)
- [ ] 6.2 Add example curl commands
- [ ] 6.3 Document error codes
- [ ] 6.4 Add troubleshooting guide

## 7. Deployment
- [ ] 7.1 Deploy to staging environment
- [ ] 7.2 Run smoke tests
- [ ] 7.3 Monitor logs for errors
- [ ] 7.4 Deploy to production (after approval)
```

**Important:** This `tasks.md` file IS your PR task list. You will:
1. Work through it during implementation
2. Mark items as complete: `- [x]`
3. Copy it into your PR description

### Step 2.5: Write Spec Deltas (if modifying existing specs)

**File:** `openspec/changes/add-stt-pipeline/specs/audio-processing/spec.md`

```markdown
## ADDED Requirements

### Requirement: Speech-to-Text Transcription
The system SHALL transcribe classroom audio using Google Cloud Speech-to-Text with speaker diarization.

#### Scenario: Audio transcription with diarization
- **GIVEN** a transcription job is processing
- **WHEN** Google Cloud STT processes the audio
- **THEN** the system uses the `latest_long` model with enhanced audio
- **AND** enables speaker diarization with up to 10 speakers
- **AND** enables automatic punctuation
- **AND** returns a full transcript with word-level timestamps

#### Scenario: Transcription completion
- **GIVEN** transcription is complete
- **WHEN** results are available
- **THEN** transcript is stored in database
- **AND** transcript segments are attributed to speakers
- **AND** student-speaker mapping is attempted
- **AND** processing job status is updated to "completed"

## MODIFIED Requirements

(If you're modifying existing requirements, copy the full requirement here with changes)
```

**Note:** If you're implementing a completely new spec (not modifying existing), you can skip this step or just note it in `proposal.md`.

### Step 2.6: Validate the Change

```bash
openspec validate add-stt-pipeline --strict
```

**Fix any validation errors:**
- Missing scenarios
- Invalid delta format
- Duplicate requirements
- Incorrect heading levels

Repeat validation until it passes.

### Step 2.7: Repeat Steps 2.2-2.6 for ALL Changes

Create all 10-15 changes identified in Step 2.1:
- `add-infrastructure-setup`
- `add-authentication-system`
- `add-stt-pipeline`
- `add-game-mission-1`
- `add-game-mission-2`
- `add-game-mission-3`
- `add-ml-inference-service`
- `add-evidence-fusion-service`
- `add-gpt4-reasoning`
- `add-teacher-dashboard-foundation`
- `add-teacher-dashboard-features`
- `add-security-compliance`

**Time estimate:** 1-2 hours per change = 10-30 hours total for all changes

---

## Phase 3: Implementation (Code Development)

Now you actually write code, using `tasks.md` as your checklist.

### Step 3.1: Choose First Change to Implement

Start with `add-infrastructure-setup` (Week 15-16 in roadmap).

### Step 3.2: Create Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/infrastructure-setup
```

**Branch naming convention:**
- `feature/[change-id]` for new features
- `fix/[change-id]` for bug fixes

### Step 3.3: Work Through tasks.md Checklist

Open `openspec/changes/add-infrastructure-setup/tasks.md` and work through each task sequentially:

**Example workflow:**
1. Read task: `1.1 Create GCP project`
2. Do the work: `gcloud projects create mass-production`
3. Verify it worked: `gcloud projects describe mass-production`
4. Mark it complete in `tasks.md`: Change `- [ ]` to `- [x]`
5. Commit: `git commit -am "feat(infra): create GCP project"`
6. Move to next task: `1.2 Enable APIs`

**Tips:**
- Commit frequently (after each task or subtask)
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`
- Keep commits atomic (one logical change per commit)

### Step 3.4: Update tasks.md as You Work

As you complete tasks, mark them in the file:

```markdown
## 1. Infrastructure Setup
- [x] 1.1 Create GCP project ✅
- [x] 1.2 Enable required APIs ✅
- [x] 1.3 Create service accounts ✅
- [ ] 1.4 Deploy Cloud SQL (in progress...)
- [ ] 1.5 Create storage buckets
```

**Commit the updated tasks.md:**
```bash
git add openspec/changes/add-infrastructure-setup/tasks.md
git commit -m "docs(openspec): update infrastructure tasks progress"
```

### Step 3.5: Handle Blockers and Changes

If you encounter blockers or need to change the plan:

**Option A: Add new tasks**
```markdown
- [ ] 1.6 ADDED: Configure VPC networking (discovered dependency)
```

**Option B: Mark tasks as blocked**
```markdown
- [ ] 1.4 Deploy Cloud SQL (BLOCKED: waiting for budget approval)
```

**Option C: Skip tasks with justification**
```markdown
- [~] 1.7 Set up Redis (SKIPPED: deferred to Phase 2)
```

### Step 3.6: Create Pull Request

When ALL tasks in `tasks.md` are complete:

```bash
# Final commit
git add .
git commit -m "feat(infra): complete GCP infrastructure setup

- All infrastructure components deployed
- Tested connectivity and permissions
- Documentation updated"

# Push to remote
git push origin feature/infrastructure-setup
```

**Create PR on GitHub** with this description:

```markdown
# Infrastructure Setup

Implements `openspec/changes/add-infrastructure-setup`

## Summary
Sets up complete GCP infrastructure for MASS system including Cloud SQL,
Cloud Storage, Cloud Tasks, and all required APIs.

## Tasks Completed
- [x] 1.1 Create GCP project
- [x] 1.2 Enable required APIs
- [x] 1.3 Create service accounts
- [x] 1.4 Deploy Cloud SQL with PostgreSQL 15
- [x] 1.5 Create storage buckets with lifecycle policies
- [x] 1.6 Configure Cloud Tasks queues
- [x] 1.7 Set up Secret Manager
- [x] 2.1 Configure IAM permissions
- [x] 2.2 Set up VPC networking
- [x] 3.1 Deploy Terraform configuration
- [x] 3.2 Verify all services accessible
- [x] 4.1 Document infrastructure setup
- [x] 4.2 Create runbook for common operations

## Testing
- ✅ All GCP services deployed successfully
- ✅ Connectivity verified from Cloud Run to Cloud SQL
- ✅ Permissions tested with service account
- ✅ Terraform state stored in GCS backend

## Next Steps
After merge: Begin implementation of authentication system

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Key points:**
- Copy the entire `tasks.md` checklist into PR description
- GitHub will render `- [x]` as checked boxes
- Add summary, testing notes, and next steps
- Link to the OpenSpec change

### Step 3.7: Code Review and Merge

1. Request reviewers
2. Address feedback
3. Update tasks.md if new work is required
4. Get approval
5. Merge PR (squash and merge recommended)

### Step 3.8: After PR Merges, Archive the Change

```bash
# Switch back to main
git checkout main
git pull origin main

# Archive the change
openspec archive add-infrastructure-setup --yes

# This moves:
# openspec/changes/add-infrastructure-setup/
# → openspec/changes/archive/2025-01-15-add-infrastructure-setup/
```

**The archive command:**
- Moves the change to `changes/archive/YYYY-MM-DD-[name]/`
- Updates specs if capabilities changed (merges deltas)
- Validates that everything is consistent

### Step 3.9: Repeat Steps 3.1-3.8 for Next Change

Move to the next change in sequence:
- `add-authentication-system` (Week 17-18)
- `add-stt-pipeline` (Week 19-20)
- etc.

**Continue until all changes are implemented.**

---

## Phase 4: Multiple PRs per Change (Optional)

If a change is too large (>500 lines of code or >20 tasks), split it into multiple PRs.

### Step 4.1: Split tasks.md into Logical Groups

**Example:** For `add-stt-pipeline`, split into:

**PR 1: Database Schema**
```markdown
## 2. Database Schema
- [ ] 2.1 Create migration: audio_files table
- [ ] 2.2 Create migration: transcripts table
- [ ] 2.3 Create migration: transcript_segments table
- [ ] 2.4 Run migrations on dev database
```

**PR 2: STT Service Implementation**
```markdown
## 3. Backend Services
- [ ] 3.1 Implement STTService class
- [ ] 3.2 Implement TranscriptionWorker
- [ ] 3.3 Implement student-speaker mapping
```

**PR 3: API Endpoints**
```markdown
## 4. API Endpoints
- [ ] 4.1 POST /api/v1/audio/upload
- [ ] 4.2 GET /api/v1/audio/status/{job_id}
- [ ] 4.3 GET /api/v1/transcripts/{transcript_id}
```

### Step 4.2: Create Branches for Each PR

```bash
git checkout -b feature/stt-pipeline-schema
# Implement database tasks only
# Create PR 1

git checkout main
git checkout -b feature/stt-pipeline-service
# Implement service tasks only
# Create PR 2

# etc.
```

### Step 4.3: Update Original tasks.md After Each PR

After each sub-PR merges, update the main `tasks.md`:

```markdown
## 2. Database Schema ✅ (PR #42 - merged)
- [x] 2.1 Create migration: audio_files table
- [x] 2.2 Create migration: transcripts table
- [x] 2.3 Create migration: transcript_segments table
- [x] 2.4 Run migrations on dev database

## 3. Backend Services (PR #45 - in review)
- [x] 3.1 Implement STTService class
- [x] 3.2 Implement TranscriptionWorker
- [ ] 3.3 Implement student-speaker mapping (in progress)
```

### Step 4.4: Archive Only When ALL Sub-PRs Are Merged

Don't archive the change until ALL tasks across ALL PRs are complete.

---

## Summary: The Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Preparation (DONE ✅)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. PRD (what to build)                                      │
│ 2. Tech Arch (how to build)                                 │
│ 3. Roadmap (when to build)                                  │
│ 4. OpenSpec specs (requirements)                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Create Changes (TODO ❌)                           │
├─────────────────────────────────────────────────────────────┤
│ 5. Identify 10-15 components from roadmap                   │
│ 6. For each component, create OpenSpec change:              │
│    - proposal.md (why & what)                               │
│    - tasks.md (PR TASK LIST! 👈)                            │
│    - design.md (optional)                                   │
│    - specs/[capability]/spec.md (deltas)                    │
│ 7. Validate each change: openspec validate --strict         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Implementation (TODO ❌)                           │
├─────────────────────────────────────────────────────────────┤
│ 8. Pick first change (e.g., add-infrastructure-setup)       │
│ 9. Create feature branch                                    │
│ 10. Work through tasks.md checklist                         │
│     - Do task → Mark complete → Commit → Repeat             │
│ 11. Create PR with tasks.md as description                  │
│ 12. Code review → Merge                                     │
│ 13. Archive change: openspec archive [change-id] --yes      │
│ 14. Repeat for next change                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
                     ALL DONE! 🎉
```

---

## Quick Reference Commands

### OpenSpec Commands

```bash
# List all specs
openspec list --specs

# List active changes
openspec list

# Show spec details
openspec show audio-processing --type spec

# Show change details
openspec show add-stt-pipeline

# Validate a change
openspec validate add-stt-pipeline --strict

# Validate all changes
openspec validate --strict

# Archive a change (after PR merge)
openspec archive add-stt-pipeline --yes

# Update OpenSpec instructions
openspec update
```

### Git Commands

```bash
# Create feature branch
git checkout -b feature/[change-id]

# Commit with conventional commit message
git commit -m "feat(scope): description"

# Push and create PR
git push origin feature/[change-id]

# After merge, clean up branch
git branch -d feature/[change-id]
git push origin --delete feature/[change-id]
```

### Typical Commit Messages

```bash
git commit -m "feat(infra): create GCP project and enable APIs"
git commit -m "feat(stt): implement STTService with diarization"
git commit -m "test(stt): add unit tests for transcription"
git commit -m "docs(api): update Swagger with audio endpoints"
git commit -m "fix(stt): handle empty audio files gracefully"
git commit -m "refactor(stt): extract speaker mapping to separate class"
```

---

## Best Practices

### Writing tasks.md

✅ **DO:**
- Break work into small, testable chunks (1-4 hours each)
- Use clear, action-oriented language ("Create", "Implement", "Test")
- Include verification steps ("Verify", "Confirm", "Check")
- Group related tasks into numbered sections
- Include file paths and function names where helpful
- Add sub-tasks with indentation for complex tasks

❌ **DON'T:**
- Make tasks too large ("Implement entire backend")
- Use vague descriptions ("Do the thing")
- Forget testing and documentation tasks
- Skip validation steps

### During Implementation

✅ **DO:**
- Update tasks.md as you work
- Commit tasks.md updates with code commits
- Add new tasks if you discover missing work
- Document blockers and skipped tasks with reasons
- Test each task before marking complete

❌ **DON'T:**
- Mark tasks complete without testing
- Wait until the end to update tasks.md
- Skip tasks without documenting why
- Batch-complete multiple unrelated tasks

### Creating PRs

✅ **DO:**
- Copy full tasks.md checklist into PR description
- Add summary explaining the change
- Include testing notes and results
- Link to OpenSpec change directory
- Request appropriate reviewers

❌ **DON'T:**
- Create PR without completing all tasks
- Skip PR description (GitHub auto-completes it poorly)
- Merge without code review
- Forget to archive the change after merge

---

## Troubleshooting

### Problem: "openspec validate fails"

**Solution:**
1. Read the error message carefully
2. Check scenario formatting: `#### Scenario: Name`
3. Ensure each requirement has at least one scenario
4. Verify delta operations: `## ADDED Requirements`, `## MODIFIED Requirements`
5. Run: `openspec show [change-id] --json --deltas-only` to debug

### Problem: "tasks.md is too large (>30 tasks)"

**Solution:**
1. Split into multiple PRs (Phase 4)
2. Or split into multiple smaller changes
3. Group related tasks into higher-level tasks with sub-tasks

### Problem: "I discovered new work during implementation"

**Solution:**
1. Add new tasks to tasks.md: `- [ ] X.X ADDED: Description`
2. Commit the updated tasks.md
3. Complete the new tasks before creating PR
4. Document in PR description: "Added tasks X.X and Y.Y during implementation"

### Problem: "Change is blocked by another change"

**Solution:**
1. Note the dependency in proposal.md: "Depends on: add-authentication-system"
2. Mark blocked tasks: `- [ ] X.X Task (BLOCKED: waiting for auth system)`
3. Work on other changes while waiting
4. Resume when dependency is unblocked

---

## Example Timeline

**Week 15-16: Infrastructure**
- Day 1-2: Create `add-infrastructure-setup` change with tasks.md
- Day 3-7: Implement tasks, update checklist
- Day 8: Create PR, get review
- Day 9: Merge, archive change

**Week 17-18: Authentication**
- Day 1: Create `add-authentication-system` change
- Day 2-8: Implement (split into 2 PRs: schema + service)
- Day 9-10: Review, merge, archive

**Repeat for all changes through Week 38.**

---

## Appendix: Full Example

### Example: `add-stt-pipeline` Complete Structure

```
openspec/changes/add-stt-pipeline/
├── proposal.md           (Why: Need transcription. What: STT pipeline)
├── tasks.md             (7 sections, 25 tasks total)
├── design.md            (Optional: STT architecture decisions)
└── specs/
    └── audio-processing/
        └── spec.md      (ADDED: Speech-to-Text requirements)
```

**Full task count breakdown:**
- Infrastructure: 6 tasks
- Database: 5 tasks
- Backend: 8 tasks
- API: 3 tasks
- Testing: 7 tasks
- Documentation: 4 tasks
- Deployment: 4 tasks
- **Total: 37 tasks** (split into 3 PRs)

**Time estimate:**
- Planning (create change): 2 hours
- Implementation: 40 hours (1 week)
- Review and merge: 4 hours
- **Total: 46 hours / 6 days**

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial version |

---

**Next Document:** [Implementation Roadmap](./MASS_Implementation_Roadmap.md)
**Related Documents:** [PRD](./MASS_Implementation_PRD_v3.md), [Technical Architecture](./MASS_Technical_Architecture_v1.md)
