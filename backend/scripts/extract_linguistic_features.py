"""
Extract linguistic features from student responses.

This script processes student text responses and extracts 16 linguistic features
using NLP techniques (spaCy, NLTK, TextBlob).

Features extracted:
- Skill-specific language markers (3)
- Psychological process markers (2)
- Sentiment scores (2)
- Linguistic complexity metrics (9)

Usage:
    python scripts/extract_linguistic_features.py --input data/synthetic_responses.csv --output data/linguistic_features.csv
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# NLP libraries
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️  spaCy not installed. Install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    # Download required NLTK data
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        print("📥 Downloading NLTK VADER lexicon...")
        nltk.download('vader_lexicon', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not installed. Install with: pip install nltk")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️  TextBlob not installed. Install with: pip install textblob")


class LinguisticFeatureExtractor:
    """Extract linguistic features from text."""

    def __init__(self):
        """Initialize NLP models."""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️  spaCy model not found. Downloading en_core_web_sm...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")

        self.sia = None
        if NLTK_AVAILABLE:
            self.sia = SentimentIntensityAnalyzer()

        # Define keyword lists
        self.empathy_words = {
            'feel', 'feeling', 'feelings', 'felt', 'understand', 'care', 'caring',
            'help', 'helped', 'helping', 'support', 'concern', 'worried', 'compassionate',
            'empathize', 'sympathy', 'kind', 'kindness', 'comfort', 'listen', 'listened'
        }

        self.problem_solving_words = {
            'solve', 'solved', 'solution', 'analyze', 'think', 'thought', 'thinking',
            'figure', 'figured', 'plan', 'planned', 'planning', 'strategy', 'approach',
            'method', 'idea', 'ideas', 'try', 'tried', 'attempt', 'work', 'fix', 'fixed'
        }

        self.perseverance_words = {
            'try', 'tried', 'trying', 'persist', 'persisted', 'continue', 'continued',
            'keep', 'kept', 'again', 'practice', 'practiced', 'determined', 'effort',
            'work', 'worked', 'working', 'challenge', 'difficult', 'hard', 'struggle'
        }

        self.social_words = {
            'we', 'us', 'our', 'friend', 'friends', 'together', 'team', 'group',
            'share', 'shared', 'talk', 'talked', 'talking', 'tell', 'told', 'people',
            'classmate', 'partner', 'everyone', 'someone', 'class'
        }

        self.cognitive_words = {
            'think', 'thought', 'know', 'knew', 'understand', 'understood', 'realize',
            'realized', 'consider', 'wondered', 'remember', 'forgot', 'learn', 'learned',
            'believe', 'believed', 'notice', 'noticed', 'recognize'
        }

    def count_word_frequency(self, text: str, word_set: set) -> float:
        """
        Calculate frequency of specific words in text.

        Args:
            text: Input text
            word_set: Set of words to count

        Returns:
            Frequency (count / total_words)
        """
        words = text.lower().split()
        if not words:
            return 0.0

        count = sum(1 for word in words if word in word_set)
        return count / len(words)

    def extract_features(self, text: str) -> Dict[str, float]:
        """
        Extract all 16 linguistic features from text.

        Args:
            text: Student response text

        Returns:
            Dictionary of features
        """
        if not text or not isinstance(text, str):
            return self._empty_features()

        features = {}

        # 1. Skill-specific language markers
        features['empathy_markers'] = self.count_word_frequency(text, self.empathy_words)
        features['problem_solving_language'] = self.count_word_frequency(text, self.problem_solving_words)
        features['perseverance_indicators'] = self.count_word_frequency(text, self.perseverance_words)

        # 2. Psychological process markers
        features['social_processes'] = self.count_word_frequency(text, self.social_words)
        features['cognitive_processes'] = self.count_word_frequency(text, self.cognitive_words)

        # 3. Sentiment scores
        if self.sia:
            sentiment = self.sia.polarity_scores(text)
            features['positive_sentiment'] = sentiment['pos']
            features['negative_sentiment'] = sentiment['neg']
        else:
            features['positive_sentiment'] = 0.0
            features['negative_sentiment'] = 0.0

        # 4. Linguistic complexity metrics
        if self.nlp:
            doc = self.nlp(text)

            # Sentence length
            sentences = list(doc.sents)
            if sentences:
                features['avg_sentence_length'] = len(doc) / len(sentences)
            else:
                features['avg_sentence_length'] = len(doc)

            # Syntactic complexity (depth of parse tree)
            features['syntactic_complexity'] = self._calculate_syntactic_complexity(doc)

            # Word counts
            features['word_count'] = len(doc)
            features['unique_word_count'] = len(set(token.text.lower() for token in doc if token.is_alpha))

            # POS counts
            features['noun_count'] = sum(1 for token in doc if token.pos_ == 'NOUN')
            features['verb_count'] = sum(1 for token in doc if token.pos_ == 'VERB')
            features['adj_count'] = sum(1 for token in doc if token.pos_ == 'ADJ')
            features['adv_count'] = sum(1 for token in doc if token.pos_ == 'ADV')

        else:
            # Fallback: simple word-based metrics
            words = text.split()
            features['word_count'] = len(words)
            features['unique_word_count'] = len(set(w.lower() for w in words))
            features['avg_sentence_length'] = features['word_count'] / max(1, text.count('.') + text.count('!') + text.count('?'))
            features['syntactic_complexity'] = 0.0
            features['noun_count'] = 0.0
            features['verb_count'] = 0.0
            features['adj_count'] = 0.0
            features['adv_count'] = 0.0

        # Readability score (simple approximation)
        if TEXTBLOB_AVAILABLE:
            blob = TextBlob(text)
            # Flesch Reading Ease approximation
            features['readability_score'] = self._calculate_readability(text)
        else:
            features['readability_score'] = 50.0  # Neutral default

        return features

    def _calculate_syntactic_complexity(self, doc) -> float:
        """
        Calculate syntactic complexity as average dependency tree depth.

        Args:
            doc: spaCy Doc object

        Returns:
            Average tree depth
        """
        def get_depth(token):
            depth = 0
            current = token
            while current.head != current:
                depth += 1
                current = current.head
            return depth

        if len(doc) == 0:
            return 0.0

        depths = [get_depth(token) for token in doc]
        return sum(depths) / len(depths)

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate Flesch Reading Ease score.

        Args:
            text: Input text

        Returns:
            Readability score (0-100, higher = easier)
        """
        sentences = text.count('.') + text.count('!') + text.count('?')
        sentences = max(1, sentences)

        words = len(text.split())
        if words == 0:
            return 50.0

        syllables = self._count_syllables(text)

        # Flesch Reading Ease formula
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0, min(100, score))

    def _count_syllables(self, text: str) -> int:
        """Simple syllable counter."""
        vowels = 'aeiouy'
        syllables = 0
        words = text.lower().split()

        for word in words:
            word = word.strip('.,!?;:')
            if len(word) == 0:
                continue

            count = 0
            previous_was_vowel = False

            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    count += 1
                previous_was_vowel = is_vowel

            # Adjust for silent e
            if word.endswith('e'):
                count -= 1

            syllables += max(1, count)

        return syllables

    def _empty_features(self) -> Dict[str, float]:
        """Return empty feature dict with zeros."""
        return {
            'empathy_markers': 0.0,
            'problem_solving_language': 0.0,
            'perseverance_indicators': 0.0,
            'social_processes': 0.0,
            'cognitive_processes': 0.0,
            'positive_sentiment': 0.0,
            'negative_sentiment': 0.0,
            'avg_sentence_length': 0.0,
            'syntactic_complexity': 0.0,
            'word_count': 0.0,
            'unique_word_count': 0.0,
            'readability_score': 50.0,
            'noun_count': 0.0,
            'verb_count': 0.0,
            'adj_count': 0.0,
            'adv_count': 0.0,
        }

    def process_dataset(self, df: pd.DataFrame, text_column: str = 'response') -> pd.DataFrame:
        """
        Extract features for entire dataset.

        Args:
            df: DataFrame with text responses
            text_column: Name of column containing text

        Returns:
            DataFrame with added feature columns
        """
        print(f"🔍 Extracting linguistic features from {len(df)} responses...")

        features_list = []
        for idx, text in enumerate(df[text_column]):
            if idx % 100 == 0 and idx > 0:
                print(f"   Processed {idx}/{len(df)} responses...")

            features = self.extract_features(text)
            features_list.append(features)

        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)

        # Combine with original DataFrame
        result = pd.concat([df.reset_index(drop=True), features_df], axis=1)

        print(f"✅ Extracted {len(features_df.columns)} linguistic features")

        # Show feature statistics
        print(f"\n📊 Feature Statistics:")
        print(features_df.describe().round(3))

        return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract linguistic features from student responses"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input CSV file with responses",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output CSV file with features",
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="response",
        help="Name of column containing text (default: response)",
    )

    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    print(f"   Loaded {len(df)} responses")

    # Extract features
    extractor = LinguisticFeatureExtractor()
    result_df = extractor.process_dataset(df, text_column=args.text_column)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)

    print(f"\n💾 Saved to {output_path}")
    print(f"   Total columns: {len(result_df.columns)}")


if __name__ == "__main__":
    main()
