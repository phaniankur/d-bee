from typing import Dict, Any, Optional
from fastapi import HTTPException
from langgraph.graph import StateGraph, END

from server.agents.tools import explain_results, generate_sql, get_schema_ctx, get_chat_history, get_tables, intent_classifier, llm_intent_classifier
from server.agents.tools import execute_sql, validate_sql, chitchat
from server.agents.state import GraphState

# Initialize the LangGraph workflow
def create_agent():
    """Initialize and return the compiled LangGraph."""
    workflow = StateGraph(GraphState)

    workflow.add_node("get_chat_history", get_chat_history)
    workflow.add_node("get_schema_ctx", get_schema_ctx)
    workflow.add_node("intent_classifier", llm_intent_classifier)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate", validate_sql)
    workflow.add_node("execute", execute_sql)
    workflow.add_node("get_tables", get_tables)
    workflow.add_node("explain_results", explain_results)
    workflow.add_node("chitchat", chitchat)

    workflow.set_entry_point("get_chat_history")
    
    # Conditional edges from intent_classifier
    workflow.add_conditional_edges(
        "intent_classifier",
        lambda state: state.get("intent"),
        {
            "sql_query": "generate_sql",
            "execute": "generate_sql",
            "explain_results": "generate_sql",
            "chitchat": "chitchat",   # 🔑 funnel chitchat through history
            # 🔑 can be extended to other intents
        },
    )

    # After Execution, decide where to go
    workflow.add_conditional_edges(
        "execute",
        lambda state: state.get("intent"),
        {
            "explain_results": "explain_results",
            "execute": END,
        },
    )

    workflow.add_edge("get_chat_history", "get_schema_ctx")
    workflow.add_edge("get_chat_history", "get_tables")

    # workflow.add_edge("get_chat_history", "intent_classifier")
    workflow.add_edge("get_schema_ctx", "intent_classifier")
    workflow.add_edge("get_tables", "intent_classifier")

    # workflow.add_edge("get_chat_history", "get_schema_ctx")
    # workflow.add_edge("get_schema_ctx", "get_tables")
    # workflow.add_edge("get_tables", "intent_classifier")
    # workflow.add_edge("get_chat_history", "get_schema_ctx")
    # workflow.add_edge("get_schema_ctx", "generate_sql")
    workflow.add_edge("generate_sql", "validate")
    workflow.add_edge("validate", "execute")
    workflow.add_edge("execute", END)
    workflow.add_edge("chitchat", END)

    return workflow.compile()

# Initialize the graph
agent = create_agent()

async def process_query(userID: str, prompt: str, sessionID: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a natural language query and return the generated SQL.
    
    Args:
        prompt: The natural language query
        sessionID: The session ID for chat history
        
    Returns:
        Dict containing the generated SQL or error message
    """
    try:
        # Create a new GraphState instance with the user input and session ID
        state = GraphState.create(user_input=prompt, sessionID=sessionID, userID=userID)
        
        # Process the state through the graph
        result = await agent.ainvoke(state)
        
        # Convert result to dict if it's not already
        result_dict = dict(result) if hasattr(result, 'items') else {}
        
        # Get the generated SQL and execution result
        generated_sql = result_dict.get('generated_sql', 'No SQL generated')
        executed_result = result_dict.get('execution_result', 'No result executed')
        final_answer = result_dict.get('final_answer', 'No final answer')
        
        return {
            "message": "success",
            "query": generated_sql,
            "executed_result": executed_result,
            "final_answer": final_answer
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Error processing query at {e.__traceback__.tb_lineno}: {str(e)}\n\nStack Trace:\n{error_trace}"
        print(f"\n=== ERROR DETAILS ===\n{error_msg}\n===================")
        raise HTTPException(status_code=500, detail=error_msg)
