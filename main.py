# main.py - Entry point for the Streamlit app
print("--> Importing main.py")

# This should work correctly if run from the project root (d:\text2SQL)
from app.app_logic import run_streamlit_app

if __name__ == "__main__":
    print("--> Starting Streamlit app from main.py")
    run_streamlit_app()
    print("--> Finished running Streamlit app from main.py")
