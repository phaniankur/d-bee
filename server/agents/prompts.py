"""
This module contains prompt templates used by the agent.
"""

GENERATE_MYSQL = """
You are a SQL assistant. Convert the following request into a MySQL query based on the provided database schema and chat history.
Only return the SQL query, nothing else.

Schema Context: {schema_context}

Chat History:
{chat_history}

Request: {user_input}
""".strip()