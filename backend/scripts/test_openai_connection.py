#!/usr/bin/env python3
"""
Test OpenAI API connection and verify setup.

This script verifies that the OPENAI_API_KEY is properly configured
and tests the connection by generating a sample response.

Usage:
    python scripts/test_openai_connection.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def check_api_key():
    """Check if OpenAI API key is configured."""
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY is not configured")
        print("\n📝 Setup instructions:")
        print("   1. Edit backend/.env file")
        print("   2. Add: OPENAI_API_KEY=sk-your-key-here")
        print("   3. Get your key from: https://platform.openai.com/api-keys")
        print("\n📖 See backend/docs/GPT4_SETUP.md for detailed instructions")
        return False

    # Check if it's a placeholder
    if settings.OPENAI_API_KEY in ["your-openai-api-key", "loaded-from-secret-manager"]:
        print("⚠️  OPENAI_API_KEY is set to a placeholder value")
        print(f"   Current value: {settings.OPENAI_API_KEY}")
        print("\n📝 You need to replace this with a real API key:")
        print("   1. Get your key from: https://platform.openai.com/api-keys")
        print("   2. Edit backend/.env file")
        print("   3. Replace with: OPENAI_API_KEY=sk-your-actual-key-here")
        print("\n📖 See backend/docs/GPT4_SETUP.md for detailed instructions")
        return False

    print("✅ OPENAI_API_KEY is configured")
    # Show partial key for verification (hide most of it)
    key = settings.OPENAI_API_KEY
    if len(key) > 10:
        masked_key = f"{key[:7]}...{key[-4:]}"
    else:
        masked_key = "***"
    print(f"   Key: {masked_key}")
    return True


def test_connection():
    """Test OpenAI API connection with a simple request."""
    print("\n🔍 Testing OpenAI API connection...")

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ OpenAI library not installed")
        print("   Install with: pip install openai")
        return False

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Simple test request - generate one response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant for testing API connections.",
                },
                {
                    "role": "user",
                    "content": "Say 'Hello from OpenAI!' if you can read this.",
                },
            ],
            max_tokens=20,
            temperature=0.5,
        )

        message = response.choices[0].message.content.strip()
        print("✅ Successfully connected to OpenAI API!")
        print(f"   Test response: {message}")

        # Show usage info
        if hasattr(response, "usage"):
            usage = response.usage
            print(f"\n📊 Token usage for this test:")
            print(f"   Input tokens: {usage.prompt_tokens}")
            print(f"   Output tokens: {usage.completion_tokens}")
            print(f"   Total tokens: {usage.total_tokens}")

        return True

    except Exception as e:
        error_message = str(e)
        print(f"❌ Failed to connect to OpenAI API")
        print(f"   Error: {error_message}")

        # Provide specific guidance based on error
        if (
            "api_key" in error_message.lower()
            or "authentication" in error_message.lower()
        ):
            print("\n💡 Troubleshooting:")
            print("   - Verify your API key is correct")
            print("   - Check it starts with 'sk-'")
            print("   - Get a new key from: https://platform.openai.com/api-keys")
        elif "rate" in error_message.lower():
            print("\n💡 Troubleshooting:")
            print("   - You've hit the rate limit")
            print("   - Wait a moment and try again")
            print("   - Check limits: https://platform.openai.com/account/limits")
        elif (
            "quota" in error_message.lower() or "insufficient" in error_message.lower()
        ):
            print("\n💡 Troubleshooting:")
            print("   - Add credits to your OpenAI account")
            print("   - Visit: https://platform.openai.com/account/billing")
        else:
            print("\n💡 Troubleshooting:")
            print("   - Check your internet connection")
            print("   - Verify OpenAI services are operational")
            print("   - Visit: https://status.openai.com/")

        return False


def estimate_costs():
    """Display cost estimates for different dataset sizes."""
    print("\n💰 Cost Estimates for GPT-4o-mini:")
    print(
        "   (Based on current pricing: $0.15/1M input tokens, $0.60/1M output tokens)"
    )
    print()

    # Assumptions:
    # - Average prompt: ~200 tokens (examples + instructions)
    # - Average response: ~50 tokens per sample
    # - For 1000 samples with balanced distribution (4 skills × 3 levels × 7 grades = 84 combinations)
    # - That's ~12 samples per combination, generated in batches

    costs = [
        (100, 0.001),
        (1000, 0.01),
        (10000, 0.10),
        (100000, 1.00),
    ]

    for samples, cost in costs:
        print(f"   {samples:>6,} samples: ~${cost:>6.3f}")

    print("\n📝 Notes:")
    print("   - Costs are estimates based on 25-word average responses")
    print("   - Actual costs may vary by ±20%")
    print("   - Concurrent generation reduces time but not cost")
    print("   - Consider starting with 100-1000 samples for initial testing")


def main():
    """Main entry point."""
    print("=" * 60)
    print("OpenAI API Connection Test")
    print("=" * 60)

    # Check if API key is configured
    if not check_api_key():
        print("\n" + "=" * 60)
        sys.exit(1)

    # Test connection
    success = test_connection()

    # Show cost estimates
    estimate_costs()

    # Final status
    print("\n" + "=" * 60)
    if success:
        print("✅ READY FOR SYNTHETIC DATA GENERATION")
        print("\n📝 Next Steps:")
        print("   1. Review backend/docs/GPT4_SETUP.md for usage examples")
        print("   2. Generate a test dataset (100 samples):")
        print(
            "      python scripts/generate_synthetic_responses.py --count 100 --use-openai"
        )
        print("   3. Review the generated data quality")
        print("   4. Generate production dataset (1000-10000 samples)")
        print(
            "\n💡 Tip: Start small to verify quality before generating large datasets"
        )
    else:
        print("❌ SETUP INCOMPLETE")
        print("\n📖 See backend/docs/GPT4_SETUP.md for setup instructions")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
