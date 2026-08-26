import streamlit as st
import requests

st.set_page_config(
    page_title="Register",
    page_icon="📝",
    layout="centered"
)

API_URL = "http://127.0.0.1:8000/register"

st.title("📝 Create New Account")

st.write("Fill in the details below to register.")

fullname = st.text_input("Full Name")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

confirm = st.text_input(
    "Confirm Password",
    type="password"
)

if st.button("Register", use_container_width=True):

    if fullname == "" or email == "" or password == "":
        st.warning("Please fill all fields.")

    elif password != confirm:
        st.error("Passwords do not match.")

    else:

        response = requests.post(
            API_URL,
            data={
                "fullname": fullname,
                "email": email,
                "password": password
            }
        )

        result = response.json()

        if result["status"] == "success":

            st.success(result["message"])

        else:

            st.error(result["message"])

st.divider()

st.info("Already have an account? Login from the Login Page.")