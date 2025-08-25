from langchain_ollama import OllamaLLM
import re

from server.agents.state import GraphState
from server.main import DatabaseQueryAssistant

# --- classify intent ---
# async def classify_intent(state: GraphState) -> GraphState:
#     text = state.user_input.lower()
#     if "sql" in text or "query" in text:
#         state.intent = "query"
#     elif any(w in text for w in ["show", "list", "all results", "give me data"]):
#         state.intent = "results"
#     else:
#         state.intent = "analysis"
#     return state

# Load local model - using the fully qualified model name from Ollama list
llm = OllamaLLM(model="llama3.1:latest")

async def generate_sql(state: GraphState) -> GraphState:
    try:
        print("\n=== Starting generate_sql ===")
        print("State received:", state)
        
        # Ensure state is properly initialized
        if not state.get('user_input'):
            error_msg = "Error: No user input provided"
            print(error_msg)
            state['generated_sql'] = error_msg
            return state
            
        prompt = f"""
        You are a SQL assistant. Convert the following request into a MySQL query.
        Only return the SQL query, nothing else.
        
        Request: {state['user_input']}
        """.strip()
        
        print("\nSending to LLM:")
        print(prompt)
        
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
        print("\nFinal state:", state)
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
    if any(tok in s for tok in ["DROP ", "TRUNCATE ", "ALTER ", "UPDATE "]):
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
    print("Executing SQL:", state)
    if state.get('intent') == "query":
        print("No execution for query")
        # No execution, just return the query
        return state
    if state.get('error'):
        print("Error in execution exiting query execution:", state.get('error'))
        return state

    sql = state.validated_sql

    try:
        # assistant = DatabaseQueryAssistant()
        # query_result = assistant.execute_query(sql)
        # print("QUERY RESULT", query_result)
        
        # state['execution_result'] = query_result
        state['execution_result'] = "query_result"
    except Exception as e:
        state['error'] = f"Execution error: {e}"
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