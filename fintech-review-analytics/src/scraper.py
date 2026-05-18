"""
Web scraping module for collecting fintech app reviews from Google Play Store.

Uses google-play-scraper to collect reviews, ratings, and metadata for specified apps.
Collects minimum 400+ reviews per bank application.
"""

import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd
from google_play_scraper import app, reviews_all
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BankReviewScraper:
    """
    Scraper for collecting reviews from multiple fintech apps on Google Play Store.
    
    Attributes:
        bank_apps (dict): Mapping of bank names to app package IDs
        min_reviews (int): Minimum reviews to collect per bank
    """
    
    def __init__(self, bank_apps: Dict[str, str], min_reviews: int = 400):
        """
        Initialize the scraper.
        
        Args:
            bank_apps: Dictionary mapping bank names to app package IDs
                      Example: {'HDFC Bank': 'com.hdfcbank.app', ...}
            min_reviews: Minimum number of reviews to collect per bank
        """
        self.bank_apps = bank_apps
        self.min_reviews = min_reviews
        self.all_reviews = []
        
    def scrape_bank_reviews(self, package_id: str, bank_name: str) -> pd.DataFrame:
        """
        Scrape all reviews for a single bank app.
        
        Args:
            package_id: Google Play Store package ID for the app
            bank_name: Human-readable bank name
            
        Returns:
            DataFrame containing reviews with normalized fields
        """
        logger.info(f"Scraping reviews for {bank_name} ({package_id})...")
        
        try:
            # Use reviews_all to get all available reviews
            reviews_data = reviews_all(
                app_id=package_id,
                sleep_milliseconds=100,
                language='en',
                country='us'
            )
            
            logger.info(f"Retrieved {len(reviews_data)} reviews for {bank_name}")
            
            # Normalize the data
            normalized_reviews = []
            for review in reviews_data:
                normalized_reviews.append({
                    'review': review.get('reviewText', ''),
                    'rating': review.get('score', 0),
                    'date': review.get('at', datetime.now()).strftime('%Y-%m-%d'),
                    'bank': bank_name,
                    'source': 'Google Play',
                    'reviewer_id': review.get('reviewId', ''),
                    'app_version': review.get('appVersion', ''),
                })
            
            df = pd.DataFrame(normalized_reviews)
            logger.info(f"Normalized {len(df)} reviews for {bank_name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error scraping {bank_name}: {str(e)}")
            return pd.DataFrame()
    
    def scrape_all_banks(self) -> pd.DataFrame:
        """
        Scrape reviews for all configured bank apps.
        
        Returns:
            Combined DataFrame with reviews from all banks
        """
        all_reviews_list = []
        
        for bank_name, package_id in tqdm(self.bank_apps.items(), 
                                          desc="Scraping banks"):
            df = self.scrape_bank_reviews(package_id, bank_name)
            
            if len(df) < self.min_reviews:
                logger.warning(
                    f"{bank_name}: Only {len(df)} reviews found "
                    f"(target: {self.min_reviews}). Consider expanding date range."
                )
            
            all_reviews_list.append(df)
        
        combined_df = pd.concat(all_reviews_list, ignore_index=True)
        logger.info(f"Total reviews collected: {len(combined_df)}")
        
        return combined_df
    
    def get_scraping_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for the scraping session.
        
        Args:
            df: DataFrame with scraped reviews
            
        Returns:
            Dictionary with summary metrics
        """
        summary = {
            'total_reviews': len(df),
            'banks_covered': df['bank'].nunique(),
            'reviews_by_bank': df['bank'].value_counts().to_dict(),
            'avg_rating': df['rating'].mean(),
            'rating_distribution': df['rating'].value_counts().sort_index().to_dict(),
            'date_range': f"{df['date'].min()} to {df['date'].max()}",
        }
        return summary


if __name__ == "__main__":
    # Example usage - Configure these with actual bank app IDs
    BANK_APPS = {
        'HDFC Bank': 'com.hdfcbank.app',
        'ICICI Bank': 'com.icicibank.imobile',
        'Axis Bank': 'com.axisinc.android',
    }
    
    scraper = BankReviewScraper(BANK_APPS, min_reviews=400)
    reviews_df = scraper.scrape_all_banks()
    
    # Display summary
    summary = scraper.get_scraping_summary(reviews_df)
    logger.info(f"Scraping Summary: {summary}")
    
    # Save raw data
    reviews_df.to_csv('data/raw/reviews_raw.csv', index=False)
    logger.info("Raw reviews saved to data/raw/reviews_raw.csv")
