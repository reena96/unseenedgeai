# Quick Start: GPT-4 Synthetic Data Generation

## Prerequisites ✅

- ✅ OpenAI API key configured in `.env`
- ✅ Virtual environment activated
- ✅ All dependencies installed

## Quick Commands

### Test Connection

```bash
# From backend directory
source venv/bin/activate
python scripts/test_openai_connection.py
```

### Generate Synthetic Data

#### Test Dataset (100 samples, ~$0.001)
```bash
python scripts/generate_synthetic_responses.py \
    --count 100 \
    --use-openai \
    --output data/synthetic_test_100.csv
```

#### Small Dataset (1,000 samples, ~$0.01)
```bash
python scripts/generate_synthetic_responses.py \
    --count 1000 \
    --use-openai \
    --output data/synthetic_1k.csv
```

#### Medium Dataset (10,000 samples, ~$0.10)
```bash
python scripts/generate_synthetic_responses.py \
    --count 10000 \
    --use-openai \
    --output data/synthetic_10k.csv
```

#### Large Dataset (100,000 samples, ~$1.00)
```bash
python scripts/generate_synthetic_responses.py \
    --count 100000 \
    --use-openai \
    --output data/synthetic_100k.csv
```

### Without OpenAI (Free, Template-based)
```bash
python scripts/generate_synthetic_responses.py \
    --count 100 \
    --output data/synthetic_template.csv
# Note: Omit --use-openai flag
```

## Expected Timing

- **100 samples**: ~30 seconds
- **1,000 samples**: ~3-5 minutes
- **10,000 samples**: ~30-40 minutes
- **100,000 samples**: ~5-6 hours

## Output Format

CSV file with columns:
- `response` - Student's verbal response text
- `skill` - Skill type (empathy, problem_solving, self_regulation, resilience)
- `skill_level` - Proficiency level (high, medium, developing)
- `grade` - Grade level (2-8)
- `source` - Generation method (gpt-4o-mini or template_expansion)

## Cost Monitoring

Check usage at: https://platform.openai.com/usage

## Full Documentation

See `backend/docs/GPT4_SETUP.md` for complete guide.

## Troubleshooting

If generation fails:

1. **Test connection**: `python scripts/test_openai_connection.py`
2. **Check API key**: Verify it's in `.env` and starts with `sk-`
3. **Verify balance**: Check OpenAI account has credits
4. **Review docs**: See `backend/docs/GPT4_SETUP.md`

## Next Steps After Generation

1. ✅ Verify CSV file was created in `data/` directory
2. ✅ Check file size and row count match expected
3. ✅ Review sample responses for quality
4. ✅ Proceed to feature extraction:
   ```bash
   python scripts/extract_linguistic_features.py
   python scripts/generate_behavioral_features.py
   python scripts/auto_label_skills.py
   ```
