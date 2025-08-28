from typing import Dict, List, Optional, TypedDict, Any, Union, Tuple

class GraphState(TypedDict, total=False):
    """State for the graph with typed dictionary."""
    sessionID: Optional[str] = None
    user_input: str
    intent: str = "query"  # "query" | "results" | "analysis"
    generated_sql: Optional[str]
    validated_sql: Optional[str] = None
    validation_report: Dict[str, Any] = {}
    execution_result: Optional[List[Dict[str, Any]]] = None
    final_answer: Optional[str] = None
    error: Optional[str] = None
    schema_context: Optional[str] = None
    chat_history: Optional[List[Tuple[str, str]]] = None
    
    @classmethod
    def create(cls, **kwargs) -> 'GraphState':
        """Create a new GraphState instance with default values."""
        state: GraphState = {
            'sessionID': None,
            'user_input': '',
            'intent': '',
            'generated_sql': None,
            'validated_sql': None,
            'validation_report': {},
            'execution_result': None,
            'final_answer': None,
            'error': None,
            'schema_context': None,
            'chat_history': [],
            **kwargs
        }
        return state
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GraphState':
        """Create a GraphState from a dictionary."""
        return cls.create(**data)