import sys
import os

# Add the project root directory (parent of 'app') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("--> Importing app.py")
import streamlit as st
import re
print("--> app.py: Imported streamlit")
from app.db_config import get_schema, run_query
print("--> app.py: Imported db_config functions")
from app.llm_utils import generate_sql
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

                # Attempt to display charts if data is suitable
                if result is not None and not result.empty:
                    try:
                        # Basic check: Use first column as index if suitable, else default index
                        chart_data = result
                        if len(result.columns) > 0:
                            # Check if the first column can be reasonably used as an index
                            # This is a simple heuristic, might need refinement
                            if result.iloc[:, 0].nunique() == len(result):
                                try:
                                    chart_data = result.set_index(result.columns[0])
                                except Exception as idx_e:
                                    print(f"--> app.py: Could not set index for chart: {idx_e}")
                                    # Proceed with default index
                        
                        # Check if there are numeric columns to plot
                        numeric_cols = chart_data.select_dtypes(include='number').columns
                        
                        if not numeric_cols.empty:
                            print("--> app.py: Attempting to display charts")
                            st.subheader("Charts")
                            # Select first numeric column for basic charts
                            # More sophisticated logic could allow user selection
                            col_to_plot = numeric_cols[0]
                            
                            st.write("Line Chart:")
                            st.line_chart(chart_data[col_to_plot])
                            
                            st.write("Bar Chart:")
                            st.bar_chart(chart_data[col_to_plot])
                            print("--> app.py: Charts displayed")
                        else:
                            print("--> app.py: No numeric columns found for charting.")
                            # st.write("No suitable numeric data found for charting.")
                    except Exception as chart_e:
                        print(f"--> app.py: ERROR displaying charts - {chart_e}")
                        st.warning(f"Could not display charts: {str(chart_e)}")

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
