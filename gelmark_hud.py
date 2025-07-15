# DIAGNOSTIC SCRIPT for Streamlit File Writing

import streamlit as st
import os

st.title("File Writing Test")

# Define the path where we will try to write the file
TARGET_DIR = "my_gm"
TEST_FILE_PATH = os.path.join(TARGET_DIR, "test_write.txt")

st.info(f"This script will try to write a test file to the path: '{TEST_FILE_PATH}'")

if st.button("Attempt to Write File"):
    
    st.write("---")
    st.write(f"Current Working Directory: `{os.getcwd()}`")
    
    # Check if the target directory exists
    if not os.path.isdir(TARGET_DIR):
        st.error(f"Error: The directory '{TARGET_DIR}' does not exist. Please create it.")
    else:
        st.success(f"Directory '{TARGET_DIR}' found.")
        
        # Try to write the file
        try:
            with open(TEST_FILE_PATH, 'w') as f:
                f.write("If you can see this, the Streamlit app has permission to write files.")
            
            st.success("✅ SUCCESS! The file was written without errors.")
            st.balloons()
            st.write("You should now be able to find a 'test_write.txt' file inside your 'my_gm' folder in the repository.")
            
        except Exception as e:
            st.error("❌ FAILED. An error occurred while trying to write the file.")
            st.exception(e) # This will display the full error message