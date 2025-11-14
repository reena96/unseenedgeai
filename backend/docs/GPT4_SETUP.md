# GPT-4 Synthetic Data Generation Setup Guide

## Overview

The UnseenEdge AI skill assessment project uses GPT-4o-mini for generating high-quality synthetic student responses. This guide walks you through setting up OpenAI API access for the synthetic data generation pipeline.

## Why GPT-4o-mini?

- **Cost-effective**: ~$0.01 per 1000 responses
- **High quality**: Generates realistic, age-appropriate student speech patterns
- **Fast**: Supports concurrent generation for large datasets
- **Suitable for synthetic data**: Balances quality and cost for training data generation

## Cost Estimates

| Sample Size | Estimated Cost | Time (Concurrent) |
|-------------|---------------|-------------------|
| 100 samples | ~$0.001 | ~30 seconds |
| 1,000 samples | ~$0.01 | ~3-5 minutes |
| 10,000 samples | ~$0.10 | ~30-40 minutes |
| 100,000 samples | ~$1.00 | ~5-6 hours |

**Note**: Actual costs may vary based on response length and API pricing. These estimates assume 25-word average responses at current GPT-4o-mini pricing ($0.15/1M input tokens, $0.60/1M output tokens).

## Setup Instructions

### Step 1: Obtain OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Name your key (e.g., "UnseenEdge AI - Synthetic Data")
6. Copy the key immediately (you won't be able to see it again!)

**Security Note**: Never commit your API key to version control.

### Step 2: Add API Key to Environment

#### Local Development (.env file)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Edit your `.env` file:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. Add or update the OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. Save and close the file

#### Production (GCP Secret Manager)

For production deployments, the API key should be stored in Google Cloud Secret Manager:

1. Create a secret in Secret Manager:
   ```bash
   echo -n "sk-your-actual-api-key-here" | gcloud secrets create openai-api-key \
       --data-file=- \
       --replication-policy="automatic"
   ```

2. Grant access to your service account:
   ```bash
   gcloud secrets add-iam-policy-binding openai-api-key \
       --member="serviceAccount:YOUR_SERVICE_ACCOUNT@unseenedgeai.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

3. The application will automatically load the key from Secret Manager in production

### Step 3: Verify Setup

Test your OpenAI API connection:

```bash
cd backend
python scripts/test_openai_connection.py
```

Expected output:
```
✅ OPENAI_API_KEY is configured
🔍 Testing OpenAI API connection...
✅ Successfully connected to OpenAI API!

📊 Cost Estimates for GPT-4o-mini:
   100 samples: ~$0.001
   1,000 samples: ~$0.01
   10,000 samples: ~$0.10

🚀 Ready to generate synthetic data!
```

## Usage

### Generate Synthetic Responses

#### Small Test Dataset (100 samples)
```bash
cd backend
python scripts/generate_synthetic_responses.py \
    --count 100 \
    --use-openai \
    --output data/synthetic_responses_test.csv
```

#### Production Dataset (1,000 samples)
```bash
cd backend
python scripts/generate_synthetic_responses.py \
    --count 1000 \
    --use-openai \
    --output data/synthetic_responses_1k.csv
```

#### Large Dataset (10,000 samples)
```bash
cd backend
python scripts/generate_synthetic_responses.py \
    --count 10000 \
    --use-openai \
    --output data/synthetic_responses_10k.csv
```

### Without OpenAI API (Template Expansion)

If you don't have an API key yet, you can still generate samples using template expansion:

```bash
cd backend
python scripts/generate_synthetic_responses.py \
    --count 100 \
    --output data/synthetic_responses_template.csv
```

**Note**: Template expansion reuses existing examples and is free, but provides less variety than GPT-4 generation.

## Generated Data Format

The script generates a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `response` | Student's verbal response | "I helped my friend with their math homework" |
| `skill` | Assessed skill | empathy, problem_solving, self_regulation, resilience |
| `skill_level` | Proficiency level | high, medium, developing |
| `grade` | Student grade level | 2-8 |
| `source` | Generation method | gpt-4o-mini, template_expansion |

## Monitoring API Usage

### Check Usage on OpenAI Dashboard

1. Visit [OpenAI Usage](https://platform.openai.com/usage)
2. View costs by day, model, and API key
3. Set up usage limits to prevent unexpected charges

### Set Spending Limits

1. Go to [Billing Settings](https://platform.openai.com/account/billing/limits)
2. Set a monthly budget limit
3. Configure email notifications for usage thresholds

**Recommended Limits for Development:**
- Soft limit: $5/month
- Hard limit: $10/month

## Troubleshooting

### "OPENAI_API_KEY not found"

**Solution**: Ensure the key is in your `.env` file and you've restarted any running services.

```bash
# Verify the key is loaded
python -c "from app.core.config import settings; print('Key present:', bool(settings.OPENAI_API_KEY))"
```

### "Rate limit exceeded"

**Solution**: OpenAI has rate limits on API requests. The script handles this automatically with retries, but for very large datasets:

1. Reduce concurrency (the script uses concurrent requests)
2. Add delays between batches
3. Check your [rate limits](https://platform.openai.com/account/limits)

### "Insufficient credits"

**Solution**: Add credits to your OpenAI account:

1. Go to [Billing](https://platform.openai.com/account/billing/overview)
2. Add payment method
3. Purchase credits (minimum $5)

### "Invalid API key"

**Solution**: Verify your key is correct and hasn't been revoked:

1. Check the key format starts with `sk-`
2. Ensure no extra spaces or newlines
3. Generate a new key if needed

## Best Practices

### For Development

1. **Start small**: Generate 100 samples first to verify quality
2. **Review samples**: Manually inspect generated responses for quality
3. **Monitor costs**: Check OpenAI dashboard after initial runs
4. **Use test keys**: Consider using a separate API key for development

### For Production

1. **Batch processing**: Generate data in batches (1,000-10,000 samples)
2. **Cache results**: Save generated data to avoid re-generating
3. **Quality checks**: Validate generated data before using for training
4. **Cost monitoring**: Set up alerts for unexpected usage

## Next Steps

After setting up GPT-4 access:

1. ✅ Test connection with `test_openai_connection.py`
2. ✅ Generate a small test dataset (100 samples)
3. ✅ Review the quality of generated responses
4. ✅ Generate production dataset (1,000-10,000 samples)
5. ✅ Proceed to feature extraction and model training

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GPT-4o-mini Pricing](https://openai.com/pricing)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

## Support

For issues related to:
- **OpenAI API**: Contact [OpenAI Support](https://help.openai.com/)
- **Synthetic data generation script**: Check `backend/scripts/SYNTHETIC_DATA_README.md`
- **UnseenEdge AI project**: Create an issue in the project repository
