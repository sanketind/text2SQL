from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.config import OPENAI_API_KEY
import streamlit as st

TEMPLATE = """
Given this schema:
{schema}

Translate the question to a SQL query:
Question: {question}
SQL:
"""

prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=TEMPLATE,
)

def get_llm():
    """Initializes and returns the Language Model."""
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    try:
        # Initialize ChatOpenAI with the specified model and temperature
        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        )
        # Simple test to ensure API key is valid (optional, depends on library)
        # llm.invoke("test") 
        return llm
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        st.stop()

@st.cache_resource
def get_llm_chain():
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain

def generate_sql(schema, question):
    chain = get_llm_chain()
    try:
        response = chain.invoke({"schema": schema, "question": question})
        if isinstance(response, dict) and 'text' in response:
            sql_result = response['text']
            return sql_result
        sql_result = str(response)
        return sql_result
    except Exception as e:
        st.error(f"Error generating SQL: {e}")
        st.stop()
