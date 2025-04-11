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
            # Get column names first
            columns = list(result_proxy.keys())
            
            # Fetch and convert data more carefully
            data_list = []
            for row in result_proxy.fetchall():
                # Convert each row to a list of values, handling potential special types
                row_values = []
                for value in row:
                    # Convert any special types to their string representation if needed
                    if value is None:
                        row_values.append(None)
                    else:
                        try:
                            # Try direct conversion first
                            row_values.append(value)
                        except:
                            # Fallback to string representation
                            row_values.append(str(value))
                data_list.append(row_values)
            
            print(f"--> run_query: Columns: {columns}")
            print(f"--> run_query: First row (if any): {data_list[0] if data_list else 'No data'}")
            
            # Create DataFrame with processed data
            df = pd.DataFrame(data_list, columns=columns)
            return df
    except Exception as e:
        st.error(f"Error running SQL query: {e}")
        st.code(sql, language="sql")
        # Return empty DataFrame on error
        return pd.DataFrame()
