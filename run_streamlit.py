import streamlit as st
from app.db_config import get_schema, run_query
from app.llm_utils import generate_sql

st.set_page_config(page_title="Text-to-SQL Internal Tool")
st.title("Ask Your Database Anything")

question = st.text_input("Enter your question:")

if question:
    with st.spinner("Generating SQL and fetching results..."):
        schema = get_schema()
        sql = generate_sql(schema, question)
        st.code(sql, language="sql")
        try:
            result = run_query(sql)
            st.dataframe(result)
        except Exception as e:
            # Errors from run_query should still be caught there ideally
            st.error(f"Error running SQL: {str(e)}")
