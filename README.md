# Bloom Spatial - Utility Data Intake Prototype

This is a professional prototype web application for Bloom Spatial designed to standardize the intake of utility customer issues from various messy sources (handwritten forms, text message screenshots, and email text).

## 🚀 Key Features

- **Multi-Channel Intake**: Support for handwritten forms (PDF/Images), text message screenshots, and raw email text.
- **Intelligent Extraction**: Automated text extraction using OCR and heuristic parsing to identify customer names, addresses, phone numbers, and dates.
- **Risk Detection**: Automatic flagging of safety-critical keywords (e.g., "power lines", "high voltage").
- **Human-in-the-Loop Review**: An intuitive interface for agents to verify and correct extracted data.
- **Standardization & Geocoding**:
  - Address geocoding to GPS coordinates (Latitude/Longitude).
  - Normalization of phone numbers and dates.
  - Automatic generation of Case IDs and standardized filenames.
- **Export**: Batch export of standardized records to CSV.

## 📁 Project Structure

- `app.py`: Main Streamlit application with custom UI/UX.
- `utils/`: Core processing logic.
  - `ocr.py`: OCR extraction using Tesseract and PDF conversion.
  - `parsing.py`: Heuristic-based text parsing.
  - `geocode.py`: OpenStreetMap Nominatim integration.
  - `standardize.py`: Data normalization utilities.
- `tests/`: Pytest suite for extraction validation.
- `render.yaml`: Configuration for one-click deployment to Render.

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- **OCR Support (Optional)**: If you want to run OCR locally, install:
  - [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
  - [Poppler](https://poppler.freedesktop.org/) (for PDF support)
  
  On Mac: `brew install tesseract poppler`

### Setup
1. **Clone the repository**
2. **Create and Activate a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 🧪 Testing
Run the automated test suite to verify extraction logic:
```bash
pytest tests/test_extraction.py -v
```

## ☁️ Deployment on Render

This project is configured for seamless deployment on Render.

### Render Web Service Configuration
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### OCR in Production
The default Render Python environment does not include Tesseract. The app is built with **graceful degradation**:
- If Tesseract is not found, the app displays a clear warning.
- Users can still manually paste text or enter data in the **Review** tab.
- The system will not crash and all other features (parsing, geocoding, standardization) remain fully functional.

## 👤 Author
Developed for Bloom Spatial.
