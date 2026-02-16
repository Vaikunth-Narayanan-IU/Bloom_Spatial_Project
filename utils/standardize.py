import re
import datetime

def standardize_date(date_val):
    if not date_val:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if isinstance(date_val, str):
        try:
            from dateutil import parser
            dt = parser.parse(date_val)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Default if parse fails
    if isinstance(date_val, (datetime.datetime, datetime.date)):
        return date_val.strftime('%Y-%m-%d %H:%M:%S')
    return str(date_val)

def standardize_phone(phone_str):
    if not phone_str:
        return ""
    # Strip non-digits
    digits = re.sub(r'\D', '', phone_str)
    # Check if length is acceptable (10 digits for US)
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}" # Remove country code 1
    return phone_str # Return as is if format unclear

def generate_case_id(counter):
    today = datetime.datetime.now().strftime('%Y%m%d')
    return f"RPC-{today}-{counter:03d}"

def generate_filename(case_id, street_address, city, state):
    # Sanitize inputs
    def clean(s):
        return re.sub(r'[^a-zA-Z0-9]', '', str(s)) if s else "UNKNOWN"
        
    s_clean = clean(street_address)
    c_clean = clean(city)
    st_clean = clean(state)
    
    return f"{case_id}_{s_clean}_{c_clean}_{st_clean}.pdf"

def normalize_text(text):
    if not text:
        return ""
    return ' '.join(text.split()).title() # Title Case and single spacing
