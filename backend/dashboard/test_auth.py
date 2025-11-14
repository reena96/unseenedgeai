"""Test streamlit-authenticator setup"""

import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Auth Test")

# Simple credentials
credentials = {
    "usernames": {
        "teacher": {
            "name": "Teacher",
            "password": "password123",  # Plain text for testing
        }
    }
}

# Create authenticator
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="test_cookie",
    cookie_key="test_key_12345",
    cookie_expiry_days=1,
    auto_hash=True,  # Auto-hash the plain text password
)

# Try login
st.title("Authentication Test")

try:
    result = authenticator.login(location="main")
    st.write(f"Login result type: {type(result)}")
    st.write(f"Login result: {result}")

    if result:
        name, authentication_status, username = result
        st.write(f"Name: {name}")
        st.write(f"Status: {authentication_status}")
        st.write(f"Username: {username}")

        if authentication_status:
            st.success(f"Welcome {name}!")
            authenticator.logout(button_name="Logout", location="sidebar")
        elif authentication_status == False:
            st.error("Username/password incorrect")
        else:
            st.warning("Please enter credentials")
    else:
        st.error("Login returned None!")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback

    st.code(traceback.format_exc())
