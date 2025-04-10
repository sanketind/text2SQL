from langchain_community.utilities import SQLDatabase
from app.config import DATABASE_URL
import streamlit as st
from sqlalchemy import text
import pandas as pd

@st.cache_resource
def get_db():
    if not DATABASE_URL:
        st.error("DATABASE_URL not found in environment variables. Please check your .env file.")
        st.stop()
    try:
        db = SQLDatabase.from_uri(
            DATABASE_URL,
            include_tables=["user_business", "channel_whatsapp"],  # Only include user_business table
            sample_rows_in_table_info=0  # Disable sample rows
        )
        db.run("SELECT 1")
        return db
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.error(f"Connection String used (check credentials/host): {DATABASE_URL}")
        st.stop()

def get_schema():
    db_conn = get_db()
    try:
        info = db_conn.get_table_info()
        return info
    except Exception as e:
        st.error(f"Error getting table schema: {e}")
        st.stop()

def run_query(sql):
    db_conn = get_db() # Langchain SQLDatabase object
    engine = db_conn._engine # Access the underlying SQLAlchemy engine
    try:
        with engine.connect() as connection:
            result_proxy = connection.execute(text(sql)) # Use SQLAlchemy text for safety
            data = result_proxy.fetchall() # Fetch all rows
            columns = list(result_proxy.keys()) # Get column names
            print(f"--> run_query: Columns: {columns}, Data: {data}")
            # Convert data to list of lists/tuples if needed (fetchall often returns list of Row objects)
            data_list = [tuple(row) for row in data]
            # Create and return a Pandas DataFrame
            df = pd.DataFrame(data_list, columns=columns)
            return df
    except Exception as e:
        st.error(f"Error running SQL query: {e}")
        st.code(sql, language="sql")
        # Return empty DataFrame on error
        return pd.DataFrame()
