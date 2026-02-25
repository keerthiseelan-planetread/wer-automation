import streamlit as st
from wer_engine.wer_calculater import calculate_wer
from config import Config
from auth.login import login_user, logout_user
import time
from wer_engine.srt_parser import parse_srt
from drive.drive_utils import find_folder, list_srt_files, traverse_structure
from drive.drive_service import get_drive_service
from drive.drive_utils import download_file_content
import os


# Configure page
st.set_page_config(
    page_title="WER Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(to bottom, #f8fafc 0%, #ffffff 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e40af 0%, #003da5 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    
    /* Header styling */
    h1 {
        color: #1e40af !important;
        border-bottom: 3px solid #3b82f6 !important;
        padding-bottom: 20px !important;
    }
    
    h2, h3 {
        color: #1e40af !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        background-color: white !important;
        color: #1f2937 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #1f2937 !important;
    }
    
    .stSelectbox > div > div > div {
        color: #1f2937 !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px !important;
        border: 2px solid #e5e7eb !important;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
    
    .stSuccess {
        background-color: #d1fae5 !important;
        color: #065f46 !important;
    }
    
    .stError {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
    }
    
    .stWarning {
        background-color: #fef3c7 !important;
        color: #92400e !important;
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #3b82f6 !important;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 10px;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        color: #1e40af;
        font-size: 28px;
        font-weight: 700;
        margin-top: 5px;
    }
    
    /* Card styling */
    .param-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        border: 2px solid #e5e7eb;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar logout button appearance */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Validate config
try:
    Config.validate()
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# If not logged in → show login
if not st.session_state["authenticated"]:
    login_user()
    st.stop()

# ===========================
# SIDEBAR - User Info & Logout
# ===========================
with st.sidebar:
    # Display logo in sidebar
    sidebar_col1, sidebar_col2, sidebar_col3 = st.columns([1, 1, 1])
    with sidebar_col2:
        st.image("app/assets/logo.jpeg", width=180)
    
    st.markdown("---")
    
    # User profile section
    user_email = st.session_state.get('user_email', 'User')
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin-bottom: 20px;">
        <p style="margin: 0; color: white; font-size: 12px; text-transform: uppercase; opacity: 0.8;">Logged In As</p>
        <p style="margin: 5px 0 0 0; color: white; font-weight: 600; font-size: 14px;">👤 {user_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        logout_user()
    
    st.markdown("---")
    
    # Info section
    st.markdown("""
    <div style="color: white; font-size: 12px; opacity: 0.8; margin-top: 30px;">
        <p><strong>📊 WER Automation</strong></p>
        <p>Evaluate and compare AI transcription models using comprehensive Word Error Rate metrics.</p>
        <hr style="border-color: rgba(255,255,255,0.2);">
        <p style="font-size: 11px;">Version 1.0 • All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# ===========================
# MAIN DASHBOARD
# ===========================

# Header
st.markdown("""
<div style="margin-bottom: 30px;">
    <h1 style="margin:0; display:inline-flex; align-items:center; gap: 15px;">
        📊 WER Automation Dashboard
    </h1>
    <p style="color: #6b7280; margin-top: 10px; font-size: 16px;">Evaluate AI model transcription quality with comprehensive Word Error Rate analysis</p>
</div>
""", unsafe_allow_html=True)

# Success message
if st.session_state.get("show_login_success"):
    success_placeholder = st.empty()
    success_placeholder.success("✅ Login Successful! Welcome back.")
    time.sleep(2)
    success_placeholder.empty()
    st.session_state["show_login_success"] = False

# Parameters section
st.markdown("""
<div class="param-card">
        <h2 style="margin-top: 0; color: #1e40af;">⚙️ Analysis Parameters</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">Select language, year, and month to view WER scores for all AI tools and compare their transcription accuracy</p>
</div>
""", unsafe_allow_html=True)

# --- Dropdown Options ---
languages = ["English", "Hindi", "Punjabi", "Tamil"]
years = ["2022", "2023", "2024", "2025"]
months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# --- Layout using columns ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])

with col1:
    selected_language = st.selectbox("🌐 Language", languages, key="language_select")

with col2:
    selected_year = st.selectbox("📅 Year", years, key="year_select")

with col3:
    selected_month = st.selectbox("📆 Month", months, key="month_select")

with col4:
    st.markdown("<p style='font-size: 12px; color: #6b7280; font-weight: 600;'>Action</p>", unsafe_allow_html=True)
    generate_clicked = st.button("🔄 Generate Report", use_container_width=True, key="generate_btn")

# Processing and results
if generate_clicked:
    service = get_drive_service()

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    with progress_placeholder.container():
        progress_bar = st.progress(0)
    
    try:
        # 1️⃣ Navigate folder structure
        with status_placeholder.container():
            st.info("🔍 Navigating folder structure...")
        
        language_id = traverse_structure(
            service,
            Config.GOOGLE_DRIVE_ROOT_ID,
            selected_year,
            selected_month,
            selected_language
        )
        progress_bar.progress(20)

        # 2️⃣ Locate subfolders
        with status_placeholder.container():
            st.info("📁 Locating Original and AI folders...")
        
        original_folder = find_folder(service, language_id, "Original_Files")
        ai_folder = find_folder(service, language_id, "AI_Generated_Files")

        if not original_folder or not ai_folder:
            status_placeholder.empty()
            progress_placeholder.empty()
            st.error("❌ Original or AI folder missing. Please check your drive structure.")
            st.stop()

        progress_bar.progress(40)

        # Only proceed with processing if folders exist
        with st.spinner("⏳ Processing WER report... This may take a moment"):
            
            original_id = original_folder[0]["id"]
            ai_id = ai_folder[0]["id"]

            # 3️⃣ Fetch all SRT files
            with status_placeholder.container():
                st.info("📄 Fetching SRT files...")
            
            original_files = list_srt_files(service, original_id)
            ai_files = list_srt_files(service, ai_id)

            if not original_files:
                st.warning("⚠️ No Original files found.")
                st.stop()

            if not ai_files:
                st.warning("⚠️ No AI files found.")
                st.stop()

            progress_bar.progress(60)

            # 4️⃣ Build AI Mapping
            ai_mapping = {}

            for file in ai_files:
                filename = file["name"]
                file_id = file["id"]

                name_without_ext = os.path.splitext(filename)[0]

                if "_" not in name_without_ext:
                    continue

                parts = name_without_ext.split("_")

                base_name, ai_tool = name_without_ext.rsplit("_", 1)

                if base_name not in ai_mapping:
                    ai_mapping[base_name] = []

                ai_mapping[base_name].append({
                    "ai_tool": ai_tool,
                    "file_id": file_id
                })

            progress_bar.progress(70)

            # 5️⃣ Process Batch
            with status_placeholder.container():
                st.info("⚡ Calculating WER scores... Processing files...")
            
            results = []

            for original in original_files:

                original_filename = original["name"]
                base_name = os.path.splitext(original_filename)[0]

                if base_name not in ai_mapping:
                    continue

                # Download original once
                original_content = download_file_content(service, original["id"])
                original_text = parse_srt(original_content)

                for ai in ai_mapping[base_name]:

                    ai_content = download_file_content(service, ai["file_id"])
                    ai_text = parse_srt(ai_content)

                    wer_result = calculate_wer(original_text, ai_text)

                    wer_score = wer_result["wer"]

                    results.append({
                        "File Name": base_name,
                        "AI Tool": ai["ai_tool"],
                        "WER Score (%)": round(wer_score, 2)
                    })

            progress_bar.progress(100)

            # Clear progress indicators
            progress_placeholder.empty()
            status_placeholder.empty()

            # 6️⃣ Display Results
            if results:
                st.toast("✅ WER evaluation report generated successfully!", icon="✅")
                st.session_state["wer_results"] = results
                st.session_state["result_language"] = selected_language
                st.session_state["result_month"] = selected_month
                st.session_state["result_year"] = selected_year
                
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.error(f"❌ An error occurred during processing: {str(e)}")

# Display persisted results
if "wer_results" in st.session_state and st.session_state["wer_results"]:
    results = st.session_state["wer_results"]
    selected_language = st.session_state.get("result_language", "")
    selected_month = st.session_state.get("result_month", "")
    selected_year = st.session_state.get("result_year", "")
    
    import pandas as pd
    df_results = pd.DataFrame(results)
    
    # Display results table
    st.markdown("<h3 style='margin-top: 30px;'>Detailed Results</h3>", unsafe_allow_html=True)
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    # Export option
    csv = df_results.to_csv(index=False)
    
    # Download button with callback
    def mark_download_clicked():
        st.session_state["download_clicked"] = True
    
    st.download_button(
        label="📥 Download Results as CSV" if not st.session_state.get("download_clicked") else "📥 Download Results Again",
        data=csv,
        file_name=f"wer_report_{selected_language}_{selected_month}_{selected_year}.csv",
        mime="text/csv",
        on_click=mark_download_clicked
    )
    
    # Show success message after download
    if st.session_state.get("download_clicked"):
        col1, col2 = st.columns([20, 1])
        with col1:
            st.success("✅ Download completed successfully!")
        with col2:
            if st.button("✕", key="close_msg_btn", help="Close message"):
                st.session_state["download_clicked"] = False
                st.rerun()
            elif generate_clicked:
                # If generate was clicked but no results found
                st.warning("⚠️ No matching Original-AI file pairs found. Please check your file naming conventions.")

    
    # Calculate tool-wise statistics
    tool_stats = df_results.groupby("AI Tool")["WER Score (%)"].agg(["mean", "min", "max"]).round(2)
    tool_stats.columns = ["Average WER", "Best Score", "Worst Score"]
    
    # Find best and worst performing tools
    best_tool = tool_stats["Average WER"].idxmin()
    best_wer = tool_stats.loc[best_tool, "Average WER"]
    worst_tool = tool_stats["Average WER"].idxmax()
    worst_wer = tool_stats.loc[worst_tool, "Average WER"]
    
    # Display summary metrics
    st.markdown("<h3 style='margin-top: 30px;'>📊 Performance Summary</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-radius: 12px; padding: 20px; text-align: center;">
            <p style="color: #065f46; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;">🏆 Best Performing Tool</p>
            <p style="color: #047857; font-size: 24px; font-weight: 700; margin: 0;">{best_tool}</p>
            <p style="color: #059669; font-size: 13px; margin: 8px 0 0 0;">Avg WER: {best_wer}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-radius: 12px; padding: 20px; text-align: center;">
            <p style="color: #991b1b; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;">⚠️ Low Performing Tool</p>
            <p style="color: #dc2626; font-size: 24px; font-weight: 700; margin: 0;">{worst_tool}</p>
            <p style="color: #b91c1c; font-size: 13px; margin: 8px 0 0 0;">Avg WER: {worst_wer}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); border-radius: 12px; padding: 20px; text-align: center;">
            <p style="color: #1e40af; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;">📈 Total Tools</p>
            <p style="color: #1e3a8a; font-size: 24px; font-weight: 700; margin: 0;">{len(tool_stats)}</p>
            <p style="color: #1e40af; font-size: 13px; margin: 8px 0 0 0;">Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display tool-wise average WER table
    st.markdown("<h3 style='margin-top: 30px;'>Tool-wise WER Metrics</h3>", unsafe_allow_html=True)
    st.dataframe(tool_stats, use_container_width=True)
    
    # Download tool-wise metrics
    tool_metrics_csv = tool_stats.to_csv()
    st.download_button(
        label="📥 Download Tool Metrics as CSV",
        data=tool_metrics_csv,
        file_name=f"wer_tool_metrics_{selected_language}_{selected_month}_{selected_year}.csv",
        mime="text/csv"
    )
    
    