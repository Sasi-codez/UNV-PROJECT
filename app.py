import streamlit as st
import pandas as pd
from io import StringIO

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# Show uploader only if file hasn't been uploaded yet
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Choose a file", key="uploader")
    if uploaded_file is not None:
        # Mark as uploaded
        st.session_state.file_uploaded = True

        # Read and display the file
        # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # df = pd.read_csv(stringio)
        # st.write("Uploaded Data:")
        # st.dataframe(df)

# Optional: Add a reset button to allow re-upload
if st.session_state.file_uploaded:
    if st.button("Upload another file"):
        st.session_state.file_uploaded = False
        st.experimental_rerun()