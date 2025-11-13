# Task 10 Validation - Quick Reference

## 🎯 One-Command Validation

Run this single script to automatically validate Task 10:

```bash
cd backend
./validate_task10.sh
```

This will:
1. ✅ Check all prerequisites (Python, database, dependencies)
2. 🚀 Start the API server automatically
3. 🌱 Seed the database with test data
4. 🧪 Run 10 comprehensive tests
5. 📊 Display detailed results
6. 🧹 Clean up automatically

## 📋 What Gets Tested

### Linguistic Features (18 metrics)
- Empathy markers, problem-solving language, perseverance
- Social/cognitive processes
- Sentiment analysis (positive/negative/neutral)
- Syntactic complexity, readability
- Word counts, lexical diversity
- Part-of-speech distribution

### Behavioral Features (12 metrics)
- Task completion rate, time efficiency
- Retry patterns, recovery rates
- Focus duration, distraction resistance
- Collaboration/leadership indicators

### API Functionality
- Single extraction endpoints
- Batch processing endpoints
- Feature retrieval endpoints
- Error handling (404, 500)
- Data persistence

## 🛠️ Manual Testing (Alternative)

If you prefer step-by-step control:

### Option A: Using the standalone test script
```bash
# Terminal 1: Start server
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Seed and test
cd backend
python scripts/seed_data.py --clear
./test_features.sh
```

### Option B: Using Swagger UI
```bash
# Start server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Seed database
python scripts/seed_data.py --clear

# Open browser
open http://localhost:8000/api/v1/docs

# Test endpoints interactively in Swagger UI
```

### Option C: Using cURL
```bash
# Get test IDs
TRANSCRIPT_ID=$(curl -s http://localhost:8000/api/v1/transcripts | jq -r '.[0].id')
SESSION_ID=$(curl -s http://localhost:8000/api/v1/game-sessions | jq -r '.[0].id')

# Extract linguistic features
curl -X POST "http://localhost:8000/api/v1/features/linguistic/${TRANSCRIPT_ID}" | jq .

# Extract behavioral features
curl -X POST "http://localhost:8000/api/v1/features/behavioral/${SESSION_ID}" | jq .

# Retrieve features
curl -X GET "http://localhost:8000/api/v1/features/linguistic/${TRANSCRIPT_ID}" | jq .
```

## 📖 Detailed Documentation

For comprehensive testing procedures, see:
- **Full Guide**: `docs/TASK_10_VALIDATION_GUIDE.md`
- **API Docs**: http://localhost:8000/api/v1/docs (when server is running)

## 🔧 Prerequisites

Required:
- Python 3.9+ with virtual environment
- PostgreSQL database
- curl and jq commands

Auto-installed by validation script:
- All Python dependencies from requirements.txt
- spaCy English model (en_core_web_sm)

## ⚠️ Troubleshooting

### Port already in use
The validation script will detect this and offer to kill the existing process.

Manually:
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database connection error
```bash
# Check PostgreSQL is running
pg_isready

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### No test data found
```bash
# Re-seed the database
python scripts/seed_data.py --clear
```

### Dependencies missing
```bash
# Reinstall dependencies
pip install -r requirements.txt
rm .deps_installed  # Force reinstall on next validation run
```

## 📊 Expected Results

After running `./validate_task10.sh`, you should see:

```
✅ All prerequisites satisfied
✅ Server is ready!
✅ Database seeded successfully
✅ All 10 tests passed

✅  ALL TESTS PASSED! ✅

Task 10: Feature Extraction Service is fully validated
```

Sample feature output will be displayed showing:
- Word counts and lexical diversity
- Sentiment scores
- Readability metrics
- Task completion rates
- Behavioral patterns

## 🚀 Next Steps After Validation

1. **Review Results**: Check the test output for any warnings
2. **Write Unit Tests**: Currently at 22% coverage for new code
3. **Performance Testing**: Test with larger batches
4. **Integration Testing**: Test with real audio transcriptions
5. **Move to Task 11**: Deploy ML Inference Models

## 📁 File Locations

```
backend/
├── validate_task10.sh          # ⭐ Main validation script (automated)
├── test_features.sh            # Test script (can run standalone)
├── scripts/
│   └── seed_data.py            # Database seeding
├── app/
│   ├── services/
│   │   └── feature_extraction.py  # Core extraction logic
│   └── api/endpoints/
│       └── features.py         # REST API endpoints
└── docs/
    └── TASK_10_VALIDATION_GUIDE.md  # Comprehensive guide
```

## 🎓 Understanding the Tests

Each test validates a specific capability:

1. **Linguistic Extraction**: NLP pipeline works correctly
2. **Behavioral Extraction**: Telemetry analysis works correctly
3. **Feature Retrieval**: Database storage and retrieval works
4. **Batch Processing**: Can handle multiple items efficiently
5. **Error Handling**: Gracefully handles invalid inputs
6. **Feature Quality**: Extracted values are reasonable and meaningful

## 💡 Tips

- The validation script is idempotent - safe to run multiple times
- Server logs are saved to `/tmp/mass_api.log`
- Seed logs are saved to `/tmp/seed_output.log`
- You can keep the server running after validation for manual testing
- Use Swagger UI for interactive exploration of the API

## 🆘 Getting Help

If validation fails:
1. Check the error messages - they're designed to be helpful
2. Review `/tmp/mass_api.log` for server errors
3. Review `/tmp/seed_output.log` for seeding issues
4. Consult `docs/TASK_10_VALIDATION_GUIDE.md` for detailed troubleshooting
5. Verify all prerequisites are met

## ✅ Success Criteria

Task 10 is validated when:
- ✅ All 10 automated tests pass
- ✅ Feature values are within expected ranges
- ✅ Data persists correctly to PostgreSQL
- ✅ Error handling works properly
- ✅ Both single and batch operations work
- ✅ API documentation is accessible
