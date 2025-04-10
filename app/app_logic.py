# app/app_logic.py
import streamlit as st
import re
import pandas as pd

# Use relative imports as this is inside the 'app' package
from .db_config import get_schema, run_query
from .llm_utils import generate_sql

def extract_sql_from_response(text):
    # Using regex to find SQL block marked with ```sql ... ```
    matches = re.findall(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    # Return the first match stripped of whitespace, or None if no match
    return matches[0].strip() if matches else None

def run_streamlit_app():
    print("--> app_logic.py: Running st.set_page_config()")
    st.set_page_config(page_title="Text-to-SQL Internal Tool")
    print("--> app_logic.py: Running st.title()")
    st.title("Ask Your Database Anything")

    print("--> app_logic.py: Running st.text_input()")
    question = st.text_input("Enter your question:")

    print(f"--> app_logic.py: Question entered: {bool(question)}")
    if question:
        print("--> app_logic.py: Entering 'if question:' block")
        with st.spinner("Generating SQL and fetching results..."):
            print("--> app_logic.py: Calling get_schema()")
            schema = get_schema()
            print("--> app_logic.py: Calling generate_sql()")
            sql_response = generate_sql(schema, question)
            print(f"--> app_logic.py: Full LLM response received: {sql_response[:100]}...")

            # Extract SQL from the response
            extracted_sql = extract_sql_from_response(sql_response)
            print(f"--> app_logic.py: Extracted SQL: {extracted_sql[:50] if extracted_sql else 'None'}...")

            if extracted_sql:
                st.code(extracted_sql, language="sql") # Display extracted SQL
                try:
                    print("--> app_logic.py: Calling run_query() with extracted SQL")
                    # Get the data list and column names
                    result_list, result_columns = run_query(extracted_sql)
                    print(f"--> app_logic.py: Result data: {result_list}")
                    print(f"--> app_logic.py: Result columns: {result_columns}")

                    if result_list is not None and result_columns is not None:
                        # Convert the list of tuples to a pandas DataFrame with columns
                        result_df = pd.DataFrame(result_list, columns=result_columns)
                        # Set the index to start from 1 instead of 0
                        result_df.index = result_df.index + 1
                        print("--> app_logic.py: run_query() successful, calling st.dataframe()")
                        st.dataframe(result_df) # Pass DataFrame with columns to streamlit
                        print("--> app_logic.py: st.dataframe() successful")
                    else:
                        st.warning("Query executed, but no data was returned.")

                except Exception as e:
                    # Errors from run_query should be caught there now, but keep this as fallback
                    print(f"--> app_logic.py: ERROR in run_query block - {e}")
                    st.error(f"Error running SQL: {str(e)}")
            else:
                # Handle case where SQL couldn't be extracted
                print("--> app_logic.py: ERROR - Could not extract SQL from LLM response.")
                st.error("Could not extract SQL query from the response. Please try rephrasing your question.")
                st.text_area("Full Response:", sql_response, height=150) # Show full response for debugging

    print("--> Finished executing run_streamlit_app()")
