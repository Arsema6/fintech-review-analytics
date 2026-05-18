import pandas as pd
from collections import Counter
import re

df = pd.read_csv('data/processed/sentiment_results.csv')

# Define key theme keywords
themes = {
    'UI/UX': ['interface', 'design', 'layout', 'navigation', 'user-friendly', 'intuitive', 'smooth', 'easy', 'simple', 'clean'],
    'Performance': ['fast', 'speed', 'slow', 'crash', 'lag', 'responsive', 'loading', 'freeze'],
    'Security': ['secure', 'safe', 'hack', 'fraud', 'authentication', 'password', 'encryption', 'trust'],
    'Features': ['feature', 'functionality', 'capability', 'transfer', 'payment', 'bill', 'loan', 'investment'],
    'Customer Service': ['support', 'customer service', 'help', 'responsive', 'team', 'communication', 'assistance'],
    'Reliability': ['reliable', 'stable', 'consistent', 'crash', 'bug', 'issue', 'problem', 'error']
}

# Analyze themes by bank
for bank in df['bank'].unique():
    bank_df = df[df['bank'] == bank]
    print(f'\n=== {bank} Bank ===')
    print(f'Total reviews: {len(bank_df)}')
    print(f'Average rating: {bank_df["rating"].mean():.2f}')
    print(f'Avg sentiment score: {bank_df["sentiment_score"].mean():.3f}')
    
    # Positive reviews themes
    pos_reviews = bank_df[bank_df['sentiment_label'] == 'positive']['review'].str.lower()
    print(f'\nPositive reviews themes:')
    for theme, keywords in themes.items():
        count = sum(pos_reviews.str.contains('|'.join(keywords), na=False))
        if count > 0:
            print(f'  {theme}: {count} mentions')
    
    # Negative reviews themes
    neg_reviews = bank_df[bank_df['sentiment_label'] == 'negative']['review'].str.lower()
    print(f'Negative reviews themes:')
    for theme, keywords in themes.items():
        count = sum(neg_reviews.str.contains('|'.join(keywords), na=False))
        if count > 0:
            print(f'  {theme}: {count} mentions')
