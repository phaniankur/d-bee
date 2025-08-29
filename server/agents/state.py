from typing import Dict, List, Optional, TypedDict, Any, Union, Tuple

class GraphState(TypedDict, total=False):
    """State for the graph with typed dictionary."""
    sessionID: Optional[str] = None
    userID: Optional[str] = None
    user_input: str
    intent: str = "sql_query"  # "sql_query" | "chitchat" | "execute" | "explain_results"
    generated_sql: Optional[str]
    validated_sql: Optional[str] = None
    validation_report: Dict[str, Any] = {}
    execution_result: Optional[List[Dict[str, Any]]] = None
    final_answer: Optional[str] = None
    error: Optional[str] = None
    schema_context: Optional[str] = None
    chat_history: Optional[List[Tuple[str, str]]] = None
    tables: Optional[List[str]] = None
    
    @classmethod
    def create(cls, user_input: str, sessionID: str, userID: str) -> 'GraphState':
        """Create a new GraphState instance with default values."""
        return GraphState(
            sessionID=sessionID,
            userID=userID,
            user_input=user_input,
            intent="sql_query",
            generated_sql=None,
            validated_sql=None,
            validation_report={},
            execution_result=None,
            final_answer=None,
            error=None,
            schema_context=None,
            chat_history=[],
            tables=None
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GraphState':
        """Create a GraphState from a dictionary."""
        return cls.create(
            user_input=data.get('user_input', ''),
            sessionID=data.get('sessionID'),
            userID=data.get('userID')
        )