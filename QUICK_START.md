# 🚀 Quick Start Guide

## Run the App

```bash
./run.sh
```

The app will open at: http://localhost:8501

## Test the Extraction

### Option 1: Self-Test (Fastest)
1. Look at the **sidebar** on the left
2. Check ✅ **"Debug Mode"**
3. Click **"Run Extraction Self-Test"**
4. See extraction results in sidebar

### Option 2: Upload Form
1. Go to **Tab 1: Upload & Extract**
2. Click **"Choose file"**
3. Select `tests/fixtures/sample_form.png`
4. Click **"Extract Data from Form"**
5. Wait ~3 seconds
6. See success message: "✅ Extraction complete! Found 6 populated fields."
7. Go to **Tab 2: Review & Edit**
8. See extracted data:
   - Customer Name: "Ante Doe"
   - Date: "Z-I(-Z26"
   - Risk Flags: "electric"
   - Raw Comments: Full OCR text

### Option 3: Command Line Test
```bash
source venv/bin/activate
python3 verify_extraction.py
```

## What to Expect

### With OCR Working (Current State) ✅
- Upload image → OCR extracts text → Parser finds fields
- Customer names, dates, addresses auto-populated
- Risk keywords flagged automatically
- Full text in "Raw Comments"

### Example Output
```
✅ Extraction complete! Found 6 populated fields.
→ Go to Review & Edit tab to verify data.
```

## Full Workflow

1. **Upload** (Tab 1)
   - Upload form/text/email
   - Click Extract
   - See success message

2. **Review** (Tab 2)
   - Verify extracted data
   - Edit any fields
   - Click "Confirm & Standardize"

3. **Output** (Tab 3)
   - See geocoded location on map
   - Get Case ID and filename
   - Click "Save Case to Database"

4. **Export**
   - Scroll to bottom
   - Click "Download All Cases as CSV"

## Troubleshooting

### App won't start
```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### OCR not working
```bash
# Check if Tesseract is installed
which tesseract

# If not found, install it
brew install tesseract poppler
```

### Tests failing
```bash
source venv/bin/activate
pytest tests/test_extraction.py -v
```

## Files to Test With

- `tests/fixtures/sample_form.png` - Handwritten permission form
- `tests/fixtures/sample_text.png` - Text message screenshot
- `tests/fixtures/sample_email.png` - Email screenshot

## Debug Mode Features

When enabled, shows:
- File metadata (size, type)
- OCR availability status
- Raw OCR text (first 400 chars)
- Parsed data as JSON
- Non-empty field count
- Current session state

---

**Everything is ready to go!** 🎉
