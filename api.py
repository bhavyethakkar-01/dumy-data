import streamlit as st
from app import *  # Import everything from your main app

# This file serves as the entry point for Vercel deployment
# It uses the same content as app.py but is structured for serverless deployment

if __name__ == "__main__":
    # Set Streamlit configuration for deployment
    st.set_page_config(
        page_title="Delhi Metro Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Run the main application logic
    main()