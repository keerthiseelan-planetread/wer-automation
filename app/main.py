import sys
import os

# Ensure workspace root is in Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.wer_engine.wer_calculater import calculate_wer
from app.config import Config
from app.auth.login import login_user, logout_user
import time
from app.wer_engine.srt_parser import parse_srt
from app.drive.drive_utils import find_folder, list_srt_files, traverse_structure
from app.drive.drive_service import get_drive_service
from app.drive.drive_utils import download_file_content

# Import incremental processing
from app.Services.incremental_processor import process_with_incremental_caching, get_processing_summary
from app.Services.file_matcher import build_ai_mapping, match_original_with_ai


# Configure page
st.set_page_config(
    page_title="WER Automation Dashboard",
    # page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styling
st.markdown("""
<style>
    /* Hide entire Streamlit header */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Hide Streamlit toolbar and header elements */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    .stToolbarActions {
        display: none !important;
    }
    
    [data-testid="stViewerBadge"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Hide header element */
    header {
        display: none !important;
    }
    
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
    
    /* Disabled button styling */
    .stButton > button:disabled {
        background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%) !important;
        color: white !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        box-shadow: 0 2px 8px rgba(107, 114, 128, 0.2) !important;
    }
    
    .stButton > button:disabled:hover {
        transform: none !important;
        box-shadow: 0 2px 8px rgba(107, 114, 128, 0.2) !important;
        background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%) !important;
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

if "generating_report" not in st.session_state:
    st.session_state["generating_report"] = False

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# If not logged in → show login
if not st.session_state["authenticated"]:
    login_user()
    st.stop()

# ===========================
# SIDEBAR - User Info & Logout
# ===========================
with st.sidebar:
    # Add vertical spacing
    st.markdown("")
    
    
    # Display logo in sidebar centered
    sidebar_col1, sidebar_col2, sidebar_col3 = st.columns([1, 1, 1])
    with sidebar_col2:
        st.image("app/assets/logo.jpeg", width=100)
    
    st.markdown("")
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
    if st.button("Logout", width='stretch', key="logout_btn"):
        logout_user()
    
    st.markdown("---")
    
    # Info section
    st.markdown("""
    <div style="color: white; font-size: 12px; opacity: 0.8; margin-top: 30px;">
        <p><strong>WER Automation</strong></p>
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
        <h2 style="margin-top: 0; color: #1e40af;">Analysis Parameters</h2>
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
    
    # Determine button text and disabled state
    has_results = "wer_results" in st.session_state and st.session_state["wer_results"]
    button_text = "🔄 Generate Report Again" if has_results else "🔄 Generate Report"
    button_disabled = st.session_state["generating_report"]
    
    generate_clicked = st.button(
        button_text, 
        width='stretch', 
        key="generate_btn",
        disabled=button_disabled
    )

# Processing and results
if generate_clicked:
    # Clear old results from session state before generating new report
    st.session_state.pop("wer_results", None)
    st.session_state.pop("result_language", None)
    st.session_state.pop("result_month", None)
    st.session_state.pop("result_year", None)
    st.session_state.pop("processing_info", None)
    st.session_state.pop("download_clicked", None)
    st.session_state.pop("metrics_download_clicked", None)
    st.session_state["show_results"] = False  # Hide results while generating
    
    st.session_state["generating_report"] = True
    st.rerun()

if st.session_state["generating_report"]:
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

            # ⚡ Initialize Database and Process with Incremental Caching
            with status_placeholder.container():
                st.info("🗄️ Checking database for cached results...")
            
            try:
                # Call incremental processor
                results_raw, processing_info = process_with_incremental_caching(
                    year=int(selected_year),
                    month=selected_month,
                    language=selected_language,
                    drive_service=service,
                    original_folder_id=original_id,
                    ai_generated_folder_id=ai_id,
                    build_ai_mapping_func=build_ai_mapping,
                    match_original_with_ai_func=match_original_with_ai,
                    download_file_content_func=download_file_content
                )
                
                progress_bar.progress(100)
                
                # Display processing summary
                with status_placeholder.container():
                    if processing_info["status"] == "success":
                        st.success(
                            f"✅ Processing complete!\n\n"
                            f"📊 Results: {processing_info['total_files']} total files\n"
                            f"🆕 Newly processed: {processing_info['newly_processed']}\n"
                            f"💾 From cache: {processing_info['cached_files']}\n"
                            f"⏱️ Processing time: {processing_info['processing_time_seconds']:.2f}s"
                        )
                    elif processing_info["status"] == "partial_success_mongodb_cache":
                        st.warning(
                            f"⚠️ Using MongoDB cached results (processing failed)\n"
                            f"📊 Results: {processing_info['total_files']} files from database cache\n"
                            f"📝 Note: Results are from previous successful run"
                        )
                    elif processing_info["status"] == "partial_success_local_cache":
                        st.warning(
                            f"⚠️ Using local cached results (MongoDB unavailable)\n"
                            f"📊 Results: {processing_info['total_files']} files from local backup\n"
                            f"📝 Note: Results are from previous successful run"
                        )
                    elif processing_info["status"] == "fresh_calculation_no_cache":
                        st.warning(
                            f"⚠️ Fresh calculation (no caching available)\n"
                            f"📊 Results: {processing_info['total_files']} files calculated fresh\n"
                            f"💾 Results saved to local backup for offline access"
                        )
                    elif processing_info["status"] == "critical_failure":
                        st.error(
                            f"❌ Report generation failed:\n"
                            f"{processing_info['error_message']}\n\n"
                            f"Troubleshooting:\n"
                            f"1. Check MongoDB connection\n"
                            f"2. Verify Google Drive access\n"
                            f"3. Check file permissions"
                        )
                    else:
                        st.error(f"❌ Processing failed: {processing_info['error_message']}")
                
                # Format results for display (transform from MongoDB format to display format)
                results = []
                for result in results_raw:
                    if result.get('file_status') != 'archived':  # Skip archived files
                        wer_score = result.get('wer_score', 0)
                        # Handle different data types
                        if isinstance(wer_score, dict):
                            wer_score = wer_score.get('$numberDouble', wer_score.get('$numberInt', 0))
                        try:
                            wer_score = float(wer_score)
                        except (ValueError, TypeError):
                            wer_score = 0.0
                        
                        results.append({
                            "File Name": result.get('base_name', 'Unknown'),
                            "AI Tool": result.get('ai_tool', 'Unknown'),
                            "WER Score (%)": round(wer_score, 2)
                        })
                
                # Clear progress indicators
                progress_placeholder.empty()
                status_placeholder.empty()
                
                # Display results if any
                if results:
                    st.toast("WER evaluation report generated successfully!", icon="✅")
                    st.session_state["wer_results"] = results
                    st.session_state["result_language"] = selected_language
                    st.session_state["result_month"] = selected_month
                    st.session_state["result_year"] = selected_year
                    st.session_state["processing_info"] = processing_info  # Store info for display
                    st.session_state["show_results"] = True  # Enable results display
                    st.session_state["generating_report"] = False
                    st.rerun()
                else:
                    st.warning("⚠️ No results to display. The files may have been processed but no WER scores were calculated. Check the terminal logs for details.")
                    st.session_state["generating_report"] = False
                    st.session_state["show_results"] = False
                    
            except Exception as e:
                progress_placeholder.empty()
                status_placeholder.empty()
                st.session_state["generating_report"] = False
                st.session_state["show_results"] = False
                st.error(f"❌ An error occurred during processing: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")
    
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.session_state["generating_report"] = False
        st.session_state["show_results"] = False
        st.error(f"❌ Error during report generation: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

# Display persisted results - only if show_results flag is True
if st.session_state.get("show_results", False) and "wer_results" in st.session_state and st.session_state["wer_results"]:
    # Initialize download state
    if "download_clicked" not in st.session_state:
        st.session_state["download_clicked"] = False
    
    results = st.session_state["wer_results"]
    selected_language = st.session_state.get("result_language", "")
    selected_month = st.session_state.get("result_month", "")
    selected_year = st.session_state.get("result_year", "")
    processing_info = st.session_state.get("processing_info", {})
    
    # Display processing summary
    if processing_info:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Files",
                processing_info.get("total_files", 0)
            )
        
        with col2:
            st.metric(
                "Newly Processed",
                processing_info.get("newly_processed", 0)
            )
        
        with col3:
            st.metric(
                "From Cache",
                processing_info.get("cached_files", 0)
            )
        
        with col4:
            st.metric(
                "Processing Time (s)",
                f"{processing_info.get('processing_time_seconds', 0):.2f}"
            )
    
    # Display Tool Summary
    try:
        tool_summary = get_processing_summary(
            [
                {
                    'base_name': r['File Name'],
                    'ai_tool': r['AI Tool'],
                    'wer_score': r['WER Score (%)'],
                    'file_status': 'current'
                }
                for r in results
            ]
        )
        
        pass
    except Exception as e:
        st.warning(f"Could not generate tool summary: {str(e)}")
    
    # Display results table
    st.markdown("<h3 style='margin-top: 30px;'>Detailed Results</h3>", unsafe_allow_html=True)
    st.dataframe(results, width='stretch', hide_index=True)

    # Export option - create CSV from results list
    import csv
    import io
    
    csv_buffer = io.StringIO()
    if results:
        writer = csv.DictWriter(csv_buffer, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        csv_content = csv_buffer.getvalue()
    else:
        csv_content = ""
    
    # Download button with callback
    def mark_download_clicked():
        st.session_state["download_clicked"] = True
    
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_content,
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
            if st.button("✕", key="close_download_msg", help="Close message"):
                st.session_state["download_clicked"] = False
                st.rerun()

    
    # Calculate tool-wise statistics using native Python
    tool_stats = {}
    for result in results:
        tool = result.get("AI Tool", "Unknown")
        wer_score = result.get("WER Score (%)", 0)
        
        if tool not in tool_stats:
            tool_stats[tool] = []
        tool_stats[tool].append(wer_score)
    
    # Calculate averages, min, max for each tool
    tool_summary = {}
    for tool, scores in tool_stats.items():
        tool_summary[tool] = {
            "Average WER Score": round(sum(scores) / len(scores), 2),
            "Best WER Score": round(min(scores), 2),
            "Worst WER Score": round(max(scores), 2)
        }
    
    # Find best and worst performing tools
    if tool_summary:
        best_tool = min(tool_summary, key=lambda x: tool_summary[x]["Average WER Score"])
        best_wer = tool_summary[best_tool]["Average WER Score"]
        worst_tool = max(tool_summary, key=lambda x: tool_summary[x]["Average WER Score"])
        worst_wer = tool_summary[worst_tool]["Average WER Score"]
    else:
        best_tool = "N/A"
        best_wer = 0
        worst_tool = "N/A"
        worst_wer = 0
    
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
    
    # AI Tool WER Metrics Section
    if tool_summary:
        st.markdown("<h3 style='margin-top: 30px;'>AI Tool WER Metrics</h3>", unsafe_allow_html=True)
        tool_summary_data = []
        for tool, metrics in tool_summary.items():
            tool_summary_data.append({
                "AI Tool": tool,
                "Average WER Score": metrics['Average WER Score'],
                "Best WER Score": metrics['Best WER Score'],
                "Worst WER Score": metrics['Worst WER Score']
            })
        st.dataframe(tool_summary_data, width='stretch', hide_index=True)
        
        # Download button for AI Tool Performance Summary
        import csv
        import io
        
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=["AI Tool", "Average WER Score", "Best WER Score", "Worst WER Score"])
        writer.writeheader()
        writer.writerows(tool_summary_data)
        summary_csv_content = csv_buffer.getvalue()
        
        def mark_metrics_download_clicked():
            st.session_state["metrics_download_clicked"] = True
        
        st.download_button(
            label="📥 Download AI Tool WER Metrics",
            data=summary_csv_content,
            file_name=f"ai_tool_wer_metrics_{selected_language}_{selected_month}_{selected_year}.csv",
            mime="text/csv",
            key="download_summary_btn",
            on_click=mark_metrics_download_clicked
        )
        
        # Show success message after download
        if st.session_state.get("metrics_download_clicked"):
            col1, col2 = st.columns([20, 1])
            with col1:
                st.success("✅ Download completed successfully!")
            with col2:
                if st.button("✕", key="close_metrics_download_msg", help="Close message"):
                    st.session_state["metrics_download_clicked"] = False
                    st.rerun()