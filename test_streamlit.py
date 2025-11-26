
import streamlit as st
import requests

st.title("Connection Test")

url = "http://127.0.0.1:8000/"
st.write(f"Testing connection to {url}...")

if st.button("Test Connection"):
    try:
        response = requests.get(url)
        st.success(f"Status Code: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"Connection failed: {e}")
