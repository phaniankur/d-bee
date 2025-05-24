from typing import Dict, Any, Union
from server.main import DatabaseQueryAssistant
from intent_classifier import IntentClassifier

RESTRICTED_OPERATIONS = {'update', 'delete', 'alter'}

def is_restricted_query(query: str) -> bool:
    print(f"restriction check {query}")
    """Check if the query contains restricted operations."""
    query_start = query.strip().lower().split()[0] if query else ''
    print(f"Restricted? {query_start in RESTRICTED_OPERATIONS}")
    return query_start in RESTRICTED_OPERATIONS

def main_controller(user_prompt: str) -> Dict[str, Any]:
    """
    Process user prompt and execute database query.
    
    Args:
        user_prompt (str): User's input query
        
    Returns:
        Dict[str, Any]: Response containing query results or error message
    """
    if not user_prompt:
        return {"error": "Empty prompt received"}
        
    generated_query = None
    try:
        assistant = DatabaseQueryAssistant()
        prompt = assistant.initialize_prompt(user_prompt, 'execute')
        generated_query = assistant.generate_query(prompt)
        
        print("Generated Query:", generated_query)
        if not isinstance(generated_query, str):
            return {"error": "Generated query is not a valid string"}
            
        if is_restricted_query(generated_query):
            print("RESTRICTED OPERATION DETECTED!!")
            return {
                "message": "warn",
                "query": generated_query,
                "executed_result": {},
            }
        
        query_result = assistant.execute_query(generated_query)
        
        return {
            "message": "success",
            "query": generated_query,
            "executed_result": query_result,
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "message": "error",
            "query": generated_query if 'generated_query' in locals() else None
        }

def execute_controller(query: str) -> Dict[str, Any]:
    try:
        assistant = DatabaseQueryAssistant()
        query_result = assistant.execute_query(query)
        
        return {
            "message": "success",
            "query": query,
            "executed_result": query_result,
        }
    except Exception as e:
        print(f"Error001: {e}")
        return {
            "error": str(e),
            "message": "error",
            "query": query if 'generated_query' in locals() else None
        }