# Task 1: Data Collection & Preprocessing

This branch focuses on **data collection and preprocessing** for the fintech review analytics project.

## Overview

Task 1 involves collecting user reviews from Google Play Store for multiple fintech banking applications and performing comprehensive data cleaning, deduplication, and validation to prepare raw data for analysis.

## Objectives

1. **Data Scraping**: Collect 1,200+ reviews from 3 fintech banking apps using web scraping
2. **Data Cleaning**: Remove duplicates, irrelevant content, and normalize text
3. **Data Validation**: Ensure data quality and completeness
4. **Data Exploration**: Perform EDA to understand review characteristics and distributions

## Key Components

### Scraping (`src/scraper.py`)
- Uses `google-play-scraper` library to collect reviews
- Collects review text, ratings, author, and metadata
- Handles pagination and error handling
- Outputs raw data to `data/raw/reviews_raw.csv`

### Preprocessing (`src/preprocessor.py`)
- **Text Normalization**: Lowercase, remove special characters, handle URLs
- **Deduplication**: Remove duplicate reviews
- **Tokenization**: Prepare text for NLP processing
- **Quality Checks**: Filter out empty or invalid reviews
- **Outputs**: Processed data to `data/processed/`

## Data Flow

```
Google Play Store
        ↓
   [Web Scraper]
        ↓
  Raw Reviews CSV
        ↓
  [Preprocessor]
        ↓
 Processed Reviews CSV
        ↓
  [EDA Notebook]
```

## Files in This Task

- `notebooks/01_task1_scraping_eda.ipynb` - Main notebook for scraping and exploration
- `src/scraper.py` - Web scraping implementation
- `src/preprocessor.py` - Data preprocessing and cleaning
- `data/raw/reviews_raw.csv` - Raw scraped data (not committed)
- `data/processed/` - Cleaned data outputs
- `tests/test_preprocessing.py` - Unit tests for preprocessing logic

## Running Task 1

### Prerequisites
```bash
pip install -r requirements.txt
```

### Execute Scraping & Preprocessing
```bash
# Run the notebook
jupyter notebook notebooks/01_task1_scraping_eda.ipynb
```

Or use the Python scripts directly:
```bash
python -c "from src.scraper import scrape_reviews; scrape_reviews()"
python -c "from src.preprocessor import preprocess_data; preprocess_data()"
```

## Testing

Run unit tests to verify preprocessing functions:
```bash
pytest tests/test_preprocessing.py
```

## Output

After Task 1 completion, you'll have:
- ✅ Raw reviews dataset (1,200+ reviews)
- ✅ Cleaned and processed reviews
- ✅ EDA visualizations and statistics
- ✅ Data quality report
- ✅ Ready-to-use dataset for Task 2 (Sentiment Analysis)

## Dependencies

Key libraries used in Task 1:
- `google-play-scraper` - Web scraping
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `nltk` - Text processing
- `spacy` - NLP preprocessing

## Next Steps

Once Task 1 is complete, proceed to **Task 2: Sentiment Analysis & Thematic Analysis** using the processed data from this task.

## Notes

- Raw data is not committed to git (see `.gitignore`)
- All preprocessing is designed to be reproducible
- Unit tests ensure data quality validation
- Review collection may take 5-10 minutes depending on network speed
