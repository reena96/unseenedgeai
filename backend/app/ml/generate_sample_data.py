"""
Generate sample training data for XGBoost skill models.
This creates synthetic data following the TRAINING_DATA_FORMAT.md specification.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

def generate_sample_data(n_samples=1000):
    """
    Generate synthetic training data.

    Args:
        n_samples: Number of student samples to generate

    Returns:
        DataFrame with all required features and labels
    """

    data = {
        'student_id': [f'student_{i:04d}' for i in range(1, n_samples + 1)]
    }

    # 1. Linguistic Features (16 columns)
    # Skill-specific markers (0.0 - 1.0)
    data['empathy_markers'] = np.random.beta(2, 5, n_samples)  # Skewed toward lower values
    data['problem_solving_language'] = np.random.beta(2, 5, n_samples)
    data['perseverance_indicators'] = np.random.beta(2, 5, n_samples)

    # Psychological processes (0.0 - 1.0)
    data['social_processes'] = np.random.beta(2, 5, n_samples)
    data['cognitive_processes'] = np.random.beta(2, 5, n_samples)

    # Sentiment scores (-1.0 to 1.0)
    data['positive_sentiment'] = np.random.uniform(-0.2, 0.8, n_samples)
    data['negative_sentiment'] = np.random.uniform(-0.8, 0.2, n_samples)

    # Linguistic complexity
    data['avg_sentence_length'] = np.random.normal(10, 3, n_samples).clip(3, 25)
    data['syntactic_complexity'] = np.random.normal(3.5, 1.2, n_samples).clip(1, 8)
    data['readability_score'] = np.random.normal(65, 15, n_samples).clip(0, 100)

    # Word counts
    data['word_count'] = np.random.poisson(200, n_samples).clip(10, 1000)
    data['unique_word_count'] = (data['word_count'] * np.random.uniform(0.4, 0.7, n_samples)).astype(int)
    data['noun_count'] = (data['word_count'] * np.random.uniform(0.15, 0.25, n_samples)).astype(int)
    data['verb_count'] = (data['word_count'] * np.random.uniform(0.12, 0.22, n_samples)).astype(int)
    data['adj_count'] = (data['word_count'] * np.random.uniform(0.08, 0.15, n_samples)).astype(int)
    data['adv_count'] = (data['word_count'] * np.random.uniform(0.05, 0.12, n_samples)).astype(int)

    # 2. Behavioral Features (9 columns)
    data['task_completion_rate'] = np.random.beta(8, 2, n_samples)  # Skewed toward higher values
    data['time_efficiency'] = np.random.gamma(2, 0.5, n_samples).clip(0.3, 2.5)
    data['retry_count'] = np.random.poisson(3, n_samples).clip(0, 20)
    data['recovery_rate'] = np.random.beta(5, 3, n_samples)
    data['distraction_resistance'] = np.random.beta(8, 2, n_samples)
    data['focus_duration'] = np.random.gamma(5, 40, n_samples).clip(30, 600)
    data['collaboration_indicators'] = np.random.poisson(5, n_samples).clip(0, 30)
    data['leadership_indicators'] = np.random.poisson(3, n_samples).clip(0, 20)
    data['event_count'] = np.random.poisson(100, n_samples).clip(10, 500)

    # 3. Derived Features (4 columns - 1 per skill)
    data['empathy_social_interaction'] = data['empathy_markers'] * data['social_processes']
    data['problem_solving_cognitive'] = data['problem_solving_language'] * data['cognitive_processes']
    data['self_regulation_focus'] = data['distraction_resistance'] * data['focus_duration']
    data['resilience_recovery'] = data['retry_count'] * data['recovery_rate']

    # 4. Target Labels (4 columns)
    # Create realistic correlations between features and labels

    # Empathy score: influenced by empathy markers, social processes, positive sentiment
    empathy_base = (
        0.3 * data['empathy_markers'] +
        0.25 * data['social_processes'] +
        0.15 * (data['positive_sentiment'] + 1) / 2 +  # Normalize to 0-1
        0.15 * data['collaboration_indicators'] / 30 +
        0.15 * np.random.random(n_samples)
    )
    data['empathy_score'] = empathy_base.clip(0, 1)

    # Problem-solving score: influenced by task completion, cognitive processes, time efficiency
    ps_base = (
        0.3 * data['task_completion_rate'] +
        0.25 * data['problem_solving_language'] +
        0.2 * data['cognitive_processes'] +
        0.1 * (data['time_efficiency'] / 2.5) +  # Normalize
        0.15 * np.random.random(n_samples)
    )
    data['problem_solving_score'] = ps_base.clip(0, 1)

    # Self-regulation score: influenced by distraction resistance, focus, task completion
    sr_base = (
        0.35 * data['distraction_resistance'] +
        0.25 * data['task_completion_rate'] +
        0.15 * (data['focus_duration'] / 600) +  # Normalize
        0.1 * (1 - data['retry_count'] / 20) +  # Fewer retries = better regulation
        0.15 * np.random.random(n_samples)
    )
    data['self_regulation_score'] = sr_base.clip(0, 1)

    # Resilience score: influenced by recovery rate, retry count, perseverance
    resilience_base = (
        0.3 * data['recovery_rate'] +
        0.25 * data['perseverance_indicators'] +
        0.15 * (data['retry_count'] / 20) +  # More retries can indicate resilience
        0.15 * data['task_completion_rate'] +
        0.15 * np.random.random(n_samples)
    )
    data['resilience_score'] = resilience_base.clip(0, 1)

    # Create DataFrame
    df = pd.DataFrame(data)

    return df


def split_data(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    Split data into train, validation, and test sets.

    Args:
        df: Full dataset
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for test

    Returns:
        train_df, val_df, test_df
    """
    from sklearn.model_selection import train_test_split

    # First split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df, test_size=(1 - train_ratio), random_state=42
    )

    # Second split: val vs test
    val_size = val_ratio / (val_ratio + test_ratio)
    val_df, test_df = train_test_split(
        temp_df, test_size=(1 - val_size), random_state=42
    )

    return train_df, val_df, test_df


def main():
    """Generate and save sample training data."""

    print("Generating sample training data...")

    # Generate 1000 samples
    df = generate_sample_data(n_samples=1000)

    print(f"\nGenerated {len(df)} samples")
    print(f"Features: {len(df.columns) - 5} (excluding student_id and 4 labels)")
    print(f"\nColumn names:")
    for col in df.columns:
        print(f"  - {col}")

    # Create data directory
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)

    # Split data
    train_df, val_df, test_df = split_data(df)

    print(f"\nSplit sizes:")
    print(f"  Training: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Validation: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

    # Save files
    train_path = data_dir / 'training_data.csv'
    val_path = data_dir / 'validation_data.csv'
    test_path = data_dir / 'test_data.csv'

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"\nSaved files:")
    print(f"  Training: {train_path}")
    print(f"  Validation: {val_path}")
    print(f"  Test: {test_path}")

    # Display sample statistics
    print(f"\nTarget label statistics (training set):")
    for label in ['empathy_score', 'problem_solving_score', 'self_regulation_score', 'resilience_score']:
        print(f"\n{label}:")
        print(f"  Mean: {train_df[label].mean():.3f}")
        print(f"  Std: {train_df[label].std():.3f}")
        print(f"  Min: {train_df[label].min():.3f}")
        print(f"  Max: {train_df[label].max():.3f}")

    print("\n✓ Sample data generation complete!")


if __name__ == '__main__':
    main()
