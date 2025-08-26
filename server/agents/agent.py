from typing import Dict, Any, Optional
from fastapi import HTTPException
from langgraph.graph import StateGraph, END

from server.agents.tools import generate_sql, get_schema_ctx, get_chat_history
from server.agents.tools import execute_sql, validate_sql
from server.agents.state import GraphState

# Initialize the LangGraph workflow
def create_agent():
    """Initialize and return the compiled LangGraph."""
    workflow = StateGraph(GraphState)
    workflow.add_node("get_chat_history", get_chat_history)
    workflow.add_node("get_schema_ctx", get_schema_ctx)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate", validate_sql)
    workflow.add_node("execute", execute_sql)

    workflow.set_entry_point("get_chat_history")
    workflow.add_edge("get_chat_history", "get_schema_ctx")
    workflow.add_edge("get_schema_ctx", "generate_sql")
    workflow.add_edge("generate_sql", "validate")
    workflow.add_edge("validate", "execute")
    workflow.add_edge("execute", END)

    return workflow.compile()

# Initialize the graph
agent = create_agent()

async def process_query(userID: str, prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a natural language query and return the generated SQL.
    
    Args:
        prompt: The natural language query
        session_id: The session ID for chat history
        
    Returns:
        Dict containing the generated SQL or error message
    """
    try:
        # Create a new GraphState instance with the user input and session ID
        state = GraphState.create(user_input=prompt, session_id=session_id, intent="execute", userID=userID)
        
        # Process the state through the graph
        result = await agent.ainvoke(state)
        
        # Convert result to dict if it's not already
        result_dict = dict(result) if hasattr(result, 'items') else {}
        
        # Get the generated SQL and execution result
        generated_sql = result_dict.get('generated_sql', 'No SQL generated')
        executed_result = result_dict.get('execution_result', 'No result executed')
        
        return {
            "message": "success",
            "query": generated_sql,
            "executed_result": executed_result
        }
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
