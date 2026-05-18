"""
Database setup and data insertion for PostgreSQL
Stores processed review data in relational schema
"""

import logging
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

logger = logging.getLogger(__name__)

# Database connection parameters
DB_USER = "postgres"
DB_PASSWORD = "password"  # Change this in production
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bank_reviews"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()


class Bank(Base):
    """Banks table - Stores metadata about banks"""
    __tablename__ = "banks"
    
    bank_id = Column(Integer, primary_key=True)
    bank_name = Column(String(100), unique=True, nullable=False)
    app_id = Column(String(100), nullable=True)
    reviews = relationship("Review", back_populates="bank")
    
    def __repr__(self):
        return f"<Bank(bank_id={self.bank_id}, bank_name='{self.bank_name}')>"


class Review(Base):
    """Reviews table - Stores processed review data"""
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(Integer, ForeignKey("banks.bank_id"), nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    review_date = Column(Date, nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_compound = Column(Float, nullable=True)
    identified_theme = Column(String(100), nullable=True)
    source = Column(String(100), default="Google Play Store")
    author = Column(String(100), nullable=True)
    helpful_count = Column(Integer, default=0)
    created_at = Column(Date, default=datetime.now)
    
    bank = relationship("Bank", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(review_id={self.review_id}, bank_id={self.bank_id}, rating={self.rating})>"


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_url=DATABASE_URL):
        """Initialize database manager"""
        logger.info(f"Initializing database connection to {db_url}")
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("✓ Tables created successfully")
    
    def insert_banks(self, banks_data: List[Dict]):
        """Insert bank metadata"""
        session = self.Session()
        try:
            for bank_data in banks_data:
                bank = Bank(
                    bank_name=bank_data['bank_name'],
                    app_id=bank_data.get('app_id', '')
                )
                session.add(bank)
            session.commit()
            logger.info(f"✓ Inserted {len(banks_data)} banks")
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting banks: {str(e)}")
        finally:
            session.close()
    
    def insert_reviews(self, df: pd.DataFrame, bank_name_map: Dict[str, int]):
        """Insert reviews from DataFrame"""
        session = self.Session()
        try:
            for idx, row in df.iterrows():
                bank_id = bank_name_map.get(row['bank'])
                if not bank_id:
                    logger.warning(f"Unknown bank: {row['bank']}, skipping")
                    continue
                
                review = Review(
                    bank_id=bank_id,
                    review_text=str(row.get('review_text', '')),
                    rating=int(row.get('rating', 0)),
                    review_date=pd.to_datetime(row.get('review_date', datetime.now())),
                    sentiment_label=str(row.get('sentiment_label', '')),
                    sentiment_score=float(row.get('sentiment_score', 0)),
                    sentiment_compound=float(row.get('sentiment_compound', 0)),
                    identified_theme=str(row.get('identified_theme', '')),
                    source=str(row.get('source', 'Google Play Store')),
                    author=str(row.get('author', 'Anonymous')),
                    helpful_count=int(row.get('helpful_count', 0))
                )
                session.add(review)
                
                if (idx + 1) % 500 == 0:
                    session.commit()
                    logger.info(f"Inserted {idx + 1} reviews...")
            
            session.commit()
            logger.info(f"✓ Inserted {len(df)} reviews total")
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting reviews: {str(e)}")
        finally:
            session.close()
    
    def get_bank_stats(self) -> pd.DataFrame:
        """Get statistics by bank"""
        query = """
        SELECT 
            b.bank_name,
            COUNT(r.review_id) as total_reviews,
            AVG(r.rating) as avg_rating,
            AVG(r.sentiment_score) as avg_sentiment,
            ROUND(SUM(CASE WHEN r.sentiment_label='positive' THEN 1 ELSE 0 END)::numeric / COUNT(r.review_id) * 100, 2) as positive_percentage
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_id, b.bank_name
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
    
    def verify_data(self):
        """Verify data integrity"""
        session = self.Session()
        try:
            banks_count = session.query(Bank).count()
            reviews_count = session.query(Review).count()
            logger.info(f"\n✓ DATA INTEGRITY CHECK")
            logger.info(f"  Banks: {banks_count}")
            logger.info(f"  Reviews: {reviews_count}")
            logger.info(f"  Avg reviews per bank: {reviews_count/banks_count:.0f}" if banks_count > 0 else "")
        finally:
            session.close()


def setup_database(data_file: str):
    """Complete database setup and data insertion"""
    logger.info("="*60)
    logger.info("DATABASE SETUP & DATA INSERTION")
    logger.info("="*60)
    
    # Initialize manager
    manager = DatabaseManager()
    
    # Create tables
    manager.create_tables()
    
    # Insert bank metadata
    banks_data = [
        {'bank_name': 'CBE', 'app_id': 'com.cbe.apps'},
        {'bank_name': 'BOA', 'app_id': 'com.addis.bank'},
        {'bank_name': 'Dashen', 'app_id': 'et.com.dashenbank.android'},
    ]
    manager.insert_banks(banks_data)
    
    # Map bank names to IDs
    session = manager.Session()
    bank_map = {bank.bank_name: bank.bank_id for bank in session.query(Bank).all()}
    session.close()
    
    # Load and insert reviews
    logger.info(f"\nLoading reviews from {data_file}")
    df = pd.read_csv(data_file)
    manager.insert_reviews(df, bank_map)
    
    # Verify
    manager.verify_data()
    
    # Print statistics
    stats = manager.get_bank_stats()
    logger.info("\n" + "="*60)
    logger.info("BANK STATISTICS")
    logger.info("="*60)
    print(stats.to_string(index=False))
    
    return manager


if __name__ == "__main__":
    import sys
    from typing import List, Dict
    
    logging.basicConfig(level=logging.INFO)
    
    data_file = sys.argv[1] if len(sys.argv) > 1 else "data/processed/sentiment_results.csv"
    setup_database(data_file)
