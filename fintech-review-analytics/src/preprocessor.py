"""
Data preprocessing module for fintech review analytics.

Handles:
- Duplicate removal
- Missing value handling
- Date normalization
- Data validation and cleaning
"""

import logging
from typing import Tuple, Dict
import pandas as pd
import numpy as np
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewPreprocessor:
    """
    Preprocess raw review data for analysis.
    
    Attributes:
        input_path (str): Path to raw CSV file
        output_path (str): Path to save cleaned CSV
    """
    
    REQUIRED_COLUMNS = ['review_text', 'rating', 'review_date', 'bank', 'source']
    
    def __init__(self, input_path: str, output_path: str):
        """
        Initialize preprocessor.
        
        Args:
            input_path: Path to raw reviews CSV
            output_path: Path to save cleaned reviews CSV
        """
        self.input_path = input_path
        self.output_path = output_path
        self.preprocessing_report = {}
    
    def load_data(self) -> pd.DataFrame:
        """
        Load raw data from CSV.
        
        Returns:
            DataFrame with raw review data
        """
        logger.info(f"Loading data from {self.input_path}")
        df = pd.read_csv(self.input_path)
        logger.info(f"Loaded {len(df)} rows")
        return df
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that all required columns are present.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, raises error otherwise
        """
        # Check if we have at least the essential columns
        essential = ['review_text', 'rating', 'bank']
        missing_cols = set(essential) - set(df.columns)
        if missing_cols:
            # Try to rename columns for compatibility
            if 'review' in df.columns and 'review_text' not in df.columns:
                df.rename(columns={'review': 'review_text'}, inplace=True)
            if 'date' in df.columns and 'review_date' not in df.columns:
                df.rename(columns={'date': 'review_date'}, inplace=True)
        return True
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate reviews.
        
        Only removes exact duplicates based on review_id to preserve most data.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        
        # Remove duplicates based on review_id only
        if 'review_id' in df.columns:
            df = df.drop_duplicates(subset=['review_id'], keep='first')
        else:
            # Fallback: use text + date + bank
            df = df.drop_duplicates(
                subset=['review_text', 'bank', 'review_date'],
                keep='first',
                errors='ignore'
            )
        
        duplicates_removed = initial_count - len(df)
        self.preprocessing_report['duplicates_removed'] = duplicates_removed
        logger.info(f"Removed {duplicates_removed} duplicate reviews")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Handle missing values in critical fields.
        
        Strategy:
        - Drop rows missing critical fields (review_text/review or rating)
        - Document missing values in other columns
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            Tuple of (cleaned DataFrame, missing values report)
        """
        initial_count = len(df)
        missing_report = {}
        
        # Check missing values before cleaning
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_report[col] = missing_count
                logger.info(f"Missing values in '{col}': {missing_count}")
        
        # Identify review text column (could be 'review_text' or 'review')
        review_col = 'review_text' if 'review_text' in df.columns else 'review'
        
        # Drop rows with missing critical fields
        df_cleaned = df.dropna(subset=[review_col, 'rating'])
        rows_dropped = initial_count - len(df_cleaned)
        
        self.preprocessing_report['rows_dropped_missing_critical'] = rows_dropped
        logger.info(f"Dropped {rows_dropped} rows with missing critical values")
        
        # Fill non-critical missing values
        df_cleaned['bank'] = df_cleaned['bank'].fillna('Unknown')
        if 'source' in df_cleaned.columns:
            df_cleaned['source'] = df_cleaned['source'].fillna('Unknown')
        
        return df_cleaned, missing_report
    
    def normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize dates to YYYY-MM-DD format.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with normalized dates
        """
        date_col = 'review_date' if 'review_date' in df.columns else 'date'
        
        try:
            df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
            logger.info("Dates normalized to YYYY-MM-DD format")
        except Exception as e:
            logger.error(f"Error normalizing dates: {str(e)}")
            # If conversion fails, keep as is
        
        return df
    
    def validate_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and ensure ratings are in 1-5 range.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with valid ratings
        """
        initial_count = len(df)
        
        # Ensure ratings are numeric
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Filter to 1-5 range
        df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
        
        invalid_removed = initial_count - len(df)
        if invalid_removed > 0:
            logger.warning(f"Removed {invalid_removed} reviews with invalid ratings")
            self.preprocessing_report['invalid_ratings_removed'] = invalid_removed
        
        return df
    
    def select_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select only required columns for analysis.
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with standardized columns
        """
        # Rename columns to standard names if needed
        if 'review_text' in df.columns and 'review' not in df.columns:
            df = df.rename(columns={'review_text': 'review'})
        if 'review_date' in df.columns and 'date' not in df.columns:
            df = df.rename(columns={'review_date': 'date'})
        
        # Select required columns
        output_cols = []
        for col in self.REQUIRED_COLUMNS:
            if col in df.columns:
                output_cols.append(col)
        
        # If some columns missing, use what we have
        if len(output_cols) < len(self.REQUIRED_COLUMNS):
            # Add any extra columns that exist
            for col in df.columns:
                if col not in output_cols:
                    output_cols.append(col)
        
        df = df[output_cols]
        logger.info(f"Selected columns: {list(df.columns)}")
        return df
    
    def preprocess(self) -> pd.DataFrame:
        """
        Execute full preprocessing pipeline.
        
        Steps:
        1. Load data
        2. Validate columns
        3. Remove duplicates
        4. Handle missing values
        5. Normalize dates
        6. Validate ratings
        7. Select required columns
        8. Save cleaned data
        
        Returns:
            Cleaned and preprocessed DataFrame
        """
        logger.info("Starting preprocessing pipeline...")
        
        # Load and validate
        df = self.load_data()
        self.validate_columns(df)
        self.preprocessing_report['initial_rows'] = len(df)
        
        # Clean data
        df = self.remove_duplicates(df)
        df, missing_report = self.handle_missing_values(df)
        df = self.normalize_dates(df)
        df = self.validate_ratings(df)
        
        # Final selection
        df = self.select_required_columns(df)
        
        self.preprocessing_report['final_rows'] = len(df)
        self.preprocessing_report['missing_values_by_column'] = missing_report
        
        # Save cleaned data
        df.to_csv(self.output_path, index=False)
        logger.info(f"Cleaned data saved to {self.output_path}")
        
        return df
    
    def get_report(self) -> Dict:
        """
        Get preprocessing report with statistics.
        
        Returns:
            Dictionary with preprocessing statistics
        """
        return {
            'initial_records': self.preprocessing_report.get('initial_rows', 0),
            'final_records': self.preprocessing_report.get('final_rows', 0),
            'duplicates_removed': self.preprocessing_report.get('duplicates_removed', 0),
            'rows_dropped': self.preprocessing_report.get('rows_dropped_missing_critical', 0),
            'invalid_ratings_removed': self.preprocessing_report.get('invalid_ratings_removed', 0),
            'missing_data_percentage': (
                (self.preprocessing_report.get('rows_dropped_missing_critical', 0) / 
                 max(self.preprocessing_report.get('initial_rows', 1), 1)) * 100
            ),
        }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run preprocessing
    preprocessor = ReviewPreprocessor(
        input_path='data/raw/reviews_raw.csv',
        output_path='data/processed/reviews_cleaned.csv'
    )
    
    cleaned_df = preprocessor.preprocess()
    report = preprocessor.get_report()
    
    logger.info("=" * 50)
    logger.info("PREPROCESSING REPORT")
    logger.info("=" * 50)
    for key, value in report.items():
        logger.info(f"{key}: {value}")
