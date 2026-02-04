import streamlit as st
import streamlit_authenticator as stauth
import os
import warnings
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
    cookie_key = os.getenv("AUTH_COOKIE_KEY", "")
    expiry_days = 30

    # 보안 경고: AUTH_COOKIE_KEY가 설정되지 않았거나 기본값인 경우
    insecure_defaults = ["", "random_key_signature_must_change", "random_signature_key_change_this"]
    if cookie_key in insecure_defaults:
        warnings.warn(
            "보안 경고: AUTH_COOKIE_KEY 환경변수가 설정되지 않았거나 기본값입니다. "
            "프로덕션 환경에서는 반드시 안전한 랜덤 키를 설정하세요. "
            "예: AUTH_COOKIE_KEY=$(openssl rand -hex 32)",
            UserWarning
        )
        # 개발 환경에서는 기본값 사용 (프로덕션에서는 경고만)
        if not cookie_key:
            cookie_key = "dev_only_insecure_key_please_change"

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
