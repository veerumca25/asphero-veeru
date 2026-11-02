import streamlit as st


st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Log in"):
    if username == "demo" and password == "demo123":
        st.success("Login successful!")
    else:
        st.error("Incorrect username or password.")
