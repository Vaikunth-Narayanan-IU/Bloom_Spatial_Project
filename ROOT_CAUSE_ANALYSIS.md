# Root Cause Analysis & Fix Report

## Problem Statement
When uploading a form image and clicking "Extract Data", the Review/Edit fields did NOT populate.

## Root Causes Identified

### 1. **File Pointer Not Reset After Read** (CRITICAL)
- **Issue**: When `uploaded_file.read()` was called for PDF conversion, the file pointer moved to EOF
- **Impact**: Subsequent attempts to read the file returned empty data
- **Fix**: Added `uploaded_file.seek(0)` after every `.read()` operation

### 2. **Session State Not Properly Initialized**
- **Issue**: `st.session_state.current_case` was initialized as empty dict `{}`
- **Impact**: Widget `value=` parameters would get `None` values, causing display issues
- **Fix**: Initialize with full schema: `{k: None for k in SCHEMA_KEYS}`

### 3. **No st.rerun() After Extraction**
- **Issue**: After writing to session_state, widgets didn't re-render with new values
- **Impact**: Tab 2 showed stale/empty values even though session_state was updated
- **Fix**: Added `st.rerun()` immediately after setting `extraction_done = True`

### 4. **Widget Keys Not Stable**
- **Issue**: Some widgets didn't have explicit `key=` parameters
- **Impact**: Streamlit couldn't track widget state across reruns
- **Fix**: Added unique `key=` to all file uploaders and buttons

### 5. **Silent Failures**
- **Issue**: OCR/parsing errors were not surfaced to user
- **Impact**: User had no idea why extraction failed
- **Fix**: Added explicit warnings, error messages, and debug mode

### 6. **Schema Inconsistency**
- **Issue**: Parsed dict didn't always contain all expected keys
- **Impact**: `get_val()` helper would fail or return inconsistent results
- **Fix**: Ensure all schema keys exist in extracted_data before writing to session_state

## Verification

### Self-Test Feature
Added "Run Extraction Self-Test" button in sidebar that:
- Loads `tests/fixtures/sample_form.png`
- Runs extraction pipeline
- Shows OCR availability, raw text, parsed dict
- Writes to session_state and confirms

### Pytest Suite
Created `tests/test_extraction.py` with 6 tests:
```
✅ test_form_fixture_exists
✅ test_form_fixture_returns_dict
✅ test_form_fixture_populates_minimum_fields
✅ test_state_population_after_extraction
✅ test_parsing_handles_empty_text
✅ test_parsing_handles_none
```

All tests **PASS**.

### Debug Mode
Added checkbox in sidebar that shows:
- File metadata (name, type, size)
- Raw OCR text (first 400 chars)
- Parsed data as JSON
- Non-empty field count
- Current session_state

## Current Status

### What Works
✅ Extraction pipeline returns valid dict
✅ Session state properly updated
✅ Pytest tests all pass
✅ Error handling and user feedback
✅ Debug mode for diagnostics
✅ Self-test feature for verification

### Known Limitation
⚠️ **Tesseract not installed on this system**
- OCR will return: "LOG: Tesseract binary not found in PATH. OCR unavailable."
- App handles this gracefully and allows manual entry
- To enable OCR locally: `brew install tesseract`
- On Render: OCR will be unavailable (expected behavior for free tier)

## How to Verify Fix

1. **Run Self-Test**:
   - Open app
   - Check "Debug Mode" in sidebar
   - Click "Run Extraction Self-Test"
   - Verify parsed dict appears in sidebar
   - Verify session_state shows the data

2. **Upload Form**:
   - Go to Tab 1
   - Upload `tests/fixtures/sample_form.png`
   - Click "Extract Data from Form"
   - See success message with field count
   - Go to Tab 2
   - **Fields should now be populated** (at minimum: raw_comments, contact_channel)

3. **Run Tests**:
   ```bash
   source venv/bin/activate
   pytest tests/test_extraction.py -v
   ```
   All 6 tests should pass.

## Next Steps (Optional Enhancements)

1. Install Tesseract locally: `brew install tesseract`
2. Install Poppler for PDF support: `brew install poppler`
3. Test with actual handwritten forms to tune parsing heuristics
4. Add more test fixtures for email and text message formats
