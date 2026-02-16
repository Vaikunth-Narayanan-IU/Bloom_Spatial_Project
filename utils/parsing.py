import re
from datetime import datetime
from dateutil import parser as date_parser

email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
phone_regex = r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
address_regex = r"\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Drive|Dr|Road|Rd|Boulevard|Blvd|Lane|Ln|Trail|Trl|Circle|Cir|Court|Ct|Way|Place|Pl|Apartment|Apt|Unit|Suite|Ste)\s*(?:#?\w+)?(?:\s*,\s*[A-Za-z\s]+)?(?:\s*,\s*[A-Z]{2})?" # Relaxed zip
risk_keywords = ["power lines", "line", "primary", "near wires", "high voltage", "pole", "electric", "spark"]

def extract_email(text):
    match = re.search(email_regex, text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(phone_regex, text)
    return match.group(0) if match else None

def extract_potential_address(text):
    # Try multiple heuristics:
    # 1. Look for explicit labels
    match = re.search(r"(?:service|site|location)\s*(?:address)?\s*[:]\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
    if match:
       # Basic cleanup
       val = match.group(1).strip()
       if len(val) > 5: return val
       
    # 2. General regex fallback
    match = re.search(address_regex, text, re.IGNORECASE)
    return match.group(0) if match else None

def extract_risk_warnings(text):
    text_lower = text.lower()
    flagged = [keyword for keyword in risk_keywords if keyword in text_lower]
    return flagged

def extract_label_value(text, label_pattern):
    match = re.search(label_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        possible = match.group(1).strip()
        # Grab just the first line if multi-line match
        return possible.split('\n')[0].strip()
    return None

def parse_messy_text(text):
    """
    Attempts to extract structured data from unstructured text using heuristics.
    Returns a dictionary of potential fields.
    """
    if not text:
        return {}
        
    extracted = {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "street_address": extract_potential_address(text),
        "risk_flags": extract_risk_warnings(text),
        
        # Heuristics for form fields
        "customer_name": extract_label_value(text, r"(?:property owner|customer name|name)\s*[:]\s*(.*?)(?:\n|$)"),
        "initial_contact_datetime": extract_label_value(text, r"(?:date)\s*[:]\s*(.*?)(?:\n|$)"),
        "raw_comments": text
    }

    # If parsing failed but we have text, ensure raw_comments contains it all
    if not extracted['raw_comments']:
         extracted['raw_comments'] = text
         
    return extracted
