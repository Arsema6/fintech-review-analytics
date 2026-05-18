"""
Visualization module for fintech review analytics.

Creates publication-quality charts and visualizations for insights.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ReviewVisualizations:
    """Creates visualizations from review data"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "data/visualizations"):
        """
        Initialize visualizations
        
        Args:
            df: DataFrame with reviews and sentiment
            output_dir: Directory to save visualizations
        """
        self.df = df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Visualizations output directory: {self.output_dir}")
    
    def sentiment_distribution_by_bank(self):
        """Create sentiment distribution chart by bank"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sentiment_counts = pd.crosstab(self.df['bank'], self.df['sentiment_label'])
        sentiment_counts.plot(kind='bar', ax=ax, color=['#d62728', '#2ca02c', '#ff7f0e'])
        
        ax.set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold')
        ax.set_xlabel('Bank', fontsize=12)
        ax.set_ylabel('Number of Reviews', fontsize=12)
        ax.legend(title='Sentiment', labels=['Negative', 'Neutral', 'Positive'])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / 'sentiment_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def rating_distribution_by_bank(self):
        """Create rating distribution boxplot by bank"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        self.df.boxplot(column='rating', by='bank', ax=ax)
        ax.set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold')
        ax.set_xlabel('Bank', fontsize=12)
        ax.set_ylabel('Star Rating', fontsize=12)
        plt.suptitle('')  # Remove automatic title
        
        plt.tight_layout()
        output_path = self.output_dir / 'rating_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def rating_histograms(self):
        """Create side-by-side rating histograms for each bank"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        banks = self.df['bank'].unique()
        
        for idx, bank in enumerate(banks):
            bank_df = self.df[self.df['bank'] == bank]
            axes[idx].hist(bank_df['rating'], bins=5, color='steelblue', edgecolor='black')
            axes[idx].set_title(f'{bank}', fontsize=12, fontweight='bold')
            axes[idx].set_xlabel('Rating')
            axes[idx].set_ylabel('Frequency')
            axes[idx].set_xlim(0.5, 5.5)
        
        fig.suptitle('Rating Distribution by Bank', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_path = self.output_dir / 'rating_histograms.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def average_metrics_by_bank(self):
        """Create grouped bar chart of metrics by bank"""
        bank_stats = self.df.groupby('bank').agg({
            'rating': 'mean',
            'sentiment_score': 'mean',
            'sentiment_compound': 'mean'
        }).round(2)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(bank_stats))
        width = 0.25
        
        ax.bar(x - width, bank_stats['rating'], width, label='Avg Rating', color='#1f77b4')
        ax.bar(x, bank_stats['sentiment_score'], width, label='Avg Sentiment Score', color='#ff7f0e')
        ax.bar(x + width, bank_stats['sentiment_compound'], width, label='Avg Compound Score', color='#2ca02c')
        
        ax.set_title('Average Metrics by Bank', fontsize=14, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(bank_stats.index)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / 'average_metrics.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def sentiment_by_rating_heatmap(self):
        """Create heatmap of sentiment vs rating"""
        pivot = pd.crosstab(self.df['rating'], self.df['sentiment_label'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt='d', cmap='RdYlGn', ax=ax, cbar_kws={'label': 'Count'})
        ax.set_title('Sentiment vs Star Rating', fontsize=14, fontweight='bold')
        ax.set_xlabel('Sentiment Label', fontsize=12)
        ax.set_ylabel('Star Rating', fontsize=12)
        
        plt.tight_layout()
        output_path = self.output_dir / 'sentiment_rating_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def top_words_by_bank(self, num_words=15):
        """Extract and visualize top words by bank"""
        from collections import Counter
        import re
        
        # Determine review column name
        review_col = 'review_text' if 'review_text' in self.df.columns else 'review'
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        banks = self.df['bank'].unique()
        
        for idx, bank in enumerate(banks):
            bank_df = self.df[self.df['bank'] == bank]
            
            # Extract words
            all_text = ' '.join(bank_df[review_col].astype(str))
            words = re.findall(r'\b\w{4,}\b', all_text.lower())  # Words with 4+ characters
            word_freq = Counter(words).most_common(num_words)
            
            if word_freq:
                words_list, freqs = zip(*word_freq)
                axes[idx].barh(words_list, freqs, color='steelblue')
                axes[idx].set_title(f'{bank} - Top Words', fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('Frequency')
                axes[idx].invert_yaxis()
        
        fig.suptitle('Most Frequent Words by Bank', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_path = self.output_dir / 'top_words_by_bank.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def sentiment_trend_over_time(self):
        """Create sentiment trend line chart over time"""
        df_time = self.df.copy()
        
        # Determine date column name
        date_col = 'review_date' if 'review_date' in df_time.columns else 'date'
        
        df_time[date_col] = pd.to_datetime(df_time[date_col])
        df_time = df_time.sort_values(date_col)
        
        # Create rolling average by bank
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for bank in df_time['bank'].unique():
            bank_df = df_time[df_time['bank'] == bank].set_index(date_col)
            rolling_sentiment = bank_df['sentiment_compound'].rolling(window=30).mean()
            ax.plot(rolling_sentiment.index, rolling_sentiment.values, marker='o', label=bank, linewidth=2)
        
        ax.set_title('Sentiment Trend Over Time (30-day Rolling Average)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Sentiment Compound Score', fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / 'sentiment_trend.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✓ Saved: {output_path}")
        plt.close()
    
    def create_all_visualizations(self):
        """Create all visualizations"""
        logger.info("\n" + "="*60)
        logger.info("CREATING VISUALIZATIONS")
        logger.info("="*60)
        
        self.sentiment_distribution_by_bank()
        self.rating_distribution_by_bank()
        self.rating_histograms()
        self.average_metrics_by_bank()
        self.sentiment_by_rating_heatmap()
        self.top_words_by_bank()
        self.sentiment_trend_over_time()
        
        logger.info(f"\n✓ All visualizations saved to {self.output_dir}")


def create_visualizations(data_file: str, output_dir: str = "data/visualizations"):
    """Create all visualizations from data"""
    logger.info(f"Loading data from {data_file}")
    df = pd.read_csv(data_file)
    
    viz = ReviewVisualizations(df, output_dir)
    viz.create_all_visualizations()
    
    return viz


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    data_file = sys.argv[1] if len(sys.argv) > 1 else "data/processed/sentiment_results.csv"
    create_visualizations(data_file)
