"""
Thematic analysis module for fintech reviews.

Extracts themes/topics from reviews using:
- TF-IDF for keyword importance
- spaCy for NLP processing
- Manual grouping into business-relevant themes
"""

import logging
from typing import Dict, List, Set, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import spacy
from collections import Counter

logger = logging.getLogger(__name__)

# Pre-defined theme taxonomy (customizable)
THEMES = {
    'account_access': {
        'keywords': ['login', 'password', 'authentication', 'sign in', 'account', 'access', 'otp', 'verification'],
        'description': 'Account Access Issues'
    },
    'transaction_performance': {
        'keywords': ['transfer', 'payment', 'slow', 'delay', 'pending', 'transaction', 'process', 'confirm'],
        'description': 'Transaction Performance & Speed'
    },
    'ui_design': {
        'keywords': ['ui', 'design', 'interface', 'layout', 'navigation', 'button', 'menu', 'app', 'easy', 'intuitive'],
        'description': 'UI & Design Quality'
    },
    'customer_support': {
        'keywords': ['support', 'help', 'customer service', 'contact', 'response', 'helpline', 'chat', 'resolve'],
        'description': 'Customer Support & Service'
    },
    'feature_requests': {
        'keywords': ['feature', 'add', 'request', 'wish', 'missing', 'need', 'want', 'should', 'option'],
        'description': 'Feature Requests & Enhancement'
    },
    'bugs_crashes': {
        'keywords': ['bug', 'crash', 'error', 'problem', 'issue', 'broken', 'fail', 'exception', 'hang'],
        'description': 'Bugs, Crashes & Technical Issues'
    },
}


class ThematicAnalyzer:
    """
    Extract themes from review texts using TF-IDF and keyword matching.
    """
    
    def __init__(self, language: str = 'en_core_web_sm'):
        """
        Initialize thematic analyzer.
        
        Args:
            language: spaCy language model to load
        """
        logger.info(f"Loading spaCy model: {language}")
        try:
            self.nlp = spacy.load(language)
        except OSError:
            logger.warning(f"spaCy model {language} not found. Install with:")
            logger.warning(f"  python -m spacy download {language}")
            self.nlp = None
        
        self.themes = THEMES
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text: tokenization, lemmatization, stop-word removal.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            List of processed tokens
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return []
        
        # Use spaCy if available, otherwise simple processing
        if self.nlp:
            doc = self.nlp(text.lower())
            tokens = [
                token.lemma_ for token in doc 
                if not token.is_stop and token.is_alpha
            ]
        else:
            # Fallback: simple tokenization
            tokens = text.lower().split()
        
        return tokens
    
    def extract_tfidf_keywords(self, df: pd.DataFrame, 
                               text_column: str = 'review',
                               top_n: int = 50) -> Dict[str, List[Tuple[str, float]]]:
        """
        Extract TF-IDF keywords by bank.
        
        Args:
            df: DataFrame with review texts
            text_column: Column containing review text
            top_n: Number of top keywords to extract per bank
            
        Returns:
            Dictionary mapping bank -> [(keyword, score), ...]
        """
        logger.info("Extracting TF-IDF keywords by bank...")
        
        keywords_by_bank = {}
        
        for bank in df['bank'].unique():
            bank_reviews = df[df['bank'] == bank][text_column].tolist()
            
            # Fit TF-IDF on bank-specific reviews
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            try:
                tfidf_matrix = vectorizer.fit_transform(bank_reviews)
                feature_names = vectorizer.get_feature_names_out()
                
                # Get mean TF-IDF scores
                tfidf_scores = tfidf_matrix.mean(axis=0).A1
                
                # Get top N keywords
                top_indices = np.argsort(tfidf_scores)[-top_n:][::-1]
                top_keywords = [
                    (feature_names[i], float(tfidf_scores[i]))
                    for i in top_indices
                ]
                
                keywords_by_bank[bank] = top_keywords
                logger.info(f"{bank}: Extracted {len(top_keywords)} keywords")
                
            except Exception as e:
                logger.error(f"Error extracting keywords for {bank}: {str(e)}")
                keywords_by_bank[bank] = []
        
        return keywords_by_bank
    
    def assign_theme(self, text: str) -> str:
        """
        Assign a review to a theme based on keyword matching.
        
        Args:
            text: Review text
            
        Returns:
            Theme identifier (or 'other' if no match)
        """
        text_lower = text.lower()
        
        # Check each theme's keywords
        theme_scores = {}
        
        for theme_id, theme_info in self.themes.items():
            keywords = theme_info['keywords']
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                theme_scores[theme_id] = matches
        
        # Return highest-scoring theme
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        else:
            return 'other'
    
    def analyze_themes(self, df: pd.DataFrame, 
                      text_column: str = 'review') -> pd.DataFrame:
        """
        Assign themes to all reviews.
        
        Args:
            df: DataFrame with reviews
            text_column: Column containing review text
            
        Returns:
            DataFrame with added 'theme' column
        """
        logger.info(f"Assigning themes to {len(df)} reviews...")
        
        themes = []
        for idx, text in enumerate(df[text_column]):
            if idx % 200 == 0 and idx > 0:
                logger.info(f"Processed {idx}/{len(df)} reviews...")
            
            theme = self.assign_theme(str(text))
            themes.append(theme)
        
        df['identified_theme'] = themes
        logger.info("Theme assignment complete")
        
        return df
    
    def get_theme_statistics(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Generate statistics on theme distribution by bank.
        
        Args:
            df: DataFrame with theme assignments
            
        Returns:
            Dictionary with theme statistics per bank
        """
        stats = {}
        
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            theme_counts = bank_df['identified_theme'].value_counts()
            
            stats[bank] = {
                'total_reviews': len(bank_df),
                'themes_distribution': theme_counts.to_dict(),
                'dominant_theme': theme_counts.index[0] if len(theme_counts) > 0 else 'unknown',
                'theme_coverage': (
                    (bank_df['identified_theme'] != 'other').sum() / len(bank_df) * 100
                ),
            }
        
        return stats
    
    def get_theme_description(self, theme_id: str) -> str:
        """Get human-readable description of a theme."""
        return self.themes.get(theme_id, {}).get('description', theme_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load sentiment data
    logger.info("Loading sentiment-analyzed reviews...")
    df = pd.read_csv('data/processed/sentiment_intermediate.csv')
    
    # Analyze themes
    analyzer = ThematicAnalyzer()
    
    # Extract TF-IDF keywords
    keywords = analyzer.extract_tfidf_keywords(df)
    
    # Assign themes
    df_with_themes = analyzer.analyze_themes(df)
    
    # Save results
    df_with_themes.to_csv('data/processed/sentiment_themes.csv', index=False)
    logger.info("Results saved to data/processed/sentiment_themes.csv")
    
    # Generate statistics
    stats = analyzer.get_theme_statistics(df_with_themes)
    
    logger.info("=" * 60)
    logger.info("THEME DISTRIBUTION BY BANK")
    logger.info("=" * 60)
    for bank, bank_stats in stats.items():
        logger.info(f"\n{bank}:")
        logger.info(f"  Total reviews: {bank_stats['total_reviews']}")
        logger.info(f"  Theme coverage: {bank_stats['theme_coverage']:.1f}%")
        logger.info(f"  Dominant theme: {analyzer.get_theme_description(bank_stats['dominant_theme'])}")
        logger.info("  Distribution:")
        for theme, count in sorted(bank_stats['themes_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
            pct = (count / bank_stats['total_reviews'] * 100)
            logger.info(f"    {analyzer.get_theme_description(theme)}: {count} ({pct:.1f}%)")
    
    logger.info("\n" + "=" * 60)
    logger.info("TOP TF-IDF KEYWORDS BY BANK")
    logger.info("=" * 60)
    for bank, keywords_list in keywords.items():
        logger.info(f"\n{bank}:")
        for keyword, score in keywords_list[:10]:
            logger.info(f"  {keyword}: {score:.4f}")
