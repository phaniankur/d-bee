from langchain_ollama import OllamaLLM
import re

from server.agents.state import GraphState
from server.agents.prompts import GENERAL_CHITCHAT, GENERATE_MYSQL, INTENT_CLASSIFIER
from server.main import DatabaseQueryAssistant
from server.memory import chat_memory

# --- classify intent ---
def intent_classifier(state: GraphState) -> GraphState:
    text = state.get('user_input').lower()
    sql_keywords = ["select", "count", "how many", "show", "list", "find", "users", "orders"]
    
    print("\n=== Intent classification ===")

    if any(kw in text for kw in sql_keywords):
        state['intent'] = "execute"
    else:
        state['intent'] = "chitchat"
    
    print("Classified Intent:", state['intent'])
    print("=== End intent_classifier ===\n")
    return state

# --- llm powered intent ---
async def llm_intent_classifier(state: GraphState) -> GraphState:
    try:
        print("\n=== Starting llm_intent_classifier ===", state)
        allowed_intents = {
            "chitchat": "The user's intent is for general chat and there is no context of database schema or query. Always return this if there is no context of MySQL.",
            "sql_query": "The user's intent is to only generate a MySQL query.",
            "execute": "The user's intent is to generate and execute a MySQL query.",
            "explain_results": "User wants an explanation of results from the query."
        }
        chat_history = state.get('chat_history', [])
        formatted_history = "\n".join([f"{role}: {message}" for role, message in chat_history])

        prompt = INTENT_CLASSIFIER.format(
            allowed_intents=allowed_intents,
            chat_history=formatted_history,
            schema_context=state['tables'],
            user_input=state['user_input']
        )
        
        print("\nSending to LLM:")
        print("PROMPT:", prompt)
        
        try:
            print("\nCalling llm.ainvoke()...")
            # Get raw response from LLM
            response = await llm.ainvoke(prompt)
            print(f"\nRaw LLM response type: {type(response)}")
            print(f"Raw LLM response: {response}")
            
            # Convert response to string if it's not already
            if hasattr(response, 'content'):
                out = response.content
            elif hasattr(response, 'text'):
                out = response.text
            elif isinstance(response, str):
                out = response
            else:
                out = str(response)

            state['intent'] = out
            print("\nProcessed LLM output:", out)
            print("\nUpdated State:", state['intent'])
            
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            print(f"\n{error_msg}")
            print(f"LLM type: {type(llm)}")
            print(f"LLM model: {getattr(llm, 'model', 'unknown')}")
            state['intent'] = f"Error: {error_msg}"
            return state

        return state

    except Exception as e:
        error_msg = f"Error calling LLM: {str(e)}"
        print(f"\n{error_msg}")
        print(f"LLM type: {type(llm)}")
        print(f"LLM model: {getattr(llm, 'model', 'unknown')}")
        state['intent'] = f"Error: {error_msg}"
        return state

# --- Chat History ---
def get_chat_history(state: GraphState) -> dict:
    """
    Retrieves chat history for the current session.
    """
    print("\n=== Getting chat history ===")
    session_id = state.get("sessionID")
    if session_id:
        history = chat_memory.get_history(session_id)
        return {"chat_history": history}
    print("=== End get_chat_history ===\n")
    return {"chat_history": []}

# --- Schema Context ---
def get_schema_ctx(state: GraphState) -> dict:
    """
    Fetch schema context from DB (cached if still valid).
    Append it into agent state.
    """
    print("\n=== Fetching schema context ===")
    db_schema = DatabaseQueryAssistant()
    schema_ctx = db_schema.get_schema_context()
    # print("Schema context:", schema_ctx)
    # state['schema_context'] = schema_ctx
    print("=== End get_schema_ctx ===\n")
    return {"schema_context": schema_ctx}

# --- Tables ---
def get_tables(state: GraphState) -> dict:
    """
    Fetch table names from DB (cached if still valid).
    Append it into agent state.
    """
    print("\n=== Fetching tables ===")
    db_schema = DatabaseQueryAssistant()
    tables = db_schema.get_table_names()
    # print("Schema context:", schema_ctx)
    # state['tables'] = tables
    print("=== End get_tables ===\n")
    # return state
    return {"tables": tables}

# --- GENERATE SQL ---
llm = OllamaLLM(model="llama3.1:latest")

async def generate_sql(state: GraphState) -> GraphState:
    try:
        print("\n=== Starting generate_sql ===")
        # print("State received:", state)
        
        # Ensure state is properly initialized
        if not state.get('user_input'):
            error_msg = "Error: No user input provided"
            print(error_msg)
            state['generated_sql'] = error_msg
            return state
            
        if not state['schema_context']:
            return state

        # Format chat history
        chat_history = state.get('chat_history', [])
        formatted_history = "\n".join([f"{role}: {message}" for role, message in chat_history])
        if not formatted_history:
            formatted_history = "No previous conversation."
            
        prompt = GENERATE_MYSQL.format(
            schema_context=state['schema_context'],
            chat_history=formatted_history,
            user_input=state['user_input']
        )
        
        print("\nSending to LLM:")
        # print("PROMPT:", prompt)
        
        try:
            print("\nCalling llm.ainvoke()...")
            # Get raw response from LLM
            response = await llm.ainvoke(prompt)
            print(f"\nRaw LLM response type: {type(response)}")
            print(f"Raw LLM response: {response}")
            
            # Convert response to string if it's not already
            if hasattr(response, 'content'):
                out = response.content
            elif hasattr(response, 'text'):
                out = response.text
            elif isinstance(response, str):
                out = response
            else:
                out = str(response)
                
            print("\nProcessed LLM output:", out)
            
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            print(f"\n{error_msg}")
            print(f"LLM type: {type(llm)}")
            print(f"LLM model: {getattr(llm, 'model', 'unknown')}")
            state['generated_sql'] = f"Error: {error_msg}"
            return state

        # Extract SQL from markdown code block if present
        try:
            # Clean up the response
            cleaned = out.strip()
            
            # Try to extract SQL from markdown code block
            sql_match = re.search(r"```(?:sql\n)?(.*?)```", cleaned, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
            else:
                # If no code block, use the whole response
                sql = cleaned
                
            # Clean up any remaining markdown or extra text
            sql = re.sub(r'^```sql\n|```$', '', sql, flags=re.MULTILINE).strip()
            
            print("\nExtracted SQL:", sql)
            
        except Exception as e:
            error_msg = f"Error parsing SQL from response: {str(e)}"
            print(f"\n{error_msg}")
            print(f"Response was: {out}")
            sql = f"-- Error: {error_msg}\n-- Original response: {out}"
        
        # Update state with the generated SQL
        state['generated_sql'] = sql
        # print("\nFinal state:", state)
        print("=== End generate_sql ===\n")
        return state
        
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error in generate_sql: {str(e)}\n{traceback.format_exc()}"
        print("\n" + "="*50)
        print("ERROR:", error_msg)
        print("="*50 + "\n")
        
        if not state.get('generated_sql'):
            state['generated_sql'] = f"Error: {str(e)}"
            
        return state


# --- Validate ---
import sqlglot

def validate_sql(state: GraphState) -> GraphState:
    print("Validating SQL:", state.get('generated_sql'))
    sql = state.get('generated_sql')

    try:
        ast = sqlglot.parse_one(sql, dialect="mysql")
    except Exception as e:
        state['error'] = f"SQL parse error: {e}"
        return state

    s = sql.upper()
    if any(tok in s for tok in ["DROP ", "TRUNCATE ", "ALTER ", "UPDATE ", "DELETE "]):
        state['error'] = "Dangerous SQL detected"
        return state

    # Auto add LIMIT if SELECT without one
    # if s.startswith("SELECT") and "LIMIT" not in s:
    #     sql += "\nLIMIT 100"
    #     if 'validation_report' not in state:
    #         state['validation_report'] = {}
    #     state['validation_report']["limit_added"] = True

    state['validated_sql'] = sql
    return state


# --- Execute ---

# MYSQL_DSN_RO = os.getenv("MYSQL_DSN_RO")  # mysql+mysqlconnector://ro_user:pwd@host/db
# engine_ro = create_engine(MYSQL_DSN_RO, pool_pre_ping=True, pool_recycle=3600)

def execute_sql(state: GraphState) -> GraphState:
    # print("Executing SQL:", state)
    if state.get('intent') == "sql_query":
        print("No execution for query")
        # No execution, just return the query
        return state
    if state.get('error'):
        print("Error in execution exiting query execution:", state.get('error'))
        return state

    sql = state.get('validated_sql')

    try:
        assistant = DatabaseQueryAssistant()
        query_result = assistant.execute_query(sql)
        print("QUERY RESULT", query_result)
        
        state['execution_result'] = query_result
        # state['execution_result'] = "query_result"
    except Exception as e:
        state['error'] = f"Execution error: {e}"
    return state


# --- Chitchat ---
async def chitchat(state: GraphState) -> GraphState:
    """
    Handle non-SQL user queries (general chat).
    """
    print("\n=== Chitchat Begin ===")
    prompt = GENERAL_CHITCHAT.format(user_input=state.get('user_input'), chat_history=state.get('chat_history'))
    out = await llm.ainvoke(prompt)
    print("\nLLM OUTPUT:", out)

    state['generated_sql'] = out.content if hasattr(out, "content") else str(out)
    print("=== End chitchat ===\n")
    return state

# --- Analyze Results ---
async def analyze_results(state: GraphState) -> GraphState:
    if state.get('intent') != "analysis" or not state.get('execution_result'):
        return state

    prompt = f"""
    User request: {state.get('user_input')}

    SQL query result (rows):
    {state.get('execution_result')}

    Write a descriptive natural language answer, summarizing the results clearly.
    """

    out = await llm.ainvoke(prompt)
    state['final_answer'] = out.strip()
    return state