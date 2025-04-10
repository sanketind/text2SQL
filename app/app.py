print("--> Importing app.py")
import streamlit as st
import re
print("--> app.py: Imported streamlit")
from .db_config import get_schema, run_query
print("--> app.py: Imported db_config functions")
from .llm_utils import generate_sql
print("--> app.py: Imported llm_utils function")

def extract_sql_from_response(text):
    # Using regex to find SQL block marked with ```sql ... ```
    matches = re.findall(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    # Return the first match stripped of whitespace, or None if no match
    return matches[0].strip() if matches else None

print("--> app.py: Running st.set_page_config()")
st.set_page_config(page_title="Text-to-SQL Internal Tool")
print("--> app.py: Running st.title()")
st.title("Ask Your Database Anything")

print("--> app.py: Running st.text_input()")
question = st.text_input("Enter your question:")

print(f"--> app.py: Question entered: {bool(question)}")
if question:
    print("--> app.py: Entering 'if question:' block")
    with st.spinner("Generating SQL and fetching results..."):
        print("--> app.py: Calling get_schema()")
        schema = get_schema()
        print("--> app.py: Calling generate_sql()")
        sql_response = generate_sql(schema, question)
        print(f"--> app.py: Full LLM response received: {sql_response[:100]}...")

        # Extract SQL from the response
        extracted_sql = extract_sql_from_response(sql_response)
        print(f"--> app.py: Extracted SQL: {extracted_sql[:50] if extracted_sql else 'None'}...")

        if extracted_sql:
            st.code(extracted_sql, language="sql") # Display extracted SQL
            try:
                print("--> app.py: Calling run_query() with extracted SQL")
                result = run_query(extracted_sql) # Use extracted SQL
                print("--> app.py: run_query() successful, calling st.dataframe()")
                st.dataframe(result)
                print("--> app.py: st.dataframe() successful")
            except Exception as e:
                # Errors from run_query should be caught there now, but keep this as fallback
                print(f"--> app.py: ERROR in run_query block - {e}")
                st.error(f"Error running SQL: {str(e)}")
        else:
            # Handle case where SQL couldn't be extracted
            print("--> app.py: ERROR - Could not extract SQL from LLM response.")
            st.error("Could not extract SQL query from the response. Please try rephrasing your question.")
            st.text_area("Full Response:", sql_response, height=150) # Show full response for debugging

print("--> Finished executing app.py script")
