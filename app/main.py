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
    login_container = st.container()
    with login_container:
        login_user()
    st.stop()

# If logged in → show app
st.sidebar.write(f"Logged in as: {st.session_state['user_email']}")
if st.sidebar.button("Logout"):
    logout_user()



st.title("WER Automation Dashboard")


if st.session_state.get("show_login_success"):
    success_placeholder = st.empty()
    success_placeholder.success("Login Successful 🎯")
    time.sleep(3)
    success_placeholder.empty()
    st.session_state["show_login_success"] = False


st.markdown("### Select Parameters")

# --- Dropdown Options ---
languages = ["English", "Hindi", "Punjabi","Tamil"]
years = ["2022","2023", "2024", "2025"]
months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# --- Layout using columns ---
col1, col2, col3 = st.columns(3)

with col1:
    selected_language = st.selectbox("Language", languages)

with col2:
    selected_year = st.selectbox("Year", years)

with col3:
    selected_month = st.selectbox("Month", months)


# --- Generate Button ---
generate_clicked = st.button("Generate Report")

if generate_clicked:
    with st.spinner("Processing WER report..."):

        service = get_drive_service()

        # 1️⃣ Navigate folder structure
        language_id = traverse_structure(
            service,
            Config.GOOGLE_DRIVE_ROOT_ID,
            selected_year,
            selected_month,
            selected_language
        )

        # 2️⃣ Locate subfolders
        original_folder = find_folder(service, language_id, "Original_Files")
        ai_folder = find_folder(service, language_id, "AI_Generated_Files")

        if not original_folder or not ai_folder:
            st.error("Original or AI folder missing.")
            st.stop()

        original_id = original_folder[0]["id"]
        ai_id = ai_folder[0]["id"]

        # 3️⃣ Fetch all SRT files
        original_files = list_srt_files(service, original_id)
        ai_files = list_srt_files(service, ai_id)

        if not original_files:
            st.warning("No Original files found.")
            st.stop()

        if not ai_files:
            st.warning("No AI files found.")
            st.stop()

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

        # 5️⃣ Process Batch
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
            # st.write("Original Files:")
            # for f in original_files:
            #     st.write(f["name"])

            # st.write("AI Mapping Keys:")
            # for key in ai_mapping.keys():
            #     st.write(key)

        # 6️⃣ Display Results
        if results:
            st.success("Batch processing completed ✅")
            st.dataframe(results)
        else:
            st.warning("No matching Original-AI file pairs found.")


    
    

   
