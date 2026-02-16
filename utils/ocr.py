import shutil
import warnings
import io

def is_tesseract_installed():
    """Check if tesseract is installed and available in PATH."""
    return shutil.which('tesseract') is not None

def extract_text_from_image(image):
    """
    Attempt to extract text from a PIL Image using pytesseract.
    Returns the extracted text or an error message if OCR is unavailable.
    """
    try:
        import pytesseract
        
        # Check system dependency explicitly
        if not is_tesseract_installed():
            return "LOG: Tesseract binary not found in PATH. OCR unavailable."

        # Simple configuration for English text + gracefully handle empty
        try:
            text = pytesseract.image_to_string(image)
            if not text or not text.strip():
                return "LOG: OCR ran but found no text. Image might be too blurry or empty."
            return text
        except Exception as pytesseract_error:
             return f"LOG: Pytesseract runtime error: {str(pytesseract_error)}"

    except ImportError:
        return "LOG: pytesseract library not installed."
    except Exception as e:
        return f"LOG: OCR Error: {str(e)}"

def convert_pdf_to_images(pdf_bytes):
    """
    Convert first page of PDF to image using pdf2image.
    Returns (image, None) or (None, error_message).
    """
    try:
        from pdf2image import convert_from_bytes
        # Try to convert just the first page
        try:
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
            if images:
                return images[0], None
            else:
                return None, "LOG: PDF conversion resulted in no images."
        except Exception as pdf_err:
             if "poppler" in str(pdf_err).lower():
                  return None, "LOG: Poppler not installed. PDF conversion unavailable."
             return None, f"LOG: PDF conversion error: {str(pdf_err)}"
             
    except ImportError:
        return None, "LOG: pdf2image library not installed."
    except Exception as e:
        return None, f"LOG: General PDF Error: {str(e)}"
