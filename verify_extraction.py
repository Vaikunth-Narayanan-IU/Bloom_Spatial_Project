#!/usr/bin/env python3
"""
Quick verification script to test extraction pipeline independently.
Run this to verify the fix without opening the Streamlit UI.
"""

from PIL import Image
from utils import ocr, parsing
import json

def test_extraction():
    print("=" * 60)
    print("EXTRACTION PIPELINE VERIFICATION")
    print("=" * 60)
    
    fixture_path = "tests/fixtures/sample_form.png"
    
    # 1. Check fixture exists
    try:
        image = Image.open(fixture_path)
        print(f"✅ Loaded fixture: {fixture_path}")
    except Exception as e:
        print(f"❌ Failed to load fixture: {e}")
        return
    
    # 2. Check OCR availability
    ocr_available = ocr.is_tesseract_installed()
    print(f"{'✅' if ocr_available else '⚠️'} Tesseract installed: {ocr_available}")
    
    # 3. Run extraction
    print("\n" + "=" * 60)
    print("RUNNING EXTRACTION...")
    print("=" * 60)
    
    raw_text = ocr.extract_text_from_image(image)
    print(f"\n📄 Raw OCR text length: {len(raw_text)}")
    print(f"📄 First 300 chars:\n{raw_text[:300]}\n")
    
    # 4. Parse
    result = parsing.parse_messy_text(raw_text)
    result['contact_channel'] = 'Form'
    
    # 5. Show results
    print("=" * 60)
    print("PARSED DATA")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    
    # 6. Count non-empty
    non_empty = len([v for v in result.values() if v])
    print(f"\n📊 Non-empty fields: {non_empty}/{len(result)}")
    
    # 7. Verify schema
    expected_keys = ['customer_name', 'phone', 'email', 'street_address', 
                     'raw_comments', 'risk_flags', 'contact_channel']
    missing = [k for k in expected_keys if k not in result]
    
    if missing:
        print(f"❌ Missing keys: {missing}")
    else:
        print(f"✅ All expected keys present")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    if not ocr_available:
        print("\n⚠️  NOTE: Tesseract not installed.")
        print("   To enable OCR: brew install tesseract poppler")
        print("   App will work with manual entry (graceful degradation)")
    else:
        print("\n✅ OCR fully functional!")

if __name__ == "__main__":
    test_extraction()
