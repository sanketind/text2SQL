# Text-to-SQL Internal Tool

## Description

This application provides a web-based interface (using Streamlit) that allows users to ask questions about the `user_business` table in a PostgreSQL database using natural language. The application translates the natural language query into a SQL query using a local AI model (Llama 3.2 via Ollama), executes the generated SQL against the database, and displays the results in a table.

## Architecture & Flow

The application follows this flow:

1.  **User Interface (Streamlit):** The user interacts with a web interface built with Streamlit (defined primarily in `app/app_logic.py` and initiated by `main.py`).
2.  **Input:** The user enters a question in plain English into the text input field.
3.  **Schema Retrieval:** When a question is submitted, the application retrieves the schema information for the `user_business` table from the configured PostgreSQL database (`app/db_config.py`).
4.  **SQL Generation:** The table schema and the user's question are sent to a local Llama 3.2 model via an Ollama API endpoint (`app/llm_utils.py`) to generate the corresponding SQL query.
5.  **SQL Extraction:** The generated SQL query is extracted from the AI model's response (`app/app_logic.py`).
6.  **Database Query:** The extracted SQL query is executed against the PostgreSQL database (`app/db_config.py`).
7.  **Results Display:** The results fetched from the database are displayed to the user in a structured table (DataFrame) within the Streamlit interface (`app/app_logic.py`).

**Key Files:**

*   `main.py`: The main entry point to start the application.
*   `app/app_logic.py`: Contains the core Streamlit UI layout and the primary application logic coordinating the steps.
*   `app/db_config.py`: Handles database connection, schema retrieval, and SQL query execution using Langchain and SQLAlchemy.
*   `app/llm_utils.py`: Interfaces with the local Ollama API (using `requests`) to generate SQL queries from natural language.
*   `requirements.txt`: Lists the necessary Python dependencies.
*   `.env.example`: Template for the required environment variables.
*   `README.md`: This file.

## Configuration

The application requires certain environment variables to be set for accessing the database.

1.  Ensure Ollama is installed and running locally, serving the `llama3.2` model at `http://localhost:11434`.
2.  Create a file named `.env` in the project root directory.
3.  Copy the contents of `.env.example` into `.env`.
4.  Replace the placeholder values in `.env` with your actual credentials:
    *   `DATABASE_URL`: Your PostgreSQL database connection string in the format `postgresql+psycopg2://user:password@host:port/dbname`.

## Dependencies

The main dependencies are:

*   `streamlit`: For the web application framework.
*   `langchain`, `langchain-community`: For core language model utilities (like prompt templating).
*   `requests`: For making HTTP requests to the Ollama API.
*   `python-dotenv`: For loading environment variables from the `.env` file.
*   `psycopg2-binary`: PostgreSQL adapter for Python.
*   `pandas`: For data manipulation and displaying results in a DataFrame.

See `requirements.txt` for the full list.

## Setup and Running

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd text2SQL
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    *   Create the `.env` file as described in the **Configuration** section above.
    *   Ensure Ollama is running with the `llama3.2` model.
5.  **Run the application:**
    ```bash
    python main.py
    ```
    This will start the Streamlit server, and you should see output in your terminal indicating the URL to access the application (usually `http://localhost:8501`). Open this URL in your web browser.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone your-repo-url
cd text-to-sql-internal-tool
```

### 2. Create a Virtual Environment & Install Packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables & Ollama

*   Ensure Ollama is running locally with the `llama3.2` model available.
*   Copy `.env.example` to `.env` and fill in:

```bash
DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
```

### 4. Run the App

```bash
streamlit run app/app.py
```

## Example Questions

- Who are the top 5 customers by revenue?
- What are the average sales by region in the last 30 days?
- List all pending invoices over $500

## Tech Stack

- Python + Streamlit
- LangChain + Ollama (Llama 3.2)
- PostgreSQL (via SQLAlchemy)
- Cursor AI-friendly structure

---

> Secure this internally. Use read-only DB users and LLM logging if needed.

---
