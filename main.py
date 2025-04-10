# main.py - Entry point for the Streamlit application

print("--> Importing main.py")
import streamlit as st
import re
print("--> main.py: Imported streamlit")
from app.db_config import get_schema, run_query
print("--> main.py: Imported db_config functions")
from app.llm_utils import generate_sql
print("--> main.py: Imported llm_utils function")

def extract_sql_from_response(text):
    # Using regex to find SQL block marked with ```sql ... ```
    print(f"--> extract_sql: Input text (first 100 chars): {text[:100]}...")
    matches = re.findall(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    print(f"--> extract_sql: Regex matches found: {matches}")
    if matches:
        raw_match = matches[0]
        print(f"--> extract_sql: Raw match before strip: '{raw_match}'")
        stripped_match = raw_match.strip()
        print(f"--> extract_sql: Stripped match: '{stripped_match}'")
        print(f"--> extract_sql: Type of stripped match: {type(stripped_match)}")
        return stripped_match
    else:
        print("--> extract_sql: No SQL block found.")
        return None

print("--> main.py: Running st.set_page_config()")
st.set_page_config(page_title="Text-to-SQL Internal Tool")
print("--> main.py: Running st.title()")
st.title("Ask Your Database Anything")

print("--> main.py: Running st.text_input()")
question = st.text_input("Enter your question:")

print(f"--> main.py: Question entered: {bool(question)}")
if question:
    print("--> main.py: Entering 'if question:' block")
    # with st.spinner("Generating SQL and fetching results..."): # Temporarily removed for debugging
    print("--> main.py: Calling get_schema()")
    schema = get_schema()
    print("--> main.py: Calling generate_sql()") # Added explicit log
    sql_response = generate_sql(schema, question)
    print(f"--> main.py: Full LLM response received: {sql_response[:100]}...")

    # Extract SQL from the response
    extracted_sql = extract_sql_from_response(sql_response)
    print(f"--> main.py: Extracted SQL: {extracted_sql[:50] if extracted_sql else 'None'}...")

    if extracted_sql:
        print(f"--> main.py: Attempting to display SQL with st.code():\n{extracted_sql}") # Log full SQL
        st.code(extracted_sql, language="sql") # Display extracted SQL
        try:
            print("--> main.py: Calling run_query() with extracted SQL")
            result = run_query(extracted_sql) # Use extracted SQL
            print("--> main.py: run_query() successful, proceeding")

            # Display the original table first
            print("--> main.py: Calling st.dataframe() with original data")
            if result is not None:
                # --- Add preprocessing for table display --- 
                table_display_df = result.copy()
                print("--> main.py: Starting preprocessing for TABLE display")
                for col in table_display_df.columns:
                    try:
                        col_data = table_display_df[col].dropna()
                        has_lists = any(isinstance(x, list) for x in col_data)
                        if has_lists:
                            # Convert the entire column to string if any lists are present
                            print(f"--> main.py: Preprocessing list-containing column '{col}' for TABLE (converting whole column to string)")
                            table_display_df[col] = table_display_df[col].astype(str)
                    except Exception as e:
                        print(f"--> main.py: Warning - Could not preprocess column '{col}' for TABLE: {e}")
                print("--> main.py: Finished preprocessing for TABLE display")
                # --- End preprocessing for table display ---
                
                st.dataframe(table_display_df) # Display the processed copy
                print("--> main.py: st.dataframe() successful")
            else:
                print("--> main.py: run_query() returned None.")
                st.write("Query returned no results.")

            # Preprocess DataFrame copy for chart compatibility
            if result is not None and not result.empty:
                processed_result = result.copy()
                print("--> main.py: Starting data preprocessing for charts")
                for col in processed_result.columns:
                    # Check if column contains lists mixed with non-lists or only lists
                    try:
                        col_data = processed_result[col].dropna()
                        has_lists = any(isinstance(x, list) for x in col_data)
                        if has_lists:
                            has_non_lists = any(not isinstance(x, list) for x in col_data)
                            if has_non_lists:
                                print(f"--> main.py: Preprocessing mixed-type column '{col}' for charts (converting lists to strings)")
                                processed_result[col] = processed_result[col].apply(lambda x: str(x) if isinstance(x, list) else x)
                            else: # Column contains only lists (and potentially None)
                                print(f"--> main.py: Preprocessing list-only column '{col}' for charts (converting lists to strings)")
                                processed_result[col] = processed_result[col].apply(lambda x: str(x) if isinstance(x, list) else x)
                    except Exception as e:
                        print(f"--> main.py: Warning - Could not preprocess column '{col}': {e}")
                        # Optionally convert the whole column to string as a fallback
                        # processed_result[col] = processed_result[col].astype(str)

                print("--> main.py: Preprocessing for charts finished.")
                
                # Attempt to display charts using the processed data
                if not processed_result.empty:
                    try:
                        print("--> main.py: Preparing chart_data")
                        # Basic check: Use first column as index if suitable, else default index
                        chart_data = processed_result
                        if len(processed_result.columns) > 0:
                            # Check if the first column can be reasonably used as an index
                            # This is a simple heuristic, might need refinement
                            try:
                                # Attempt to check uniqueness, might fail if mixed types persist after str conversion
                                potential_index_col = processed_result.iloc[:, 0]
                                # Ensure we don't try to index on actual list objects if conversion failed somehow
                                if not any(isinstance(x, list) for x in potential_index_col.dropna()):
                                    if potential_index_col.nunique() == len(processed_result):
                                        try:
                                            chart_data = processed_result.set_index(processed_result.columns[0])
                                            print(f"--> main.py: Set column '{processed_result.columns[0]}' as index for charts.")
                                        except Exception as idx_e:
                                            print(f"--> main.py: Could not set index for chart: {idx_e}")
                                            # Proceed with default index
                                    else:
                                        print("--> main.py: First column not unique, using default index for charts.")
                                else:
                                    print("--> main.py: First column still contains lists after processing, using default index for charts.")
                            except TypeError as unique_err:
                                print(f"--> main.py: Could not check uniqueness for index due to types: {unique_err}")
                                # Proceed with default index
                        
                        # Check if there are numeric columns to plot
                        # Note: numeric check might be affected if numbers were in mixed lists and converted to str
                        print("--> main.py: Identifying numeric columns for charts")
                        numeric_cols = chart_data.select_dtypes(include='number').columns
                        
                        if not numeric_cols.empty:
                            print("--> main.py: Attempting to display charts")
                            st.subheader("Charts")
                            # Select first numeric column for basic charts
                            col_to_plot = numeric_cols[0]
                            
                            st.write("Line Chart:")
                            st.line_chart(chart_data[col_to_plot])
                            
                            st.write("Bar Chart:")
                            st.bar_chart(chart_data[col_to_plot])
                            print("--> main.py: Charts displayed")
                        else:
                            print("--> main.py: No numeric columns found for charting.")
                            # Check if there are *any* columns left after potential index setting
                            if not chart_data.columns.empty:
                                print(f"--> main.py: Displaying bar chart for the first available column: {chart_data.columns[0]}")
                                st.subheader("Charts (Non-Numeric)")
                                st.bar_chart(chart_data[chart_data.columns[0]])
                            else:
                                st.write("No data suitable for charting after processing.")
                    except Exception as chart_e:
                        print(f"--> main.py: ERROR displaying charts - {chart_e}")
                        st.warning(f"Could not display charts: {str(chart_e)}")
            elif result is None:
                # Already handled above when displaying the table
                pass
            else: # Result is an empty DataFrame
                print("--> main.py: run_query() returned an empty DataFrame. No charts to display.")
                # st.write("Query returned no results.") # Already shown with table

        except Exception as e:
            # Errors from run_query should be caught there now, but keep this as fallback
            print(f"--> main.py: ERROR in run_query block - {e}")
            st.error(f"Error running SQL: {str(e)}")
    else:
        # Handle case where SQL couldn't be extracted
        print("--> main.py: ERROR - Could not extract SQL from LLM response.")
        st.error("Could not extract SQL query from the response. Please try rephrasing your question.")
        st.text_area("Full Response:", sql_response, height=150) # Show full response for debugging

print("--> Finished executing main.py script")
