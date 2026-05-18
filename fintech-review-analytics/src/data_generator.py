"""
Data generator for simulating Google Play Store reviews
Creates realistic sample data for three Ethiopian banks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

# Sample reviews data by bank and sentiment
REVIEWS_DATA = {
    "CBE": {
        "positive": [
            "Fast and reliable transfers, excellent app!",
            "Love the new interface, very intuitive",
            "Great security features, feels safe using this app",
            "Quick transaction processing, impressed!",
            "Smooth user experience, highly recommend",
            "Best fintech app in Ethiopia, well done",
            "Easy to navigate, very user-friendly",
            "Fast money transfer, no issues",
            "Excellent customer service integration",
            "App never crashes, very stable",
            "Perfect for business transactions",
            "Love the UI design, modern and clean",
            "Transactions are instant, very satisfying",
            "Great balance between security and speed",
            "The app is responsive and never lags",
        ],
        "negative": [
            "App crashes frequently during peak hours",
            "Slow loading times, very frustrating",
            "OTP never arrives, can't complete transactions",
            "Login errors too often",
            "Poor customer support response",
            "Keeps asking for biometric when not needed",
            "Balance not updating in real time",
            "Too many verification steps",
            "App is slow on slow network",
            "Frequent server errors",
            "Transaction fees are too high",
            "Can't reset password easily",
            "App freezes when checking balance",
            "Notifications delayed",
            "Support team very slow to respond",
        ],
        "neutral": [
            "Regular banking app, does the job",
            "Same as other banks' apps",
            "Nothing special but works",
            "Average performance",
            "Standard features available",
            "It's okay for basic transactions",
            "Nothing impressive",
            "Typical fintech app",
            "Does what it says",
            "No complaints but no praise either",
        ]
    },
    "BOA": {
        "positive": [
            "Finally, fingerprint login works great!",
            "Better UI than before, much improved",
            "Quick transaction settlement",
            "Mobile wallet feature is excellent",
            "Great budgeting tools built in",
            "Money transfer is seamless",
            "Love the transaction history feature",
            "Support team is responsive",
            "Secure and fast",
            "Best update yet",
            "Simple and straightforward",
            "Great investment features",
            "Easy bill payment",
            "Quick account opening",
            "Excellent notifications",
        ],
        "negative": [
            "Still slow compared to competitors",
            "Constantly getting authentication errors",
            "App freezes when checking balance",
            "Feature requests never implemented",
            "Very outdated interface",
            "Charges hidden fees without notice",
            "Password reset never works",
            "Support is unresponsive",
            "App consumes too much battery",
            "Data syncing is unreliable",
            "Hard to reach support team",
            "Limited features compared to others",
            "Transaction fees are high",
            "App outdated looking",
            "Slow money transfer sometimes",
        ],
        "neutral": [
            "It's a banking app",
            "Works for basic transactions",
            "No issues but nothing great",
            "Standard features",
            "Adequate functionality",
            "Okay for banking",
            "Middle of the road app",
            "Does what it's supposed to",
            "Average experience",
            "Normal functionality",
        ]
    },
    "Dashen": {
        "positive": [
            "Fastest app among the three banks",
            "Very responsive customer support",
            "Clean and modern design",
            "No lag issues experienced",
            "Great investment features",
            "Easy bill payment",
            "Quick account opening",
            "Excellent notifications",
            "Reliable service",
            "Best security updates",
            "Professional interface",
            "Smooth transactions",
            "Quick loading times",
            "Great user support",
            "Beautiful UI design",
        ],
        "negative": [
            "Hard to reach support team",
            "Limited features compared to others",
            "Transaction fees are high",
            "App outdated looking",
            "Slow money transfer sometimes",
            "Can't change PIN easily",
            "Limited payment options",
            "Interface is confusing",
            "No savings goals feature",
            "Notification delays",
            "Very expensive",
            "Limited transaction history",
            "No budgeting tools",
            "Few investment options",
            "Poor fund transfer UX",
        ],
        "neutral": [
            "Okay for banking",
            "Middle of the road app",
            "Does what it's supposed to",
            "Average experience",
            "Normal functionality",
            "Standard app",
            "Nothing special",
            "Adequate service",
            "Good enough",
            "Passable application",
        ]
    }
}

RATINGS_BY_SENTIMENT = {
    "positive": [4, 5, 5, 5, 4, 5, 4, 5, 4, 5],
    "negative": [1, 1, 2, 1, 2, 1, 2, 1, 1, 2],
    "neutral": [3, 3, 3, 2, 3]
}

def generate_sample_reviews(output_dir='data/raw', reviews_per_bank=400):
    """
    Generate realistic sample review data for all three banks
    
    Parameters:
    -----------
    output_dir : str
        Directory to save generated reviews
    reviews_per_bank : int
        Number of reviews per bank
    
    Returns:
    --------
    pd.DataFrame : DataFrame with generated reviews
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    reviews_list = []
    start_date = datetime.now() - timedelta(days=365)
    
    for bank_name in ["CBE", "BOA", "Dashen"]:
        for i in range(reviews_per_bank):
            # Distribute sentiments: 50% positive, 30% negative, 20% neutral
            rand = random.random()
            if rand < 0.50:
                sentiment = "positive"
            elif rand < 0.80:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Select review text and rating
            review_text = random.choice(REVIEWS_DATA[bank_name][sentiment])
            # Add variation to review text to reduce duplicates
            variations = [
                review_text,
                review_text + " Highly satisfied.",
                "I " + review_text.lower(),
                review_text + " 👍",
                review_text[:-1] if review_text.endswith("!") else review_text,
            ]
            review_text = random.choice(variations)
            
            rating = random.choice(RATINGS_BY_SENTIMENT[sentiment])
            
            # Generate date within past year
            review_date = start_date + timedelta(days=random.randint(0, 365))
            
            reviews_list.append({
                'review_id': f"{bank_name}_{i}_{review_date.timestamp()}",
                'review_text': review_text,
                'rating': rating,
                'review_date': review_date.strftime('%Y-%m-%d'),
                'bank': bank_name,
                'source': 'Google Play Store',
                'author': f"User_{random.randint(1000, 9999)}",
                'helpful_count': random.randint(0, 50)
            })
    
    df = pd.DataFrame(reviews_list)
    
    # Save raw data
    output_path = Path(output_dir) / 'reviews_raw.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Generated {len(df)} sample reviews saved to {output_path}")
    
    return df

if __name__ == "__main__":
    df = generate_sample_reviews()
    print(f"\n✓ Successfully generated {len(df)} reviews!")
    print(df.head())
