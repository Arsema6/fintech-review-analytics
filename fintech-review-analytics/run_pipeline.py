"""
Main data pipeline orchestration script.

Coordinates all steps:
1. Generate/load raw data
2. Preprocess
3. Sentiment analysis
4. Database insertion
5. Create visualizations
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_generator import generate_sample_reviews
from src.preprocessor import ReviewPreprocessor
from src.sentiment import SentimentAnalyzer
from src.visualizations import create_visualizations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main_pipeline():
    """Execute complete data pipeline"""
    
    logger.info("\n" + "="*80)
    logger.info(" FINTECH REVIEW ANALYTICS - COMPLETE PIPELINE")
    logger.info("="*80)
    
    # Step 1: Generate/Load Raw Data
    logger.info("\n[STEP 1/5] GENERATING SAMPLE REVIEWS DATA")
    logger.info("-" * 80)
    df_raw = generate_sample_reviews(output_dir='data/raw', reviews_per_bank=400)
    logger.info(f"✓ Generated {len(df_raw)} reviews from 3 banks")
    logger.info(f"  Reviews per bank: {df_raw['bank'].value_counts().to_dict()}")
    
    # Step 2: Preprocess Data
    logger.info("\n[STEP 2/5] PREPROCESSING DATA")
    logger.info("-" * 80)
    preprocessor = ReviewPreprocessor(
        input_path='data/raw/reviews_raw.csv',
        output_path='data/processed/reviews_cleaned.csv'
    )
    df_cleaned = preprocessor.preprocess()
    logger.info(f"✓ Preprocessing complete: {len(df_cleaned)} clean reviews")
    report = preprocessor.get_report()
    logger.info(f"  Initial records: {report.get('initial_records', 'N/A')}")
    logger.info(f"  Final records: {report.get('final_records', 'N/A')}")
    logger.info(f"  Duplicates removed: {report.get('duplicates_removed', 'N/A')}")
    
    # Step 3: Sentiment Analysis
    logger.info("\n[STEP 3/5] SENTIMENT ANALYSIS")
    logger.info("-" * 80)
    analyzer = SentimentAnalyzer()
    
    # Analyze each review
    sentiment_results = []
    for idx, row in df_cleaned.iterrows():
        review_text = row.get('review', row.get('review_text', ''))
        result = analyzer.classify_sentiment(review_text)
        sentiment_results.append(result)
    
    df_sentiment = df_cleaned.copy()
    df_sentiment['sentiment_label'] = [r['label'].lower() for r in sentiment_results]
    df_sentiment['sentiment_score'] = [r['score'] for r in sentiment_results]
    df_sentiment['sentiment_compound'] = [r['compound'] for r in sentiment_results]
    df_sentiment.to_csv('data/processed/sentiment_results.csv', index=False)
    logger.info(f"✓ Sentiment analysis complete")
    
    # Print sentiment statistics
    sentiment_stats = analyzer.aggregate_by_bank(df_sentiment)
    logger.info("\nSentiment Statistics by Bank:")
    for bank, stats in sentiment_stats.items():
        logger.info(f"\n  {bank}:")
        logger.info(f"    Total Reviews: {stats['total_reviews']}")
        logger.info(f"    Positive: {stats['positive_count']} ({stats['positive_percentage']:.1f}%)")
        logger.info(f"    Negative: {stats['negative_count']}")
        logger.info(f"    Neutral: {stats['neutral_count']}")
        logger.info(f"    Avg Sentiment Score: {stats['mean_sentiment_score']:.3f}")
    
    # Step 4: Create Visualizations
    logger.info("\n[STEP 4/5] CREATING VISUALIZATIONS")
    logger.info("-" * 80)
    viz = create_visualizations(
        data_file='data/processed/sentiment_results.csv',
        output_dir='data/visualizations'
    )
    
    # Step 5: Database Operations (Optional - requires PostgreSQL)
    logger.info("\n[STEP 5/5] DATABASE OPERATIONS (OPTIONAL)")
    logger.info("-" * 80)
    logger.info("Note: Database setup requires PostgreSQL installation")
    logger.info("To use: python -c \"from src.database import setup_database; setup_database('data/processed/sentiment_results.csv')\"")
    
    # Final Summary
    logger.info("\n" + "="*80)
    logger.info(" PIPELINE EXECUTION COMPLETE")
    logger.info("="*80)
    logger.info("\nGenerated Outputs:")
    logger.info("  ✓ Raw data: data/raw/reviews_raw.csv")
    logger.info("  ✓ Cleaned data: data/processed/reviews_cleaned.csv")
    logger.info("  ✓ Sentiment analysis: data/processed/sentiment_results.csv")
    logger.info("  ✓ Visualizations: data/visualizations/")
    logger.info("\nNext Steps:")
    logger.info("  1. Review visualizations in data/visualizations/")
    logger.info("  2. Run unit tests: pytest tests/")
    logger.info("  3. Setup PostgreSQL database (optional): python -m src.database")
    logger.info("  4. Review interim report: INTERIM_REPORT.md")
    logger.info("="*80 + "\n")
    
    return df_sentiment


if __name__ == "__main__":
    df = main_pipeline()
