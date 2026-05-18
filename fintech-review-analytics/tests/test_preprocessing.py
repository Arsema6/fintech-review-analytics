"""
Unit tests for preprocessing module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preprocessor import ReviewPreprocessor


class TestPreprocessor:
    """Test suite for ReviewPreprocessor."""
    
    def test_required_columns_validation(self):
        """Test that required columns are validated."""
        # Create test data with missing columns
        test_df = pd.DataFrame({
            'review': ['Great app', 'Poor service'],
            'rating': [5, 1],
            # Missing 'date', 'bank', 'source'
        })
        
        # This should raise an error
        with pytest.raises(ValueError):
            preprocessor = ReviewPreprocessor('dummy.csv', 'output.csv')
            preprocessor.validate_columns(test_df)
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        test_data = {
            'review': ['Test review', 'Test review', 'Another review'],
            'rating': [5, 5, 4],
            'date': ['2026-01-01', '2026-01-01', '2026-01-02'],
            'bank': ['Bank A', 'Bank A', 'Bank B'],
            'source': ['Google Play', 'Google Play', 'Google Play']
        }
        test_df = pd.DataFrame(test_data)
        
        preprocessor = ReviewPreprocessor('dummy.csv', 'output.csv')
        cleaned_df = preprocessor.remove_duplicates(test_df)
        
        # Should have 2 rows (1 duplicate removed)
        assert len(cleaned_df) == 2
    
    def test_missing_values_handling(self):
        """Test missing value handling."""
        test_data = {
            'review': ['Valid review', None, 'Another review'],
            'rating': [5, 4, None],
            'date': ['2026-01-01', '2026-01-02', '2026-01-03'],
            'bank': ['Bank A', 'Bank B', 'Bank C'],
            'source': ['Google Play', 'Google Play', 'Google Play']
        }
        test_df = pd.DataFrame(test_data)
        
        preprocessor = ReviewPreprocessor('dummy.csv', 'output.csv')
        cleaned_df, missing_report = preprocessor.handle_missing_values(test_df)
        
        # Should drop rows with missing review or rating
        assert len(cleaned_df) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
