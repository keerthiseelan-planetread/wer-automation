import streamlit as st
from config import Config
import bcrypt


def apply_login_styles():
    """Apply professional styling to login page"""
    st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        /* Login container */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        /* Main input styling */
        .stTextInput > div > div > input {
            border: 2px solid #e0e7ff !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #9ca3af !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Alert styling */
        .stAlert {
            border-radius: 8px !important;
            border: none !important;
        }
        
        .stError {
            background-color: #fee2e2 !important;
            color: #991b1b !important;
        }
        
        /* Label styling */
        .stTextInput > label {
            color: #1f2937 !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def login_user():
    """Professional login page"""
    apply_login_styles()
    
    # Create centered layout
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 40px; margin-top: 60px;">
            <h1 style="color: #1f2937; margin: 0; font-size: 32px;">WER Automation Tool</h1>
            <p style="color: #6b7280; margin-top: 8px; font-size: 16px;">AI Transcription Evaluation & Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form container
        # st.markdown("""
        # <div style="background: black; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);">
        # """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #1f2937; margin-top: 0;'>Sign In</h2>", unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
        
        # Login button
        if st.button("Sign In", use_container_width=True, key="login_btn"):
            if not email or not password:
                st.error("Please fill in all fields")
                return
            
            allowed_users = Config.get_allowed_users()

            # Check if email exists
            if email.strip() not in allowed_users:
                st.error("❌ Unauthorized email. Please contact administrator.")
                return

            stored_hash = allowed_users[email.strip()].encode("utf-8")

            # Validate password
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = email
                st.session_state["show_login_success"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px;">
            <p>Protected Access • Version 1.0</p>
        </div>
        """, unsafe_allow_html=True)


def logout_user():
    """Logout and clear session"""
    st.session_state.clear()
    st.rerun()
