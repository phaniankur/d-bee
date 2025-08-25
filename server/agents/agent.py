from typing import Dict, Any
from fastapi import HTTPException
from langgraph.graph import StateGraph, END

from server.agents.tools import generate_sql
from server.agents.tools import execute_sql, validate_sql
from server.agents.state import GraphState

# Initialize the LangGraph workflow
def create_agent():
    """Initialize and return the compiled LangGraph."""
    workflow = StateGraph(GraphState)
    # workflow.add_node("classify", classify_intent)
    # workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate", validate_sql)
    workflow.add_node("execute", execute_sql)
    # workflow.add_node("analyze", analyze_results)

    # workflow.set_entry_point("classify")
    workflow.set_entry_point("generate_sql")
    workflow.add_edge("generate_sql", "validate")
    # workflow.add_edge("validate", "execute")
    workflow.add_edge("validate", "execute")
    # workflow.add_edge("execute", "analyze")

    workflow.add_edge("execute", END)
    # workflow.add_edge("analyze", END)

    return workflow.compile()

# Initialize the graph
agent = create_agent()

async def process_query(prompt: str) -> Dict[str, Any]:
    """
    Process a natural language query and return the generated SQL.
    
    Args:
        prompt: The natural language query
        
    Returns:
        Dict containing the generated SQL or error message
    """
    try:
        # Create a new GraphState instance with the user input and default intent
        state = GraphState.create(user_input=prompt, intent="query")
        
        print("\nState received:", state)
        # Process the state through the graph
        result = await agent.ainvoke(state)
        print("\nFinal result:", result)
        
        # Convert result to dict if it's not already
        result_dict = dict(result) if hasattr(result, 'items') else {}
        
        # Get the generated SQL
        generated_sql = result_dict.get('generated_sql', 'No SQL generated')
        
        return {
            "message": "success",
            "query": generated_sql
        }
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
