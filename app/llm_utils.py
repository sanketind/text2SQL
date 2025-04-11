import requests
from langchain.prompts import PromptTemplate
import streamlit as st
import time
from .prompts import SQL_TEMPLATE

prompt_template = PromptTemplate(
    input_variables=["schema", "question"],
    template=SQL_TEMPLATE,
)

def generate_sql(schema, question):
    """Generates SQL query using local Ollama LLM."""
    # Format the prompt using the template
    formatted_prompt = prompt_template.format(schema=schema, question=question)
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"--> Attempt {attempt + 1} to call Ollama API")
            # Call the Ollama API
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.2",  # Using llama3.2 as it's available
                "prompt": formatted_prompt,
                "stream": False
            }, timeout=120)  # 120 second timeout
            
            res.raise_for_status()  # Raise an exception for bad status codes
            response_data = res.json()
            
            if 'response' in response_data:
                sql_result = response_data['response'].strip()
                return sql_result
            else:
                error_msg = "Error: 'response' key not found in Ollama API response."
                print(f"--> {error_msg}")
                print(f"--> Full response: {response_data}")
                if attempt == max_retries - 1:  # Last attempt
                    st.error(error_msg)
                    st.json(response_data)
                    st.stop()
                    
        except requests.exceptions.Timeout:
            error_msg = f"Timeout on attempt {attempt + 1} of {max_retries}"
            print(f"--> {error_msg}")
            if attempt == max_retries - 1:  # Last attempt
                st.error(f"Error calling Ollama API: Request timed out after {max_retries} attempts")
                st.stop()
            time.sleep(retry_delay)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error on attempt {attempt + 1}: {str(e)}"
            print(f"--> {error_msg}")
            if attempt == max_retries - 1:  # Last attempt
                st.error(f"Error calling Ollama API: {str(e)}")
                st.stop()
            time.sleep(retry_delay)
            
        except Exception as e:
            error_msg = f"Unexpected error on attempt {attempt + 1}: {str(e)}"
            print(f"--> {error_msg}")
            if attempt == max_retries - 1:  # Last attempt
                st.error(f"An unexpected error occurred: {str(e)}")
                st.stop()
            time.sleep(retry_delay)
    
    st.error("Failed to generate SQL after all retry attempts")
    st.stop()
