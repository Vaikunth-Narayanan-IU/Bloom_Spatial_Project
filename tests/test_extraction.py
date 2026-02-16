import pytest
import sys
import os
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import ocr, parsing

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_form.png')

def test_form_fixture_exists():
    """Test that the fixture file exists."""
    assert os.path.exists(FIXTURE_PATH), f"Fixture not found: {FIXTURE_PATH}"

def test_form_fixture_returns_dict():
    """Test that extraction returns a dictionary."""
    image = Image.open(FIXTURE_PATH)
    raw_text = ocr.extract_text_from_image(image)
    
    # Parse should always return a dict
    result = parsing.parse_messy_text(raw_text)
    
    assert isinstance(result, dict), "parse_messy_text should return a dict"
    assert len(result) > 0, "Parsed dict should not be empty"

def test_form_fixture_populates_minimum_fields():
    """Test that extraction populates at least some fields."""
    image = Image.open(FIXTURE_PATH)
    raw_text = ocr.extract_text_from_image(image)
    
    result = parsing.parse_messy_text(raw_text)
    
    # Check that we have at least raw_comments (which should always be populated)
    assert 'raw_comments' in result, "Should have raw_comments field"
    assert result['raw_comments'] is not None, "raw_comments should not be None"
    
    # If OCR is working, we should have some text
    if not raw_text.startswith("LOG:"):
        assert len(raw_text) > 0, "OCR should return some text"

def test_state_population_after_extraction():
    """Test that extraction result has expected schema keys."""
    image = Image.open(FIXTURE_PATH)
    raw_text = ocr.extract_text_from_image(image)
    
    result = parsing.parse_messy_text(raw_text)
    result['contact_channel'] = 'Form'
    
    # Expected schema keys
    expected_keys = [
        'customer_name', 'phone', 'email', 'street_address', 
        'raw_comments', 'risk_flags', 'contact_channel'
    ]
    
    for key in expected_keys:
        assert key in result, f"Missing expected key: {key}"

def test_parsing_handles_empty_text():
    """Test that parsing handles empty text gracefully."""
    result = parsing.parse_messy_text("")
    
    assert isinstance(result, dict), "Should return dict even for empty text"

def test_parsing_handles_none():
    """Test that parsing handles None gracefully."""
    result = parsing.parse_messy_text(None)
    
    assert isinstance(result, dict), "Should return dict even for None"
