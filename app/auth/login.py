import streamlit as st
from config import Config
import bcrypt


def login_user():
    st.subheader("Login")

    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login"):

        allowed_users = Config.get_allowed_users()

        # Check if email exists
        if email.strip() not in allowed_users:
            st.error("Unauthorized email ❌")
            return

        stored_hash = allowed_users[email.strip()].encode("utf-8")

        # Validate password
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):

            st.session_state["authenticated"] = True
            st.session_state["user_email"] = email
            st.session_state["show_login_success"] = True
            st.rerun()

        else:
            st.error("Incorrect password ❌")

def logout_user():
    st.session_state.clear()
    st.rerun()
