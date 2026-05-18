"""
Sentiment analysis module for fintech reviews.

Uses VADER for sentiment classification (positive, negative, neutral).
Provides confidence scores and aggregation by bank/rating.
"""

import logging
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analysis for reviews using VADER.
    
    Uses VADER (Valence Aware Dictionary and sEntiment Reasoner)
    for multi-class sentiment classification.
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with VADER."""
        logger.info("Initializing VADER sentiment analyzer")
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER analyzer ready")
    
    def classify_sentiment(self, text: str) -> Dict:
        """
        Classify sentiment of a single review using VADER.
        
        Args:
            text: Review text to classify
            
        Returns:
            Dictionary with label and score
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return {'label': 'NEUTRAL', 'score': 0.5, 'compound': 0.0}
        
        try:
            scores = self.analyzer.polarity_scores(str(text))
            compound = scores['compound']
            
            # Classify based on compound score
            if compound >= 0.05:
                label = 'POSITIVE'
                score = scores['pos']
            elif compound <= -0.05:
                label = 'NEGATIVE'
                score = scores['neg']
            else:
                label = 'NEUTRAL'
                score = scores['neu']
            
            return {'label': label, 'score': score, 'compound': compound}
        except Exception as e:
            logger.error(f"Error classifying text: {str(e)}")
            return {'label': 'NEUTRAL', 'score': 0.5, 'compound': 0.0}
    
    def normalize_label(self, label: str) -> str:
        """
        Normalize labels to lowercase.
        
        Args:
            label: Raw label from model
            
        Returns:
            Normalized label
        """
        return label.lower()
    
    def analyze_reviews(self, df: pd.DataFrame, 
                       text_column: str = 'review_text') -> pd.DataFrame:
        """
        Analyze sentiment for all reviews in DataFrame.
        
        Args:
            df: DataFrame with reviews
            text_column: Column name containing review text
            
        Returns:
            DataFrame with added sentiment columns
        """
        logger.info(f"Analyzing sentiment for {len(df)} reviews...")
        
        sentiments = []
        scores = []
        compounds = []
        
        for idx, text in enumerate(df[text_column]):
            if idx % 200 == 0 and idx > 0:
                logger.info(f"Processed {idx}/{len(df)} reviews...")
            
            result = self.classify_sentiment(str(text))
            label = self.normalize_label(result['label'])
            score = result['score']
            compound = result['compound']
            
            sentiments.append(label)
            scores.append(score)
            compounds.append(compound)
        
        df_out = df.copy()
        df_out['sentiment_label'] = sentiments
        df_out['sentiment_score'] = scores
        df_out['sentiment_compound'] = compounds
        
        logger.info(f"✓ Sentiment analysis complete")
        return df_out
    
    def aggregate_by_bank(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Aggregate sentiment metrics by bank.
        
        Args:
            df: DataFrame with sentiment labels and scores
            
        Returns:
            Dictionary with aggregation statistics per bank
        """
        aggregations = {}
        
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            
            aggregations[bank] = {
                'total_reviews': len(bank_df),
                'positive_count': (bank_df['sentiment_label'] == 'positive').sum(),
                'negative_count': (bank_df['sentiment_label'] == 'negative').sum(),
                'neutral_count': (bank_df['sentiment_label'] == 'neutral').sum(),
                'mean_sentiment_score': bank_df['sentiment_score'].mean(),
                'positive_percentage': (
                    (bank_df['sentiment_label'] == 'positive').sum() / len(bank_df) * 100
                ),
                'negative_percentage': (
                    (bank_df['sentiment_label'] == 'negative').sum() / len(bank_df) * 100
                ),
            }
        
        return aggregations
    
    def aggregate_by_rating(self, df: pd.DataFrame) -> Dict[int, Dict]:
        """
        Aggregate sentiment by star rating.
        
        Useful for validating sentiment alignment with ratings.
        
        Args:
            df: DataFrame with sentiment labels and star ratings
            
        Returns:
            Dictionary with sentiment distribution per star rating
        """
        aggregations = {}
        
        for rating in sorted(df['rating'].unique()):
            rating_df = df[df['rating'] == rating]
            
            aggregations[int(rating)] = {
                'count': len(rating_df),
                'mean_sentiment_score': rating_df['sentiment_score'].mean(),
                'positive_percentage': (
                    (rating_df['sentiment_label'] == 'positive').sum() / len(rating_df) * 100
                ),
                'negative_percentage': (
                    (rating_df['sentiment_label'] == 'negative').sum() / len(rating_df) * 100
                ),
            }
        
        return aggregations
    
    def get_coverage(self, df: pd.DataFrame) -> float:
        """
        Calculate percentage of reviews with sentiment assigned.
        
        Args:
            df: DataFrame with sentiment labels
            
        Returns:
            Percentage of reviews with valid sentiment
        """
        valid = (df['sentiment_label'].notna()).sum()
        total = len(df)
        coverage = (valid / total * 100) if total > 0 else 0
        return coverage


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load cleaned data
    logger.info("Loading cleaned reviews...")
    df = pd.read_csv('data/processed/reviews_cleaned.csv')
    
    # Analyze sentiment
    analyzer = SentimentAnalyzer()
    df_with_sentiment = analyzer.analyze_reviews(df)
    
    # Save intermediate results
    df_with_sentiment.to_csv('data/processed/sentiment_intermediate.csv', index=False)
    logger.info("Sentiment analysis saved to data/processed/sentiment_intermediate.csv")
    
    # Generate reports
    coverage = analyzer.get_coverage(df_with_sentiment)
    logger.info(f"Sentiment coverage: {coverage:.2f}%")
    
    bank_agg = analyzer.aggregate_by_bank(df_with_sentiment)
    rating_agg = analyzer.aggregate_by_rating(df_with_sentiment)
    
    logger.info("=" * 60)
    logger.info("SENTIMENT AGGREGATION BY BANK")
    logger.info("=" * 60)
    for bank, stats in bank_agg.items():
        logger.info(f"\n{bank}:")
        for key, value in stats.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info("SENTIMENT AGGREGATION BY RATING")
    logger.info("=" * 60)
    for rating, stats in rating_agg.items():
        logger.info(f"\nRating {rating} stars:")
        for key, value in stats.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
