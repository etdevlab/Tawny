import streamlit as st
from multiapp import MultiApp
from apps import home, organizations, graphexplorer, fingerprintx, sqs

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "backend")
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database

### SIMPLE AUTHENTICATION
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"] and st.session_state["username"] == st.secrets["username"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Username", key="username"
        )
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Username", key="username"
        )
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )        
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if __name__ == "__main__":
    if check_password():
        #PAST AUTHENTICATION PAGE
        app = MultiApp()
        app.add_app("Home", home.app)
        app.add_app("SQS", sqs.app)
        app.add_app("Organizations", organizations.app)
        app.add_app("Graph Explorer", graphexplorer.app)
        app.add_app("FingerprintX", fingerprintx.app)
        app.run()
