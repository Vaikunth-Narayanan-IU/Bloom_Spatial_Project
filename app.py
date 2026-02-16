import streamlit as st
import pandas as pd
from PIL import Image
import io
import datetime
import json
import os
from utils import parsing, standardize, geocode, ocr

# Page Config
st.set_page_config(
    page_title="Bloom Spatial - Intake",
    page_icon="bloom_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    /* Step indicators */
    .step-indicator {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Progress indicator */
    .progress-step {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .step-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .step-complete {
        background: #10b981;
        color: white;
    }
    
    .step-pending {
        background: #e5e7eb;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State with schema
SCHEMA_KEYS = [
    'customer_name', 'phone', 'email', 'street_address', 'city', 'state', 'zip',
    'initial_contact_datetime', 'contact_channel', 'work_order_summary', 
    'raw_comments', 'risk_flags', 'gps_lat', 'gps_lng'
]

if 'cases_db' not in st.session_state:
    st.session_state.cases_db = []
if 'case_counter' not in st.session_state:
    st.session_state.case_counter = 1
if 'current_case' not in st.session_state:
    st.session_state.current_case = {k: None for k in SCHEMA_KEYS}
if 'extraction_done' not in st.session_state:
    st.session_state.extraction_done = False
if 'standardization_done' not in st.session_state:
    st.session_state.standardization_done = False

# Sidebar
st.sidebar.title("Bloom Spatial")
st.sidebar.caption("Utility Data Intake Prototype v2.1")
debug_mode = False

# How It Works Section
with st.sidebar.expander("📖 How This Works", expanded=True):
    st.markdown("""
    ### Workflow Overview
    
    **1. Upload & Extract** 📥
    - Upload handwritten forms, text screenshots, or email text
    - OCR automatically extracts text from images
    - AI parser identifies key fields (name, address, date, etc.)
    
    **2. Review & Edit** 🧐
    - Verify extracted data for accuracy
    - Edit any fields manually
    - Add missing information
    
    **3. Standardize & Output** 🗺️
    - Auto-format phone numbers and dates
    - Geocode addresses to GPS coordinates
    - Generate unique Case IDs
    - Export to CSV
    
    ### Key Features
    - ✅ OCR text extraction (Tesseract)
    - ✅ Smart field parsing
    - ✅ Risk keyword detection
    - ✅ Address geocoding
    - ✅ Batch export to CSV
    """)



with st.sidebar:
    if st.button("Reset Session", type="secondary", help="Clear all data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Header
st.markdown("""
<div class="main-header">
    <h1>Bloom Spatial - Data Intake System</h1>
    <p>Transform messy customer issues into clean, standardized, geocoded records</p>
</div>
""", unsafe_allow_html=True)

# Progress Indicator
step1_class = "step-complete" if st.session_state.extraction_done else "step-active"
step2_class = "step-complete" if st.session_state.standardization_done else ("step-active" if st.session_state.extraction_done else "step-pending")
step3_class = "step-active" if st.session_state.standardization_done else "step-pending"

st.markdown(f"""
<div style="text-align: center; margin: 2rem 0;">
    <span class="progress-step {step1_class}">1. Upload & Extract</span>
    <span style="color: #cbd5e0;">→</span>
    <span class="progress-step {step2_class}">2. Review & Edit</span>
    <span style="color: #cbd5e0;">→</span>
    <span class="progress-step {step3_class}">3. Standardize & Output</span>
</div>
""", unsafe_allow_html=True)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📥 Upload & Extract", "🧐 Review & Edit", "🗺️ Standardize & Output"])

# --- TAB 1: UPLOAD & EXTRACT ---
with tab1:
    st.markdown("""
    <div class="info-box">
        <h3 style="margin-top: 0;">📥 Step 1: Upload Customer Issue</h3>
        <p>Upload a handwritten form, text message screenshot, or paste email content. Our OCR engine will automatically extract key information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    inputType = st.radio(
        "Select Input Type:",
        ["Handwritten Form (Image/PDF)", "Text Message (Image)", "Email (Text)"],
        horizontal=True,
        help="Choose the type of customer issue you want to process"
    )
    
    if inputType == "Handwritten Form (Image/PDF)":
        st.info("💡 **Tip**: For best OCR results, use high-resolution scans with good lighting and contrast.")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            key="form_uploader",
            help="Supported formats: PNG, JPG, JPEG, PDF"
        )
        
        if uploaded_file is not None:
            if debug_mode:
                with st.expander("🔍 Debug: File Metadata", expanded=True):
                    st.json({
                        "filename": uploaded_file.name,
                        "type": uploaded_file.type,
                        "size": f"{uploaded_file.size / 1024:.2f} KB"
                    })

            raw_text = ""
            error_msg = ""
            
            try:
                is_pdf = uploaded_file.type == "application/pdf"
                image = None
                
                if is_pdf:
                    pdf_bytes = uploaded_file.read()
                    uploaded_file.seek(0)
                    
                    image, err = ocr.convert_pdf_to_images(pdf_bytes)
                    if err:
                        error_msg = err
                        st.warning(err)
                else:
                    image = Image.open(uploaded_file)
                    uploaded_file.seek(0)
                
                if image:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.image(image, caption='📄 Uploaded Document Preview', width=500)
                    
                    with col2:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Ready to Extract</h4>
                            <p>Click the button below to start OCR processing</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 Extract Data from Form", type="primary", key="extract_form_btn", use_container_width=True):
                            with st.spinner("🔄 Running OCR and parsing..."):
                                if not ocr.is_tesseract_installed():
                                    st.warning("⚠️ Tesseract not installed. OCR unavailable. Please enter data manually in Review tab.")
                                    raw_text = "LOG: Tesseract not available"
                                else:
                                    raw_text = ocr.extract_text_from_image(image)
                                
                                if debug_mode:
                                    with st.expander("🔍 Debug: Raw OCR Text", expanded=True):
                                        st.write(f"**Length:** {len(raw_text)}")
                                        st.text_area("Content:", raw_text[:1000], height=200)
                                
                                extracted_data = parsing.parse_messy_text(raw_text)
                                extracted_data['contact_channel'] = 'Form'
                                
                                for key in SCHEMA_KEYS:
                                    if key not in extracted_data:
                                        extracted_data[key] = None
                                
                                non_empty_count = len([v for v in extracted_data.values() if v])
                                
                                if debug_mode:
                                    with st.expander("🔍 Debug: Parsed Data", expanded=True):
                                        st.json(extracted_data)
                                        st.write(f"**Non-empty fields:** {non_empty_count}")
                                
                                st.session_state.current_case = extracted_data
                                st.session_state.extraction_done = True
                                
                                # Success message with animation
                                st.markdown(f"""
                                <div class="success-box">
                                    <h3 style="margin: 0;">✅ Extraction Complete!</h3>
                                    <p style="margin: 0.5rem 0 0 0;">Successfully extracted and populated <strong>{non_empty_count} fields</strong></p>
                                    <p style="margin: 0.5rem 0 0 0;">→ Go to <strong>Review & Edit</strong> tab to verify the data</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.balloons()
                                
                                # Auto-switch hint
                                st.info("💡 Click on the **Review & Edit** tab above to continue")
                                
                elif error_msg:
                    st.error(f"Could not process file: {error_msg}")

            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                if debug_mode:
                    st.exception(e)

    elif inputType == "Text Message (Image)":
        st.markdown("""
        <div class="info-box">
            <p>📱 Upload a screenshot of the text conversation, or paste the message content manually.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("Choose screenshot", type=['png', 'jpg', 'jpeg'], key="text_uploader")
            if uploaded_file:
                image = Image.open(uploaded_file)
                uploaded_file.seek(0)
                st.image(image, caption='📱 Text Message Screenshot', width='stretch')
        
        with col2:
            st.write("**Or paste text content manually:**")
            manual_text = st.text_area(
                "Message Content",
                height=200,
                placeholder="Paste text here if OCR is not needed...",
                key="manual_text_input"
            )

        if st.button("🚀 Extract Data from Text", type="primary", key="extract_text_btn", use_container_width=True):
            raw_text = ""
            if manual_text:
                raw_text = manual_text
            elif uploaded_file:
                with st.spinner("🔄 Running OCR on screenshot..."):
                    if not ocr.is_tesseract_installed():
                        st.warning("⚠️ Tesseract not installed. Please paste text manually.")
                    else:
                        image = Image.open(uploaded_file)
                        raw_text = ocr.extract_text_from_image(image)
            
            if raw_text:
                if debug_mode:
                    with st.expander("🔍 Debug: Raw Text", expanded=True):
                        st.text(raw_text[:1000])

                extracted_data = parsing.parse_messy_text(raw_text)
                extracted_data['contact_channel'] = 'Text'
                
                for key in SCHEMA_KEYS:
                    if key not in extracted_data:
                        extracted_data[key] = None
                
                st.session_state.current_case = extracted_data
                st.session_state.extraction_done = True
                
                extracted_count = len([v for v in extracted_data.values() if v])
                
                st.markdown(f"""
                <div class="success-box">
                    <h3 style="margin: 0;">✅ Extraction Complete!</h3>
                    <p style="margin: 0.5rem 0 0 0;">Found <strong>{extracted_count} populated fields</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                st.info("💡 Click on the **Review & Edit** tab above to continue")
            else:
                st.error("❌ Please provide text or an image.")

    elif inputType == "Email (Text)":
        st.markdown("""
        <div class="info-box">
            <p>📧 Paste the complete email including headers (From, Sent, Subject) and body.</p>
        </div>
        """, unsafe_allow_html=True)
        
        email_content = st.text_area(
            "Email Content",
            height=300,
            placeholder="From: customer@example.com\nSent: Monday, February 15, 2026\nSubject: Tree trimming request\n\nBody...",
            key="email_input"
        )
        
        if st.button("🚀 Extract Data from Email", type="primary", key="extract_email_btn", use_container_width=True):
            if email_content:
                extracted_data = parsing.parse_messy_text(email_content)
                extracted_data['contact_channel'] = 'Email'
                
                for key in SCHEMA_KEYS:
                    if key not in extracted_data:
                        extracted_data[key] = None
                
                st.session_state.current_case = extracted_data
                st.session_state.extraction_done = True
                
                extracted_count = len([v for v in extracted_data.values() if v])
                
                st.markdown(f"""
                <div class="success-box">
                    <h3 style="margin: 0;">✅ Extraction Complete!</h3>
                    <p style="margin: 0.5rem 0 0 0;">Found <strong>{extracted_count} populated fields</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                st.info("💡 Click on the **Review & Edit** tab above to continue")
            else:
                st.error("❌ Please paste email content.")

# --- TAB 2: REVIEW & EDIT ---
with tab2:
    st.markdown("""
    <div class="info-box">
        <h3 style="margin-top: 0;">🧐 Step 2: Review & Edit Extracted Data</h3>
        <p>Verify the automatically extracted information and make any necessary corrections before standardization.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.extraction_done:
        st.warning("⚠️ Please complete **Step 1 (Upload & Extract)** first.")
        st.info("👈 Go to the **Upload & Extract** tab to get started")
    else:
        if debug_mode:
            with st.expander("🔍 Debug: Current Case Data", expanded=True):
                st.json(st.session_state.current_case)

        current = st.session_state.current_case
        
        def get_val(k):
            val = current.get(k, '')
            return str(val) if val is not None and val != 'None' else ''

        with st.form("review_form"):
            st.subheader("👤 Customer Details")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Customer Name", value=get_val('customer_name'), help="Full name of property owner")
                phone = st.text_input("Phone", value=get_val('phone'), help="Contact phone number")
                email = st.text_input("Email", value=get_val('email'), help="Email address")
                
            with col2:
                d_val = get_val('initial_contact_datetime')
                if not d_val:
                    d_val = pd.to_datetime('today').strftime('%Y-%m-%d')
                     
                contact_date = st.text_input("Contact Date", value=str(d_val), help="Date of initial contact")
                
                channels = ["Form", "Text", "Email", "Phone Call"]
                curr_channel = current.get('contact_channel', 'Form')
                idx = channels.index(curr_channel) if curr_channel in channels else 0
                channel = st.selectbox("Channel", channels, index=idx, help="How the customer contacted us")

            st.subheader("📍 Location & Issue")
            address = st.text_input("Street Address (As Written)", value=get_val('street_address'), help="Service address")
            
            c1, c2, c3 = st.columns(3)
            with c1: city = st.text_input("City", value=get_val('city'))
            with c2: state = st.text_input("State", value=get_val('state'))
            with c3: zip_code = st.text_input("Zip", value=get_val('zip'))

            summary = st.text_area("Work Order Summary", value=get_val('work_order_summary'), help="Brief description of the work needed")
            
            risk_raw = current.get('risk_flags', [])
            if isinstance(risk_raw, list):
                risk_val = ",".join(risk_raw)
            else:
                risk_val = str(risk_raw) if risk_raw else ""
            
            risk = st.text_input("Risk Flags (CSV)", value=risk_val, help="Safety concerns: power lines, high voltage, etc.")
            
            comments = st.text_area("Raw Notes", value=get_val('raw_comments'), height=150, help="Full extracted text for reference")

            submit_review = st.form_submit_button("✅ Confirm & Standardize", type="primary", use_container_width=True)
            
            if submit_review:
                updated_case = {
                    'customer_name': name,
                    'phone': phone,
                    'email': email,
                    'initial_contact_datetime': contact_date,
                    'contact_channel': channel,
                    'street_address': address,
                    'city': city,
                    'state': state,
                    'zip': zip_code,
                    'work_order_summary': summary,
                    'risk_flags': risk,
                    'raw_comments': comments,
                    'gps_lat': current.get('gps_lat'), 
                    'gps_lng': current.get('gps_lng')
                }
                
                st.session_state.current_case = updated_case
                st.session_state.standardization_done = True
                
                st.markdown("""
                <div class="success-box">
                    <h3 style="margin: 0;">✅ Data Confirmed!</h3>
                    <p style="margin: 0.5rem 0 0 0;">Proceed to <strong>Standardize & Output</strong> tab</p>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 3: STANDARDIZE & OUTPUT ---
with tab3:
    if not st.session_state.standardization_done:
        st.warning("⚠️ Please review and confirm data in **Step 2 (Review & Edit)**.")
        st.info("👈 Go to the **Review & Edit** tab to verify your data")
    else:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">🗺️ Step 3: Standardization & Geocoding</h3>
            <p>Automatic formatting, geocoding, and case ID generation for your standardized record.</p>
        </div>
        """, unsafe_allow_html=True)
        
        case = st.session_state.current_case
        
        std_phone = standardize.standardize_phone(case.get('phone'))
        std_name = standardize.normalize_text(case.get('customer_name'))
        std_date = standardize.standardize_date(case.get('initial_contact_datetime'))
        
        full_addr_str = f"{case.get('street_address')}, {case.get('city')}, {case.get('state')} {case.get('zip')}"
        if 'gps_lat' not in case or not case['gps_lat']:
            with st.spinner(f"🌍 Geocoding address: {full_addr_str}..."):
                lat, lng, formatted_addr = geocode.get_lat_long(full_addr_str)
        else:
            lat, lng = case['gps_lat'], case['gps_lng']
            formatted_addr = "Previously Geocoded"

        if 'case_id' not in case:
            new_id = standardize.generate_case_id(st.session_state.case_counter)
        else:
            new_id = case['case_id']
            
        rec_filename = standardize.generate_filename(new_id, case.get('street_address'), case.get('city'), case.get('state'))

        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📍 Geocoded Location")
            if lat and lng:
                st.success(f"✅ Found: {formatted_addr}")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Latitude", f"{lat:.6f}")
                with metric_col2:
                    st.metric("Longitude", f"{lng:.6f}")
                
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lng]})
                st.map(map_data, zoom=15)
            else:
                st.error("❌ Could not geocode address automatically.")
                st.info("Please enter coordinates manually:")
                m_lat = st.number_input("Latitude", value=0.0, format="%.6f")
                m_lng = st.number_input("Longitude", value=0.0, format="%.6f")
                if m_lat != 0.0:
                    lat, lng = m_lat, m_lng

        with col2:
            st.subheader("📄 Standardized Record")
            
            st.text_input("🆔 Case ID", value=new_id, disabled=True, help="Unique identifier for this case")
            st.text_input("📞 Standardized Phone", value=std_phone, disabled=True, help="Formatted phone number")
            st.text_input("📅 Standardized Date", value=std_date, disabled=True, help="ISO 8601 format")
            st.text_input("⚠️ Risk Flags", value=case.get('risk_flags'), disabled=True, help="Safety concerns identified")
            
            st.markdown("**📁 Recommended Filename:**")
            st.code(rec_filename, language="text")
            
            st.divider()
            
            if st.button("💾 Save Case to Database", type="primary", use_container_width=True):
                final_record = case.copy()
                final_record.update({
                    'case_id': new_id,
                    'customer_name': std_name,
                    'phone': std_phone,
                    'initial_contact_datetime': std_date,
                    'gps_lat': lat,
                    'gps_lng': lng,
                    'formatted_address': formatted_addr,
                    'recommended_filename': rec_filename,
                    'timestamp_added': datetime.datetime.now().isoformat()
                })
                
                st.session_state.cases_db.append(final_record)
                st.session_state.case_counter += 1
                st.session_state.current_case = {k: None for k in SCHEMA_KEYS}
                st.session_state.extraction_done = False
                st.session_state.standardization_done = False
                
                st.markdown(f"""
                <div class="success-box">
                    <h3 style="margin: 0;">🎉 Case {new_id} Saved Successfully!</h3>
                    <p style="margin: 0.5rem 0 0 0;">Your case has been added to the database</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                st.rerun()

# --- BOTTOM: SESSION DB ---
st.markdown("---")
st.markdown("""
<div class="info-box">
    <h3 style="margin-top: 0;">📚 Session Cases Database</h3>
    <p>All cases created in this session. Export to CSV for permanent storage.</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.cases_db:
    df = pd.DataFrame(st.session_state.cases_db)
    
    # Show metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Cases", len(df))
    with metric_col2:
        st.metric("Latest Case ID", df.iloc[-1]['case_id'] if len(df) > 0 else "N/A")
    with metric_col3:
        channels = df['contact_channel'].value_counts()
        st.metric("Most Common Channel", channels.index[0] if len(channels) > 0 else "N/A")
    
    st.dataframe(df, width='stretch')
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download All Cases as CSV",
        data=csv,
        file_name=f'bloom_spatial_cases_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv',
        type="primary",
        use_container_width=True
    )
else:
    st.info("📭 No cases created yet. Start by uploading a document in the **Upload & Extract** tab!")
