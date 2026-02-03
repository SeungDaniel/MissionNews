import streamlit as st
import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv
from src.user_manager import UserManager

load_dotenv()

# Singleton for UserManager (Request Scope is fine, or simple init)
def get_user_manager():
    return UserManager()

def get_authenticator():
    """
    Creates and returns a Streamlit Authenticator object based on users.yaml.
    """
    user_manager = get_user_manager()
    credentials = user_manager.get_credentials_dict()

    cookie_name = os.getenv("AUTH_COOKIE_NAME", "mnap_auth")
    cookie_key = os.getenv("AUTH_COOKIE_KEY", "random_key_signature_must_change")
    expiry_days = 30

    # Initialize Authenticator
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        expiry_days
    )

    return authenticator

def get_user_role():
    """
    Returns the role of the currently authenticated user.
    """
    if st.session_state.get("authentication_status"):
        username = st.session_state.get("username")
        user_manager = get_user_manager()
        user = user_manager.get_user(username)
        if user:
            return user.get('role', 'operator')
    return None
