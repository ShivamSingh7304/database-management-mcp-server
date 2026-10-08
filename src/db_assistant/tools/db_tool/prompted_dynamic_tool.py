from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from db_assistant.tools.db_tool.execute_read_query import execute_read_query
from db_assistant.tools.db_tool.get_schema import get_schema

import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_sql_with_llm(
    user_question: str,
    schema: str
) -> str:
    """
    Generate a PostgreSQL SQL query from a natural-language
    database question using the LLM.
    """

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an expert PostgreSQL database analyst.

Your task is to convert the user's natural-language
question into a valid PostgreSQL SQL query.

Rules:

1. Generate ONLY SQL.
2. Do not use markdown.
3. Do not include ```sql.
4. Only generate read-only queries.
5. Allowed operations:
   - SELECT
   - WITH
6. Never generate:
   - INSERT
   - UPDATE
   - DELETE
   - DROP
   - ALTER
   - TRUNCATE
   - CREATE
7. Use only tables and columns present in the provided schema.
8. Do not invent tables or columns.
9. Return only the SQL query.

Database schema:

{schema}
"""
        ),
        (
            "human",
            "{question}"
        )
    ])

    chain = prompt | llm

    response = chain.invoke({
        "schema": schema,
        "question": user_question
    })

    sql_query = response.content.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]

    if sql_query.startswith("```"):
        sql_query = sql_query[3:]

    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]

    return sql_query.strip()
def execute_dynamic_query(user_question: str):
    """
    Convert a natural-language database question into SQL
    using an LLM and execute it using execute_read_query().
    """

    try:
        schema = get_schema()

        if not schema:
            return {
                "success": False,
                "error": "Unable to retrieve database schema."
            }
        sql_query = generate_sql_with_llm(
            user_question=user_question,
            schema=schema
        )

        if not sql_query:
            return {
                "success": False,
                "error": "LLM did not generate a SQL query."
            }
        result = execute_read_query(sql_query)
        return {
            "success": result.get("success", False),
            "question": user_question,
            "generated_sql": sql_query,
            "result": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }